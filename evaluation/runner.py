import json
import csv
import asyncio
import sys
from pathlib import Path

# Add the repository root to the path so app imports work
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.core.llm import generate_email
from metrics import evaluate_email


def load_test_cases(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def evaluate_case(test_case: dict) -> dict:
    generated = await generate_email(
        intent=test_case["intent"],
        key_facts=test_case["key_facts"],
        tone=test_case["tone"],
    )
    print(f"Generated email for {test_case['id']}: {generated}")

    scores = evaluate_email(generated, test_case["key_facts"], test_case["tone"])
    return {
        "id": test_case["id"],
        "intent": test_case["intent"],
        "tone": test_case["tone"],
        "reference_email": test_case.get("reference_email", ""),
        "subject": generated.get("subject", ""),
        "body": generated.get("body", ""),
        "fact_coverage": scores["fact_coverage_score"],
        "tone_score": scores["tone_score"],
        "structure_score": scores["structure_score"],
        "avg": scores["avg"]
    }


def export_csv(results: list[dict], path: str):
    keys = ["id", "fact_coverage", "tone_score", "structure_score", "avg"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, delimiter="\t")
        writer.writeheader()
        for row in results:
            writer.writerow({k: row[k] for k in keys})


def export_json(results: list[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def main():
    test_cases_file = Path(__file__).parent / "test_cases.json"
    test_cases = load_test_cases(str(test_cases_file))

    results = []
    for case in test_cases:
        print(f"Evaluating {case['id']} - {case['intent']}")
        print(case)
        result = asyncio.run(evaluate_case(case))
        results.append(result)

    csv_path = Path(__file__).parent / "evaluation_report.csv"
    json_path = Path(__file__).parent / "evaluation_report.json"
    export_csv(results, str(csv_path))
    export_json(results, str(json_path))

    print(f"Saved CSV report to {csv_path}")
    print(f"Saved JSON report to {json_path}")


if __name__ == "__main__":
    main()