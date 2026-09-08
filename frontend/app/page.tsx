"use client";

import { FormEvent, useEffect, useState } from "react";

type Scan = { scan_id: string; status: string; status_url: string };
type Status = { status: string; progress: number; error?: string | null };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [url, setUrl] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [scan, setScan] = useState<Scan | null>(null);
  const [status, setStatus] = useState<Status | null>(null);
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
        if (nextStatus.status === "done" || nextStatus.status === "failed") return;
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
      {status && <div className="progress"><div className="status-line"><strong>{status.status}</strong><span>{status.progress}%</span></div><div className="track"><div style={{ width: `${status.progress}%` }} /></div>{status.error && <p className="error">{status.error}</p>}{status.status === "done" && scan && <a href={`${API_URL}/api/scan/${scan.scan_id}/report`}>Open report</a>}</div>}
    </section>
    <footer>Built for authorized testing only · detection is read-only</footer>
  </main>;
}
