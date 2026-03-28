import { ChatResult, Progress, Task, User, UserAccessPayload, UserCreatePayload } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API request failed (${response.status}): ${errorText}`);
  }

  return (await response.json()) as T;
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
