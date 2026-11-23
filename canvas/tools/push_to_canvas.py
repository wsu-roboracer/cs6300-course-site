"""Create or update the Canvas course from the definitions in canvas/.

Usage (from the repository root):

    python canvas/tools/push_to_canvas.py --dry-run      # render to canvas/_build/, no network
    python canvas/tools/push_to_canvas.py --test         # check the connection, list courses
    python canvas/tools/push_to_canvas.py                # push everything
    python canvas/tools/push_to_canvas.py --only lab3    # push one page or assignment
    python canvas/tools/push_to_canvas.py --only lab2a --only lab2b   # or several
    python canvas/tools/push_to_canvas.py --only module:aeb           # one module and its items

The server, token, and course come from .env at the repository root
(see canvas/.env.example). Canvas IDs are remembered in canvas/canvas_ids.json,
so pushing again updates the same items instead of creating new ones.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlencode

from check_sync import report
from course_data import CANVAS, REPO, CourseData

STATE_PATH = CANVAS / 'canvas_ids.json'
MODULE_PREFIX = 'module:'
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
    def __init__(self, data, course, state, url=None, token=None):
        from canvasapi.exceptions import ResourceDoesNotExist

        self.missing = ResourceDoesNotExist
        self.data = data
        self.course = course
        self.state = state
        self.publish = bool(data.course['canvas'].get('publish'))
        # Rubrics are posted directly: their criteria and ratings are deeply nested
        # form parameters that canvasapi does not model.
        self.url = url
        self.token = token

    def _api(self, method, path, fields):
        request = urllib.request.Request(
            f'{self.url}/api/v1/{path}',
            data=urlencode(fields).encode(),
            method=method,
            headers={'Authorization': f'Bearer {self.token}'},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)

    # Rating ladders, widest first. A criterion worth a lot is worth more steps; a
    # small one does not need five. Each entry is (fraction of the points, label).
    RATING_LADDERS = (
        (20, [(1.0, 'Full credit'), (0.75, 'Minor issues'), (0.5, 'Half working'),
              (0.25, 'Barely working'), (0.0, 'Not demonstrated')]),
        (10, [(1.0, 'Full credit'), (0.75, 'Minor issues'), (0.5, 'Half working'),
              (0.0, 'Not demonstrated')]),
        (4, [(1.0, 'Full credit'), (0.5, 'Partial credit'), (0.0, 'Not demonstrated')]),
        (0, [(1.0, 'Full credit'), (0.0, 'Not demonstrated')]),
    )

    @classmethod
    def _ratings(cls, points):
        """Return the clickable ratings for a criterion worth `points`.

        Canvas shows these as buttons in SpeedGrader, so the grade for a criterion is one
        click. A typed score still overrides them, which is what the rubrics promising
        credit "for the fraction of the loop covered" need.
        """
        ladder = next(steps for floor, steps in cls.RATING_LADDERS if points >= floor)
        ratings, seen = [], set()
        for fraction, label in ladder:
            value = int(round(points * fraction))
            if value in seen:          # rounding can collapse two steps onto one score
                continue
            seen.add(value)
            ratings.append((value, f'{label} ({value} pts)' if value else label))
        return ratings

    def canvas_key(self, key):
        """Return the Canvas identity of an assignment file, which outlives its name.

        Everything in canvas/ refers to a lab part by filename, so renaming a part or
        renumbering its lab is a local edit. Canvas IDs are remembered under the part's
        canvas_key instead, so neither rename reaches Canvas. See docs/adr/0002.
        """
        return self.data.assignments[key]['canvas_key']

    def push_rubric(self, key, assignment_id):
        """Create or update the Canvas rubric for an assignment, from its rubric_source."""
        criteria = self.data.rubric_criteria(key)
        if not criteria:
            return
        title = self.data.assignments[key]['title']
        state_key = self.canvas_key(key)
        fields = {
            'rubric[title]': f'{title} rubric',
            # 0, not 1: free-form comments REPLACE the clickable ratings in
            # SpeedGrader with a comment box, which is the opposite of what we want.
            'rubric[free_form_criterion_comments]': '0',
            'rubric_association[association_id]': str(assignment_id),
            'rubric_association[association_type]': 'Assignment',
            'rubric_association[use_for_grading]': '1',
            'rubric_association[purpose]': 'grading',
        }
        for i, criterion in enumerate(criteria):
            fields[f'rubric[criteria][{i}][description]'] = criterion['description']
            fields[f'rubric[criteria][{i}][long_description]'] = criterion['long_description']
            fields[f'rubric[criteria][{i}][points]'] = str(criterion['points'])
            for j, (points, label) in enumerate(self._ratings(criterion['points'])):
                fields[f'rubric[criteria][{i}][ratings][{j}][description]'] = label
                fields[f'rubric[criteria][{i}][ratings][{j}][points]'] = str(points)

        saved = self.state['rubrics'].get(state_key) or {}
        if saved.get('id'):
            # Pass the association back, or Canvas adds a second one to the assignment.
            if saved.get('association_id'):
                fields['rubric_association_id'] = str(saved['association_id'])
            body = self._api('PUT', f'courses/{self.course.id}/rubrics/{saved["id"]}', fields)
            verb = 'updated'
        else:
            body = self._api('POST', f'courses/{self.course.id}/rubrics', fields)
            verb = 'created'

        rubric = body.get('rubric') or body
        association = body.get('rubric_association') or {}
        self.state['rubrics'][state_key] = {
            'id': rubric.get('id') or saved.get('id'),
            'association_id': association.get('id') or saved.get('association_id'),
        }
        total = sum(c['points'] for c in criteria)
        print(f'{verb:9} rubric: {title} - {len(criteria)} criteria, {total} points')

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
        state_key = self.canvas_key(key)
        found = self._existing('assignments', state_key, self.course.get_assignment)
        payload = self._published({
            'name': assignment['title'],
            'description': self.data.render_assignment(key),
            'assignment_group_id': group_ids[assignment['assignment_group']],
        }, not found)
        if assignment.get('points') is not None:
            payload['points_possible'] = assignment['points']
        if assignment.get('submission_types'):
            payload['submission_types'] = assignment['submission_types']
        # Always send all three, empty when unset: Canvas keeps whatever it already has
        # for a field that is left out, so a date removed here has to be cleared there.
        # lock_at is the gate, not due_at - Canvas keeps accepting submissions after the
        # due date (flagging them late) until the lock date closes them off.
        for field in ('due_at', 'lock_at', 'unlock_at'):
            payload[field] = assignment.get(field) or ''
        if assignment.get('team'):
            payload['group_category_id'] = team_set_id
        if found:
            found.edit(assignment=payload)
            print(f'updated   assignment: {assignment["title"]}')
        else:
            found = self.course.create_assignment(assignment=payload)
            print(f'created   assignment: {assignment["title"]}')
        self.state['assignments'][state_key] = found.id
        self.push_rubric(key, found.id)

    def _module_item(self, item):
        """Return (match key, Canvas payload) for a modules.yml item, or None if it was not pushed."""
        if 'page' in item:
            slug = self.state['pages'].get(item['page'])
            return slug and (('Page', slug), {'type': 'Page', 'page_url': slug})
        if 'assignment' in item:
            if item['assignment'] not in self.data.assignments:
                return None
            canvas_id = self.state['assignments'].get(self.canvas_key(item['assignment']))
            return canvas_id and (
                ('Assignment', canvas_id), {'type': 'Assignment', 'content_id': canvas_id}
            )
        if 'link' in item:
            # A plain link out to the course site, for things that are not Sphinx pages:
            # the interactive steppers under docs/_static/, for example.
            url = (item['link'] if item['link'].startswith(('http://', 'https://'))
                   else f'{self.data.course["site"]["base_url"]}/{item["link"].lstrip("/")}')
            title = item.get('title') or item['link']
        else:
            url = self.data.site_url(item['site'])
            title = self.data.site_title(self.data.docs / f'{item["site"]}.rst')
        return ('ExternalUrl', url), {'type': 'ExternalUrl', 'external_url': url, 'title': title, 'new_tab': True}

    def push_late_policy(self):
        """Apply the course-wide late policy from course.yml, if one is set.

        Canvas has no per-assignment late policy, so this lands on everything. Sim parts
        are the ones meant to feel it; car parts are due at the end of their slack window
        so Canvas never marks one late. See the late_policy comment in course.yml.
        """
        policy = self.data.course['canvas'].get('late_policy')
        if not policy:
            return
        percent = policy['percent_per_day']
        floor = policy.get('lowest_possible_grade')
        fields = {
            'late_policy[late_submission_deduction_enabled]': 'true',
            'late_policy[late_submission_deduction]': str(percent),
            'late_policy[late_submission_interval]': 'day',
            'late_policy[late_submission_minimum_percent_enabled]': 'true' if floor else 'false',
            'late_policy[late_submission_minimum_percent]': str(floor or 0),
        }
        path = f'courses/{self.course.id}/late_policy'
        try:
            self._api('PATCH', path, fields)
            verb = 'updated'
        except urllib.error.HTTPError as error:
            # Canvas 404s the PATCH until a policy exists on the course.
            if error.code != 404:
                raise
            self._api('POST', path, fields)
            verb = 'created'
        floor_note = f', floor {floor}%' if floor else ', no floor'
        print(f'{verb:9} late policy: {percent}% per day{floor_note}')

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

    def push_module_by_id(self, module_id):
        """Push one module, at the position it has in modules.yml.

        The position matters: taking it from the file rather than counting the
        modules pushed so far keeps a single-module push from reordering the
        course the next time everything is pushed.
        """
        for position, module in enumerate(self.data.modules, start=1):
            if module['id'] == module_id:
                self.push_module(module, position)
                return
        raise KeyError(f'no module with id "{module_id}"')

    def push(self, only=None):
        if only:
            keys = [only] if isinstance(only, str) else list(only)
            groups = team_set = None
            for key in keys:
                if key.startswith(MODULE_PREFIX):
                    self.push_module_by_id(key[len(MODULE_PREFIX):])
                elif key in self.data.pages:
                    self.push_page(key)
                else:
                    # Only paid for when an assignment is actually being pushed.
                    if groups is None:
                        groups, team_set = self.push_assignment_groups(), self.team_set_id()
                    self.push_assignment(key, groups, team_set)
            return

        self.push_late_policy()
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
    parser.add_argument('--only', metavar='ID', action='append',
                        help='push one page or assignment, by file name without .md, or one '
                             'module as "module:<id>" from modules.yml. Repeat the flag to '
                             'push several.')
    args = parser.parse_args()

    data = CourseData()
    if report(data):
        sys.exit('Fix the errors above before pushing.')
    print()

    module_ids = {module['id'] for module in data.modules}
    for key in args.only or []:
        if key.startswith(MODULE_PREFIX):
            if key[len(MODULE_PREFIX):] not in module_ids:
                sys.exit(f'No module with id "{key[len(MODULE_PREFIX):]}" in canvas/modules.yml.')
        elif key not in data.pages and key not in data.assignments:
            sys.exit(f'No page or assignment named "{key}".')

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
    for kind in ('pages', 'assignments', 'modules', 'rubrics'):
        state.setdefault(kind, {})

    try:
        Pusher(data, course, state, url, token).push(args.only)
    finally:
        STATE_PATH.write_text(json.dumps(all_state, indent=2) + '\n', encoding='utf-8')

    print(f'\nDone. Canvas IDs saved to {STATE_PATH.relative_to(REPO).as_posix()}.')


if __name__ == '__main__':
    main()
