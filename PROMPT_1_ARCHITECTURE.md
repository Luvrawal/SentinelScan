ROLE: You are a Principal Solutions Architect designing the technical foundation for
"SentinelScan," a web-based automated vulnerability scanner and AI-driven remediation
reporting tool, built for a hackathon with a hard deadline (feature-complete by Sep 13,
demo on Sep 15). Do not write implementation code in this step — produce planning
artifacts only.

CONTEXT:
SentinelScan takes a user-submitted URL, runs it through Nuclei (subprocess) plus custom
Python checks, cross-references findings against NVD/CVE and CISA KEV, maps everything to
OWASP Top 10:2025 categories, scores severity via CVSS, and generates an AI-enhanced
report (dashboard + downloadable PDF) using the Gemini API free tier.

LOCKED FEATURE SCOPE (build in this exact priority order):
Tier 1 — mandatory: (1) URL intake form with authorization checkbox, (2) FastAPI + Celery
+ Redis job orchestration with endpoints POST /scan, GET /scan/{id}/status, GET
/scan/{id}/report, (3) Nuclei subprocess integration (-tags cve,exposure,misconfig,tech,
JSON export), (4) tech/CMS/version fingerprinting from Nuclei tech-tag output, (5)
NVD/CVE REST API matching by CPE/version with response caching, (6) a maintained lookup
table mapping Nuclei tags + custom-module outputs to OWASP Top 10:2025 categories A01–A10,
(7) CVSS v3 severity bucketing (Critical 9.0-10, High 7.0-8.9, Medium 4.0-6.9, Low
0.1-3.9), (8) Jinja2 + WeasyPrint report generator (dashboard view + downloadable PDF:
exec summary, tech profile, findings table, detail cards, remediation roadmap).

Tier 2/3 — build after Tier 1 is fully working: (9) SPF/DKIM/DMARC via dnspython, (10)
cookie Secure/HttpOnly/SameSite audit, (15) CISA KEV JSON feed cross-check with
escalation badge, (17) CycloneDX SBOM export from the tech profile.

Tier 4 — AI layer via Google Gemini API free tier (gemini-2.5-flash-lite, ~15 req/min and
1000/day — cache by finding-type+tech to stay under this): (18) AI-generated pastable
remediation snippet per finding, (19) AI 2-3 sentence executive summary from top 3-5
findings.

EXPLICITLY OUT OF SCOPE for this build (design a one-paragraph "future work" note only):
domain-ownership verification, rate limiting, encryption at rest, observability stack,
SOAR alert/approval/execution/verification loop, multi-tenancy/RBAC, scheduled scans,
CI/CD hooks, compliance report variants, shareable links, trust badges, HaveIBeenPwned
integration.

DELIVERABLES (produce all of these as structured markdown, in this order):
1. Requirements recap: functional + non-functional requirements, explicit assumptions
   you're making, and anything you consider ambiguous — flag it, then state the
   assumption you're proceeding with rather than leaving it open.
2. Confirmed tech stack with version numbers: Next.js/React + Tailwind (frontend),
   FastAPI (backend), Celery + Redis (async), PostgreSQL (data), Nuclei binary
   (detection), Gemini API (AI), WeasyPrint (PDF), CycloneDX (SBOM), Docker +
   docker-compose (deployment). Flag any substitution you'd recommend and why.
3. Full PostgreSQL schema: tables for users, scans, findings, tech_profile entries, and
   any junction tables needed — columns, types, keys, indexes.
4. Complete REST API contract: every endpoint, method, request/response JSON shape,
   status codes, auth requirement (JWT).
5. Full repo folder structure (frontend + backend + worker + docker), down to key file
   names.
6. Sequenced build roadmap mapped to this window: Sep 6-7, 7-9, 9-10, 10-12, 12-13
   (integration/polish), 14-15 (buffer) — one paragraph per phase stating exactly what
   "done" looks like.
7. Key technical decisions and trade-offs made up front (e.g., how Nuclei JSON maps to
   the DB schema, how NVD rate limits are handled, how the OWASP lookup table is
   structured so it's easy to extend).
8. Minimal security posture for a hackathon build: input validation on the submitted URL
   (block internal/private IP ranges and localhost to prevent SSRF against your own
   infra), safe subprocess invocation of Nuclei (no shell=True, argument list not string
   interpolation), and API key handling via environment variables — call out that
   domain-ownership verification and rate limiting are explicitly deferred.
9. A short "what we're not building and why" section, worded for a judge-facing roadmap
   slide.

OUTPUT FORMAT: markdown only, headed sections matching the deliverables above. No code
in this step.