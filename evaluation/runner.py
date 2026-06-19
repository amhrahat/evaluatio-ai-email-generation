import json
import csv
import asyncio
import sys
from pathlib import Path

# Add the repository root to the path so app imports work
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from app.core.llm import generate_email
from app.core.llm2 import generate_email2
from metrics import evaluate_email


def load_test_cases(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


async def evaluate_case1(test_case: dict) -> dict:
    generated = await generate_email(
        intent=test_case["intent"],
        key_facts=test_case["key_facts"],
        tone=test_case["tone"],
    )

    scores = evaluate_email(generated, test_case["key_facts"], test_case["tone"])
    return {
        "id": test_case["id"],
        "intent": test_case["intent"],
        "key_facts": test_case["key_facts"],
        "tone": test_case["tone"],
        "reference_email": test_case.get("reference_email", ""),
        "subject": generated.get("subject", ""),
        "body": generated.get("body", ""),
        "fact_coverage": scores["fact_coverage_score"],
        "tone_score": scores["tone_score"],
        "structure_score": scores["structure_score"],
        "avg": scores["avg"]
    }

async def evaluate_case2(test_case: dict) -> dict:
    generated = await generate_email2(
        intent=test_case["intent"],
        key_facts=test_case["key_facts"],
        tone=test_case["tone"],
    )

    scores = evaluate_email(generated, test_case["key_facts"], test_case["tone"])
    return {
        "id": test_case["id"],
        "intent": test_case["intent"],
        "key_facts": test_case["key_facts"],
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
    keys = [
        "id",
        "intent",
        "key_facts",
        "tone",
        "reference_email",
        "subject",
        "body",
        "fact_coverage",
        "tone_score",
        "structure_score",
        "avg",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        # Write metric definitions as comments
        f.write("# Metric definitions:\n")
        f.write("# fact_coverage: Average, per key fact, of the proportion of that fact's significant (non-stopword) words found in the generated email, matched on word boundaries. 1.0 means every fact's content words are fully present; partially-covered facts get partial credit instead of all-or-nothing.\n")
        f.write("# tone_score: Degree to which the generated email matches the requested tone, rated 0-1 by an LLM judge (response is parsed for the first number and clamped to [0,1]). Falls back to keyword matching only if the judge call fails or returns no parseable number.\n")
        f.write("# structure_score: Email structure score, capped at 1.0: non-empty subject (0.3) + body length between 20-300 words (0.3) + a recognized greeting e.g. Dear/Hello/Hi (0.2) + a recognized closing e.g. Regards/Sincerely/Best/Thank you (0.2).\n")
        f.write("\n")

        # Use proper CSV quoting for multi-line content
        writer = csv.DictWriter(f, fieldnames=keys, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writeheader()

        for row in results:
            writer.writerow({
                "id": row["id"],
                "intent": row["intent"],
                "key_facts": json.dumps(row["key_facts"], ensure_ascii=False),
                "tone": row["tone"],
                "reference_email": row["reference_email"],
                "subject": row["subject"],
                "body": row["body"],
                "fact_coverage": row["fact_coverage"],
                "tone_score": row["tone_score"],
                "structure_score": row["structure_score"],
                "avg": row["avg"],
            })


def export_json(results: list[dict], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)


def main():
    test_cases_file = Path(__file__).parent / "test_cases.json"
    test_cases = load_test_cases(str(test_cases_file))

    results1 = []
    results2 = []

    for case in test_cases:
        print(f"Evaluating {case['id']} - {case['intent']}")
        result1 = asyncio.run(evaluate_case1(case))
        result2 = asyncio.run(evaluate_case2(case))
        results1.append(result1)
        results2.append(result2)


    csv_path1 = Path(__file__).parent / "evaluation_report1.csv"
    json_path1 = Path(__file__).parent / "evaluation_report1.json"
    export_csv(results1, str(csv_path1))
    export_json(results1, str(json_path1))


    csv_path2 = Path(__file__).parent / "evaluation_report2.csv"
    json_path2 = Path(__file__).parent / "evaluation_report2.json"
    export_csv(results2, str(csv_path2))
    export_json(results2, str(json_path2))


    print(f"Saved CSV report to {csv_path1}")
    print(f"Saved JSON report to {json_path1}")
    print(f"Saved CSV report to {csv_path2}")
    print(f"Saved JSON report to {json_path2}")


if __name__ == "__main__":
    main()