export type AccessStatus = "not_requested" | "pending" | "granted" | "denied";

export type UserCreatePayload = {
  name: string;
  email: string;
  role: string;
  team: string;
  level: string;
  manager_name: string;
  start_date: string;
};

export type UserAccessPayload = {
  tool_name: string;
  status: AccessStatus;
  notes?: string;
};

export type User = {
  id: number;
  name: string;
  email: string;
  role: string;
  team: string;
  level: string;
  manager_name: string;
  start_date: string;
};

export type ChatResult = {
  user_id: number;
  response: string;
  sources: string[];
};

export type Task = {
  id: number;
  user_id: number;
  task_name: string;
  category: string;
  status: "not_started" | "in_progress" | "blocked" | "complete";
  priority: string;
  depends_on_task_id: number | null;
  doc_reference: string | null;
};

export type Blocker = {
  id: number;
  user_id?: number;
  task_id?: number | null;
  blocker_type: string;
  description: string;
  severity: string;
  status: string;
  recommended_action: string | null;
  classification_reason?: string | null;
  alternate_tasks?: string[];
};

export type Progress = {
  user_id: number;
  total_tasks: number;
  completed_tasks: number;
  blocked_tasks: number;
  pending_tasks: number;
  current_blocker: Blocker | null;
  recommended_next_action: string | null;
  recommended_alternate_tasks: string[];
};

export type BlockerCreatePayload = {
  task_id?: number;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  blocker_type?: "access" | "environment" | "documentation" | "dependency" | "ownership";
};
