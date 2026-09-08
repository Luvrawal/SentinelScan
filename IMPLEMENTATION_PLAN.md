# SentinelScan Build Roadmap

This is the implementation sequence for the locked Tier 1-Tier 4 scope. `MASTER_BLUEPRINT.md` is authoritative; `PROMPT_1_ARCHITECTURE.md` defines the locked deliverables. Feature-complete target: September 13, 2026. Finale: September 15, 2026.

## September 6-7: Foundation

Build the Next.js URL intake form, client-side HTTP(S) validation, authorization checkbox, FastAPI scan creation, PostgreSQL scan record, Celery/Redis dispatch, and status polling. Done means an approved public test URL creates a queued scan and reaches a terminal state without blocking the API.

## September 7-9: Core MVP

Add safe Nuclei execution with `cve,exposure,misconfig,tech` tags and JSON export, technology/version extraction, NVD CPE/version matching with response caching, OWASP A01-A10 mapping, CVSS v3 buckets, report data, Jinja2 templates, and WeasyPrint PDF generation. Done means Tier 1 produces a prioritized dashboard and downloadable report. This is the non-negotiable floor.

## September 9-10: Enhanced Detection and Intelligence

Add SPF/DKIM/DMARC checks through dnspython, cookie `Secure`/`HttpOnly`/`SameSite` checks, CISA KEV feed caching and actively-exploited badges/escalation, and CycloneDX 1.6 SBOM export. Done means a completed scan includes these results and exports its technology profile as SBOM JSON.

## September 10-12: AI Layer

Add Gemini `gemini-2.5-flash-lite` remediation snippets keyed by finding type and normalized technology, then one executive-summary call using the top three-to-five findings. Done means the report contains a pastable remediation suggestion per finding and a two-to-three sentence summary while remaining within the approximately 15 requests/minute and 1,000 requests/day free-tier assumptions.

## September 12-13: Integration and Polish

Run the entire pipeline from a clean Docker Compose start, test approved targets, repair failure and timeout paths, polish the dashboard and PDF, and freeze scope. Done means frontend, API, worker, PostgreSQL, and Redis start together and the complete locked pipeline is demoable by the end of September 13.

## September 14-15: Buffer and Rehearsal

Use the final dates for regression against approved targets, fallback demo recording, live-pitch rehearsal, and prepared answers about roadmap work. Done means there is a known-good live path and a fallback recording. No new roadmap feature enters the build.

## Cut rule

If a checkpoint slips, remove roadmap-only work and optional polish first. Do not cut Tier 1, Features 9, 10, 15, or 17, or mandatory Tier 4 Features 18 and 19 from this locked plan.

## Scope boundary

Domain ownership verification, rate limiting, encryption at rest, observability, SOAR, multi-tenancy/RBAC, scheduled scans, CI/CD hooks, compliance variants, shareable links, trust badges, HaveIBeenPwned, CT discovery, reputation lookup, API exposure/SRI auditing, LLM false-positive triage, and report chat are not implementation tasks in this plan.
