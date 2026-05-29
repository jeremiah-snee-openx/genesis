#!/usr/bin/env python3
"""Profile real token consumption from a Copilot CLI process log.

Copilot CLI writes per-turn usage JSON blocks of the form::

    {
      "prompt_tokens": 150643,
      "completion_tokens": 259,
      "total_tokens": 150902,
      "prompt_tokens_details": {
        "cached_tokens": 0,
        "cache_creation_tokens": 150637
      }
    }

This script extracts every such block in a log, aggregates by turn,
and computes a hypothetical dollar cost at supplied per-Mtok rates.

Usage::

    python3 profile-tokens.py <log_path> [--rates anthropic-sonnet|anthropic-opus|anthropic-haiku]

Defaults to anthropic-sonnet rates (typical Copilot CLI backing model).
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

# $ / Mtok, Anthropic family (see genesis runtime-affordances/per-harness/claude-code.md S9)
RATES = {
    "anthropic-opus": {"input": 15.0, "output": 75.0, "cache_write": 18.75, "cache_read": 1.50},
    "anthropic-sonnet": {"input": 3.0, "output": 15.0, "cache_write": 3.75, "cache_read": 0.30},
    "anthropic-haiku": {"input": 1.0, "output": 5.0, "cache_write": 1.25, "cache_read": 0.10},
}

USAGE_RE = re.compile(
    r'\{\s*"prompt_tokens":\s*(\d+),\s*"completion_tokens":\s*(\d+),'
    r'\s*"total_tokens":\s*(\d+),'
    r'\s*"prompt_tokens_details":\s*\{\s*"cached_tokens":\s*(\d+),'
    r'\s*"cache_creation_tokens":\s*(\d+)\s*\}\s*\}',
    re.MULTILINE,
)


def parse_log(path: Path) -> list[dict]:
    text = path.read_text(errors="replace")
    turns = []
    for m in USAGE_RE.finditer(text):
        prompt_tokens = int(m.group(1))
        completion = int(m.group(2))
        cached = int(m.group(4))
        cache_write = int(m.group(5))
        new_input = max(0, prompt_tokens - cached - cache_write)
        turns.append(
            {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion,
                "cached_tokens": cached,
                "cache_creation_tokens": cache_write,
                "new_input_tokens": new_input,
            }
        )
    return turns


def cost(turn: dict, rates: dict) -> float:
    return (
        turn["new_input_tokens"] * rates["input"] / 1_000_000
        + turn["cache_creation_tokens"] * rates["cache_write"] / 1_000_000
        + turn["cached_tokens"] * rates["cache_read"] / 1_000_000
        + turn["completion_tokens"] * rates["output"] / 1_000_000
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("log", type=Path)
    ap.add_argument("--rates", default="anthropic-sonnet", choices=list(RATES))
    ap.add_argument("--per-turn", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.log.exists():
        print(f"log not found: {args.log}", file=sys.stderr)
        return 1

    turns = parse_log(args.log)
    if not turns:
        print(f"no usage blocks found in {args.log}", file=sys.stderr)
        return 1

    rates = RATES[args.rates]
    totals = {
        "turns": len(turns),
        "prompt_tokens": sum(t["prompt_tokens"] for t in turns),
        "completion_tokens": sum(t["completion_tokens"] for t in turns),
        "cached_tokens": sum(t["cached_tokens"] for t in turns),
        "cache_creation_tokens": sum(t["cache_creation_tokens"] for t in turns),
        "new_input_tokens": sum(t["new_input_tokens"] for t in turns),
    }
    totals["total_cost_usd"] = sum(cost(t, rates) for t in turns)
    totals["cache_hit_ratio"] = (
        totals["cached_tokens"] / max(1, totals["prompt_tokens"])
    )

    if args.json:
        print(json.dumps({"rates": args.rates, "rates_table": rates, "totals": totals, "turns": turns if args.per_turn else None}, indent=2))
        return 0

    print(f"Log:   {args.log}")
    print(f"Rates: {args.rates} (input ${rates['input']}/Mtok, output ${rates['output']}/Mtok)")
    print()
    if args.per_turn:
        print(f"{'turn':>5} {'prompt':>10} {'cached':>10} {'cwrite':>8} {'new_in':>8} {'out':>6} {'$':>8}")
        for i, t in enumerate(turns, 1):
            print(
                f"{i:>5} {t['prompt_tokens']:>10} {t['cached_tokens']:>10} "
                f"{t['cache_creation_tokens']:>8} {t['new_input_tokens']:>8} "
                f"{t['completion_tokens']:>6} ${cost(t, rates):>7.4f}"
            )
        print()
    print(f"Turns:                  {totals['turns']}")
    print(f"Total prompt tokens:    {totals['prompt_tokens']:>12,}")
    print(f"  - cached (hit):       {totals['cached_tokens']:>12,}  ({totals['cache_hit_ratio']:.1%})")
    print(f"  - cache write:        {totals['cache_creation_tokens']:>12,}")
    print(f"  - new input:          {totals['new_input_tokens']:>12,}")
    print(f"Total completion:       {totals['completion_tokens']:>12,}")
    print(f"Total cost (USD):       ${totals['total_cost_usd']:>11,.4f}")
    print(f"  $/turn (avg):         ${totals['total_cost_usd']/totals['turns']:>11,.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
