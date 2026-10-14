"""Create or update the Canvas course from the definitions in canvas/.

Usage (from the repository root):

    python canvas/tools/push_to_canvas.py --dry-run      # render to canvas/_build/, no network
    python canvas/tools/push_to_canvas.py --test         # check the connection, list courses
    python canvas/tools/push_to_canvas.py                # push everything
    python canvas/tools/push_to_canvas.py --only lab3    # push one page or assignment

The server, token, and course come from .env at the repository root
(see canvas/.env.example). Canvas IDs are remembered in canvas/canvas_ids.json,
so pushing again updates the same items instead of creating new ones.
"""

import argparse
import json
import os
import sys

from check_sync import report
from course_data import CANVAS, REPO, CourseData

STATE_PATH = CANVAS / 'canvas_ids.json'
BUILD = CANVAS / '_build'


def dry_run(data):
    for folder, items, render in (
        ('pages', data.pages, data.render_page),
        ('assignments', data.assignments, data.render_assignment),
    ):
        (BUILD / folder).mkdir(parents=True, exist_ok=True)
        for key, item in items.items():
            path = BUILD / folder / f'{key}.html'
            path.write_text(f'<h1>{item["title"]}</h1>\n{render(key)}', encoding='utf-8')
            print(f'rendered  {path.relative_to(REPO).as_posix()}')
    print('\nNothing was sent to Canvas.')


def settings(data):
    """Return (url, token, course_id) from .env, falling back to course.yml."""
    from dotenv import load_dotenv

    load_dotenv(REPO / '.env')
    url = os.environ.get('CANVAS_API_URL') or data.course['canvas']['base_url']
    token = os.environ.get('CANVAS_API_TOKEN')
    course_id = os.environ.get('CANVAS_COURSE_ID') or data.course['canvas']['course_id']
    if not token:
        sys.exit('No CANVAS_API_TOKEN. Copy canvas/.env.example to .env and fill it in.')
    return url.rstrip('/'), token, course_id


def test_connection(canvas, url, course_id):
    user = canvas.get_current_user()
    print(f'Server: {url}')
    print(f'Signed in as: {user.name} (id {user.id})\n')
    print('Courses this token can see:')
    for course in canvas.get_courses():
        marker = '  <-- CANVAS_COURSE_ID' if str(course.id) == str(course_id) else ''
        print(f'  {course.id:<8} {getattr(course, "name", "(no name)")}{marker}')
    if not course_id:
        print('\nSet CANVAS_COURSE_ID in .env to one of the IDs above.')


class Pusher:
    def __init__(self, data, course, state):
        from canvasapi.exceptions import ResourceDoesNotExist

        self.missing = ResourceDoesNotExist
        self.data = data
        self.course = course
        self.state = state
        self.publish = bool(data.course['canvas'].get('publish'))

    def _existing(self, kind, key, fetch):
        """Return the Canvas object remembered for an item, or None if it is gone."""
        canvas_id = self.state[kind].get(key)
        if canvas_id is None:
            return None
        try:
            return fetch(canvas_id)
        except self.missing:
            return None

    def _published(self, payload, created):
        # Only ever turn publishing on. With publish off, a new item starts
        # unpublished and an item published by hand in Canvas is left alone.
        if self.publish:
            payload['published'] = True
        elif created:
            payload['published'] = False
        return payload

    def push_assignment_groups(self):
        existing = {group.name: group for group in self.course.get_assignment_groups()}
        ids = {}
        for group in self.data.course['assignment_groups']:
            if group['name'] in existing:
                found = existing[group['name']]
                found.edit(group_weight=group['weight'])
                print(f'updated   assignment group: {group["name"]}')
            else:
                found = self.course.create_assignment_group(name=group['name'], group_weight=group['weight'])
                print(f'created   assignment group: {group["name"]}')
            ids[group['name']] = found.id
        self.course.update(course={'apply_assignment_group_weights': True})
        return ids

    def team_set_id(self):
        """Return the ID of the Canvas group set used for team labs, creating it if needed."""
        name = self.data.course['canvas']['team_group_set']
        for category in self.course.get_group_categories():
            if category.name == name:
                return category.id
        print(f'created   group set: {name}')
        return self.course.create_group_category(name).id

    def push_page(self, key):
        page = self.data.pages[key]
        found = self._existing('pages', key, self.course.get_page)
        payload = self._published({'title': page['title'], 'body': self.data.render_page(key)}, not found)
        if page.get('front_page') and self.publish:
            payload['front_page'] = True
        if found:
            found = found.edit(wiki_page=payload)
            print(f'updated   page: {page["title"]}')
        else:
            found = self.course.create_page(wiki_page=payload)
            print(f'created   page: {page["title"]}')
        # Canvas changes the slug when the title changes, so always record it.
        self.state['pages'][key] = found.url

    def push_assignment(self, key, group_ids, team_set_id):
        assignment = self.data.assignments[key]
        found = self._existing('assignments', key, self.course.get_assignment)
        payload = self._published({
            'name': assignment['title'],
            'description': self.data.render_assignment(key),
            'assignment_group_id': group_ids[assignment['assignment_group']],
        }, not found)
        if assignment.get('points') is not None:
            payload['points_possible'] = assignment['points']
        if assignment.get('submission_types'):
            payload['submission_types'] = assignment['submission_types']
        if assignment['due_at']:
            payload['due_at'] = assignment['due_at']
        if assignment.get('team'):
            payload['group_category_id'] = team_set_id
        if found:
            found.edit(assignment=payload)
            print(f'updated   assignment: {assignment["title"]}')
        else:
            found = self.course.create_assignment(assignment=payload)
            print(f'created   assignment: {assignment["title"]}')
        self.state['assignments'][key] = found.id

    def _module_item(self, item):
        """Return (match key, Canvas payload) for a modules.yml item, or None if it was not pushed."""
        if 'page' in item:
            slug = self.state['pages'].get(item['page'])
            return slug and (('Page', slug), {'type': 'Page', 'page_url': slug})
        if 'assignment' in item:
            canvas_id = self.state['assignments'].get(item['assignment'])
            return canvas_id and (
                ('Assignment', canvas_id), {'type': 'Assignment', 'content_id': canvas_id}
            )
        url = self.data.site_url(item['site'])
        title = self.data.site_title(self.data.docs / f'{item["site"]}.rst')
        return ('ExternalUrl', url), {'type': 'ExternalUrl', 'external_url': url, 'title': title, 'new_tab': True}

    def push_module(self, module, position):
        found = self._existing('modules', module['id'], self.course.get_module)
        payload = {'name': module['name'], 'position': position}
        if found:
            found.edit(module=payload)
            print(f'updated   module: {module["name"]}')
        else:
            found = self.course.create_module(module=payload)
            print(f'created   module: {module["name"]}')
        self.state['modules'][module['id']] = found.id
        if self.publish:
            found.edit(module={'published': True})

        existing = {}
        for item in found.get_module_items():
            target = (
                getattr(item, 'page_url', None)
                or getattr(item, 'content_id', None)
                or getattr(item, 'external_url', None)
            )
            existing[(item.type, target)] = item

        # Items added by hand in Canvas are left in place, below the ones listed here.
        wanted = [entry for entry in map(self._module_item, module['items']) if entry]
        for index, (match, item_payload) in enumerate(wanted, start=1):
            item = existing.get(match)
            if item is None:
                item = found.create_module_item(module_item={**item_payload, 'position': index})
                if self.publish and match[0] == 'ExternalUrl':
                    item.edit(module_item={'published': True})
            elif item.position != index:
                item.edit(module_item={'position': index})

    def push(self, only=None):
        if only:
            if only in self.data.pages:
                self.push_page(only)
            else:
                self.push_assignment(only, self.push_assignment_groups(), self.team_set_id())
            return

        group_ids = self.push_assignment_groups()
        team_set_id = self.team_set_id()
        for key in self.data.pages:
            self.push_page(key)
        for key in self.data.assignments:
            self.push_assignment(key, group_ids, team_set_id)
        for position, module in enumerate(self.data.modules, start=1):
            self.push_module(module, position)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--dry-run', action='store_true', help='render to canvas/_build/ without contacting Canvas')
    parser.add_argument('--test', action='store_true', help='check the connection and list courses')
    parser.add_argument('--only', metavar='ID', help='push one page or assignment, by file name without .md')
    args = parser.parse_args()

    data = CourseData()
    if report(data):
        sys.exit('Fix the errors above before pushing.')
    print()

    if args.only and args.only not in data.pages and args.only not in data.assignments:
        sys.exit(f'No page or assignment named "{args.only}".')

    if args.dry_run:
        dry_run(data)
        return

    from canvasapi import Canvas

    url, token, course_id = settings(data)
    canvas = Canvas(url, token)

    if args.test:
        test_connection(canvas, url, course_id)
        return

    if not course_id:
        sys.exit('No course ID. Run with --test to list courses, then set CANVAS_COURSE_ID in .env.')

    course = canvas.get_course(course_id)
    print(f'Pushing to: {course.name} (id {course.id}) on {url}\n')

    # IDs are kept per server and course, so a test server and the real one do not collide.
    all_state = json.loads(STATE_PATH.read_text(encoding='utf-8')) if STATE_PATH.is_file() else {}
    state = all_state.setdefault(f'{url}#{course_id}', {})
    for kind in ('pages', 'assignments', 'modules'):
        state.setdefault(kind, {})

    try:
        Pusher(data, course, state).push(args.only)
    finally:
        STATE_PATH.write_text(json.dumps(all_state, indent=2) + '\n', encoding='utf-8')

    print(f'\nDone. Canvas IDs saved to {STATE_PATH.relative_to(REPO).as_posix()}.')


if __name__ == '__main__':
    main()
