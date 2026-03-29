from __future__ import annotations

from collections.abc import Callable

from app.agent.nodes import (
    classify_blocker,
    detect_blocker,
    draft_escalation,
    generate_plan,
    handoff_to_human,
    load_context,
    recommend_next_action,
    retrieve_docs,
    suggest_alternate_tasks,
    synthesize_answer,
    update_progress,
)
from app.agent.state import WorkflowState

NodeFn = Callable[[WorkflowState], dict]


FLOW_DEFINITIONS: dict[str, list[tuple[str, NodeFn]]] = {
    "onboarding-run": [
        ("load_context", load_context.run),
        ("generate_plan", generate_plan.run),
        ("update_progress", update_progress.run),
    ],
    "question-run": [
        ("load_context", load_context.run),
        ("retrieve_docs", retrieve_docs.run),
        ("synthesize_answer", synthesize_answer.run),
        ("update_progress", update_progress.run),
    ],
    "blocker-run": [
        ("load_context", load_context.run),
        ("detect_blocker", detect_blocker.run),
        ("classify_blocker", classify_blocker.run),
        ("recommend_next_action", recommend_next_action.run),
        ("suggest_alternate_tasks", suggest_alternate_tasks.run),
        ("draft_escalation", draft_escalation.run),
        ("handoff_to_human", handoff_to_human.run),
        ("update_progress", update_progress.run),
    ],
}


def execute_flow(state: WorkflowState) -> dict[str, dict]:
    flow = FLOW_DEFINITIONS.get(state.workflow_type, [])
    outputs: dict[str, dict] = {}
    for node_name, node_fn in flow:
        result = node_fn(state)
        outputs[node_name] = result
        state.outputs[node_name] = result
    return outputs
