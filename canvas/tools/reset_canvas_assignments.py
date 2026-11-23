"""Delete every Canvas assignment in the course and forget their IDs.

Usage (from the repository root):

    python canvas/tools/reset_canvas_assignments.py --dry-run   # list what would go
    python canvas/tools/reset_canvas_assignments.py             # delete them

This exists for one job: the Spring 2027 restructure renamed every lab part, and the
assignment keys that Canvas IDs used to be remembered under are gone. Rather than leave
eighteen assignments in the course that no module points at, this clears them so the next
push recreates the course cleanly under the new canvas_key values. See docs/adr/0002.

It refuses to delete a published assignment or one with a submission, so it is safe to run
against a course that has not been given to students and useless against one that has.
Pages and modules are left alone: their identities did not change.
"""

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

CANVAS = pathlib.Path(__file__).resolve().parent.parent
REPO = CANVAS.parent
STATE_PATH = CANVAS / 'canvas_ids.json'
# The localization area became two areas, so this module id no longer exists.
RETIRED_MODULES = ('localization-pure-pursuit',)


def settings():
    from dotenv import load_dotenv

    load_dotenv(REPO / '.env')
    url = os.environ.get('CANVAS_API_URL')
    token = os.environ.get('CANVAS_API_TOKEN')
    course = os.environ.get('CANVAS_COURSE_ID')
    if not (url and token and course):
        sys.exit('Need CANVAS_API_URL, CANVAS_API_TOKEN and CANVAS_COURSE_ID in .env.')
    return url.rstrip('/'), token, course


def api(url, token, method, path):
    request = urllib.request.Request(
        f'{url}/api/v1/{path}', method=method, headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--dry-run', action='store_true',
                        help='list the assignments that would be deleted and stop')
    args = parser.parse_args()

    url, token, course_id = settings()
    print(f'Course {course_id} on {url}\n')

    assignments = api(url, token, 'GET', f'courses/{course_id}/assignments?per_page=100')

    # A published assignment, or one with a submission, belongs to a course that is
    # already running. Deleting it would take a student's work with it.
    guarded = [
        a for a in assignments
        if a.get('published') or a.get('has_submitted_submissions')
    ]
    if guarded:
        for a in guarded:
            why = 'published' if a.get('published') else 'has submissions'
            print(f'  {a["id"]:>5}  {a["name"]}  <-- {why}')
        sys.exit(f'\nRefusing to run: {len(guarded)} assignment(s) are in use.')

    for a in sorted(assignments, key=lambda a: a['id']):
        if args.dry_run:
            print(f'would delete  {a["id"]:>5}  {a["name"]}')
            continue
        api(url, token, 'DELETE', f'courses/{course_id}/assignments/{a["id"]}')
        print(f'deleted       {a["id"]:>5}  {a["name"]}')

    if args.dry_run:
        print(f'\n{len(assignments)} assignments would be deleted. Nothing was changed.')
        return

    state = json.loads(STATE_PATH.read_text(encoding='utf-8')) if STATE_PATH.is_file() else {}
    course = state.setdefault(f'{url}#{course_id}', {})
    course['assignments'] = {}
    # Rubrics are attached to assignments, so Canvas drops them with their assignment.
    course['rubrics'] = {}
    for module_id in RETIRED_MODULES:
        canvas_id = course.get('modules', {}).pop(module_id, None)
        if canvas_id is None:
            continue
        try:
            api(url, token, 'DELETE', f'courses/{course_id}/modules/{canvas_id}')
            print(f'deleted       module {canvas_id}  ({module_id})')
        except urllib.error.HTTPError as error:
            print(f'module {canvas_id} ({module_id}) delete returned {error.code}; '
                  'forgetting it anyway')
    STATE_PATH.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')

    print(f'\n{len(assignments)} assignments deleted. Pages and modules were left alone.')
    print('Now run: python canvas/tools/push_to_canvas.py')


if __name__ == '__main__':
    main()
