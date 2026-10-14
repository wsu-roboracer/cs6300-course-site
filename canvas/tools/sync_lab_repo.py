"""Push a lab folder in this repo to its student-facing GitHub repo.

Usage (from the repository root):

    python canvas/tools/sync_lab_repo.py lab1                      # dry run
    python canvas/tools/sync_lab_repo.py lab1 --push
    python canvas/tools/sync_lab_repo.py lab1 --push --solutions   # also the solutions branch
    python canvas/tools/sync_lab_repo.py --all                     # dry run, every lab

Dry run is the default. These repos are what students copy, so nothing leaves
this machine without --push.

The lab folder in this repo is the source of truth. The lab repo's main branch
is made identical to it: a file deleted from the folder is deleted from the
repo too. Folders named solution or solutions are never pushed to main.

The solutions branch is main plus the solved files. Those live outside this
repo, in <solutions_dir>/<repo_task>/ (see lab_repos in canvas/course.yml),
laid out like the lab repo and holding only the files that differ from main.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from check_sync import report
from course_data import REPO, CourseData

# Never copied into a student repo.
SKIP_DIRS = {'solution', 'solutions', '.git', '__pycache__', '.pytest_cache', '.claude'}


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and result.returncode:
        raise RuntimeError(f'{" ".join(map(str, cmd))}\n{result.stdout}\n{result.stderr}')
    return result


def mirror(src, dst):
    """Make dst's content identical to src, minus SKIP_DIRS.

    Everything in dst except .git is removed first, so a file deleted from the
    lab folder also disappears from the student repo.
    """
    for entry in dst.iterdir():
        if entry.name == '.git':
            continue
        shutil.rmtree(entry) if entry.is_dir() else entry.unlink()
    overlay(src, dst)


def overlay(src, dst):
    """Copy src over dst, minus SKIP_DIRS."""
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        out = dst / Path(root).relative_to(src)
        out.mkdir(parents=True, exist_ok=True)
        for name in files:
            shutil.copy2(Path(root) / name, out / name)


def commit(workdir, message):
    """Commit whatever changed in workdir. Return False if nothing did."""
    run(['git', 'add', '-A'], cwd=workdir)
    if not run(['git', 'status', '--porcelain'], cwd=workdir).stdout.strip():
        return False
    run(['git', 'commit', '-q', '-m', message], cwd=workdir)
    return True


def show(names):
    for line in names.splitlines():
        print(f'    {line}')


def sync_main(src, workdir, push, message):
    branch = run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=workdir).stdout.strip()
    mirror(src, workdir)
    if not commit(workdir, message):
        print(f'  {branch}: already identical, nothing to push')
        return
    print(f'  {branch}: changes')
    show(run(['git', 'show', '--name-status', '--format=', 'HEAD'], cwd=workdir).stdout.strip())
    if push:
        run(['git', 'push', '-q', 'origin', 'HEAD'], cwd=workdir)
        print(f'  {branch}: pushed')


def sync_solutions(solution, workdir, push, message):
    """Rebuild the solutions branch as the just-synced main plus the solved files."""
    if not solution.is_dir():
        print(f'  solutions: no folder {solution}, skipped')
        return
    exists = 'origin/solutions' in run(['git', 'branch', '-r'], cwd=workdir).stdout

    run(['git', 'checkout', '-q', '-B', 'solutions'], cwd=workdir)
    overlay(solution, workdir)
    if not commit(workdir, f'{message} (solutions)'):
        print('  solutions: the solutions folder is identical to main, skipped')
        return

    # Compare with the branch's own tip, not main, so a run that changes
    # nothing does not push the same tree again under a new commit.
    if exists:
        names = run(['git', 'diff', '--name-status', 'origin/solutions', 'HEAD'], cwd=workdir).stdout.strip()
        if not names:
            print('  solutions: already identical, nothing to push')
            return
        print('  solutions: changes')
    else:
        names = run(['git', 'show', '--name-status', '--format=', 'HEAD'], cwd=workdir).stdout.strip()
        print('  solutions: new branch, differs from main in')
    show(names)
    if push:
        run(['git', 'push', '-q', '--force-with-lease', 'origin', 'solutions'], cwd=workdir)
        print('  solutions: pushed')


def sync(src, clone_url, push, message, solution=None):
    """Mirror src into a fresh clone of clone_url, and optionally rebuild its solutions branch."""
    workdir = Path(tempfile.mkdtemp(prefix='sync-lab-'))
    try:
        run(['git', 'clone', '--quiet', clone_url, workdir])
        sync_main(src, workdir, push, message)
        if solution is not None:
            sync_solutions(solution, workdir, push, message)
    finally:
        # Git marks its object files read-only, which stops rmtree on Windows.
        shutil.rmtree(workdir, onerror=lambda func, path, _: (os.chmod(path, 0o700), func(path)))


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('lab', nargs='?', help='assignment ID, e.g. lab1')
    parser.add_argument('--all', action='store_true', help='every lab that has a folder')
    parser.add_argument('--push', action='store_true', help='actually push; without it nothing leaves this machine')
    parser.add_argument('--solutions', action='store_true', help='also rebuild the solutions branch')
    parser.add_argument('--message', '-m', default='Sync from course repo', help='commit message')
    args = parser.parse_args()
    if not args.lab and not args.all:
        parser.error('name a lab, or pass --all')

    data = CourseData()
    if report(data):
        sys.exit('Fix the errors above before syncing.')
    print()

    org = data.course['lab_repos']['org']
    if not org:
        sys.exit('Set lab_repos.org in canvas/course.yml to the GitHub org that holds the lab repos.')
    solutions_dir = (REPO / data.course['lab_repos']['solutions_dir']).resolve()

    labs = {key: a for key, a in data.assignments.items() if a.get('repo_task') and a.get('repo_folder')}
    if args.lab:
        if args.lab not in labs:
            sys.exit(f'"{args.lab}" has no repo_task and repo_folder. Labs that do: {", ".join(labs) or "none"}')
        labs = {args.lab: labs[args.lab]}

    if not args.push:
        print('DRY RUN: nothing will be pushed. Add --push when it looks right.\n')

    for assignment in labs.values():
        task = assignment['repo_task']
        repo = f'{org}/{task}'
        print(f'{repo}  <-  {assignment["repo_folder"]}')
        if run(['gh', 'repo', 'view', repo], check=False).returncode:
            print('  no such repo on GitHub. Create it as a private template first:')
            print(f'    gh repo create {repo} --private --add-readme')
            print(f'    gh repo edit {repo} --template')
            continue
        sync(
            REPO / assignment['repo_folder'],
            f'https://github.com/{repo}.git',
            args.push,
            args.message,
            solutions_dir / task if args.solutions else None,
        )


if __name__ == '__main__':
    main()
