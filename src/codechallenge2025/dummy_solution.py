from typing import List, Dict


def find_matches(database_path: str, queries_path: str) -> List[Dict]:
    import pandas as pd

    queries_df = pd.read_csv(queries_path)
    results = []
    for qid in queries_df["PersonID"]:
        results.append({"query_id": qid, "top_candidates": []})
    print("Dummy solution ran — returning no matches.")
    return results
