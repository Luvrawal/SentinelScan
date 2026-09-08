# Key Technical Decisions

## Scope and authority

`MASTER_BLUEPRINT.md` is the source of truth. `PROMPT_1_ARCHITECTURE.md` locks the implementation boundary. The build includes Tier 1 features 1-8, Tier 2/3 features 9, 10, 15, and 17, and Tier 4 features 18 and 19. Blueprint-only roadmap work does not enter the implementation plan.

## API prefix and authentication

The public API uses `/api` because the blueprint explicitly shows `/api/scan`; the required Prompt 1 operations remain POST `/scan`, GET `/scan/{id}/status`, and GET `/scan/{id}/report` conceptually beneath that prefix. A minimal token endpoint makes the mandated JWT contract usable. Full account lifecycle and RBAC would consume time without improving the locked demo.

## Scan ownership and authorization

JWT identifies the requester. The scan stores the authorization checkbox, timestamp, and submitting IP. Domain ownership verification is intentionally not substituted for the checkbox because it belongs to Tier 5 roadmap work. Every report and artifact request checks scan ownership.

## Nuclei data model

Each JSONL event becomes a finding or technology profile entry. Raw Nuclei evidence is retained in JSONB for traceability, while normalized title, description, template ID, CVE, score, severity, and OWASP category support filtering and reporting. Duplicate events are collapsed with a scan-local finding key and evidence digest.

## OWASP mapping

A versioned lookup table maps Nuclei tags and custom check identifiers to A01-A10. The parser applies the most specific matching tag, then falls back to A02 for an explicitly labeled misconfiguration/unknown check. Custom DNS checks map to A02 and cookie checks to A04. The mapping is data-driven so new tags do not require report or schema changes.

## CVSS scoring

Use the score supplied by NVD or Nuclei metadata and preserve the source version. Buckets are fixed: Critical 9.0-10, High 7.0-8.9, Medium 4.0-6.9, Low 0.1-3.9. Missing scores retain the source severity or become Low and are visibly marked as unscored; they are never invented.

## NVD and KEV caching

Normalize CPE/version queries before using them as NVD cache keys. Cache successful NVD responses for 24 hours and retry transient failures with bounded exponential backoff. Use a six-hour CISA KEV snapshot cache. If an upstream is unavailable and a stale cache exists, use the stale value and record the age; otherwise continue the scan with a non-fatal enrichment warning unless the core finding cannot be interpreted.

## AI free-tier behavior

Use `gemini-2.5-flash-lite`. Cache remediation by finding type plus normalized technology context. Send one executive-summary request per completed scan using the top three-to-five findings. Timeout and API failures do not fail the scan; the report displays deterministic fallback guidance. This keeps calls near the documented approximately 15 requests/minute and 1,000/day free-tier limits.

## Async orchestration

FastAPI only validates, persists, enqueues, polls, and retrieves. Celery owns the long-running pipeline and writes progress after each stage. Redis is the broker/result backend. A failed subprocess or upstream call produces a terminal failed state with a safe reason rather than leaving a scan indefinitely queued.

## PDF and SBOM

Use Jinja2 to produce a single report representation and WeasyPrint to render the downloadable PDF. Generate CycloneDX 1.6 JSON directly from the technology profile; it is a structured artifact, not a second scanning pipeline. ReportLab is a contingency substitution only if WeasyPrint's native dependencies cannot be made reliable in Docker.

## Deployment and trade-offs

Docker Compose is mandatory for judge reproducibility. PostgreSQL is used instead of a document store because scans, findings, technologies, caches, and ownership have clear relationships and indexed query paths. Object storage is represented as artifact metadata in the hackathon schema; local artifact storage is sufficient for the demo.

## Security boundaries

Reject unsafe URL targets before persistence and repeat resolution before the worker launches Nuclei. Use fixed subprocess arguments, no shell interpolation, timeouts, bounded output, and environment-backed secrets. This is deliberately a minimal hackathon posture; rate limiting, cryptographic ownership, encryption at rest, and observability remain future work.
