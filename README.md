```
   .---------.
   | [ OFF ] |   C Y B E R D Y N E · the safety governor
   |  HALT   |   the off switch Skynet never had.
   '---------'
```

# cyberdyne

> The safety governor — **the off switch Skynet never had.** Heartbeat dead-man's-switch, step and
> time budgets, and human-approval gates for automated runs. Fails closed.
>
> Technika11y **Labs**

[![ci](https://github.com/technika11y/cyberdyne/actions/workflows/ci.yml/badge.svg)](https://github.com/technika11y/cyberdyne/actions/workflows/ci.yml)
![status](https://img.shields.io/badge/status-pre--alpha-orange)
![license](https://img.shields.io/badge/license-Apache--2.0-blue)

> Affectionate homage to the fictional Cyberdyne Systems of *The Terminator*. **Unrelated** to the
> real Cyberdyne Inc. (which, fittingly, builds assistive robotics). Marks belong to their owners.

---

## The joke, and the point

Fictional Cyberdyne built an autonomous system with no off switch, and we all know how that went.
This one builds the off switch — the boring, essential supervisor that sits *around* an automated
agent and pulls the plug the moment it exceeds what a human authorized. The realistic version of
"Skynet" isn't the AI. It's the governor that guarantees a human is still holding the leash.

## Quick start

```bash
git clone https://github.com/technika11y/cyberdyne && cd cyberdyne
PYTHONPATH=src python3 -m cyberdyne.cli guard examples/policy.json examples/events.jsonl
```

## Status

| Capability | State |
|---|---|
| Step budget (halt when an agent takes more actions than allowed) | ✅ works, tested |
| Time budget (halt past a wall-clock allowance) | ✅ works, tested |
| Heartbeat dead-man's-switch (halt when the heartbeat goes stale) | ✅ works, tested |
| Human-approval gate (halt on a flagged action taken without approval) | ✅ works, tested |
| Hard deny-list (`forbidden_actions` halt even *with* approval — a wall, not a gate) | ✅ works, tested |
| **Fails closed** — any breach halts; deterministic replay | ✅ works, tested |
| Live process supervision / signal delivery / sidecar mode | ❌ not built — this decides; wiring the actual kill is yours |

Honesty note: this is a **policy decision engine**, not a process killer. It tells you *when* to
halt (exit 1); connecting that to a real SIGKILL / API stop is deliberately left to the integrator.

## Usage

```bash
PYTHONPATH=src python -m cyberdyne.cli guard examples/policy.json examples/events.jsonl
# [ OK ] within-limits @ step 3 — no breach — the leash held

# an agent that runs away:
#   [HALT] step-budget-exceeded @ step 6 — step 6 exceeds the 5-step budget
```

Events are one JSON object per line: `{"t": <seconds>, "kind": "action"|"heartbeat", "action": "...", "approved": true?}`.

## License

[Apache-2.0](LICENSE). Report issues privately — see [`SECURITY.md`](SECURITY.md).

---

**Part of the [Technika11y](https://github.com/technika11y) suite** · [technika11y.github.io](https://technika11y.github.io/) · security, compliance, and accessibility as one discipline.
