# SentinelScan — Master Project Blueprint (v2, Updated)
### Automated Website Vulnerability & OWASP Top 10:2025 Scanner with AI-Driven Remediation (SOAR Response on Roadmap)
**Built for:** GLS University Hackathon | Problem Statement: "Website Scanning Tool" (posted by Uplers) | **Team:** Divyanshu & Luv | **Feature-complete target:** September 13, 2026 | **Grand Finale:** September 15, 2026

> **How to use this document:** Self-contained — it doesn't assume you've read any prior version. To brief an AI coding tool (Claude Code, ChatGPT, Cursor, etc.) on one part of the build, paste the **Architecture** section plus the specific **Feature** entry you're working on. Each feature entry keeps the *What / Why / How / Steps* structure, plus a **Status tag** telling you whether it's actually in this build or on the roadmap slide only.

> **Cost policy:** every tool, library, and API used in the hackathon-phase features is free, no credit card required. HaveIBeenPwned (Feature #16) remains **deferred to a future production phase** and is not part of this build.

---

## 0. What Changed in v2

The v1 blueprint was written against a 20-day plan (Aug 26 → Sep 15). Build actually started Sep 6, leaving **7 working days to a Sep 13 feature-complete target**, then **2 buffer/rehearsal days before the Sep 15 finale** — a third of the originally assumed time. Three changes follow from that:

1. **Phased Build Plan (Section 9) is fully rewritten** against real dates, not the original 20-day cadence.
2. **Every feature in Section 7 now carries a Status tag** — `BUILD` (going into the actual hackathon codebase) or `ROADMAP ONLY` (designed, presented on a slide, not implemented this cycle). Nothing was deleted; the full-vision spec is preserved for post-hackathon production work.
3. **Tier 5 (Trust & Production Readiness), Tier 6 (SOAR), and Tier 7 (Platform & Scale) move to `ROADMAP ONLY`** by default. Tier 6 has one conditional exception — see Feature #26.

Everything else — architecture, differentiation, USPs, OWASP mapping, tech stack — is materially unchanged; only scope and schedule are corrected.

---

## 1. Problem Statement

Security teams and website owners need a way to scan a website for vulnerabilities — including outdated software versions and OWASP Top 10 risks — and receive a report with findings and remediation recommendations. Expected solution: a web portal where a user submits a URL and receives a comprehensive security scan report.

---

## 2. Our Solution — Overview

**SentinelScan** is a web portal where a user submits a URL, confirms authorization, and receives an automated, AI-enhanced, prioritized security report within minutes. A closed-loop SOAR response layer is architected as part of the full product vision (Tier 6) but is **not part of the live hackathon demo** — it is presented as a roadmap item unless the team's existing capstone SOAR proves fast to wire in (see Feature #26).

**Core pipeline (as built for the hackathon):**
```
URL Submitted → Recon & Fingerprinting → Detection (Nuclei + Custom Modules)
→ Vulnerability Intelligence (NVD/CVE, KEV) → OWASP Top 10:2025 Mapping
→ CVSS Scoring → AI Enrichment (summary, remediation)
→ Report (dashboard + PDF + SBOM)
```

**Full product vision (post-hackathon):** the above, plus `[Optional] SOAR: Alert → Propose → Approve → Execute → Verify`.

**Delivered for the hackathon as:** an interactive web dashboard, a downloadable PDF report, an exportable SBOM. Chat-with-report and FP triage are stretch goals if the core finishes early (see Section 9).

---

## 3. System Architecture

**Layer 1 — Presentation**
React/Next.js portal: URL intake form, authorization checkbox, live scan progress, findings dashboard, report viewer. *(Chat-with-report widget and SOAR approval screen: stretch/roadmap — see Tier 4/6.)*

**Layer 2 — API & Orchestration**
FastAPI (Python) backend. REST endpoints for scan submission, status polling, report retrieval. JWT-based auth; role field reserved for future RBAC.

**Layer 3 — Async Scan Engine**
Celery workers + Redis broker. Scans run as background jobs so the portal never blocks; supports parallel scans.

**Layer 4 — Detection Engine (hybrid: Nuclei + custom Python modules)**
- *Nuclei subprocess integration* handles: technology fingerprinting, known-CVE detection, exposed panels/default configs, most misconfiguration checks.
- *Custom Python modules built for this cycle:* SPF/DKIM/DMARC, cookie flags.
- *Custom Python modules on the roadmap:* Certificate Transparency subdomain discovery, domain/IP reputation, API endpoint exposure, third-party script/SRI audit, A10:2025 exceptional-condition probing.

**Layer 5 — Vulnerability Intelligence**
NVD/CVE API lookups, CVSS v3 scoring, CISA KEV cross-referencing — all built, all free. (HaveIBeenPwned correlation remains a future production addition, Feature #16.)

**Layer 6 — OWASP Mapping Engine**
Translates Nuclei tags and custom-module outputs into OWASP Top 10:2025 categories (A01–A10) via a maintained lookup table — this is the team's own logic layer, built for the hackathon in full.

**Layer 7 — AI Layer (Google Gemini API — free tier, no credit card required)**
AI-generated remediation snippets and AI executive summaries are built. LLM false-positive triage and RAG-based chat-with-report are stretch goals. *(Production upgrade path: Anthropic Claude API, once the platform is monetized.)*

**Layer 8 — Report Generation**
Jinja2 templates + WeasyPrint/ReportLab for PDF; CycloneDX/SPDX formatting for SBOM export — built. Compliance-mapped (ISO 27001/SOC 2) report variant: roadmap only (Tier 7).

**Layer 9 — SOAR Integration** — **`ROADMAP ONLY`** *(builds out from the team's existing capstone SOAR, which currently only detects and reports)*
Ingests high-severity findings as alerts → proposes a remediation action → human-approval gate → executes approved safe actions → triggers a targeted re-scan to verify the fix. Not implemented this cycle; presented as designed future work unless Feature #26's condition is met.

**Layer 10 — Trust & Production Readiness** — **`ROADMAP ONLY`**
Domain-ownership verification (DNS TXT/file challenge), rate limiting/abuse prevention, encryption at rest, observability (Prometheus/Grafana). For the hackathon, authorization is a logged checkbox (see Feature #1) rather than a cryptographic ownership challenge.

**Layer 11 — Data**
PostgreSQL (users, scans, findings, audit-log stub). Object storage for PDFs/SBOMs. `pgcrypto` encryption at rest: roadmap only.

**Layer 12 — Deployment**
Docker + docker-compose — built, and non-negotiable (this is the "it just runs" story for judges). A hosted demo on Render/Railway is a stretch goal, not a requirement.

---

## 4. How This Differs From Existing Solutions

| | Nikto | OWASP ZAP | SentinelScan |
|---|---|---|---|
| Audience | Security pros (CLI) | Security engineers | Developers, site owners, compliance teams, non-experts |
| Interface | CLI | Proxy / scripting | One-click web portal |
| Output | Raw text list | Technical alert list | OWASP-2025-mapped, CVSS-prioritized report |
| Remediation | None | None | Plain-language + AI-generated fix snippets |
| Response | None | None | SOAR-driven propose → approve → execute → verify *(designed, roadmap)* |
| Framework alignment | N/A | Not OWASP-2025-native | Built around 2025 categories from day one |
| Detection engine | Built-in, limited | Built-in, broad | Nuclei (12,000+ maintained templates) + custom modules |

**Honest framing for judges:** SentinelScan doesn't try to out-build ZAP's scanning engine from scratch — it integrates an industry-standard engine (Nuclei) and puts its own value in orchestration, OWASP-2025 mapping, and AI-driven remediation, all live in the demo. The closed-loop SOAR response layer — the piece neither ZAP nor Nikto has at all — is fully designed and shown as the next milestone, not claimed as working today.

---

## 5. Our USPs

1. Built on **OWASP Top 10:2025** from day one — most tools in the market are still mapped to 2021. *(Live in demo.)*
2. **Unified coverage**: outdated-component detection and OWASP Top 10 in a single scan. *(Live in demo.)*
3. **AI-generated fixes**, not generic advice — an actual pastable config snippet per finding. *(Live in demo.)*
4. **CISA KEV-aware prioritization** — distinguishes "critical" from "critical and being exploited right now." *(Live in demo.)*
5. **Closed-loop response via SOAR** — detection alone is a report; SentinelScan's roadmap adds propose-and-approve remediation with verification. *(Designed, roadmap — not live in demo.)*
6. **Domain-ownership verification**, not just a checkbox — a legally defensible authorization model. *(Roadmap; hackathon build uses a logged checkbox.)*
7. **SBOM export** — a compliance artifact most student projects never think to generate. *(Live in demo.)*
8. **Chat-with-report** — ask questions about your own scan in plain language. *(Stretch goal — live only if core finishes early.)*

---

## 6. OWASP Top 10:2025 Coverage Map

**Full product vision:**

| Category (2025) | What We Detect | Detection Source |
|---|---|---|
| A01 Broken Access Control (absorbs SSRF) | Exposed admin panels, directory listing, unprotected `.env`/`.git`, unauthenticated API endpoints, SSRF-style params | Nuclei + custom API-exposure module |
| A02 Security Misconfiguration | Verbose errors, default configs, missing headers, weak SPF/DKIM/DMARC | Nuclei + custom DNS module |
| A03 Software Supply Chain Failures | Outdated CMS/plugins/libraries with known CVEs, risky third-party scripts | Nuclei + NVD/CVE + custom SRI audit |
| A04 Cryptographic Failures | Weak/expired TLS, deprecated protocols, mixed content, insecure cookie flags | Nuclei + custom TLS/cookie module |
| A05 Injection | Reflected-input handling issues (safe, non-destructive probes) | Custom module |
| A06 Insecure Design | Missing security-header patterns | Nuclei + custom module |
| A07 Authentication Failures | Login pages missing lockout/CAPTCHA signals | Custom module |
| A08 Software & Data Integrity Failures | Scripts without Subresource Integrity (SRI) | Custom module |
| A09 Security Logging & Alerting Failures | Informational — not externally testable black-box | Guidance note |
| A10 Mishandling of Exceptional Conditions | Stack traces/undefined states on malformed input | Custom module |

**What's actually live in the hackathon build** (so the team can answer a judge's "does it really do that?" honestly):

| Category | Hackathon Status |
|---|---|
| A01 Broken Access Control | Partial — Nuclei's exposure/panel checks only; custom API-exposure module is roadmap |
| A02 Security Misconfiguration | **Full** — Nuclei + SPF/DKIM/DMARC module built |
| A03 Software Supply Chain Failures | Partial — Nuclei + NVD/CVE built; SRI audit is roadmap |
| A04 Cryptographic Failures | Partial — Nuclei TLS checks + cookie-flag module built |
| A05 Injection | Roadmap — custom module not built this cycle |
| A06 Insecure Design | **Full** — Nuclei header checks |
| A07 Authentication Failures | Roadmap |
| A08 Software & Data Integrity Failures | Roadmap |
| A09 Security Logging & Alerting Failures | Guidance note only (as originally scoped — not black-box testable either way) |
| A10 Mishandling of Exceptional Conditions | Roadmap |

All checks, built or roadmap, are read-only and non-destructive by design.

---

## 7. Complete Feature Specification

Status tags: **`BUILD`** = going into the hackathon codebase. **`ROADMAP ONLY`** = fully specified, not implemented this cycle, presented on the roadmap slide.

### TIER 1 — Core MVP — **`BUILD`, all mandatory** (this is the literal problem statement)

**1. URL Intake Portal** — `BUILD`
- **What:** Web form where a user submits a target URL and confirms authorization.
- **Why:** The literal input mechanism the problem statement requires.
- **How:** React/Next.js form posting to the backend API.
- **Steps:** 1) Build form with URL input + authorization checkbox. 2) Client-side URL validation. 3) POST to `/api/scan`. 4) Poll `/api/scan/{id}/status` for live progress.
- **Hackathon note:** the authorization step is a logged checkbox (timestamp + submitting IP recorded), not a cryptographic domain-ownership challenge — that's Feature #22, roadmap only.

**2. Backend API & Job Orchestration** — `BUILD`
- **What:** REST API managing scan lifecycle.
- **Why:** Connects the frontend to the async scanning engine.
- **How:** FastAPI + Celery + Redis.
- **Steps:** 1) Build `/scan` (POST), `/scan/{id}/status` (GET), `/scan/{id}/report` (GET). 2) Configure Celery worker + Redis broker. 3) On request, create a DB record and dispatch a Celery task. 4) Task updates status as it progresses.

**3. Nuclei Integration** — `BUILD`
- **What:** Run ProjectDiscovery's open-source scanner as the core detection engine.
- **Why:** 12,000+ maintained templates instead of hand-written detection logic.
- **How:** Subprocess call from the Celery worker.
- **Steps:** 1) Install Nuclei binary in the Docker image; run `nuclei -update-templates` on build. 2) From the Celery task: `nuclei -u <url> -tags cve,exposure,misconfig,tech -json-export results.json`. 3) Parse JSON output. 4) Store raw findings in DB linked to the scan ID.

**4. Tech/CMS Fingerprinting** — `BUILD`
- **What:** Identify CMS, server, frameworks, JS libraries + versions.
- **Why:** Required to detect outdated components.
- **How:** Nuclei's `-tags tech` templates.
- **Steps:** 1) Filter Nuclei run to tech-detection templates. 2) Extract tech + version from output. 3) Store as a "technology profile" per scan.

**5. NVD/CVE Matching** — `BUILD`
- **What:** Cross-reference each fingerprinted tech + version against the National Vulnerability Database.
- **Why:** This is the "outdated software" half of the problem statement.
- **How:** NVD public REST API.
- **Steps:** 1) Query `https://services.nvd.nist.gov/rest/json/cves/2.0` by CPE/version. 2) Parse CVE ID, description, CVSS score, publish date. 3) Store matches linked to the finding. 4) Cache responses to respect NVD rate limits.

**6. OWASP Top 10:2025 Mapping** — `BUILD`
- **What:** Translate Nuclei tags and custom-module outputs into OWASP 2025 categories.
- **Why:** Your own logic layer — the credibility centerpiece of the project.
- **How:** A maintained lookup table (Nuclei tag/category → A01–A10:2025).
- **Steps:** 1) Build a dict mapping Nuclei tags (`exposed-panel`, `cve`, `misconfig`, `default-login`, etc.) to OWASP categories. 2) Apply during Nuclei-output parsing. 3) Manually tag each custom module's output with its OWASP category at creation time.

**7. CVSS Severity Scoring** — `BUILD`
- **What:** Bucket findings into Critical/High/Medium/Low.
- **Why:** Lets users prioritize instead of facing a flat list.
- **How:** CVSS v3 ranges from NVD/Nuclei metadata.
- **Steps:** 1) Pull CVSS score per finding. 2) Apply thresholds (Critical 9.0–10, High 7.0–8.9, Medium 4.0–6.9, Low 0.1–3.9). 3) Sort findings by severity for the report.

**8. Report Generator (Dashboard + PDF)** — `BUILD`
- **What:** Aggregate findings into a structured report.
- **Why:** The literal deliverable the problem statement asks for.
- **How:** Jinja2 templates + WeasyPrint/ReportLab.
- **Steps:** 1) Design report template (exec summary, tech profile, findings table, detailed cards, remediation roadmap). 2) Build an endpoint rendering it from DB data. 3) Convert to PDF via WeasyPrint. 4) Add "Download PDF" on the dashboard.

> **MVP checkpoint:** once 1–8 work end to end, the literal problem statement is satisfied. Everything below is enhancement.

### TIER 2 — Enhanced Detection

**9. SPF/DKIM/DMARC Check** — `BUILD`
- **What:** Verify the domain's email-spoofing protection records.
- **Why:** Cheap to build, most scanners skip it, a real-world common attack vector.
- **How:** DNS TXT record lookups via `dnspython`.
- **Steps:** 1) Query TXT records for the domain. 2) Check for valid SPF (`v=spf1`), DKIM selector, DMARC (`_dmarc` subdomain). 3) Flag missing/weak records under A02:2025.

**10. Cookie Security Audit** — `BUILD`
- **What:** Check session cookies for missing security flags.
- **Why:** Trivial to add, a genuine session-security finding.
- **How:** Inspect `Set-Cookie` response headers.
- **Steps:** 1) Capture `Set-Cookie` headers during recon. 2) Parse for `Secure`/`HttpOnly`/`SameSite`. 3) Flag missing flags under A04:2025.

**11. Certificate Transparency Subdomain Discovery** — `ROADMAP ONLY`
- **What:** Discover related subdomains via public CT logs.
- **Why:** Expands attack-surface visibility beyond the single submitted URL.
- **How:** crt.sh free API.
- **Steps:** 1) Query `crt.sh/?q=%25.<domain>&output=json`. 2) Parse subdomains. 3) Present as a "Discovered Attack Surface" section (informational, not deep-scanned by default).
- **Why deferred:** genuinely useful but not differentiating enough to earn a build day inside a 7-day window.

**12. Domain/IP Reputation Lookup** — `ROADMAP ONLY`
- **What:** Check if the target's IP/domain has a known bad-reputation history.
- **Why:** Adds threat context most scanners omit.
- **How:** VirusTotal or AbuseIPDB free-tier API.
- **Steps:** 1) Resolve domain to IP. 2) Query reputation API. 3) Surface as contextual info in the report.
- **Why deferred:** same reasoning as #11 — real value, but low priority against Tier 1/4 in this window.

**13. API Endpoint Exposure Detection** — `ROADMAP ONLY`
- **What:** Passively identify exposed REST/GraphQL endpoints lacking auth.
- **Why:** Modern sites are API-driven; almost no free scanner covers this well.
- **How:** Pattern detection on JS bundles + path probing.
- **Steps:** 1) Scan linked JS files for API path patterns. 2) Probe discovered endpoints with unauthenticated GETs. 3) Flag endpoints returning data without auth under A01:2025.
- **Why deferred:** the highest-effort custom module in Tier 2 relative to its judge-visible payoff; revisit only if Phase 3 finishes early.

**14. Third-Party Script / Supply-Chain Audit** — `ROADMAP ONLY`
- **What:** Flag risky or unvetted external JS (ad tags, analytics, embedded widgets).
- **Why:** Directly maps to A03:2025; most scanners don't check this.
- **How:** Parse `<script src>` tags, check SRI attributes.
- **Steps:** 1) Extract all external script sources. 2) Flag missing `integrity` attributes. 3) Cross-check domains against a small curated risky-domain list.
- **Why deferred:** same bucket as #11–13; keep the spec ready, build only with schedule slack.

### TIER 3 — Threat Intelligence

**15. CISA KEV Cross-Check** — `BUILD`
- **What:** Flag which detected CVEs are actively exploited in the wild.
- **Why:** "Critical and actively exploited" is a different urgency tier than "critical but theoretical."
- **How:** CISA's free KEV JSON feed.
- **Steps:** 1) Cache `cisa.gov/.../known_exploited_vulnerabilities.json`. 2) Match detected CVE IDs against it. 3) Badge and auto-escalate matches.

**16. HaveIBeenPwned Correlation** — `ROADMAP ONLY` *(paid service — excluded regardless of timeline)*
- **What:** Check if accounts/emails tied to the domain appear in known breaches.
- **Why:** A data point most scanners don't surface.
- **How:** HIBP's domain-search API now requires a paid subscription (~$4.39/month); the free tier only covers a test/demo domain, not real targets.
- **Steps (for a future production phase):** 1) Extract any publicly listed contact emails during recon. 2) Query HIBP with a paid key. 3) Present as informational context, not a "vulnerability." **For the hackathon, skip the build entirely — just name it on the roadmap slide.**

**17. SBOM Export** — `BUILD`
- **What:** Structured, exportable list of every detected component and version.
- **Why:** A live compliance requirement in many regulatory contexts; near-free byproduct of fingerprinting.
- **How:** CycloneDX/SPDX JSON formatting.
- **Steps:** 1) Take existing tech-profile data. 2) Map into CycloneDX schema. 3) Add "Export SBOM" on the dashboard.

### TIER 4 — AI Layer (Google Gemini API — free tier, no credit card required)

**18. AI-Generated Remediation Snippets** — `BUILD`
- **What:** LLM generates the actual fix, not generic advice.
- **Why:** Highest "wow" factor per hour of build time.
- **How:** Gemini API (free tier — `gemini-2.5-flash-lite` recommended for the highest free request volume) call per finding, with finding + tech stack as context.
- **Steps:** 1) Construct a prompt with finding description + affected component. 2) Request a specific, pastable fix (config block, code line). 3) Display alongside the finding. 4) Cache by finding-type + tech combo — this also helps stay under the free tier's per-minute request cap.

**19. AI Executive Summary** — `BUILD`
- **What:** 2–3 sentence plain-English risk narrative.
- **Why:** Cheap to build, large perceived-polish gain.
- **How:** Gemini API (free tier) summarizing top findings.
- **Steps:** 1) Send top 3–5 findings + overall score to Gemini in a single call. 2) Prompt for a concise, non-technical summary. 3) Display at the top of the report.

**20. LLM False-Positive Triage** — `BUILD (stretch)` — *only attempt if Phases 1–4 finish ahead of schedule*
- **What:** Model sanity-checks evidence before surfacing a finding.
- **Why:** False-positive rate is what makes or breaks scanner trust.
- **How:** Gemini API (free tier) reviewing raw evidence per ambiguous finding type.
- **Steps:** 1) For probe-based findings (e.g., reflected input), send raw request/response evidence. 2) Prompt for a confidence rating. 3) Route low-confidence findings to a "Needs Manual Review" section.

**21. Chat With Your Report** — `BUILD (stretch)` — *only attempt if #20 is also done with time to spare*
- **What:** Natural-language Q&A over a completed scan.
- **Why:** Memorable AI-native demo feature.
- **How:** RAG using the scan's own findings as context, Gemini API (free tier).
- **Steps:** 1) On report load, structure that scan's findings as context (no vector DB needed at this scale). 2) Build a chat UI on the report page. 3) On each question, send relevant findings + the question to Gemini. 4) Stream the response.

*Free-tier note: Gemini 2.5 Flash-Lite allows roughly 15 requests/min and 1,000/day with no credit card. Batch or cache calls per scan (one summary call, one triage call per ambiguous finding — not one call per every single finding) to stay comfortably inside this during testing and live demos.*

### TIER 5 — Trust & Production Readiness — **`ROADMAP ONLY`**

**22. Domain Ownership Verification** — `ROADMAP ONLY`
- **What:** Cryptographically prove domain control before an active scan runs.
- **Why:** The real line between "toy" and a legally defensible product.
- **How:** DNS TXT challenge or file-upload challenge (like Google Search Console).
- **Steps:** 1) Generate a unique token per scan request. 2) Ask the user to add it as a DNS TXT record or upload it at `/.well-known/sentinelscan-verify.txt`. 3) Verify before allowing the scan. 4) Cache verified domains.
- **Why deferred:** valuable for production, adds a full verification flow with no judge-visible payoff in a live demo.

**23. Rate Limiting / Abuse Prevention** — `ROADMAP ONLY`
- **What:** Prevent your own platform from being used to mass-scan arbitrary targets.
- **Why:** A real production concern for any scanning-as-a-service tool.
- **How:** Per-user and per-target limits.
- **Steps:** 1) Add rate-limiting middleware (e.g., `slowapi`). 2) Add per-target cooldown windows. 3) Log and flag suspicious patterns.
- **Why deferred:** low build cost if Day 8 has slack — revisit then, but not scheduled.

**24. Encryption at Rest** — `ROADMAP ONLY`
- **What:** Encrypt stored findings/reports.
- **Why:** Scan data is sensitive; a real company would require this.
- **How:** PostgreSQL `pgcrypto` or disk-level encryption.
- **Steps:** 1) Encrypt sensitive columns or enable volume encryption. 2) Encrypt stored PDFs/SBOMs. 3) Decrypt only for authenticated requests.

**25. Observability** — `ROADMAP ONLY`
- **What:** Monitor platform health (queue depth, failure rate, latency).
- **Why:** Shows you're thinking about this as a service, not a script.
- **How:** Prometheus + Grafana.
- **Steps:** 1) Instrument FastAPI/Celery with Prometheus metrics. 2) Stand up a Grafana dashboard. 3) Add basic threshold alerting.

### TIER 6 — SOAR Integration — **`ROADMAP ONLY`** (conditional exception below)

**26. SOAR Alert Ingestion** — `ROADMAP ONLY, unless the existing capstone SOAR is already a working, reusable codebase`
- **What:** Feed high-severity findings into the SOAR engine as alerts.
- **Why:** Connects detection to response — the piece the current SOAR is missing.
- **How:** Webhook/API call on scan completion.
- **Steps:** 1) Filter findings ≥ High severity. 2) POST each as a structured alert to the SOAR ingestion endpoint. 3) Let existing correlation/dedup logic run as it does today.
- **Conditional build:** if the capstone SOAR can accept a webhook with days, not weeks, of integration work, features #26–27 only (alert ingestion + proposal engine) can be attempted as a Phase 4.5 add-on. Do not attempt #28–30 (approval/execution/verification) in this window regardless — that loop is the highest-risk block in the entire original plan.

**27. Remediation Proposal Engine** — `ROADMAP ONLY` (same condition as #26)
- **What:** SOAR proposes a specific action per alert instead of stopping at reporting.
- **Why:** This is what makes it a SOAR (Orchestration, Automation, **and Response**) rather than a detector.
- **How:** Rule-based finding-type → action mapping (LLM-assisted proposals can be added later).
- **Steps:** 1) Build a mapping (e.g., "outdated plugin" → "propose update command"; "missing header" → "propose config change"). 2) Generate a proposal object on alert ingestion. 3) Store it in a pending-approval queue.

**28. Human-Approval Gate** — `ROADMAP ONLY`
- **What:** A human approves a proposed remediation before it executes.
- **Why:** Real SOAR platforms (Splunk SOAR, XSOAR) use this pattern — full autonomy is considered risky even by mature security teams.
- **How:** Approval UI in the portal.
- **Steps:** 1) Build a "Pending Remediations" screen with approve/reject actions. 2) On approval, trigger execution (#29). 3) On rejection, log and close as manually handled.

**29. Automated Execution (Safe Actions Only)** — `ROADMAP ONLY`
- **What:** Execute approved low-risk actions automatically.
- **Why:** Completes the loop without the risk of autonomous production changes.
- **How:** Whitelisted action types only.
- **Steps:** 1) Start with ticket creation and Slack/email alerts. 2) For config-level fixes, generate the change but require a manual "apply" step rather than auto-applying to a live site. 3) Log every executed action for audit.

**30. Verification Loop** — `ROADMAP ONLY`
- **What:** Re-scan the specific finding after it's marked resolved to confirm the fix worked.
- **Why:** Closes the loop — "we fixed it" should be verifiable, not assumed.
- **How:** Targeted single-check re-run, not a full re-scan.
- **Steps:** 1) On case resolution, trigger the original check again. 2) Auto-close if it no longer triggers. 3) Reopen and re-alert if it does.

### TIER 7 — Platform & Scale — **`ROADMAP ONLY`** (name on the roadmap slide; do not attempt to build)

**31. Multi-Tenancy & RBAC** — `ROADMAP ONLY`
- **What:** Account isolation with team roles and audit logs.
- **Why:** Required for any real company to adopt this as a shared tool.
- **How:** `organization_id` + `role` fields, row-level access checks.

**32. Scheduled/Recurring Scans + Diffing** — `ROADMAP ONLY`
- **What:** Auto re-run scans on a schedule, flagging only what's new since the last run.
- **Why:** Turns a one-off check into continuous monitoring.
- **How:** Celery Beat + comparison logic.

**33. CI/CD Hook** — `ROADMAP ONLY`
- **What:** A GitHub Action that scans on every deploy.
- **Why:** Signals real product thinking, integrates into existing dev workflows.
- **How:** Wrap the scan API in a GitHub Action.

**34. Compliance-Mapped Reports** — `ROADMAP ONLY`
- **What:** Reformat findings against ISO 27001/SOC 2 control language.
- **Why:** This is literally what companies pay pentest firms for.
- **How:** A static OWASP-category → compliance-control mapping.

**35. Shareable Expiring Report Links** — `ROADMAP ONLY`
- **What:** A public, no-account-needed link to a report, with an expiry.
- **Why:** Agencies want to hand clients a link, not an attachment; expiry protects data over time.
- **How:** Signed, time-limited tokens (JWT with expiry claim).

**36. Public Trust Badge** — `ROADMAP ONLY`
- **What:** An embeddable badge showing a site's current SentinelScan score.
- **Why:** Doubles as organic marketing; gives site owners something to display.
- **How:** A dynamic SVG endpoint.

---

## 8. Full Tech Stack

- **Frontend:** React.js/Next.js, Tailwind CSS
- **Backend/API:** Python, FastAPI
- **Async Processing:** Celery + Redis *(Celery Beat for scheduled scans: roadmap only, Tier 7)*
- **Detection Engine:** Nuclei (Go binary, subprocess), Python (`requests`, `BeautifulSoup`, `dnspython`, `ssl`/`socket`)
- **Vulnerability Intelligence:** NVD REST API, CISA KEV feed — built. VirusTotal/AbuseIPDB, crt.sh — roadmap only, Tier 2. *(HaveIBeenPwned intentionally excluded — paid service; see Feature #16.)*
- **AI Layer:** Google Gemini API — free tier, no credit card (remediation generation + summaries built; FP triage + chat/RAG stretch). *Production upgrade path: Anthropic Claude API.*
- **Database:** PostgreSQL *(`pgcrypto` encryption at rest: roadmap only, Tier 5)*
- **Report Generation:** Jinja2, WeasyPrint/ReportLab, CycloneDX (SBOM) — all built
- **Auth/Security:** JWT — built. `slowapi` rate limiting — roadmap only, Tier 5.
- **Observability:** Prometheus + Grafana — roadmap only, Tier 5
- **Deployment:** Docker + docker-compose — built and required. Hosted demo on Render/Railway — stretch goal only.
- **SOAR:** Existing capstone SOAR engine — roadmap only, Tier 6, with the conditional exception noted at Feature #26.

---

## 9. Phased Build Plan (Sep 6 → Sep 15, real remaining runway)

**Phase 1 — Foundation (Sep 6–7):** Features 1–4. Get a URL submitted end-to-end returning raw Nuclei findings.

**Phase 2 — Core MVP Complete (Sep 7–9):** Features 5–8. Full Must-Have list working. **This is the non-negotiable floor** — if nothing else in this document gets built, this satisfies the literal problem statement.

**Phase 3 — Enhanced Detection + Intelligence (Sep 9–10):** Features 9, 10, 15, 17. Report now includes DNS/cookie checks, KEV badges, and SBOM export. *(Features 11–14 stay on the roadmap unless this phase finishes with a full day to spare.)*

**Phase 4 — AI Layer (Sep 10–12):** Features 18–19 (mandatory). Attempt 20–21 only if 18–19 are solid with time left in this window. *(If the capstone SOAR is confirmed reusable, insert Phase 4.5 here for Features 26–27 only — alert ingestion and proposal engine, nothing further.)*

**Phase 5 — Integration & Polish (Sep 12–13):** Full pipeline test from a clean Docker Compose clone, bug fixes, UI polish, report formatting pass. **Target: feature-complete and demoable by end of Sep 13.**

**Phase 6 — Buffer & Rehearsal (Sep 14–15):** Full run-through against a real test site, fix anything that breaks, record a fallback demo video, rehearse the live pitch and prepare answers for "what's not built yet and why" (this document's roadmap tags answer that directly).

**The one rule that matters most, unchanged from v1:** if behind at any checkpoint, cut top-down from Tier 7 first, then Tier 6, then Tier 5, then the Tier 2/3 stretch items, then Tier 4's stretch features (20–21) — never from Tier 1–2's mandatory items. A working core scanner with a polished report beats a half-broken stretch feature — judges forgive "we didn't get to X," not a live demo that errors out.