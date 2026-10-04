"""Instructor tool: add or update a team's score on the Lab 5 leaderboard.

Usage (paste the line the student's notebook printed, inside single quotes):
    python add_score.py '{"team": "Ali & Sara", "accuracy": 97.3, "clean": 100.0, "hard": 94.6, "mean_error_px": 5.1, "fps": 180.2}'
Then commit and push leaderboard.json - the Labs page shows the new ranking within a minute or two.
"""
import json
import os
import sys

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard.json")
KEYS = ("team", "accuracy", "clean", "hard", "mean_error_px", "fps")

entry = json.loads(sys.argv[1])
missing = [k for k in KEYS if k not in entry]
if missing:
    sys.exit(f"missing fields: {missing}")
entry = {k: entry[k] for k in KEYS}

board = json.load(open(PATH, encoding="utf-8"))
board["entries"] = [e for e in board["entries"] if e["team"] != entry["team"]] + [entry]
board["entries"].sort(key=lambda e: (-e["accuracy"], e["mean_error_px"], -e["fps"]))
json.dump(board, open(PATH, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

for i, e in enumerate(board["entries"], 1):
    print(f"{i:2d}. {e['team']:<40} {e['accuracy']:5.1f}%  clean {e['clean']:5.1f}%  hard {e['hard']:5.1f}%  "
          f"err {e['mean_error_px']:5.1f}px  {e['fps']:6.1f} fps")
