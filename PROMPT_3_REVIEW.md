ROLE: You are a Principal Security Engineer and QA Lead auditing the SentinelScan
codebase produced in the previous step, for a hackathon demo on Sep 15 with zero
opportunity for the human owner to debug code personally. Assume nobody will read your
review except you acting on it — fix what you find rather than just listing it, then
report what you fixed.

REVIEW PASS 1 — Correctness & Robustness:
- Trace the full pipeline end to end (URL submit → Nuclei → parse → NVD/CVE → OWASP
  mapping → CVSS → AI enrichment → report) and identify any point where a failure (bad
  URL, Nuclei timeout, empty findings, NVD API down, Gemini rate-limited) would crash the
  worker, hang the job, or silently produce a broken/empty report instead of a clear
  "failed" state.
- Check that OWASP Top 10:2025 category mapping actually covers every Nuclei tag being
  used and every custom module's output — no finding should end up uncategorized.
- Check CVSS bucketing thresholds and sort order are applied correctly in both the
  dashboard and PDF.

REVIEW PASS 2 — Security of the Scanner Itself (this tool scans other people's sites —
it must not become an attack vector):
- Confirm the URL intake validates scheme and blocks localhost/private/link-local/
  metadata-endpoint IPs (SSRF guard), including after any redirect the target site
  issues.
- Confirm the Nuclei subprocess call cannot be manipulated via a crafted URL into
  command/argument injection (list-based args, no shell=True, no string interpolation).
- Confirm API keys and DB credentials are not logged, not in error messages returned to
  the frontend, and not committed anywhere in the repo.
- Confirm the authorization checkbox is actually enforced (no submitting a scan without
  it, and the acceptance is timestamped/logged) even though full domain-ownership
  verification is out of scope for this build.

REVIEW PASS 3 — Testing:
- Write and run a pytest suite covering: each API endpoint (happy path + validation
  failures), the OWASP mapping table (spot-check tag → category), CVSS bucketing edge
  values (exactly 9.0, 7.0, 4.0, 0.1), and the Nuclei-output parser against at least one
  realistic sample JSON fixture.
- Mock all external calls (NVD, CISA KEV, Gemini, Nuclei subprocess) in tests so the
  suite runs offline and deterministically.
- Confirm `docker-compose up` succeeds from a clean clone and the full user flow
  (submit → poll → view report → download PDF → export SBOM) works against a real test
  target.

REVIEW PASS 4 — Demo Readiness:
- Run the actual pipeline against a real, safe test target and confirm the report reads
  as polished and judge-ready, not like debug output.
- List every feature from the original scope that is NOT fully working right now, in
  plain language, so the human owner knows exactly what to avoid clicking on during the
  live demo.
- Produce a one-paragraph "known limitations & roadmap" writeup (mentioning the deferred
  SOAR/trust/scale tiers) suitable for a judge Q&A slide.

DELIVERABLE: a prioritized fix list of everything found (with what you changed), the
test suite, and the final "known limitations" writeup. Do not mark anything as done that
you have not actually verified by running it.