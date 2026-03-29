"use client";

import { FormEvent, useState } from "react";

import { login, signup } from "@/lib/api-client";

export default function AuthPage() {
  const [mode, setMode] = useState<"signup" | "login">("signup");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    const form = new FormData(event.currentTarget);

    try {
      const response =
        mode === "signup"
          ? await signup({
              name: String(form.get("name") || ""),
              email: String(form.get("email") || ""),
              password: String(form.get("password") || ""),
              organization_name: String(form.get("organization_name") || ""),
              organization_slug: String(form.get("organization_slug") || ""),
              role: String(form.get("role") || "admin"),
              team: String(form.get("team") || "platform"),
              level: String(form.get("level") || "senior"),
              manager_name: String(form.get("manager_name") || "CTO"),
              start_date: String(form.get("start_date") || new Date().toISOString().slice(0, 10)),
            })
          : await login({
              email: String(form.get("email") || ""),
              password: String(form.get("password") || ""),
              organization_slug: String(form.get("organization_slug") || ""),
            });

      localStorage.setItem("onboardai_token", response.access_token);
      localStorage.setItem("onboardai_org_id", String(response.organization_id));
      localStorage.setItem("onboardai_user_id", String(response.user_id));
      setResult(`Authenticated as user ${response.user_id} in org ${response.organization_id}.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Authentication failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">Authentication</h2>
      <div className="flex gap-2">
        <button className="button" onClick={() => setMode("signup")} type="button">
          Signup
        </button>
        <button className="button" onClick={() => setMode("login")} type="button">
          Login
        </button>
      </div>
      <form className="card grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        {mode === "signup" ? <input className="input" name="name" placeholder="Full name" required /> : null}
        <input className="input" name="email" placeholder="Email" required />
        <input className="input" name="password" placeholder="Password" type="password" required />
        <input className="input" name="organization_slug" placeholder="Organization slug" required />
        {mode === "signup" ? (
          <>
            <input className="input" name="organization_name" placeholder="Organization name" required />
            <input className="input" name="role" placeholder="Role (admin/manager/new_hire)" defaultValue="admin" />
            <input className="input" name="team" placeholder="Team" defaultValue="platform" />
            <input className="input" name="level" placeholder="Level" defaultValue="senior" />
            <input className="input" name="manager_name" placeholder="Manager" defaultValue="CTO" />
            <input className="input" type="date" name="start_date" />
          </>
        ) : null}
        <button className="button md:col-span-2" disabled={loading}>
          {loading ? "Submitting..." : mode === "signup" ? "Create account" : "Login"}
        </button>
      </form>
      {result ? <p className="text-sm text-emerald-700">{result}</p> : null}
      {error ? <p className="text-sm text-rose-700">{error}</p> : null}
    </section>
  );
}
