# tests/run_challenge.py
"""
Runs the participant's solution, evaluates correctness, and outputs results.
Works locally and in GitHub Actions.
"""

import os
import time
import pandas as pd
import importlib.util
import sys


def load_participant():
    """Dynamically load the participant_solution module"""
    spec = importlib.util.spec_from_file_location(
        "participant_solution", "src/codechallenge2025/participant_solution.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["participant_solution"] = module
    spec.loader.exec_module(module)
    return module


def evaluate_results(participant_results: list) -> tuple:
    """Evaluate how many true matches were found in top candidate"""
    gt_path = "data/ground_truth.csv"
    if not os.path.exists(gt_path):
        print("Warning: ground_truth.csv not found — skipping evaluation")
        return 0.0, 0, 35

    gt = pd.read_csv(gt_path)
    gt_dict = dict(zip(gt["QueryID"], gt["TrueCounterpartID"]))

    correct = 0
    total_with_match = len(gt_dict)

    for result in participant_results:
        query_id = result["query_id"]
        if query_id not in gt_dict:
            continue  # negative control query
        true_id = gt_dict[query_id]
        top_candidates = result.get("top_candidates", [])
        if top_candidates and top_candidates[0]["person_id"] == true_id:
            correct += 1

    accuracy = correct / total_with_match if total_with_match > 0 else 0.0
    return accuracy, correct, total_with_match


def main():
    print("=== #codechallenge2025 Local Test Run ===")

    # Generate fresh dataset
    print("Generating dataset...")
    os.system("uv run src/codechallenge2025/dataset_generator.py")

    # Load participant code
    print("Loading participant solution...")
    participant = load_participant()

    db_path = "data/str_database.csv"
    queries_path = "data/str_queries.csv"

    # Run matching
    print("Running find_matches()...")
    start_time = time.time()
    results = participant.find_matches(db_path, queries_path)
    duration = time.time() - start_time

    # Evaluate
    accuracy, correct, total = evaluate_results(results)

    # Scoring
    base_score = accuracy * 100
    if duration < 300:
        speed_bonus = 20
    elif duration < 600:
        speed_bonus = 10
    else:
        speed_bonus = 0
    final_score = base_score + speed_bonus

    # Print summary
    print("\n=== RESULTS ===")
    print(f"Execution time : {duration:.2f} seconds")
    print(f"Correct matches: {correct}/{total}")
    print(f"Accuracy       : {accuracy:.1%}")
    print(f"Speed bonus    : +{speed_bonus}")
    print(f"Final score    : {final_score:.1f}/120")

    # Save results for leaderboard (local + CI compatible)
    output_file = "test_results.txt"
    with open(output_file, "w") as f:
        print(f"time={duration:.2f}", file=f)
        print(f"accuracy={accuracy:.6f}", file=f)
        print(f"correct={correct}", file=f)
        print(f"score={final_score:.1f}", file=f)

    # Also write to GITHUB_OUTPUT if in CI
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            print(f"time={duration:.2f}", file=f)
            print(f"accuracy={accuracy:.6f}", file=f)
            print(f"correct={correct}", file=f)
            print(f"score={final_score:.1f}", file=f)

    print(f"\nResults saved to {output_file} → ready for leaderboard update")


if __name__ == "__main__":
    main()
