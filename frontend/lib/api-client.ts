import { Blocker, BlockerCreatePayload, ChatResult, Progress, Task, User, UserAccessPayload, UserCreatePayload } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("onboardai_token") : null;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed (${response.status}): ${errorText}`);
  }

  return (await response.json()) as T;
}

export async function signup(payload: {
  name: string;
  email: string;
  password: string;
  organization_name: string;
  organization_slug: string;
  role?: string;
  team?: string;
  level?: string;
  manager_name?: string;
  start_date?: string;
}): Promise<{ access_token: string; organization_id: number; user_id: number; role: string }> {
  return request("/auth/signup", { method: "POST", body: JSON.stringify(payload) });
}

export async function login(payload: {
  email: string;
  password: string;
  organization_slug: string;
}): Promise<{ access_token: string; organization_id: number; user_id: number; role: string }> {
  return request("/auth/login", { method: "POST", body: JSON.stringify(payload) });
}

export async function createUser(payload: UserCreatePayload): Promise<User> {
  return request<User>("/users", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function upsertUserAccess(userId: number, payload: UserAccessPayload): Promise<void> {
  await request(`/users/${userId}/access`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function generatePlan(userId: number): Promise<void> {
  await request(`/users/${userId}/plan/generate`, { method: "POST" });
}

export async function sendChat(userId: number, message: string): Promise<ChatResult> {
  return request<ChatResult>(`/users/${userId}/chat`, {
    method: "POST",
    body: JSON.stringify({ message }),
  });
}

export async function getProgress(userId: number): Promise<Progress> {
  return request<Progress>(`/users/${userId}/progress`);
}

export async function getPlan(userId: number): Promise<Task[]> {
  return request<Task[]>(`/users/${userId}/plan`);
}

export async function createBlocker(userId: number, payload: BlockerCreatePayload): Promise<Blocker> {
  return request<Blocker>(`/users/${userId}/blockers`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getOrgDashboard(orgId: number): Promise<{
  organization_id: number;
  active_new_hires: number;
  active_blockers: number;
  high_severity_blockers: number;
  completion_rate: number;
}> {
  return request(`/organizations/${orgId}/dashboard`);
}

export async function getOrgBlockers(orgId: number): Promise<Array<{ blocker_type: string; count: number }>> {
  return request(`/organizations/${orgId}/dashboard/blockers`);
}
