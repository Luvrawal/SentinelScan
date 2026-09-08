"use client";

import { FormEvent, useEffect, useState } from "react";

type Scan = { scan_id: string; status: string; status_url: string };
type Status = { status: string; progress: number; error?: string | null };
type Technology = { name: string; version: string | null; category: string | null; source: string };
type Finding = { id: string; title: string; description: string; severity: string; cvss_score: number | null; cve_id: string | null; owasp_category: string; remediation: string | null; kev_known_exploited: boolean };
type Report = { scan_id: string; target_url: string; executive_summary: string; technologies: Technology[]; findings: Finding[]; pdf_url: string };

const API_URL = "";

export default function Home() {
  const [url, setUrl] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [scan, setScan] = useState<Scan | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!scan) return;
    let active = true;
    const poll = async () => {
      try {
        const response = await fetch(`${API_URL}${scan.status_url}`);
        if (!response.ok) throw new Error("Could not read scan status.");
        const nextStatus: Status = await response.json();
        if (active) setStatus(nextStatus);
        if (nextStatus.status === "done") {
          const reportResponse = await fetch(`${API_URL}/api/scan/${scan.scan_id}/report`);
          if (!reportResponse.ok) throw new Error("The completed report could not be loaded.");
          if (active) setReport(await reportResponse.json());
          return;
        }
        if (nextStatus.status === "failed") return;
        window.setTimeout(poll, 2000);
      } catch (cause) {
        if (active) setError(cause instanceof Error ? cause.message : "Could not read scan status.");
      }
    };
    poll();
    return () => {
      active = false;
    };
  }, [scan]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      const parsed = new URL(url);
      if (!/^https?:$/.test(parsed.protocol)) throw new Error("Use an HTTP(S) URL.");
      if (!authorized) throw new Error("Confirm authorization before scanning.");
      const response = await fetch(`${API_URL}/api/scan`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_url: url, authorization_confirmed: true }) });
      const body = await response.json();
      if (!response.ok) throw new Error(body.detail ?? "Could not start scan.");
      setScan(body);
      setReport(null);
      setStatus({ status: body.status, progress: 0 });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not start scan.");
    }
  }

  return <main className="shell">
    <section className="hero"><p className="eyebrow">SENTINELSCAN / SECURITY WORKBENCH</p><h1>See what your public surface is exposing.</h1><p className="lede">A read-only scan combining Nuclei detection, OWASP Top 10:2025 mapping, CVE intelligence, and plain-language remediation.</p></section>
    <section className="panel">
      <form onSubmit={submit}><label htmlFor="url">Target URL</label><div className="url-row"><input id="url" type="url" required placeholder="https://example.com" value={url} onChange={(event) => setUrl(event.target.value)} /><button type="submit">Start scan</button></div><label className="check"><input type="checkbox" checked={authorized} onChange={(event) => setAuthorized(event.target.checked)} /> I confirm I am authorized to scan this target.</label></form>
      {error && <p className="error">{error}</p>}
      {status && <div className="progress"><div className="status-line"><strong>{status.status}</strong><span>{status.progress}%</span></div><div className="track"><div style={{ width: `${status.progress}%` }} /></div>{status.error && <p className="error">{status.error}</p>}</div>}
    </section>
    {report && <section className="report-shell">
      <div className="report-heading"><div><p className="eyebrow">SCAN REPORT</p><h2>Security findings for {report.target_url}</h2></div><a className="download" href={`${API_URL}${report.pdf_url}`} download>Download PDF</a></div>
      <div className="summary-card"><p className="eyebrow">EXECUTIVE SUMMARY</p><p>{report.executive_summary}</p></div>
      <h2>Technology profile</h2><div className="tech-grid">{report.technologies.length ? report.technologies.map((tech) => <div className="tech-card" key={`${tech.name}-${tech.version}`}><strong>{tech.name}</strong><span>{tech.version ?? "Version unknown"}</span><small>{tech.category ?? "Technology"}</small></div>) : <p className="muted">No technologies detected.</p>}</div>
      <h2>Findings</h2><div className="finding-table"><div className="finding-row finding-header"><span>Finding</span><span>Severity</span><span>CVSS</span><span>OWASP</span></div>{report.findings.length ? report.findings.map((finding) => <article className="finding-row" key={finding.id}><strong>{finding.title}</strong><span className={`severity ${finding.severity.toLowerCase()}`}>{finding.severity}</span><span>{finding.cvss_score ?? "Not scored"}</span><span>{finding.owasp_category}</span></article>) : <p className="muted">No findings detected.</p>}</div>
      <h2>Finding details and remediation</h2><div className="detail-grid">{report.findings.map((finding) => <article className="detail-card" key={`detail-${finding.id}`}><div className="detail-meta"><span className={`severity ${finding.severity.toLowerCase()}`}>{finding.severity}</span><span>{finding.owasp_category}</span>{finding.cve_id && <span>{finding.cve_id}</span>}</div><h3>{finding.title}</h3><p>{finding.description}</p><h4>Remediation</h4><p>{finding.remediation ?? "Remediation guidance is pending. Review the evidence and apply the vendor-recommended fix."}</p></article>)}</div>
    </section>}
    <footer>Built for authorized testing only · detection is read-only</footer>
  </main>;
}
