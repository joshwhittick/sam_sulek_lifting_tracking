"""Safely re-parse video_data_final.json with the new keyword-based parser.

Non-destructive by design. The user made manual edits to video_data_final.json
early in the project, so this script never overwrites it. Instead it:

  1. copies the original to video_data_final.backup.json
  2. re-derives event/day/lift/muscle_group from each title (preserving the
     source fields title/video_url/upload_date) into
     video_data_final.regenerated.json
  3. writes reparse_diff.md, a human-readable report of every field that changed
     versus the original, plus the titles still left unmatched

Review reparse_diff.md, and only then promote the regenerated file with:
    Copy-Item video_data_final.regenerated.json video_data_final.json

Inputs:  video_data_final.json (current dataset)
Outputs: video_data_final.backup.json, video_data_final.regenerated.json,
         reparse_diff.md
"""

import json
import logging
import shutil
from collections import Counter

from analyse import clean_and_enrich_json, PHASE_DICT

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("reparse")

SRC = "video_data_final.json"
BACKUP = "video_data_final.backup.json"
OUT = "video_data_final.regenerated.json"
DIFF = "reparse_diff.md"


def _norm(value):
    """Order-insensitive comparison key for ';'-joined muscle strings."""
    if not value or value == "None":
        return "None"
    return ";".join(sorted(p.strip() for p in value.split(";")))


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        original = json.load(f)
    log.info("Loaded %d videos from %s", len(original), SRC)

    shutil.copyfile(SRC, BACKUP)
    log.info("Backed up original -> %s", BACKUP)

    regenerated = clean_and_enrich_json([dict(x) for x in original])
    assert len(regenerated) == len(original), "row count changed during reparse"

    by_url_old = {x["video_url"]: x for x in original}

    # Preserve manually-curated event/day. Many videos with no 'Day N' in the
    # title had their phase assigned by hand, so we keep the original values and
    # only (a) fill gaps where the original was 'None' and (b) normalise known
    # phase typos/variants via PHASE_DICT (e.g. Cuzilla -> Cutzilla).
    event_filled, event_typo_fixed = 0, 0
    for new in regenerated:
        old = by_url_old.get(new["video_url"], {})
        o_event, o_day = old.get("event", "None"), old.get("day", "None")

        if o_event != "None":
            normalised = PHASE_DICT.get(o_event, o_event)
            if normalised != o_event:
                event_typo_fixed += 1
            new["event"] = normalised
        elif new["event"] != "None":
            event_filled += 1  # keep newly-derived event (gap fill)

        new["day"] = o_day if o_day != "None" else new["day"]

    log.info("Event preserved from original; gaps filled: %d, typos normalised: %d",
             event_filled, event_typo_fixed)

    lift_changes, event_changes, day_changes = [], [], []
    gained, lost, unmatched = [], [], []

    for new in regenerated:
        old = by_url_old.get(new["video_url"], {})
        o_lift, n_lift = _norm(old.get("lift", "None")), _norm(new["lift"])
        o_event = old.get("event", "None")
        o_day = old.get("day", "None")

        if o_lift != n_lift:
            lift_changes.append((new["title"], old.get("lift", "None"), new["lift"]))
            if o_lift == "None" and n_lift != "None":
                gained.append((new["title"], new["lift"]))
            elif o_lift != "None" and n_lift == "None":
                lost.append((new["title"], old.get("lift", "None")))
        if o_event != new["event"]:
            event_changes.append((new["title"], o_event, new["event"]))
        if o_day != new["day"]:
            day_changes.append((new["title"], o_day, new["day"]))
        if new["lift"] == "None":
            unmatched.append(new["title"])

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(regenerated, f, indent=4, ensure_ascii=False)
    log.info("Wrote regenerated dataset -> %s", OUT)

    matched = sum(1 for x in regenerated if x["lift"] != "None")
    lines = []
    lines.append("# Re-parse diff report\n")
    lines.append(f"- Total videos: **{len(regenerated)}**")
    lines.append(f"- Lift matched: **{matched}** ({matched/len(regenerated):.0%})  |  "
                 f"unmatched (None): **{len(unmatched)}**")
    lines.append(f"- Lift values changed vs original: **{len(lift_changes)}**  "
                 f"(newly matched: {len(gained)}, now None: {len(lost)})")
    lines.append(f"- Event values changed: **{len(event_changes)}**  |  "
                 f"Day values changed: **{len(day_changes)}**\n")

    def table(rows, headers):
        out = ["| " + " | ".join(headers) + " |",
               "| " + " | ".join("---" for _ in headers) + " |"]
        for r in rows:
            out.append("| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |")
        return "\n".join(out)

    lines.append("## Newly matched (was None -> now a muscle) - verify no false positives\n")
    lines.append(table(gained, ["Title", "New lift"]) if gained else "_none_")
    lines.append("\n## Now None (was set -> now None) - these were almost all old garbage values\n")
    lines.append(table(lost, ["Title", "Old lift"]) if lost else "_none_")
    lines.append("\n## Changed lift (both set, differ) - new parser normalising old values\n")
    lines.append(table([(t, o, n) for t, o, n in lift_changes
                        if _norm(o) != "None" and _norm(n) != "None"],
                       ["Title", "Old", "New"]) or "_none_")
    lines.append("\n## Event changes\n")
    lines.append(table(event_changes, ["Title", "Old event", "New event"]) if event_changes else "_none_")
    lines.append("\n## Still unmatched (lift = None) - genuine non-lift videos or puns to add\n")
    lines.append(table([(t,) for t in unmatched], ["Title"]) if unmatched else "_none_")

    with open(DIFF, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log.info("Wrote diff report -> %s", DIFF)

    log.info("Summary: matched %d/%d (%.0f%%), lift changes %d, event changes %d, day changes %d",
             matched, len(regenerated), 100*matched/len(regenerated),
             len(lift_changes), len(event_changes), len(day_changes))
    log.info("Top muscle_group counts: %s",
             Counter(g for x in regenerated if x["muscle_group"] != "None"
                     for g in x["muscle_group"].split(";")).most_common())


if __name__ == "__main__":
    main()
