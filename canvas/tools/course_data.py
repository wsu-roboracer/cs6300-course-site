"""Load the Canvas definitions in canvas/, check them against the site, and render them.

Shared by check_sync.py and push_to_canvas.py.
"""

import html
import re
from datetime import date, datetime, time
from pathlib import Path
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import yaml

REPO = Path(__file__).resolve().parents[2]
CANVAS = REPO / 'canvas'

ASSIGNMENT_FIELDS = ('site_page', 'assignment_group', 'points', 'due', 'team', 'submission_types')
TBD_FIELDS = ('points', 'due', 'submission_types')
TOTAL_POINTS = re.compile(r'Total:\s*(\d+)\s*Points', re.IGNORECASE)

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
        self.pages = self._load_pages()
        self.assignments = self._load_assignments()
        self.modules = yaml.safe_load((CANVAS / 'modules.yml').read_text(encoding='utf-8'))['modules']
        self._check_course()
        self._check_site_coverage()
        self._check_modules()

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

            try:
                due_at = self.due_at(meta.get('due'))
            except ValueError:
                self.errors.append(f'{name}: due "{meta["due"]}" is not a date like 2027-03-05 23:59')
                due_at = None

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
                'due_at': due_at,
            }

        return assignments

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

    # -- checks ---------------------------------------------------------------

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
                if 'site' in item:
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
                    self.errors.append(f'{where}: item {item} must be a site, assignment, or page')

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
        if assignment['repo_url']:
            parts.append('<h3>Get your repository</h3>')
            if assignment.get('team'):
                parts.append(
                    '<p>This is a team lab. Every member opens the link below and chooses your team. '
                    'The first member creates the team repository and the rest are added to it.</p>'
                )
            else:
                parts.append('<p>Open the link below to create your own copy of the lab repository.</p>')
            parts.append(self._button(assignment['repo_url'], 'Create my lab repository'))
            parts.append('<p>Sign in to GitHub before you open the link.</p>')
        return '\n'.join(parts) + '\n'
