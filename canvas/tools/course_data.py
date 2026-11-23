"""Load the Canvas definitions in canvas/, check them against the site, and render them.

Shared by check_sync.py and push_to_canvas.py.
"""

import html
import os
import re
from datetime import date, datetime, time, timedelta
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import yaml

REPO = Path(__file__).resolve().parents[2]
CANVAS = REPO / 'canvas'

# The repo creator's course passcode. It comes from the environment and is never
# read from course.yml, because this repository is public and the passcode is what
# stops anyone on the internet from creating repositories in the course's org.
# Canvas is behind a login, which is why the passcode is published there and only
# there - the creator page itself tells students to get it "from Canvas".
PASSCODE_ENV = 'REPO_CREATOR_PASSCODE'

ASSIGNMENT_FIELDS = (
    'canvas_key', 'site_page', 'assignment_group', 'points', 'due_week', 'team',
    'submission_types',
)
# A canvas_key is the lab part's identity in Canvas, so it has to survive the file
# being renamed and the lab being renumbered. See docs/adr/0002.
CANVAS_KEY = re.compile(r'^[a-z0-9][a-z0-9-]*$')
TBD_FIELDS = ('points', 'due_week', 'submission_types')
WEEKDAYS = {'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6}
# A late sim part is deducted 10% a day, so it is worthless after ten; two weeks closes it.
LOCK_WEEKS = 2
TOTAL_POINTS = re.compile(r'Total:\s*(\d+)\s*Points', re.IGNORECASE)
# Inline Markdown that should not reach a Canvas rubric label.
MARKUP = re.compile(r'[*`]+')

BUTTON_STYLE = (
    'display: inline-block; padding: 10px 24px; font-size: 1em; font-weight: 600; '
    'color: #fff; background-color: #0b874b; border-radius: 4px; text-decoration: none;'
)


class CourseData:
    def __init__(self):
        self.course = yaml.safe_load((CANVAS / 'course.yml').read_text(encoding='utf-8'))
        self.docs = REPO / self.course['site']['docs_dir']
        self.errors = []
        self.warnings = []
        self.passcode = self._load_passcode()
        self.pages = self._load_pages()
        self.assignments = self._load_assignments()
        self.modules = yaml.safe_load((CANVAS / 'modules.yml').read_text(encoding='utf-8'))['modules']
        self._check_course()
        self._check_site_coverage()
        self._check_modules()
        self._check_rubrics()

    # -- site -----------------------------------------------------------------

    def site_url(self, page):
        return f'{self.course["site"]["base_url"]}/{page}.html'

    def site_title(self, rst_path):
        """Return the first heading of an .rst page."""
        lines = rst_path.read_text(encoding='utf-8-sig').splitlines()
        for line, underline in zip(lines, lines[1:]):
            if line.strip() and re.fullmatch(r'=+', underline.strip()):
                return line.strip()
        return None

    def site_toc(self, index_rst):
        """Return [(title, page)] for the pages listed in an index page's toctree."""
        entries = []
        in_toctree = False
        for line in index_rst.read_text(encoding='utf-8-sig').splitlines():
            if line.strip().startswith('.. toctree::'):
                in_toctree = True
            elif in_toctree and line.strip():
                if not line.startswith((' ', '\t')):
                    in_toctree = False
                    continue
                entry = line.strip()
                if entry.startswith(':') or '://' in entry:
                    continue
                titled = re.fullmatch(r'(.+?)\s*<(.+)>', entry)
                title, target = titled.groups() if titled else (None, entry)
                rst = (index_rst.parent / f'{target}.rst').resolve()
                if rst.is_file():
                    page = rst.relative_to(self.docs).with_suffix('').as_posix()
                    entries.append((title or self.site_title(rst) or target, page))
        return entries

    # -- loading --------------------------------------------------------------

    def _read(self, path):
        """Return (front matter dict, body) for a Markdown file with YAML front matter."""
        text = path.read_text(encoding='utf-8-sig')
        match = re.match(r'---\r?\n(.*?)\r?\n---\r?\n?(.*)', text, re.DOTALL)
        if not match:
            self.errors.append(f'{path.relative_to(REPO).as_posix()}: missing YAML front matter')
            return {}, text
        return yaml.safe_load(match.group(1)) or {}, match.group(2)

    def _site_page(self, name, meta):
        """Return the .rst path for an item's site_page, or None."""
        page = meta.get('site_page')
        if not page:
            return None
        rst = self.docs / f'{page}.rst'
        if not rst.is_file():
            self.errors.append(f'{name}: site_page "{page}" does not exist in {self.docs.name}/')
            return None
        return rst

    def _load_pages(self):
        pages = {}
        for path in sorted((CANVAS / 'pages').glob('*.md')):
            name = path.relative_to(REPO).as_posix()
            meta, body = self._read(path)
            rst = self._site_page(name, meta)
            title = meta.get('title') or (self.site_title(rst) if rst else None)
            if not title:
                self.errors.append(f'{name}: needs a "title" or a "site_page" to take one from')
            pages[path.stem] = {
                **meta,
                'title': title,
                'body': body,
                'url': self.site_url(meta['site_page']) if rst else None,
                'toc': self.site_toc(rst) if rst else [],
            }
        return pages

    def _load_assignments(self):
        groups = {g['name'] for g in self.course['assignment_groups']}
        assignments = {}

        for path in sorted((CANVAS / 'assignments').glob('*.md')):
            name = path.relative_to(REPO).as_posix()
            meta, body = self._read(path)

            for field in ASSIGNMENT_FIELDS:
                if field not in meta:
                    self.errors.append(f'{name}: missing field "{field}"')
            for field in TBD_FIELDS:
                if field in meta and meta[field] is None:
                    self.warnings.append(f'{name}: "{field}" is still TBD')
            if not meta.get('repo_task'):
                self.warnings.append(f'{name}: no "repo_task", so there is no repository link')
            elif not meta.get('repo_folder'):
                self.warnings.append(f'{name}: no "repo_folder", so the lab repo is not built from this repo')
            elif not (REPO / meta['repo_folder']).is_dir():
                self.errors.append(f'{name}: repo_folder "{meta["repo_folder"]}" does not exist')

            rst = self._site_page(name, meta)

            if 'assignment_group' in meta and meta['assignment_group'] not in groups:
                self.errors.append(f'{name}: assignment_group "{meta["assignment_group"]}" is not in course.yml')

            due_day, lock_day = self.weeks_to_days(name, meta.get('due_week'))
            dates = {'due': due_day, 'lock': lock_day, 'unlock': meta.get('unlock')}
            for field, value in list(dates.items()):
                try:
                    dates[field] = self.due_at(value)
                except ValueError:
                    self.errors.append(
                        f'{name}: {field} "{value}" is not a date like 2027-03-05 23:59'
                    )
                    dates[field] = None
            due_at, lock_at, unlock_at = dates['due'], dates['lock'], dates['unlock']

            # A lock before the due date would shut submissions before they are due;
            # an unlock after it would open the assignment only once it is late.
            if lock_at and due_at and lock_at < due_at:
                self.errors.append(f'{name}: lock is before due')
            if unlock_at and due_at and unlock_at > due_at:
                self.errors.append(f'{name}: unlock is after due')
            for field, day in (('due', due_day), ('lock', lock_day),
                               ('unlock', meta.get('unlock'))):
                self._check_calendar(name, field, day)

            rubric = meta.get('rubric_source')
            if rubric:
                rubric_path = REPO / rubric
                if not rubric_path.is_file():
                    self.errors.append(f'{name}: rubric_source "{rubric}" does not exist')
                else:
                    total = TOTAL_POINTS.search(rubric_path.read_text(encoding='utf-8-sig'))
                    if total and meta.get('points') is not None and int(total.group(1)) != meta['points']:
                        self.errors.append(
                            f'{name}: points is {meta["points"]} but {rubric} says Total: {total.group(1)} Points'
                        )

            assignments[path.stem] = {
                **meta,
                'title': meta.get('title') or (self.site_title(rst) if rst else None),
                'body': body,
                'url': self.site_url(meta['site_page']) if rst else None,
                'repo_url': self.repo_url(meta.get('repo_task')),
                'due': due_day,
                'lock': lock_day,
                'due_at': due_at,
                'lock_at': lock_at,
                'unlock_at': unlock_at,
            }

        # Checked once every assignment is loaded, since these point at other ones.
        claimed = {}
        for key, assignment in assignments.items():
            name = f'canvas/assignments/{key}.md'

            earlier = assignment.get('repo_continues')
            if earlier and earlier not in assignments:
                self.errors.append(f'{name}: repo_continues "{earlier}" is not an assignment')

            canvas_key = assignment.get('canvas_key')
            if canvas_key is None:
                continue
            if not CANVAS_KEY.match(str(canvas_key)):
                self.errors.append(
                    f'{name}: canvas_key "{canvas_key}" must be lowercase letters, digits and dashes'
                )
            elif canvas_key in claimed:
                # Two files sharing a key would make the second silently overwrite the
                # Canvas assignment belonging to the first.
                self.errors.append(
                    f'{name}: canvas_key "{canvas_key}" is already used by {claimed[canvas_key]}'
                )
            else:
                claimed[canvas_key] = name

        return assignments

    def week_sunday(self, week):
        """Return the date a lab part is due in a given week of the semester.

        Week 1 ends on the first due_weekday on or after the day the term starts, so a
        new semester only has to change calendar.starts in canvas/course.yml.
        """
        calendar = self.course['calendar']
        weekday = WEEKDAYS[calendar.get('due_weekday', 'sunday').lower()]
        start = calendar['starts']
        first = start + timedelta(days=(weekday - start.weekday()) % 7)
        return first + timedelta(weeks=week - 1)

    def last_week(self):
        """Return the highest week number whose due day still falls inside the term."""
        calendar = self.course['calendar']
        week = 1
        while self.week_sunday(week + 1) <= calendar['ends']:
            week += 1
        return week

    def weeks_to_days(self, name, due_week):
        """Return (due, lock) dates for a due_week, or (None, None) if it is unusable.

        The lock is always two weeks after the due date, clamped to the last week of the
        term: a submission cannot be accepted after the semester it belongs to has ended.
        """
        if due_week is None or not self.course.get('calendar'):
            return None, None
        if not isinstance(due_week, int) or due_week < 1:
            self.errors.append(f'{name}: due_week "{due_week}" is not a week number')
            return None, None
        last = self.last_week()
        if due_week > last:
            self.errors.append(
                f'{name}: due_week {due_week} is past the end of the term, which is week {last}'
            )
            return None, None
        return self.week_sunday(due_week), self.week_sunday(min(due_week + LOCK_WEEKS, last))

    def _check_calendar(self, name, field, value):
        """Flag a date that falls outside the semester or inside the break.

        The semester is the one thing that moves every time the course runs, so a date
        left over from the last run lands in a week with no classes. See calendar in
        canvas/course.yml.
        """
        calendar = self.course.get('calendar')
        if not calendar or value is None:
            return
        day = value.date() if isinstance(value, datetime) else value
        if not isinstance(day, date):
            return
        if day < calendar['starts']:
            self.errors.append(f'{name}: {field} {day} is before the term starts')
        elif day > calendar['ends']:
            self.errors.append(f'{name}: {field} {day} is after the term ends')
        elif (brk := calendar.get('break')) and brk['starts'] <= day <= brk['ends']:
            self.errors.append(f'{name}: {field} {day} is inside the break')

    def due_at(self, value):
        """Return a due date as an ISO 8601 string in the course time zone, or None."""
        if value is None:
            return None
        if isinstance(value, datetime):
            due = value
        elif isinstance(value, date):
            due = datetime.combine(value, time(23, 59))
        else:
            due = datetime.strptime(str(value), '%Y-%m-%d %H:%M')
        if due.tzinfo is None:
            due = due.replace(tzinfo=ZoneInfo(self.course['time_zone']))
        return due.isoformat()

    def repo_url(self, task):
        """Return the repo creator link that gives a student their copy of a lab repo."""
        if not task:
            return None
        creator = self.course['repo_creator']
        return f'{creator["base_url"]}?{urlencode({"course": creator["course"], "task": task}, safe="/")}'

    def rubric_criteria(self, key):
        """Return [{'description', 'long_description', 'points'}] for an assignment's rubric.

        Read from the assignment's rubric_source, so the lab instructions stay the one
        place a rubric is written. Two shapes are in use and both are supported: a
        Markdown table whose last column is the points, and a bulleted list of
        "Item: **N** Points (what is graded)". In both cases the rubric is the block
        immediately above the "Total: N Points" line.
        """
        source = self.assignments.get(key, {}).get('rubric_source')
        if not source:
            return []
        path = REPO / source
        if not path.is_file():
            return []
        lines = path.read_text(encoding='utf-8-sig').splitlines()
        total_at = next(
            (i for i, line in enumerate(lines) if TOTAL_POINTS.search(line)), None
        )
        if total_at is None:
            return []

        # Back up over blank lines to whatever the rubric block is.
        end = total_at - 1
        while end >= 0 and not lines[end].strip():
            end -= 1
        if end < 0:
            return []

        if lines[end].strip().startswith('|'):
            criteria = self._rubric_from_table(lines, end)
        else:
            criteria = self._rubric_from_list(lines, end)

        points = self.assignments[key].get('points')
        got = sum(c['points'] for c in criteria)
        if criteria and points is not None and got != points:
            self.warnings.append(
                f'canvas/assignments/{key}.md: rubric criteria total {got}, not {points}; '
                f'no Canvas rubric will be built from {source}'
            )
            return []
        return criteria

    @staticmethod
    def _rubric_from_table(lines, end):
        start = end
        while start >= 0 and lines[start].strip().startswith('|'):
            start -= 1
        rows = [line.strip() for line in lines[start + 1:end + 1]]
        criteria = []
        for row in rows[2:]:                      # skip the header and its divider
            cells = [c.strip() for c in row.strip('|').split('|')]
            if len(cells) < 2:
                continue
            value = re.fullmatch(r'\*{0,2}(\d+)\*{0,2}', cells[-1])
            if not value:
                continue
            # Two columns means the label carries the detail; three means label + detail.
            label, detail = (cells[0], ' '.join(cells[1:-1])) if len(cells) > 2 else (cells[0], '')
            label = MARKUP.sub('', label).strip()
            detail = MARKUP.sub('', detail).strip()
            # Some rubrics number their rows ("| 1 | Map files ... | 40 |"). A criterion
            # called "1" is useless in SpeedGrader, so lead with the detail instead.
            if re.fullmatch(r'\d+', label):
                label = CourseData._shorten(detail) or f'Item {label}'
            criteria.append({
                'description': label or 'Criterion',
                'long_description': detail,
                'points': int(value.group(1)),
            })
        return criteria

    @staticmethod
    def _shorten(text, limit=70):
        """Return a short criterion label taken from a longer description."""
        text = text.strip()
        if len(text) <= limit:
            return text
        cut = text[:limit]
        # Prefer a clause boundary, then a word boundary, so labels do not end mid-word.
        for sep in (': ', ' - ', ', ', ' '):
            if sep in cut:
                return cut[:cut.rindex(sep)].strip(' :,-')
        return cut.strip()

    @staticmethod
    def _rubric_from_list(lines, end):
        start = end
        while start >= 0 and (lines[start].strip().startswith(('-', '*')) or not lines[start].strip()):
            start -= 1
        criteria = []
        for line in lines[start + 1:end + 1]:
            stripped = line.strip()
            if not stripped.startswith(('-', '*')):
                continue
            if line.startswith(('  -', '  *', '\t-')):
                continue                           # a sub-bullet belongs to the item above it
            item = stripped.lstrip('-* ').strip()
            value = re.search(r'\*{0,2}(\d+)\*{0,2}\s*(?:points|pts)\b', item, re.IGNORECASE)
            if not value:
                continue
            label = item.split(':')[0] if ':' in item else item[:value.start()]
            detail = ''
            parenthetical = re.search(r'\(([^)]*)\)\s*$', item)
            if parenthetical:
                detail = parenthetical.group(1)
            criteria.append({
                'description': MARKUP.sub('', label).strip(' :') or 'Criterion',
                'long_description': MARKUP.sub('', detail).strip(),
                'points': int(value.group(1)),
            })
        return criteria

    def _load_passcode(self):
        """Return the repo creator passcode from the environment, or None."""
        try:
            from dotenv import load_dotenv
        except ImportError:
            pass
        else:
            load_dotenv(REPO / '.env')
        passcode = (os.environ.get(PASSCODE_ENV) or '').strip()
        if not passcode:
            self.warnings.append(
                f'no ${PASSCODE_ENV}, so assignment pages will tell students to ask for the '
                f'passcode instead of showing it. Set it in .env (never in course.yml - '
                f'this repository is public).'
            )
        return passcode or None

    def repo_instructions(self, task, team):
        """Return the how-to-get-your-repository steps for a Canvas assignment."""
        steps = [
            'Sign in to GitHub first. If you do not have an account yet, create one at '
            '<a href="https://github.com/join" target="_blank" rel="noopener">github.com/join</a>.',
            'Open the button below.',
        ]
        if team:
            steps.append(
                'Choose <strong>your team</strong> from the list. The first member of a team to do '
                'this creates the repository; everyone after that is added to the one that '
                'already exists. Do not create a second one.'
            )
        steps.append(
            'Enter <strong>your GitHub username</strong> - not your W number and not your email. '
            'It is the name in your profile URL, <code>github.com/&lt;username&gt;</code>.'
        )
        if self.passcode:
            steps.append(
                f'Enter the course passcode: <strong><code>{html.escape(self.passcode)}</code></strong>'
            )
        else:
            steps.append(
                'Enter the course passcode for this class. '
                '<em>(Instructor: the passcode is not configured yet.)</em>'
            )
        steps.append(
            'Click <strong>Create my repository</strong>. GitHub emails you an invitation - '
            'accept it, then clone your repository.'
        )
        items = ''.join(f'<li>{step}</li>' for step in steps)
        return (
            f'<ol>{items}</ol>\n'
            '<p>The repo creator never asks for your GitHub password and cannot sign in as you. '
            'It only needs your username, so it can add you to the repository it makes.</p>\n'
            '<p>Keep the passcode inside this class. Anyone who has it can create repositories '
            'in the course organization.</p>'
        )

    # -- checks ---------------------------------------------------------------

    def _check_rubrics(self):
        """Parse every rubric once, so a rubric that cannot be built is reported up front."""
        for key in self.assignments:
            self.rubric_criteria(key)

    def _check_course(self):
        weight = sum(g['weight'] for g in self.course['assignment_groups'])
        if weight != 100:
            self.errors.append(f'canvas/course.yml: assignment group weights total {weight}, not 100')

    def _check_site_coverage(self):
        """Every lab page and tutorial area on the site needs a Canvas item."""
        site = self.course['site']
        ignored = set(site.get('ignore_pages', []))
        for patterns, items, folder in (
            (site['assignment_pages'], self.assignments, 'assignments'),
            (site['area_pages'], self.pages, 'pages'),
        ):
            covered = {item.get('site_page') for item in items.values()}
            for pattern in patterns:
                for rst in sorted(self.docs.glob(pattern)):
                    rel = rst.relative_to(self.docs).as_posix()
                    if rel not in ignored and rel[:-len('.rst')] not in covered:
                        self.errors.append(
                            f'{self.docs.name}/{rel}: no file in canvas/{folder}/ points at this page'
                        )

    def _check_modules(self):
        placed = {'assignment': set(), 'page': set()}
        ids = set()

        for module in self.modules:
            where = f'canvas/modules.yml: "{module.get("name")}"'
            if not module.get('id'):
                self.errors.append(f'{where}: missing "id"')
            elif module['id'] in ids:
                self.errors.append(f'{where}: duplicate id "{module["id"]}"')
            ids.add(module.get('id'))

            for item in module['items']:
                if 'link' in item:
                    # Either an absolute URL (a walkthrough in its own repo, say) or a path
                    # under docs/ served as-is rather than built by Sphinx. A path is checked
                    # on disk so a typo is caught here and not by a student hitting a 404; a
                    # URL cannot be checked without the network, so it is taken on trust.
                    if not item['link'].startswith(('http://', 'https://')):
                        target = self.docs / item['link'].lstrip('/')
                        if not target.is_file():
                            self.errors.append(f'{where}: link target "{item["link"]}" does not exist')
                    if not item.get('title'):
                        self.errors.append(f'{where}: link "{item["link"]}" needs a "title"')
                elif 'site' in item:
                    if not (self.docs / f'{item["site"]}.rst').is_file():
                        self.errors.append(f'{where}: site page "{item["site"]}" does not exist')
                elif 'assignment' in item:
                    if item['assignment'] not in self.assignments:
                        self.errors.append(f'{where}: unknown assignment "{item["assignment"]}"')
                    placed['assignment'].add(item['assignment'])
                elif 'page' in item:
                    if item['page'] not in self.pages:
                        self.errors.append(f'{where}: unknown page "{item["page"]}"')
                    placed['page'].add(item['page'])
                else:
                    self.errors.append(f'{where}: item {item} must be a site, link, assignment, or page')

        for missing in sorted(set(self.assignments) - placed['assignment']):
            self.errors.append(f'canvas/assignments/{missing}.md: not placed in any module in canvas/modules.yml')
        for missing in sorted(set(self.pages) - placed['page']):
            self.errors.append(f'canvas/pages/{missing}.md: not placed in any module in canvas/modules.yml')

    # -- rendering ------------------------------------------------------------

    def _markdown(self, body):
        from markdown_it import MarkdownIt

        body = body.replace('{{ site_base_url }}', self.course['site']['base_url'])
        return MarkdownIt().render(body).strip()

    @staticmethod
    def _button(url, label):
        return (
            f'<p><a style="{BUTTON_STYLE}" href="{html.escape(url)}" target="_blank" rel="noopener">'
            f'{html.escape(label)}</a></p>'
        )

    def render_page(self, key):
        """Return the Canvas HTML for a page: its overview, then links into the site."""
        page = self.pages[key]
        parts = [self._markdown(page['body'])]
        if page['url']:
            parts.append(self._button(page['url'], 'Open this tutorial on the course site'))
        if page['toc']:
            parts.append('<h3>In this tutorial</h3>')
            links = ''.join(
                f'<li><a href="{html.escape(self.site_url(target))}" target="_blank" rel="noopener">'
                f'{html.escape(title)}</a></li>'
                for title, target in page['toc']
            )
            parts.append(f'<ol>{links}</ol>')
        return '\n'.join(parts) + '\n'

    def render_assignment(self, key):
        """Return the Canvas description for an assignment."""
        assignment = self.assignments[key]
        parts = [self._markdown(assignment['body'])]
        if assignment['url']:
            parts.append('<h3>Lab instructions</h3>')
            parts.append(self._button(assignment['url'], 'Open the lab on the course site'))
        earlier = assignment.get('repo_continues')
        if earlier:
            # The second half of a split lab: the repository already exists, so offering
            # the creation button again would contradict the lab's own instructions.
            title = self.assignments.get(earlier, {}).get('title') or earlier
            parts.append('<h3>Your repository</h3>')
            parts.append(
                f'<p>There is no new repository for this half. Keep working in the one you '
                f'already have from <strong>{title}</strong>, and submit that same URL here.</p>'
            )
        elif assignment['repo_url']:
            team = bool(assignment.get('team'))
            parts.append('<h3>Get your repository</h3>')
            if team:
                parts.append(
                    '<p>This is a team lab. Every member does this and chooses your team. '
                    'The first member creates the team repository and the rest are added to it.</p>'
                )
            else:
                parts.append('<p>This creates your own copy of the lab repository.</p>')
            parts.append(self.repo_instructions(assignment['repo_task'], team))
            parts.append(self._button(assignment['repo_url'], 'Create my lab repository'))
        return '\n'.join(parts) + '\n'
