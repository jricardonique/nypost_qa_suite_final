
from __future__ import annotations
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin
import time
from common.http import ThrottledSession
from common.output import write_csv, write_json


def extract_media_urls(html: str, base_url: str, selectors) -> List[str]:
    soup = BeautifulSoup(html, 'lxml')
    urls = []
    for img in soup.select(selectors.images):
        src = img.get('src') or img.get('data-src')
        if src:
            urls.append(urljoin(base_url, src))
    for v in soup.select(selectors.videos):
        src = v.get('src') or v.get('data-src') or v.get('data-video-src')
        if src:
            urls.append(urljoin(base_url, src))
    return list(dict.fromkeys(urls))


def validate_url(session: ThrottledSession, url: str) -> Dict:
    row = {'url': url, 'status': None, 'ok': False, 'elapsed_ms': None, 'size_bytes': None}
    t0 = time.time()
    try:
        resp = session.get(url, stream=True)
        elapsed = (time.time() - t0) * 1000
        row['status'] = resp.status_code
        row['ok'] = resp.ok
        row['elapsed_ms'] = round(elapsed, 1)
        size = 0
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk:
                size += len(chunk)
                if size > 5_000_000:
                    break
        row['size_bytes'] = size
        resp.close()
    except Exception as e:
        row['status'] = str(e)
        row['ok'] = False
    return row


def run(base_url: str, article_urls: List[str], selectors, session: ThrottledSession, out_dir: Path) -> Dict:
    results: List[Dict] = []
    for url in article_urls:
        r = session.get(url)
        if not r.ok:
            results.append({'article_url': url, 'type': 'article_fetch', 'ok': False, 'status': r.status_code})
            continue
        media = extract_media_urls(r.text, base_url, selectors)
        for m in media:
            row = validate_url(session, m)
            row['article_url'] = url
            results.append(row)
    write_csv(out_dir / 'multimedia_validation.csv', results)
    write_json(out_dir / 'multimedia_validation.json', results)
    errors = [r for r in results if not r.get('ok')]
    return {'checked': len(results), 'errors': len(errors)}
