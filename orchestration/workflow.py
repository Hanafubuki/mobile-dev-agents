"""Checkpointed feature delivery around the repository's role skills."""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt


class Stage(TypedDict):
    role: str
    key: str
    side: str
    slice: str


class State(TypedDict, total=False):
    ticket: str
    workspace: str
    thread_id: str
    scope: str
    api_scope: str
    queue: list[Stage]
    history: list[dict]
    repairs: dict[str, int]
    sequence: int
    feedback: dict
    intake: dict
    pause: dict | None
    status: str


def stage(role, side="", slice_id="", key=None):
    return {
        "role": role, "side": side, "slice": slice_id,
        "key": key or ":".join((side, role, slice_id)),
    }


def initial_stages(scope, api_scope):
    stages = [stage("cto-intake"), stage("approve")]
    if scope in ("backend", "both"):
        stages.extend([stage("be-architect", "be"), stage("be-planner", "be")])
    if scope in ("frontend", "both"):
        stages.extend([stage("fe-designer", "fe"), stage("fe-planner", "fe")])
        if api_scope != "none":
            stages.append(stage("cross-stack-verifier", "fe"))
        stages.append(stage("cto-accept", "fe"))
    return stages


def after_plan(side, slices):
    stages = []
    for slice_id in slices:
        stages.extend([
            stage(f"{side}-developer", side, slice_id),
            stage(f"{side}-tester", side, slice_id),
        ])
    stages.append(stage(f"{side}-reviewer", side))
    if side == "be":
        stages.append(stage("cto-accept", side))
    return stages


def repair_stages(current, result):
    role = current["role"]
    side = current["side"]
    if role == "cross-stack-verifier":
        side = {"backend": "be", "frontend": "fe"}.get(result.get("owner"))
    if not side or role.endswith(("architect", "designer", "planner")):
        return []
    if role.endswith("-developer"):
        return [current]
    slice_id = current["slice"]
    stages = [stage(f"{side}-developer", side, slice_id)]
    if not role.endswith("-tester"):
        stages.append(stage(f"{side}-tester", side, slice_id))
    if role in ("cto-accept", "cross-stack-verifier"):
        stages.append(stage(f"{side}-reviewer", side))
    if role == "cross-stack-verifier" and side == "be":
        stages.append(stage("cto-accept", side))
    # Charge the original gate even if a repair stage itself reports failure.
    return [{**item, "key": current["key"]} for item in stages] + [current]


def build_workflow(runner, checkpointer, max_repairs=2):
    def initialize(state):
        return {
            "queue": initial_stages(state["scope"], state["api_scope"]),
            "history": [], "repairs": {}, "sequence": 0,
            "feedback": {}, "pause": None, "status": "running",
        }

    def execute(state):
        current, *remaining = state["queue"]
        role = current["role"]
        request = {
            **current,
            "request_id": f'{state["thread_id"]}:{state["sequence"]}',
            "ticket": state["ticket"],
            "scope": state["scope"],
            "api_scope": state["api_scope"],
            "feedback": state["feedback"],
            "intake": state.get("intake", {}),
        }
        result = runner(request, state["workspace"])
        status = result["status"]
        history = [*state["history"], {"stage": current, "result": result}]
        update = {"history": history, "feedback": result}
        if status == "pass":
            if role == "cto-intake":
                update["intake"] = result
            followups = after_plan(current["side"], result["slices"]) if role.endswith("-planner") else []
            return {
                **update, "queue": followups + remaining,
                "sequence": state["sequence"] + 1,
                "status": "running" if followups or remaining else "completed",
            }

        key = current["key"]
        count = state["repairs"].get(key, 0)
        repair = repair_stages(current, result) if status == "fail" else []
        if repair and count < max_repairs:
            return {
                **update, "repairs": {**state["repairs"], key: count + 1},
                "queue": repair + remaining, "sequence": state["sequence"] + 1,
            }
        return {
            **update, "status": "blocked",
            "pause": {"kind": "blocked", "stage": current, "detail": result, "repairs_used": count},
        }

    def wait_for_user(state):
        current = state["queue"][0]
        prompt = state["pause"] or {
            "kind": "approval",
            "instruction": "Approve the intake brief or cancel the run.",
            "brief": state["feedback"],
        }
        decision = interrupt(prompt)
        if decision == "cancel":
            return {"queue": [], "pause": None, "status": "cancelled"}
        if prompt["kind"] == "approval":
            return {"queue": state["queue"][1:], "pause": None, "status": "running"}
        # A manual retry permits the blocked stage to run again without resetting its budget.
        sequence = state["sequence"] + 1
        return {"pause": None, "status": "running", "sequence": sequence,
                "feedback": {**state["feedback"], "manual_retry": True}}

    def route(state):
        if not state["queue"]:
            return END
        if state["pause"] or state["queue"][0]["role"] == "approve":
            return "wait"
        return "execute"

    graph = StateGraph(State)
    graph.add_node("initialize", initialize)
    graph.add_node("execute", execute)
    graph.add_node("wait", wait_for_user)
    graph.add_edge(START, "initialize")
    for node in ("initialize", "execute", "wait"):
        graph.add_conditional_edges(node, route, {"wait": "wait", "execute": "execute", END: END})
    return graph.compile(checkpointer=checkpointer)
