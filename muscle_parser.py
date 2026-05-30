"""Keyword-based muscle-group parser for Sam Sulek video titles.

Replaces the old positional-regex + exact-string-dictionary approach with a
whole-title keyword scan. The muscle group(s) trained are almost always present
as a keyword somewhere in the title regardless of the surrounding creative
wording, so we extract those directly.

Inputs:  a video title string (str) and the config in muscle_groups.json.
Outputs: parse_title -> dict with keys:
            lift          detailed ';'-joined sorted muscles (or 'None')
            muscle_group  rolled-up ';'-joined sorted major groups (or 'None')
            matched       bool (True if any muscle was detected)

Matching rules:
- Patterns are matched case-insensitively against the lower-cased title.
- Each alias pattern is wrapped in word boundaries so e.g. 'leg' does not fire
  inside 'illegal' and 'arm' does not fire inside 'Armbrust'.
- Patterns are applied longest-first and matched spans are blanked out, so a
  qualified term ('side delts') is consumed before a generic one ('delts') can
  match the same text.
- The word 'back' is dropped before matching when it appears only in a
  'returning' context (e.g. 'back home', 'is back') so it is not read as the
  back muscle.
"""

import json
import re
from functools import lru_cache


@lru_cache(maxsize=1)
def _load_config(path="muscle_groups.json"):
    with open(path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    # Pre-compile: a flat list of (compiled_regex, muscle) sorted so that the
    # longest raw patterns are tried first (specific before generic).
    compiled = []
    for muscle, patterns in cfg["muscles"].items():
        for pat in patterns:
            compiled.append((len(pat), pat, muscle))
    compiled.sort(key=lambda t: t[0], reverse=True)

    ordered = []
    for _, pat, muscle in compiled:
        # Add word boundaries unless the pattern already specifies its own.
        body = pat if pat.startswith("\\b") else r"\b" + pat
        body = body if body.endswith("\\b") else body + r"\b"
        ordered.append((re.compile(body, re.IGNORECASE), muscle))

    back_ctx = re.compile(
        "|".join(cfg.get("back_returning_context", [])),
        re.IGNORECASE,
    ) if cfg.get("back_returning_context") else None

    return ordered, cfg["rollup"], back_ctx


def extract_muscles(title, path="muscle_groups.json"):
    """Return a sorted list of detailed muscle names found in the title."""
    ordered, _rollup, back_ctx = _load_config(path)

    work = title.lower()

    # Neutralise 'back' used in a returning sense so it is not read as a muscle.
    if back_ctx is not None:
        work = back_ctx.sub(lambda m: m.group(0).replace("back", "____"), work)

    found = set()
    for rgx, muscle in ordered:
        new_work, n = rgx.subn(" ", work)
        if n:
            found.add(muscle)
            work = new_work  # consume matched spans so generics can't re-match

    return sorted(found)


@lru_cache(maxsize=1)
def _load_overrides(path="manual_overrides.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f).get("overrides", {})
    except FileNotFoundError:
        return {}


def parse_title(title, path="muscle_groups.json", overrides_path="manual_overrides.json"):
    """Parse a title into detailed lift, rolled-up muscle_group and a matched flag.

    A manual override (keyed by exact whitespace-normalised title) takes
    precedence over the keyword scan. 'overridden' is True when one was applied.
    """
    norm_title = " ".join(title.split())
    overrides = _load_overrides(overrides_path)
    if norm_title in overrides:
        ov = overrides[norm_title]
        return {
            "lift": ov.get("lift", "None"),
            "muscle_group": ov.get("muscle_group", "None"),
            "matched": ov.get("lift", "None") != "None",
            "overridden": True,
        }

    _ordered, rollup, _back = _load_config(path)
    muscles = extract_muscles(title, path)

    if not muscles:
        return {"lift": "None", "muscle_group": "None", "matched": False, "overridden": False}

    groups = sorted({rollup.get(m, m) for m in muscles})
    return {
        "lift": ";".join(muscles),
        "muscle_group": ";".join(groups),
        "matched": True,
        "overridden": False,
    }
