# SentinelScan Architecture

## 1. Requirements

### Functional requirements

- Accept an absolute HTTP(S) target URL through a Next.js portal and require an authorization confirmation checkbox.
- Create an asynchronous scan through FastAPI, Celery, Redis, and PostgreSQL.
- Poll scan progress and expose queued, scanning, analyzing, completed, and failed states.
- Run Nuclei as a subprocess with the tags `cve,exposure,misconfig,tech` and JSON export.
- Extract CMS, framework, server, library, and version fingerprints from Nuclei technology output.
- Match fingerprinted components to NVD CVEs by normalized CPE/version and cache responses.
- Map Nuclei tags and custom checks to OWASP Top 10:2025 categories A01-A10.
- Bucket CVSS v3 scores as Critical 9.0-10, High 7.0-8.9, Medium 4.0-6.9, or Low 0.1-3.9.
- Run SPF/DKIM/DMARC checks, cookie flag checks, CISA KEV matching, and CycloneDX SBOM export after Tier 1 is complete.
- Generate a dashboard and downloadable PDF containing an executive summary, technology profile, findings table, detailed finding cards, and remediation roadmap.
- Generate Gemini remediation snippets per finding and a two-to-three sentence executive summary from the top three-to-five findings.
- Deploy locally through Docker Compose with frontend, backend, worker, PostgreSQL, and Redis services.

### Non-functional requirements

- Scans are read-only and non-destructive.
- The API must remain responsive while scans execute in Celery workers.
- External calls have bounded timeouts, retries where appropriate, cached responses, and failure states.
- Secrets are supplied through environment variables.
- Nuclei receives an argument list, never a shell command string.
- The dashboard is usable on desktop and mobile and reports progress clearly.
- The core pipeline must be demonstrable from a clean Docker Compose start by September 13, 2026.
- The implementation uses only free hackathon-phase tools and APIs and requires no credit card.

### Assumptions and resolved ambiguities

| Ambiguity | Decision |
|---|---|
| Blueprint paths say `/api/scan`, while Prompt 1 names `/scan`. | Public routes use the `/api` prefix: `/api/scan`, `/api/scan/{id}/status`, and `/api/scan/{id}/report`. These are the Prompt 1 operations with an explicit API prefix. |
| JWT is required but token issuance is unspecified. | Provide a minimal `/api/auth/token` endpoint for a demo token. Full registration, refresh, password reset, and RBAC are out of scope. |
| SBOM is required but has no locked endpoint. | Provide `/api/scan/{id}/sbom`; this makes the required export usable without adding a product feature. |
| The blueprint permits WeasyPrint or ReportLab. | Use WeasyPrint because Prompt 1 names it directly. |
| The blueprint calls Features 20-21 stretch work. | They are excluded from this locked planning scope; only Features 18-19 are planned. |
| The blueprint conditionally permits SOAR Features 26-27. | Do not include them. Prompt 1 explicitly excludes the SOAR loop. |
| Authorization and authentication are different concepts. | JWT authenticates the requester; the per-scan checkbox records target authorization timestamp and submitting IP. Cryptographic ownership proof is deferred. |
| NVD and KEV retention duration is unspecified. | Cache NVD responses for 24 hours and the KEV feed for 6 hours, with stale-cache fallback when an upstream call fails. |

## 2. Confirmed Tech Stack

| Area | Version / choice | Purpose |
|---|---|---|
| Frontend runtime | Node.js 22 LTS | Reproducible frontend builds |
| Frontend | Next.js 15.1.4, React 19.0.0 | Portal, polling, report views |
| Styling | Tailwind CSS 4.0.0 | UI styling |
| Backend runtime | Python 3.12.x | API and worker runtime |
| API | FastAPI 0.115.6, Uvicorn 0.34.0 | REST API |
| Async jobs | Celery 5.4.0 | Scan orchestration |
| Broker/result backend | Redis 7.4 | Queue and task results |
| Data | PostgreSQL 16 | Relational scan data and cache metadata |
| Detection | Nuclei 3.3.7 | Fingerprinting and vulnerability templates |
| Supporting checks | dnspython 2.7, HTTP client, socket/SSL utilities | DNS and cookie checks |
| Intelligence | NVD CVE 2.0 REST API and CISA KEV JSON | CVE enrichment and active-exploitation context |
| AI | Gemini API, `gemini-2.5-flash-lite` | Remediation and executive summary |
| Reports | Jinja2 3.1.5 and WeasyPrint 63.1 | HTML templates and PDF output |
| SBOM | CycloneDX 1.6 JSON | Component export |
| Deployment | Docker Engine 27.x and Docker Compose v2.x | Clean local deployment |
| Authentication | JWT | Request authentication |

These are baseline pins for the planning artifact. A clean-image dependency install remains a pre-implementation compatibility check. ReportLab is the only reasonable PDF substitution if WeasyPrint system libraries block the build; it is not the selected implementation.

## 3. Repo Structure

The planned repository structure is:

- `frontend/`: Next.js application, including `app/page.tsx`, report view, polling client, URL validation, and global styling.
- `backend/app/main.py`: FastAPI application and route registration.
- `backend/app/config.py`: environment-backed settings.
- `backend/app/auth.py`: JWT issuance and validation.
- `backend/app/db.py` and `backend/app/models.py`: SQLAlchemy database session and models.
- `backend/app/schemas.py`: request and response contracts.
- `backend/app/celery_app.py`: Celery configuration.
- `backend/app/tasks.py`: scan lifecycle task and failure handling.
- `backend/app/security.py`: URL parsing and SSRF target validation.
- `backend/app/nuclei.py`: safe subprocess invocation and JSONL parsing.
- `backend/app/mapping.py`: versioned Nuclei/custom-check to OWASP lookup.
- `backend/app/scoring.py`: CVSS v3 bucket logic.
- `backend/app/checks.py`: SPF/DKIM/DMARC and cookie checks.
- `backend/app/nvd.py` and `backend/app/kev.py`: cached intelligence clients.
- `backend/app/ai.py`: Gemini calls and cache lookup.
- `backend/app/reporting.py`: Jinja2 rendering and WeasyPrint PDF generation.
- `backend/app/sbom.py`: CycloneDX serialization.
- `backend/migrations/`: schema migration history.
- `backend/tests/`: URL validation, mapping, scoring, API, and worker tests.
- `backend/Dockerfile`: backend and worker image.
- `frontend/Dockerfile`: frontend image.
- `docker-compose.yml`: frontend, backend, worker, PostgreSQL, and Redis.
- `.env.example`, `.gitignore`, and `README.md`: configuration and clean-start instructions.

## 4. Build Roadmap: September 6-15

**September 6-7, Foundation:** Build the URL intake form, authorization checkbox, client-side validation, FastAPI scan creation, PostgreSQL scan record, Celery/Redis dispatch, and status polling. Done means an approved public test URL creates a queued scan and the UI reaches a terminal status without blocking the API.

**September 7-9, Core MVP:** Add safe Nuclei execution, JSON parsing, technology/version extraction, NVD CPE/version matching and cache, OWASP A01-A10 mapping, CVSS buckets, report data, Jinja2 templates, and WeasyPrint PDF output. Done means the Tier 1 pipeline produces a prioritized dashboard and downloadable report; this is the non-negotiable floor.

**September 9-10, Enhanced detection and intelligence:** Add SPF/DKIM/DMARC, cookie `Secure`/`HttpOnly`/`SameSite` checks, CISA KEV cache and badges/escalation, and CycloneDX SBOM export. Done means one completed scan contains DNS and cookie findings, marks KEV CVEs, and exports the detected technology profile as SBOM JSON.

**September 10-12, AI layer:** Add Gemini remediation snippets keyed by finding type and technology, then one executive-summary call using the top three-to-five findings. Done means the report shows a pastable remediation suggestion per finding and a concise plain-language summary while caching calls within the free-tier limits.

**September 12-13, integration and polish:** Run the full pipeline from a clean Compose start, test approved targets, repair failure paths, polish the dashboard and PDF, and freeze scope. Done means frontend, API, worker, database, and Redis start together and the complete Tier 1-4 flow is demoable by end of September 13.

**September 14-15, buffer and rehearsal:** Use these dates only for full-run regression, approved-target retesting, fallback demo recording, presentation rehearsal, and judge questions about deferred work. Done means there is a known-good live path and a fallback recording; no new roadmap feature enters the build.

If a checkpoint slips, cut roadmap-only work first, then any optional polish. Do not cut Tier 1 or the mandatory Tier 2/3 and Tier 4 items from the locked scope.

## 5. Minimal Security Posture

The intake accepts only absolute HTTP(S) URLs, rejects credentials, fragments, unsupported ports, localhost, loopback, private, link-local, reserved, multicast, unspecified, and cloud-metadata/internal destinations, and resolves hostnames before scanning. Resolution is repeated at the worker boundary to reduce DNS-rebinding exposure. Nuclei is invoked with a fixed argument list, `shell=False`, bounded execution time, and bounded output handling. Findings and evidence are treated as untrusted display data. JWT secrets, Gemini keys, and NVD keys come from environment variables. Scan records retain the authorization-confirmation timestamp and submitting IP, and report access checks scan ownership. This is a hackathon posture, not a production abuse-control claim: domain-ownership verification, rate limiting, encryption at rest, and observability are deferred.

## 6. Not Building: Judge-Ready Scope

For the hackathon, SentinelScan deliberately delivers a reliable read-only Tier 1-4 scanner rather than pretending to be a production platform. We are not building cryptographic domain ownership verification, rate limiting, encryption at rest, Prometheus/Grafana observability, the SOAR alert/approval/execution/verification loop, multi-tenancy or RBAC, scheduled scans, CI/CD hooks, compliance report variants, shareable links, trust badges, HaveIBeenPwned correlation, CT discovery, reputation lookup, API exposure/SRI auditing, LLM false-positive triage, or chat with the report. These are roadmap items because the available window prioritizes a working scan, defensible OWASP/CVSS/CVE enrichment, AI remediation, PDF reporting, and SBOM output over incomplete production-scale features.
