
from __future__ import annotations
import os, json, requests

def email_alert(subject: str, message: str) -> bool:
    api = os.getenv('SENDGRID_API_KEY')
    from_email = os.getenv('FROM_EMAIL')
    to_email = os.getenv('TO_EMAIL')
    if not api or not from_email or not to_email:
        print('[Email] Missing SENDGRID_API_KEY / FROM_EMAIL / TO_EMAIL')
        return False
    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": message}]
    }
    try:
        r = requests.post('https://api.sendgrid.com/v3/mail/send',
                          headers={'Authorization': f'Bearer {api}', 'Content-Type':'application/json'},
                          data=json.dumps(payload), timeout=15)
        ok = r.status_code in (200, 202)
        if not ok:
            print('[Email] SendGrid error:', r.status_code, r.text[:200])
        return ok
    except Exception as e:
        print('[Email] Exception:', e)
        return False
