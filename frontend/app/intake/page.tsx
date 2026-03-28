"use client";

import { FormEvent, useState } from "react";

import { createUser, generatePlan, upsertUserAccess } from "@/lib/api-client";
import { AccessStatus } from "@/lib/types";

const DEFAULT_TOOLS = ["github", "vpn", "internal_wiki", "docker"];

export default function IntakePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData(event.currentTarget);

    try {
      const user = await createUser({
        name: String(formData.get("name") || ""),
        email: String(formData.get("email") || ""),
        role: String(formData.get("role") || ""),
        team: String(formData.get("team") || ""),
        level: String(formData.get("level") || ""),
        manager_name: String(formData.get("manager_name") || ""),
        start_date: String(formData.get("start_date") || ""),
      });

      for (const tool of DEFAULT_TOOLS) {
        const status = String(formData.get(`tool_${tool}`) || "not_requested") as AccessStatus;
        await upsertUserAccess(user.id, {
          tool_name: tool,
          status,
        });
      }

      await generatePlan(user.id);
      localStorage.setItem("onboardai_user_id", String(user.id));
      setResult(`Profile created and onboarding plan generated for user #${user.id}.`);
      event.currentTarget.reset();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create profile");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">New Hire Intake</h2>
      <form className="card grid gap-3 md:grid-cols-2" onSubmit={onSubmit}>
        <input className="input" name="name" placeholder="Full name" required />
        <input className="input" name="email" placeholder="Email" required />
        <input className="input" name="role" placeholder="Role (e.g. backend_engineer)" required />
        <input className="input" name="team" placeholder="Team (e.g. payments)" required />
        <input className="input" name="level" placeholder="Level (e.g. mid)" required />
        <input className="input" name="manager_name" placeholder="Manager name" required />
        <input className="input" type="date" name="start_date" required />
        <div />

        <label className="text-sm font-medium">GitHub access</label>
        <select className="input" name="tool_github" defaultValue="not_requested">
          <option value="not_requested">not_requested</option>
          <option value="pending">pending</option>
          <option value="granted">granted</option>
          <option value="denied">denied</option>
        </select>

        <label className="text-sm font-medium">VPN access</label>
        <select className="input" name="tool_vpn" defaultValue="not_requested">
          <option value="not_requested">not_requested</option>
          <option value="pending">pending</option>
          <option value="granted">granted</option>
          <option value="denied">denied</option>
        </select>

        <label className="text-sm font-medium">Internal wiki access</label>
        <select className="input" name="tool_internal_wiki" defaultValue="not_requested">
          <option value="not_requested">not_requested</option>
          <option value="pending">pending</option>
          <option value="granted">granted</option>
          <option value="denied">denied</option>
        </select>

        <label className="text-sm font-medium">Docker setup</label>
        <select className="input" name="tool_docker" defaultValue="not_requested">
          <option value="not_requested">not_requested</option>
          <option value="pending">pending</option>
          <option value="granted">granted</option>
          <option value="denied">denied</option>
        </select>

        <button className="button md:col-span-2" type="submit" disabled={loading}>
          {loading ? "Saving..." : "Save Profile + Generate Plan"}
        </button>
      </form>

      {result ? <p className="text-sm text-emerald-700">{result}</p> : null}
      {error ? <p className="text-sm text-rose-700">{error}</p> : null}
    </section>
  );
}
