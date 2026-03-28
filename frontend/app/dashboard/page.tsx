"use client";

import { useEffect, useState } from "react";

import { getPlan, getProgress } from "@/lib/api-client";
import { Progress, Task } from "@/lib/types";

export default function DashboardPage() {
  const [userId, setUserId] = useState("");
  const [progress, setProgress] = useState<Progress | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem("onboardai_user_id");
    if (stored) setUserId(stored);
  }, []);

  async function loadDashboard() {
    if (!userId) {
      setError("Enter a valid user ID.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const [progressData, tasksData] = await Promise.all([getProgress(Number(userId)), getPlan(Number(userId))]);
      setProgress(progressData);
      setTasks(tasksData);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Progress Dashboard</h2>

      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium">User ID</label>
          <input className="input w-40" value={userId} onChange={(e) => setUserId(e.target.value)} />
        </div>
        <button className="button" onClick={loadDashboard} disabled={loading}>
          {loading ? "Loading..." : "Load Progress"}
        </button>
      </div>

      {error ? <p className="text-sm text-rose-700">{error}</p> : null}

      {progress ? (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <article className="card">
              <p className="text-xs text-slate-500">Total tasks</p>
              <p className="text-2xl font-semibold">{progress.total_tasks}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">Completed</p>
              <p className="text-2xl font-semibold">{progress.completed_tasks}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">Blocked</p>
              <p className="text-2xl font-semibold">{progress.blocked_tasks}</p>
            </article>
            <article className="card">
              <p className="text-xs text-slate-500">Pending</p>
              <p className="text-2xl font-semibold">{progress.pending_tasks}</p>
            </article>
          </div>

          <article className="card space-y-2">
            <h3 className="font-semibold">Current blocker</h3>
            {progress.current_blocker ? (
              <>
                <p className="text-sm">
                  <span className="font-medium">Type:</span> {progress.current_blocker.blocker_type}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Description:</span> {progress.current_blocker.description}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Recommended next action:</span>{" "}
                  {progress.recommended_next_action || "No recommendation yet"}
                </p>
                <p className="text-sm">
                  <span className="font-medium">Alternate tasks:</span>{" "}
                  {progress.recommended_alternate_tasks.join(", ") || "None"}
                </p>
              </>
            ) : (
              <p className="text-sm text-slate-600">No active blocker.</p>
            )}
          </article>

          <article className="card space-y-2">
            <h3 className="font-semibold">Plan tasks</h3>
            <ul className="space-y-2">
              {tasks.map((task) => (
                <li key={task.id} className="rounded border border-slate-200 p-3 text-sm">
                  <p className="font-medium">{task.task_name}</p>
                  <p className="text-slate-600">
                    {task.category} | {task.priority} | {task.status}
                  </p>
                  {task.doc_reference ? <p className="text-xs text-slate-500">Doc: {task.doc_reference}</p> : null}
                </li>
              ))}
            </ul>
          </article>
        </>
      ) : null}
    </section>
  );
}
