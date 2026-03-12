from __future__ import annotations
import os, json
from pathlib import Path
from dotenv import load_dotenv
from common.config import load_config
from common.http import ThrottledSession
from common.output import run_dir, write_json
from common.logging_config import setup_logging
from common.email import email_alert
def main():
    load_dotenv()
    cfg = load_config(Path('config.yaml'))
    logger = setup_logging(Path('logs'), name='pipeline')
    out = run_dir(Path(cfg.output_dir))
    logger.info(f'Pipeline output: {out}')
    # Offline smoke test mode
    offline = os.getenv('SKIP_NETWORK', 'false').lower() == 'true'
    h = {'count': 0}
    m = {'checked': 0, 'errors': 0}
    p = {'checked': 0, 'slow': 0}
    s = {'checked': 0, 'issues': 0}
    write_json(out / 'headlines_sections.json', [])
    summary = {'headlines': h, 'multimedia': m, 'perf': p, 'schema': s, 'output': str(out)}
    write_json(out / 'pipeline_summary.json', summary)
    logger.info(f'Summary: {summary}')
    alerts = []
    if os.getenv('DISABLE_EMAIL', 'false').lower() != 'true' and (m.get('errors',0)>0 or p.get('slow',0)>0 or s.get('issues',0)>0):
        if m.get('errors',0)>0: alerts.append(f"Multimedia broken assets: {m['errors']}")
        if p.get('slow',0)>0: alerts.append(f"Slow URLs: {p['slow']}")
        if s.get('issues',0)>0: alerts.append(f"Articles with schema issues: {s['issues']}")
        msg = "\n".join(alerts) + f"\n\nOutput: {out}"
        email_alert("[NYPost QA] Pipeline Alerts", msg)
if __name__ == '__main__':
    main()