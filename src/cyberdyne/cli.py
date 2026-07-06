"""cyberdyne guard <policy.json> <events.jsonl> — enforce the off switch on an automated run.

Exit 1 if the run is HALTed."""
import argparse
import json
import sys

from .governor import evaluate, halted


def _load_jsonl(path):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(prog="cyberdyne")
    parser.add_argument("command", choices=["guard"])
    parser.add_argument("policy", help="safety policy JSON")
    parser.add_argument("events", help="agent events, one JSON object per line")
    args = parser.parse_args(argv)

    with open(args.policy) as fh:
        policy = json.load(fh)
    decision = evaluate(policy, _load_jsonl(args.events))

    tag = "HALT" if halted(decision) else " OK "
    print(f"[{tag}] {decision['reason']} @ step {decision['at_step']} — {decision['message']}",
          file=sys.stderr)
    return 1 if halted(decision) else 0


if __name__ == "__main__":
    raise SystemExit(main())
