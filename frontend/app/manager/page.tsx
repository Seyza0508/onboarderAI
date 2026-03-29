"use client";

import { useState } from "react";

import { getOrgBlockers, getOrgDashboard } from "@/lib/api-client";

export default function ManagerPage() {
  const [orgId, setOrgId] = useState("1");
  const [dashboard, setDashboard] = useState<{
    organization_id: number;
    active_new_hires: number;
    active_blockers: number;
    high_severity_blockers: number;
    completion_rate: number;
  } | null>(null);
  const [blockers, setBlockers] = useState<Array<{ blocker_type: string; count: number }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const orgNum = Number(orgId);
      const [dash, block] = await Promise.all([getOrgDashboard(orgNum), getOrgBlockers(orgNum)]);
      setDashboard(dash);
      setBlockers(block);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load manager dashboard");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Manager Dashboard</h2>
      <div className="card flex items-end gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium">Organization ID</label>
          <input className="input w-40" value={orgId} onChange={(e) => setOrgId(e.target.value)} />
        </div>
        <button className="button" onClick={load} disabled={loading}>
          {loading ? "Loading..." : "Load Org Metrics"}
        </button>
      </div>
      {error ? <p className="text-sm text-rose-700">{error}</p> : null}
      {dashboard ? (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <article className="card">
              <p className="text-xs text-slate-500">Active new hires</p>
              <p className="text-2xl font-semibold">{dashboard.active_new_hires}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">Active blockers</p>
              <p className="text-2xl font-semibold">{dashboard.active_blockers}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">High severity blockers</p>
              <p className="text-2xl font-semibold">{dashboard.high_severity_blockers}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">Completion rate</p>
              <p className="text-2xl font-semibold">{(dashboard.completion_rate * 100).toFixed(0)}%</p>
            </article>
          </div>
          <article className="card">
            <h3 className="mb-2 font-semibold">Blocker categories</h3>
            <ul className="space-y-1 text-sm">
              {blockers.map((item) => (
                <li key={item.blocker_type}>
                  {item.blocker_type}: {item.count}
                </li>
              ))}
            </ul>
          </article>
        </>
      ) : null}
    </section>
  );
}
