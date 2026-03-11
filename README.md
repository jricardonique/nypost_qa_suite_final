
# NYPost QA Scraper Suite — FINAL

This repo is ready for **GitHub Actions** + **Netlify UI**. Do **NOT** upload the ZIP file itself to GitHub. **Extract** the ZIP and upload the **contents** at repo root so that the hidden folder `.github/workflows/` is present.

## Quick start
1. Create a new GitHub repo **you own**.
2. Upload the **contents** of this folder (ensure `.github/workflows/scraper.yml` exists in the repo tree).
3. In GitHub → **Actions** → Enable workflows.
4. Repo → **Settings → Secrets and variables → Actions**
   - **Variables (plain text)** for smoke test:
     - `SKIP_NETWORK = true`
     - `DISABLE_EMAIL = true`
     - `HTTP_USER_AGENT = NYPost-QA-Scraper/1.0 (+QA)`
     - `RATE_LIMIT_PER_SEC = 2`
     - `REQUEST_TIMEOUT = 15`
   - **Secrets (encrypted)** for live mode:
     - `SENDGRID_API_KEY`
     - `FROM_EMAIL`
     - `TO_EMAIL`
     - (optional) `NETLIFY_BUILD_HOOK`
5. Actions → **NYPost QA Scraper Suite** → **Run workflow**.
6. When green, set `SKIP_NETWORK=false` and `DISABLE_EMAIL=false` to go live.

## Verify structure
Your repo must contain:
```
.github/workflows/scraper.yml   ✅
config.yaml                     ✅
pipeline.py                     ✅
requirements.txt                ✅
web/ (with data/)               ✅
```
