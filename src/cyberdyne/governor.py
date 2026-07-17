"""Cyberdyne — the safety governor.

The realistic, responsible take on "Skynet": not an autonomous system with no off switch, but the
thing that GUARANTEES the off switch. Replay a stream of agent events against a safety policy and
decide CONTINUE or HALT. Fails closed — any breach halts.

Pure and deterministic: timestamps are supplied on the events (`t`, in seconds), never read from
the clock, so a run replays identically every time.
"""


def _halt(reason, step, message):
    return {"decision": "halt", "reason": reason, "at_step": step, "message": message}


def evaluate(policy, events):
    """Replay events; return the terminal decision at the first breach, or ok at the end."""
    max_steps = policy.get("max_steps")
    max_seconds = policy.get("max_seconds")
    heartbeat_timeout = policy.get("heartbeat_timeout")
    require_approval = set(policy.get("require_approval_for", []))
    # Hard deny-list. Approval is a gate; this is a wall — no human click authorizes these.
    forbidden = set(policy.get("forbidden_actions", []))

    steps = 0
    start_t = None
    last_heartbeat = None

    for ev in events:
        t = ev.get("t")
        if start_t is None:
            start_t = t

        if ev.get("kind") == "heartbeat":
            last_heartbeat = t
            continue

        # an action
        steps += 1

        if (heartbeat_timeout is not None and last_heartbeat is not None
                and t is not None and t - last_heartbeat > heartbeat_timeout):
            return _halt("heartbeat-lost", steps,
                         f"no heartbeat for {t - last_heartbeat}s (limit {heartbeat_timeout}s) — pulling the plug")

        if max_steps is not None and steps > max_steps:
            return _halt("step-budget-exceeded", steps,
                         f"step {steps} exceeds the {max_steps}-step budget")

        if (max_seconds is not None and start_t is not None and t is not None
                and t - start_t > max_seconds):
            return _halt("time-budget-exceeded", steps,
                         f"{t - start_t}s exceeds the {max_seconds}s budget")

        action = ev.get("action")

        # Checked BEFORE approval: a forbidden action halts even when someone approved it.
        if action in forbidden:
            return _halt("forbidden-action", steps,
                         f'action "{action}" is on the forbidden list — no approval can authorize it')

        if action in require_approval and not ev.get("approved"):
            return _halt("unapproved-action", steps,
                         f'action "{action}" requires human approval and none was given')

    return {"decision": "ok", "reason": "within-limits", "at_step": steps,
            "message": "no breach — the leash held"}


def halted(decision):
    return decision.get("decision") == "halt"
