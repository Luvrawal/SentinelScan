ROLE: You are a Principal Full-Stack + Security Engineer implementing "SentinelScan"
end-to-end from the architecture in [PASTE PROMPT 1 OUTPUT HERE]. Build production-
quality, working code — not scaffolding or TODOs — for every item in the locked scope
below. Work phase by phase in the order given; after each phase, run/build/lint the code
yourself and fix errors before moving to the next phase — do not hand off code you have
not verified runs.

BUILD ORDER (do not skip ahead; do not silently drop a feature — if something can't be
implemented as specified, say so explicitly and propose the closest working alternative):

Phase 1: URL intake form (Next.js + Tailwind, client-side validation + authorization
checkbox) → FastAPI POST /scan, GET /scan/{id}/status → Celery + Redis wiring → Nuclei
subprocess call (-tags cve,exposure,misconfig,tech -json-export) → parse JSON → store
raw findings in PostgreSQL linked to scan ID.

Phase 2: Tech/CMS fingerprint extraction from Nuclei tech-tag output → NVD/CVE REST API
matching (with local caching to respect rate limits) → OWASP Top 10:2025 mapping table
(Nuclei tag → A01-A10) applied at parse time → CVSS v3 bucketing and sort → GET
/scan/{id}/report → Jinja2 + WeasyPrint PDF generation (exec summary, tech profile,
findings table, detail cards, remediation roadmap) → "Download PDF" in the dashboard.

Phase 3: SPF/DKIM/DMARC check via dnspython → cookie Secure/HttpOnly/SameSite audit from
Set-Cookie headers → CISA KEV JSON feed cached and cross-referenced against detected
CVEs, with a badge on matches → CycloneDX SBOM JSON export endpoint + "Export SBOM"
button.

Phase 4: Gemini API integration (env var for API key, gemini-2.5-flash-lite) —
remediation snippet generation per finding (prompt: finding description + affected
component + tech stack, request a specific pastable fix), cached by finding-type+tech
pair — executive summary generation from top 3-5 findings, one call per completed scan,
displayed at the top of the report.

Phase 5: Dockerfile(s) for frontend, backend, and worker; docker-compose.yml wiring
Postgres, Redis, backend, worker, frontend; a README with exact setup/run steps (env
vars needed: DATABASE_URL, REDIS_URL, GEMINI_API_KEY, NVD_API_KEY if used). Verify
`docker-compose up` brings the full stack up from a clean clone with no manual steps
beyond copying a `.env.example` to `.env` and filling in keys.

NON-NEGOTIABLE IMPLEMENTATION REQUIREMENTS (apply throughout, not just at the end):
- Real error handling on every external call (Nuclei subprocess, NVD API, CISA KEV feed,
  Gemini API): timeouts, retries where sensible, and a state the scan can land in
  ("failed" with a reason) rather than hanging or crashing the worker.
- Validate and sanitize the submitted URL before it ever reaches Nuclei or a subprocess
  call: reject non-http(s) schemes, reject localhost/private/link-local IP ranges (SSRF
  guard), and never build the Nuclei command via string concatenation — use an argument
  list.
- All secrets (Gemini key, NVD key, DB credentials) via environment variables, never
  hardcoded, with a `.env.example` checked in and the real `.env` gitignored.
- Every Celery task must update scan status in the DB at each stage (queued → scanning →
  analyzing → done/failed) so the frontend's polling reflects real progress.
- Cache Gemini calls by (finding-type, tech-stack) key and cache NVD/CISA responses
  locally so repeated demo runs don't hit rate limits live.
- Write the code as if a stranger has to run it cold from the README with zero verbal
  explanation from you.

DELIVERABLE: the complete, working repository (all files), plus the README, plus a short
"how to demo this in 5 minutes" script at the end (exact URL to submit, what to click,
what to expect at each stage).