#!/usr/bin/env python3
"""Scan an evidence packet and describe each file. Changes nothing.

For every file under incident/ (recursively, .gz decompressed) it records the
detected format, the number of lines, the number of malformed lines, the number of
duplicate lines, and a few sample malformed lines. The exact definitions it applies
are written into the output under "definitions" (see DEFINITIONS below).

Use the malformed and duplicate counts only if the impact report actually needs the
number of malformed or duplicate rows, and only if these definitions match the ones
the report must follow (app/contracts/evidence.md and task.md). Where a definition
differs, or a file's format is "unknown", count that part yourself by the contract's
rules; the formats and samples are still useful as a starting point.

Usage: python3 tools/generic_malformed_duplicate_check.py [incident_dir] [out_file]
Defaults: incident/  out/generic_malformed_duplicate_check.json
"""

import csv
import gzip
import json
import sys
from pathlib import Path

SAMPLE_LINES = 200
MAX_SAMPLES = 5

ABOUT = (
    "Generic malformed/duplicate line check of incident/, not tailored to this incident. Deterministic, written before the agent started. Nothing was "
    "removed from the logs. Use the malformed/duplicate counts only if the impact "
    "report needs the number of malformed or duplicate rows, and only if the "
    "definitions below match the ones app/contracts/evidence.md and task.md require. "
    "If a definition differs, or a file's format is unknown, count that part yourself."
)

DEFINITIONS = {
    "lines": "Non-blank lines in the file (CRLF normalised, .gz decompressed). "
             "For csv: data rows, header excluded. For json-document: 1.",
    "malformed": {
        "json-lines": "The line is not valid JSON on its own.",
        "key-value": "The last whitespace-separated token has no '=' or ends with '=' "
                     "(e.g. '... attempt=' or '... att'), i.e. the line was cut off.",
        "csv": "The row, parsed on its own, has fewer fields than the header. Empty "
               "cells still count as fields ('a,,c' has 3 fields), so blank or null "
               "values are NOT malformed. A row cut inside its last field (field count "
               "unchanged) is not detected.",
        "json-document": "The whole file is not valid JSON (counts as 1).",
        "note": "Malformed lines are counted every time they appear, including copies.",
    },
    "duplicates": "Extra copies of a line that is byte-identical (after CRLF "
                  "normalisation) to a line seen earlier in the same file, malformed "
                  "or not. The first occurrence is not counted. Not detected: "
                  "duplicates across files, or repeated events whose lines differ "
                  "(e.g. different timestamps or field order).",
}


def read_text(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def is_json(line):
    try:
        json.loads(line)
        return True
    except ValueError:
        return False


def kv_tokens(line):
    return [t for t in line.split() if "=" in t]


def kv_malformed(line):
    last = line.split()[-1]
    return "=" not in last or last.endswith("=")


def csv_row(line):
    # Parse each line on its own so a cut-off quoted field can't swallow later lines.
    return next(csv.reader([line]), [])


def detect(text, lines):
    sample = lines[:SAMPLE_LINES]
    if not sample:
        return "empty"
    if is_json(text):
        return "json-document" if len(lines) <= 1 or not all(is_json(l) for l in sample[:5]) else "json-lines"
    if sum(is_json(l) for l in sample) >= 0.8 * len(sample):
        return "json-lines"
    if sum(len(kv_tokens(l)) >= 2 for l in sample) >= 0.8 * len(sample):
        return "key-value"
    header = csv_row(sample[0])
    if len(header) >= 2 and "=" not in sample[0]:
        widths = [len(csv_row(l)) for l in sample[1:]]
        if widths and sum(w == len(header) for w in widths) >= 0.8 * len(widths):
            return "csv"
    return "unknown"


def scan(path):
    text = read_text(path)
    lines = [l for l in text.split("\n") if l.strip()]
    fmt = detect(text, lines)
    rec = {"format": fmt, "lines": len(lines), "malformed": None, "duplicates": None, "samples": []}
    if fmt in ("unknown", "empty"):
        return rec
    if fmt == "json-document":
        rec.update(lines=1, malformed=0 if is_json(text) else 1, duplicates=0)
        return rec
    if fmt == "csv":
        width = len(csv_row(lines[0]))
        rec["header"] = csv_row(lines[0])
        lines = lines[1:]
        rec["lines"] = len(lines)
        bad = [l for l in lines if len(csv_row(l)) < width]
    elif fmt == "json-lines":
        bad = [l for l in lines if not is_json(l)]
    else:  # key-value
        bad = [l for l in lines if kv_malformed(l)]
    seen, dups = set(), 0
    for l in lines:
        if l in seen:
            dups += 1
        seen.add(l)
    rec.update(malformed=len(bad), duplicates=dups, samples=[b[-160:] for b in bad[:MAX_SAMPLES]])
    return rec


def main():
    root = Path(__file__).resolve().parent.parent
    incident = Path(sys.argv[1]) if len(sys.argv) > 1 else root / "incident"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else root / "out" / "generic_malformed_duplicate_check.json"
    files = {}
    for p in sorted(incident.rglob("*")):
        if p.is_file():
            try:
                files[p.relative_to(incident).as_posix()] = scan(p)
            except Exception as e:  # never let the scan break run.sh
                files[p.relative_to(incident).as_posix()] = {"format": "error", "error": repr(e)}
    result = {
        "about": ABOUT,
        "definitions": DEFINITIONS,
        "total_malformed": sum(f.get("malformed") or 0 for f in files.values()),
        "total_duplicates": sum(f.get("duplicates") or 0 for f in files.values()),
        "files": files,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, f in files.items():
        print(f"  {name:40} {f['format']:14} lines={f.get('lines')} malformed={f.get('malformed')} duplicates={f.get('duplicates')}")
    print(f"  total malformed={result['total_malformed']} duplicates={result['total_duplicates']} -> {out}")


if __name__ == "__main__":
    main()
