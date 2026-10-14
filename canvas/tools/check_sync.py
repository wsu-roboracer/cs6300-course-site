"""Check that the Canvas definitions in canvas/ agree with the course site in docs/.

Usage (from the repository root):

    python canvas/tools/check_sync.py           # check, exit 1 on errors
    python canvas/tools/check_sync.py --list    # also print the modules and assignments
"""

import argparse
import sys

from course_data import CourseData


def print_modules(data):
    for module in data.modules:
        print(module['name'])
        for item in module['items']:
            if 'page' in item:
                page = data.pages.get(item['page'], {})
                print(f'  page        {page.get("title") or item["page"]}')
            elif 'assignment' in item:
                assignment = data.assignments.get(item['assignment'], {})
                print(f'  assignment  {assignment.get("title") or item["assignment"]}')
            elif 'site' in item:
                print(f'  site link   {item["site"]}')
    print()


def print_assignments(data):
    rows = [('ID', 'Title', 'Points', 'Due', 'Team', 'Repo task')]
    for key, a in data.assignments.items():
        rows.append((
            key,
            a['title'] or '?',
            'TBD' if a.get('points') is None else str(a['points']),
            'TBD' if a.get('due') is None else str(a['due']),
            'yes' if a.get('team') else 'no',
            a.get('repo_task') or '-',
        ))
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    for row in rows:
        print('  '.join(cell.ljust(width) for cell, width in zip(row, widths)).rstrip())
    print()


def report(data):
    """Print warnings and errors. Return the exit code."""
    for message in data.warnings:
        print(f'warning: {message}')
    for message in data.errors:
        print(f'error: {message}')
    print(
        f'{len(data.modules)} modules, {len(data.pages)} pages, {len(data.assignments)} assignments, '
        f'{len(data.errors)} errors, {len(data.warnings)} warnings'
    )
    return 1 if data.errors else 0


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--list', action='store_true', help='print the modules and assignments')
    args = parser.parse_args()

    data = CourseData()
    if args.list:
        print_modules(data)
        print_assignments(data)
    return report(data)


if __name__ == '__main__':
    sys.exit(main())
