# PostgreSQL Schema

## Conventions

PostgreSQL 16 is the target database. Primary identifiers use `uuid`. Timestamps use `timestamptz` in UTC. JSON evidence is stored as `jsonb`. The schema is designed for one user-owned scan at a time; organization isolation and RBAC are intentionally deferred.

## Tables

### `users`

| Column | Type | Rules |
|---|---|---|
| `id` | uuid | Primary key |
| `email` | varchar(320) | Required, unique |
| `password_hash` | varchar(255) | Required; password material is never returned |
| `role` | varchar(32) | Required, default `user`; reserved for future RBAC |
| `created_at` | timestamptz | Required, default now |

Indexes: unique index on `email`.

### `scans`

| Column | Type | Rules |
|---|---|---|
| `id` | uuid | Primary key |
| `user_id` | uuid | Foreign key to `users.id`, nullable only for explicitly anonymous demo mode |
| `target_url` | text | Required |
| `target_hostname` | varchar(253) | Required, normalized hostname |
| `status` | varchar(20) | Required; `queued`, `scanning`, `analyzing`, `completed`, or `failed` |
| `progress` | smallint | Required, 0-100; check constraint |
| `error_code` | varchar(64) | Nullable |
| `error_message` | text | Nullable, sanitized worker failure reason |
| `authorization_confirmed` | boolean | Required, must be true for a submitted scan |
| `authorization_confirmed_at` | timestamptz | Required |
| `submitting_ip` | inet | Required |
| `executive_summary` | text | Nullable until AI enrichment completes |
| `created_at` | timestamptz | Required, default now |
| `updated_at` | timestamptz | Required, default now |
| `completed_at` | timestamptz | Nullable |

Indexes: `(user_id, created_at desc)`, `(status, updated_at)`, unique `(id, user_id)` for ownership lookups. Check constraints enforce valid statuses, progress range, and authorization confirmation.

### `findings`

| Column | Type | Rules |
|---|---|---|
| `id` | uuid | Primary key |
| `scan_id` | uuid | Required foreign key to `scans.id` with cascade delete |
| `finding_key` | varchar(255) | Required stable template/check key |
| `title` | text | Required |
| `description` | text | Required |
| `source` | varchar(32) | Required: `nuclei`, `dns`, or `cookie` |
| `template_id` | varchar(255) | Nullable Nuclei template identifier |
| `evidence` | jsonb | Required raw or normalized evidence |
| `owasp_category` | varchar(3) | Required `A01` through `A10` |
| `cvss_version` | varchar(8) | Nullable, normally `3.1` or `3.0` |
| `cvss_score` | numeric(3,1) | Nullable, 0.0-10.0 check constraint |
| `severity` | varchar(10) | Required: Critical, High, Medium, or Low |
| `cve_id` | varchar(32) | Nullable |
| `kev_known_exploited` | boolean | Required, default false |
| `remediation` | text | Nullable AI-generated or deterministic guidance |
| `created_at` | timestamptz | Required, default now |

Indexes: `(scan_id, severity)`, `(scan_id, owasp_category)`, `cve_id`, and unique `(scan_id, finding_key, evidence_hash)` where `evidence_hash` is a generated or application-maintained digest used for deduplication.

### `tech_profile_entries`

| Column | Type | Rules |
|---|---|---|
| `id` | uuid | Primary key |
| `scan_id` | uuid | Required foreign key to `scans.id` with cascade delete |
| `name` | varchar(255) | Required normalized component name |
| `version` | varchar(100) | Nullable |
| `category` | varchar(100) | Nullable: CMS, framework, server, library, or other |
| `cpe` | varchar(512) | Nullable normalized CPE used for NVD matching |
| `source` | varchar(32) | Required, normally `nuclei-tech` |
| `raw_evidence` | jsonb | Required |
| `created_at` | timestamptz | Required, default now |

Indexes: `(scan_id, name)`, `(name, version)`, and `cpe`.

### `nvd_cache`

| Column | Type | Rules |
|---|---|---|
| `cache_key` | varchar(768) | Primary key; normalized CPE/version query |
| `response_body` | jsonb | Required |
| `fetched_at` | timestamptz | Required |
| `expires_at` | timestamptz | Required |
| `last_error` | text | Nullable |

Index: `expires_at` for cleanup and stale-cache selection.

### `kev_cache`

| Column | Type | Rules |
|---|---|---|
| `feed_key` | varchar(64) | Primary key, normally `cisa-kev` |
| `response_body` | jsonb | Required source snapshot |
| `cve_ids` | jsonb | Required normalized CVE set/list |
| `fetched_at` | timestamptz | Required |
| `expires_at` | timestamptz | Required |
| `last_error` | text | Nullable |

Index: `expires_at`.

### `ai_remediation_cache`

| Column | Type | Rules |
|---|---|---|
| `cache_key` | varchar(512) | Primary key; finding type plus normalized technology context |
| `model` | varchar(100) | Required, `gemini-2.5-flash-lite` for this build |
| `response_text` | text | Required |
| `created_at` | timestamptz | Required |
| `expires_at` | timestamptz | Required |

Index: `expires_at`.

### `report_artifacts`

| Column | Type | Rules |
|---|---|---|
| `id` | uuid | Primary key |
| `scan_id` | uuid | Required unique foreign key to `scans.id` |
| `pdf_storage_key` | text | Nullable artifact path/key |
| `sbom_storage_key` | text | Nullable artifact path/key |
| `created_at` | timestamptz | Required |

Index: unique `scan_id`.

## Relationships

One user owns many scans. One scan owns many findings and technology profile entries. A finding may reference a CVE but does not own a separate CVE row because NVD data is cached by query and the finding stores the matched identifier and score. Cache tables are shared across scans. One scan has at most one report-artifact record.

## Integrity and retention

Foreign keys cascade scan-owned findings, technology entries, and artifacts when a scan is deleted. Application code validates OWASP categories, severity values, CVSS ranges, and scan statuses before persistence. The schema does not claim encryption at rest; that is explicitly roadmap work.
