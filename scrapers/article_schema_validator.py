
from __future__ import annotations
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin
from common.http import ThrottledSession
from common.output import write_csv

FIELDS = ['title', 'author', 'published', 'section', 'lead_image']


def parse_article(html: str, selectors, base_url: str) -> Dict:
    soup = BeautifulSoup(html, 'lxml')
    title = soup.find('meta', property='og:title')
    if title: title = title.get('content')
    title = title or (soup.find('title').get_text(strip=True) if soup.find('title') else '')
    author = (soup.select_one(selectors.author).get_text(strip=True) if soup.select_one(selectors.author) else '')
    time_el = soup.select_one(selectors.time)
    published = time_el.get('datetime') if time_el and time_el.has_attr('datetime') else (time_el.get_text(strip=True) if time_el else '')
    section_el = soup.select_one(selectors.section_tag)
    section = section_el.get_text(strip=True) if section_el else ''
    img = soup.find('meta', property='og:image')
    lead_image = img.get('content') if img else ''
    if lead_image and lead_image.startswith('/'):
        lead_image = urljoin(base_url, lead_image)
    return {'title': title, 'author': author, 'published': published, 'section': section, 'lead_image': lead_image}


def validate_article(fields: Dict) -> Dict:
    missing = [k for k in FIELDS if not fields.get(k)]
    return {'missing_fields': ', '.join(missing)}


def run(base_url: str, urls: List[str], selectors, session: ThrottledSession, out_dir: Path) -> Dict:
    rows: List[Dict] = []
    for url in urls:
        r = session.get(url)
        ok = r.ok
        data = parse_article(r.text if ok else '', selectors, base_url) if ok else {k: '' for k in FIELDS}
        issues = validate_article(data)
        rows.append({'url': url, 'http_ok': ok, **data, **issues})
    write_csv(out_dir / 'article_schema_validation.csv', rows)
    issues_count = sum(1 for r in rows if r.get('missing_fields'))
    return {'checked': len(rows), 'issues': issues_count}
