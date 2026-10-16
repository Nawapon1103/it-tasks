"""Build data.json (the public read-only snapshot) from the Excel text dump.

Usage: python3 tools/build_data.py <dump.txt> [data.json]

<dump.txt> is the text the Microsoft 365 connector returns when reading
GMPV.IT.JOBTASK.xlsx: a header line starting with "ID\tDate\tTitle", then one
tab-separated line per task. Other lines (sheet titles, "[1 empty row]") are ignored.
"""
import json
import sys
from datetime import datetime, timedelta, timezone

COLS = ["ID", "Date", "Title", "Category", "Owner", "Priority", "Status",
        "Deadline", "Note", "CreatedAt", "UpdatedAt", "CompletedAt"]


def excel_date(v, with_time):
    """Convert an Excel serial number to text; leave anything else as is."""
    try:
        n = float(v)
    except ValueError:
        return v
    if n < 20000:
        return v
    d = datetime(1899, 12, 30) + timedelta(days=n)
    return d.strftime("%Y-%m-%d %H:%M" if with_time else "%Y-%m-%d")


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else "data.json"
    lines = open(src, encoding="utf-8").read().splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("ID\tDate\tTitle"))
    except StopIteration:
        sys.exit("header row not found — refusing to overwrite data.json")
    tasks = []
    for line in lines[start + 1:]:
        if "\t" not in line:
            continue
        v = [x.strip() for x in line.split("\t")]
        v += [""] * (len(COLS) - len(v))
        t = dict(zip(COLS, v[:len(COLS)]))
        if not t["ID"] or not t["Title"]:
            continue
        for c in ("Date", "Deadline"):
            t[c] = excel_date(t[c], False)
        for c in ("CreatedAt", "UpdatedAt", "CompletedAt"):
            t[c] = excel_date(t[c], True)
        tasks.append(t)
    now = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M")
    json.dump({"updatedAt": now, "tasks": tasks}, open(out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"wrote {len(tasks)} tasks to {out} at {now}")


if __name__ == "__main__":
    main()
