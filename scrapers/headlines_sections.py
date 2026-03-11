
from __future__ import annotations
from bs4 import BeautifulSoup
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin
from common.http import ThrottledSession
from common.output import write_csv, write_json

@dataclass
class Story:
    rank: int
    section: str
    title: str
    url: str


def crawl_section(base_url: str, section: str, limit: int, selectors, session: ThrottledSession) -> List[Story]:
    # Minimal implementation for reliability; you can extend with real parsing
    url = f"{base_url.rstrip('/')}/{section.strip('/')}" if section != 'top-stories' else base_url
    r = session.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, 'lxml')
    cards = soup.select(selectors.article_card) or soup.find_all('article')
    stories: List[Story] = []
    rank = 1
    for c in cards:
        h = c.select_one(selectors.headline) or c.find(['h1','h2','h3'])
        a = (h.find('a') if h else None) or c.select_one(selectors.link)
        title = (h.get_text(strip=True) if h else '')
        href = a['href'] if a and a.has_attr('href') else ''
        if href and href.startswith('/'):
            href = urljoin(base_url, href)
        if href and title:
            stories.append(Story(rank=rank, section=section, title=title, url=href))
            rank += 1
        if limit and len(stories) >= limit:
            break
    return stories


def run(base_url: str, sections: List[str], limit: int, selectors, session: ThrottledSession, out_dir: Path) -> Dict:
    all_rows: List[Dict] = []
    for sec in sections:
        for s in crawl_section(base_url, sec, limit, selectors, session):
            all_rows.append({'rank': s.rank,'section': s.section,'title': s.title,'url': s.url})
    write_csv(out_dir / 'headlines_sections.csv', all_rows)
    write_json(out_dir / 'headlines_sections.json', all_rows)
    return {'count': len(all_rows)}
