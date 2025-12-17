# tests/update_leaderboard.py
"""
Updates Leaderboard.md and leaderboard.json from test results.
Works locally AND in GitHub Actions.
"""

import json
import os
from datetime import datetime
import pandas as pd

LEADERBOARD_JSON = "leaderboard.json"
LEADERBOARD_MD = "Leaderboard.md"


def load_leaderboard():
    if os.path.exists(LEADERBOARD_JSON):
        with open(LEADERBOARD_JSON, "r") as f:
            return json.load(f)
    return []


def save_leaderboard(entries):
    with open(LEADERBOARD_JSON, "w") as f:
        json.dump(entries, f, indent=2)


def generate_markdown(entries):
    if not entries:
        return "# 🏆 #codechallenge2025 Leaderboard\n\nNo submissions yet.\n\n---\n*Auto-updated on every test run.*\n"

    df = pd.DataFrame(entries)
    df["score"] = pd.to_numeric(df["score"])
    df["time"] = pd.to_numeric(df["time"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(by=["score", "time"], ascending=[False, True])
    df = df.reset_index(drop=True)
    df["rank"] = range(1, len(df) + 1)

    md = "# 🏆 #codechallenge2025 Leaderboard\n\n"
    md += f"_Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}_\n\n"
    md += "| Rank | User          | Score  | Accuracy | Time (s) | Date       | Run        |\n"
    md += "|------|---------------|--------|----------|----------|------------|------------|\n"

    for _, row in df.iterrows():
        user = row["user"]
        run = row["pr"] if row["pr"] != "local-run" else "local"
        run_link = (
            f"[{row['pr']}]({row['pr_url']})"
            if row.get("pr_url") and row["pr"] != "local-run"
            else run
        )
        md += f"| {row['rank']} | @{user} | **{row['score']:.1f}** | {row['accuracy']:.1%} | {row['time']:.2f} | {row['timestamp'].strftime('%Y-%m-%d')} | {run_link} |\n"

    md += "\n---\n*Leaderboard auto-updated on every test run (local or CI).*\n"
    return md


def main():
    # Try CI environment variables first
    score = os.getenv("SCORE")
    accuracy = os.getenv("ACCURACY")
    time_taken = os.getenv("TIME")
    username = os.getenv("GH_USERNAME")
    pr_number = os.getenv("PR_NUMBER")
    pr_url = os.getenv("PR_URL")

    # Fallback: read from local test_results.txt
    local_file = "test_results.txt"
    if not score and os.path.exists(local_file):
        print("No CI environment detected — loading results from test_results.txt")
        with open(local_file) as f:
            lines = [line.strip() for line in f.readlines() if "=" in line]
        vars_dict = {}
        for line in lines:
            k, v = line.split("=", 1)
            vars_dict[k] = v

        score = vars_dict.get("score")
        accuracy = vars_dict.get("accuracy")
        time_taken = vars_dict.get("time")
        username = os.getenv(
            "USER", os.getenv("USERNAME", "local-tester")
        )  # best effort
        pr_number = "local"
        pr_url = ""

    if not score:
        print("No results found — skipping leaderboard update")
        return

    new_entry = {
        "user": username or "unknown",
        "score": float(score),
        "accuracy": float(accuracy or 0),
        "time": float(time_taken or 0),
        "timestamp": datetime.utcnow().isoformat(),
        "pr": f"#{pr_number}" if pr_number and pr_number != "local" else "local-run",
        "pr_url": pr_url or "",
    }

    entries = load_leaderboard()
    # Remove previous entry from same run (local or same PR)
    entries = [e for e in entries if e.get("pr") != new_entry["pr"]]
    entries.append(new_entry)

    save_leaderboard(entries)

    md_content = generate_markdown(entries)
    with open(LEADERBOARD_MD, "w") as f:
        f.write(md_content)

    print(f"Leaderboard updated → {LEADERBOARD_MD} & {LEADERBOARD_JSON}")
    print(f"   New entry: @{new_entry['user']} — Score: {new_entry['score']:.1f}")


if __name__ == "__main__":
    main()
