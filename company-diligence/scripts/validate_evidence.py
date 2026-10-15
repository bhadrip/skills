#!/usr/bin/env python3
"""Validate a diligence ledger and local HTML links without network access.

Checks structural/provenance integrity, not factual truth or financial arithmetic.
"""
import argparse
import collections
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.assets = [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'a' and attrs.get('href'):
            self.links.append(attrs['href'])
        if tag == 'base':
            self.assets.append(('base', attrs.get('href', '')))
        if tag in {'script', 'img', 'iframe', 'video', 'audio', 'source', 'embed'}:
            if attrs.get('src'):
                self.assets.append((tag, attrs['src']))
        if tag == 'link' and 'stylesheet' in attrs.get('rel', '').split():
            self.assets.append((tag, attrs.get('href', '')))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(data, root, html_path=None):
    root = Path(root).resolve()
    errors, captures = [], []
    counts = collections.Counter()

    def check(ok, message):
        counts['checks'] += 1
        if not ok:
            errors.append(message)
        return ok

    def text_fields(record, fields, label):
        for key in fields:
            check(isinstance(record.get(key), str) and bool(record[key].strip()),
                  f'{label}: {key} must be nonempty text')

    def choice(value, choices):
        return isinstance(value, str) and value in choices

    def parse_url(value, label):
        try:
            return urlsplit(value)
        except (ValueError, TypeError):
            check(False, f'{label}: malformed url')
            return None

    def records(key, required=False):
        value = data.get(key, [] if not required else None)
        if not check(isinstance(value, list), f'{key} must be a list'):
            return []
        result = []
        for i, entry in enumerate(value):
            if check(isinstance(entry, dict), f'{key}[{i}] must be an object'):
                result.append(entry)
        return result

    def index(rows, label):
        result = {}
        for row in rows:
            ident = row.get('id')
            if check(isinstance(ident, str) and bool(ident.strip()), f'{label}: missing text id'):
                check(ident not in result, f'{label}: duplicate id {ident}')
                result[ident] = row
        return result

    def references(row, key, choices, label, required=False):
        values = row.get(key, [])
        if not check(isinstance(values, list) and all(isinstance(v, str) for v in values),
                     f'{label}: {key} must be a list of IDs'):
            return []
        if required:
            check(bool(values), f'{label}: {key} must not be empty')
        for value in values:
            check(value in choices, f'{label}: unresolved {key} {value}')
        return values

    def local_path(raw, label, base=root):
        if not check(isinstance(raw, str) and bool(raw), f'{label}: missing path'):
            return None
        path = Path(raw)
        if not check(not path.is_absolute(), f'{label}: path must be relative'):
            return None
        resolved = (base / path).resolve()
        if not check(resolved.is_relative_to(root), f'{label}: path escapes investigation root'):
            return None
        return resolved

    def artifacts(row, label, nonempty=False):
        items = row.get('artifacts')
        if not check(isinstance(items, list), f'{label}: artifacts must be a list'):
            return
        if nonempty:
            check(bool(items), f'{label}: saved experiment artifacts required')
        for i, item in enumerate(items):
            loc = f'{label}.artifacts[{i}]'
            if not check(isinstance(item, dict), f'{loc}: must be an object'):
                continue
            path = local_path(item.get('path'), loc)
            digest = item.get('sha256')
            valid_hash = isinstance(digest, str) and bool(re.fullmatch('[0-9a-f]{64}', digest))
            check(valid_hash, f'{loc}: valid lowercase SHA256 required')
            if path and check(path.is_file(), f'{loc}: missing file {item.get("path")}') and valid_hash:
                actual = sha(path)
                check(actual == digest, f'{loc}: hash mismatch for {item["path"]}')
                captures.append({'path': item['path'], 'sha256': actual, 'matches': actual == digest})

    if not isinstance(data, dict):
        return {'status': 'failed', 'errors': ['root must be an object'], 'counts': {}, 'captures': []}
    check(data.get('schema_version') == 1, 'schema_version must be 1')
    subject = data.get('subject')
    if check(isinstance(subject, dict), 'subject must be an object'):
        text_fields(subject, ['name', 'as_of', 'decision'], 'subject')
    else:
        subject = {}
    sources = records('sources', True)
    findings = records('findings', True)
    experiments = records('experiments')
    metrics = records('metrics')
    assumptions = records('assumptions')
    si, ei, mi, ai = (index(rows, label) for rows, label in [(sources, 'sources'), (experiments, 'experiments'), (metrics, 'metrics'), (assumptions, 'assumptions')])
    index(findings, 'findings')
    check(not (mi.keys() & ai.keys()), 'metric and assumption IDs must not collide')
    classes = {'primary_record', 'company_statement', 'independent_reporting', 'source_code', 'local_experiment', 'provided_document'}
    for row in sources:
        label = f'source {row.get("id")}'
        text_fields(row, ['title', 'accessed_at', 'publisher_group', 'scope'], label)
        check(choice(row.get('evidence_class'), classes), f'{label}: invalid evidence_class')
        url = row.get('url')
        parsed = parse_url(url, label) if isinstance(url, str) else None
        check('url' in row and (url is None or parsed is not None and parsed.scheme in {'https', 'http'} and bool(parsed.netloc)), f'{label}: url must be HTTP(S) or null')
        artifacts(row, label)
    for row in experiments:
        label = f'experiment {row.get("id")}'
        text_fields(row, ['revision', 'environment', 'command', 'expected', 'observed', 'control', 'scope_limit'], label)
        artifacts(row, label, nonempty=True)
    for row in findings:
        label = f'finding {row.get("id")}'
        text_fields(row, ['lens', 'title', 'claim', 'impact', 'recommendation', 'validation', 'boundary'], label)
        grade = row.get('evidence_grade')
        check(choice(grade, {'reproduced', 'source_supported', 'reported', 'hypothesis', 'unknown'}), f'{label}: invalid evidence_grade')
        check(choice(row.get('severity'), {'critical', 'high', 'medium', 'low', 'opportunity', 'unrated'}), f'{label}: invalid severity')
        check(choice(row.get('confidence'), {'high', 'medium', 'low'}), f'{label}: invalid confidence')
        references(row, 'source_ids', si, label, choice(grade, {'source_supported', 'reported'}))
        references(row, 'experiment_ids', ei, label, grade == 'reproduced')
    for row in assumptions:
        text_fields(row, ['name', 'unit', 'rationale'], f'assumption {row.get("id")}')
        check('value' in row and row['value'] is not None, f'assumption {row.get("id")}: value required')
    dependency_graph = {}
    for row in metrics:
        label = f'metric {row.get("id")}'
        text_fields(row, ['name', 'unit', 'period', 'population'], label)
        basis = row.get('basis')
        check(choice(basis, {'documented', 'reported', 'assumed', 'derived', 'unknown'}), f'{label}: invalid basis')
        check('value' in row, f'{label}: value is required (null for unknown)')
        if basis == 'unknown':
            check(row.get('value') is None, f'{label}: unknown value must be null, not zero')
        else:
            check(row.get('value') is not None, f'{label}: known/assumed value cannot be null')
        references(row, 'source_ids', si, label, choice(basis, {'documented', 'reported'}))
        references(row, 'assumption_ids', ai, label, basis == 'assumed')
        if basis == 'derived':
            text_fields(row, ['formula'], label)
            deps = references(row, 'input_ids', mi.keys() | ai.keys(), label, True)
            if isinstance(row.get('id'), str):
                dependency_graph[row['id']] = deps
    for row in metrics + assumptions:
        value = row.get('value')
        check(value is None or type(value) in {str, int, float}, f'{row.get("id")}: value must be number, text or null')
        if isinstance(value, float):
            check(math.isfinite(value), f'{row.get("id")}: numeric value must be finite')
    done, active = set(), set()
    def visit(ident):
        if ident in active:
            check(False, f'derived metric dependency cycle at {ident}')
            return
        if ident in done:
            return
        active.add(ident)
        for dep in dependency_graph.get(ident, []):
            visit(dep)
        active.remove(ident)
        done.add(ident)
    for ident in dependency_graph:
        visit(ident)
    for row, field, label in [(subject or {}, 'as_of', 'subject')] + [(s, 'accessed_at', s.get('id')) for s in sources]:
        try:
            dt.datetime.fromisoformat(str(row.get(field)).replace('Z', '+00:00'))
        except ValueError:
            check(False, f'{label}: {field} must be ISO 8601')
    if html_path:
        path = Path(html_path).resolve()
        if check(path.is_relative_to(root) and path.is_file(), 'HTML must exist inside investigation root'):
            markup = path.read_text(encoding='utf-8')
            page = Page(); page.feed(markup)
            check(len(page.ids) == len(set(page.ids)), 'HTML IDs must be unique')
            for tag, url in page.assets:
                check(tag != 'base', 'HTML base overrides are not portable')
                parsed = parse_url(url, f'asset {tag}')
                if parsed is None:
                    continue
                if parsed.scheme == 'data':
                    continue
                check(not parsed.scheme and not parsed.netloc, f'external render asset: {url}')
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    asset = local_path(unquote(parsed.path), f'asset {url}', path.parent)
                    if asset:
                        check(asset.is_file(), f'missing local asset {url}')
            for url in page.links:
                parsed = parse_url(url, 'HTML link')
                if parsed is None:
                    continue
                if parsed.scheme or parsed.netloc:
                    check(parsed.scheme in {'https', 'http', 'mailto'}, f'unsupported link scheme: {url}')
                    continue
                target = local_path(unquote(parsed.path), f'link {url}', path.parent) if parsed.path else path
                if target and check(target.is_file(), f'missing local link target {url}') and parsed.fragment:
                    if target.suffix.lower() in {'.html', '.htm'}:
                        other = page
                        if target != path:
                            other = Page(); other.feed(target.read_text(encoding='utf-8'))
                        check(unquote(parsed.fragment) in other.ids, f'missing HTML fragment {url}')
            counts['html_links'] = len(page.links)
            counts['html_ids'] = len(page.ids)
    counts.update(sources=len(sources), findings=len(findings), experiments=len(experiments), metrics=len(metrics), assumptions=len(assumptions), artifact_pairs=len(captures))
    return {'status': 'failed' if errors else 'passed', 'errors': errors, 'counts': dict(counts), 'captures': captures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--html', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.data.read_text(encoding='utf-8'))
        result = validate(data, args.root, args.html)
        result['ledger_sha256'] = sha(args.data)
        if args.html and args.html.is_file():
            result['html_sha256'] = sha(args.html)
    except (OSError, ValueError, TypeError) as exc:
        result = {'status': 'failed', 'errors': [str(exc)], 'counts': {}}
    result['checked_at_utc'] = dt.datetime.now(dt.timezone.utc).isoformat()
    result['scope'] = 'Structural and local artifact integrity only; no factual, financial, remote-source or production verification.'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result[k] for k in ['status', 'errors', 'counts']}))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
