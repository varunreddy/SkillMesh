from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def test_human_eval_prepare_and_aggregate(tmp_path: Path):
    script = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_human_eval.py"

    bench_csv = tmp_path / "bench.csv"
    _write_csv(
        bench_csv,
        [
            "task_id",
            "domain",
            "query",
            "expected_role",
            "config_id",
            "config",
            "ranked_ids",
        ],
        [
            {
                "task_id": "T01",
                "domain": "BI",
                "query": "build KPI dashboard",
                "expected_role": "role.analytics-engineer",
                "config_id": "A",
                "config": "All cards",
                "ranked_ids": "role.analytics-engineer;bi.dashboard-design",
            },
            {
                "task_id": "T01",
                "domain": "BI",
                "query": "build KPI dashboard",
                "expected_role": "role.analytics-engineer",
                "config_id": "B",
                "config": "Routed",
                "ranked_ids": "role.analytics-engineer;bi.dashboard-design",
            },
            {
                "task_id": "T01",
                "domain": "BI",
                "query": "build KPI dashboard",
                "expected_role": "role.analytics-engineer",
                "config_id": "C",
                "config": "Role routed",
                "ranked_ids": "role.analytics-engineer;bi.dashboard-design",
            },
            {
                "task_id": "T02",
                "domain": "DevOps",
                "query": "build CI/CD",
                "expected_role": "role.devops-engineer",
                "config_id": "A",
                "config": "All cards",
                "ranked_ids": "role.devops-engineer;devops.cicd-patterns",
            },
            {
                "task_id": "T02",
                "domain": "DevOps",
                "query": "build CI/CD",
                "expected_role": "role.devops-engineer",
                "config_id": "B",
                "config": "Routed",
                "ranked_ids": "role.devops-engineer;devops.cicd-patterns",
            },
            {
                "task_id": "T02",
                "domain": "DevOps",
                "query": "build CI/CD",
                "expected_role": "role.devops-engineer",
                "config_id": "C",
                "config": "Role routed",
                "ranked_ids": "role.devops-engineer;devops.cicd-patterns",
            },
        ],
    )

    template_csv = tmp_path / "template.csv"
    key_csv = tmp_path / "key.csv"

    prepare = subprocess.run(
        [
            sys.executable,
            str(script),
            "prepare",
            "--input-csv",
            str(bench_csv),
            "--output-template",
            str(template_csv),
            "--output-key",
            str(key_csv),
            "--seed",
            "7",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert prepare.returncode == 0, prepare.stderr
    assert template_csv.exists()
    assert key_csv.exists()

    template_rows = _read_csv(template_csv)
    assert len(template_rows) == 6

    rater_one = tmp_path / "rater-one.csv"
    rater_two = tmp_path / "rater-two.csv"

    rows_one: list[dict[str, str]] = []
    rows_two: list[dict[str, str]] = []
    for i, row in enumerate(template_rows, start=1):
        row_one = dict(row)
        row_one["rater_id"] = "one"
        row_one["quality_score"] = "5" if i % 2 else "4"
        row_one["notes"] = "ok"
        rows_one.append(row_one)

        row_two = dict(row)
        row_two["rater_id"] = "two"
        row_two["quality_score"] = "4"
        row_two["notes"] = "ok"
        rows_two.append(row_two)

    _write_csv(rater_one, list(template_rows[0].keys()), rows_one)
    _write_csv(rater_two, list(template_rows[0].keys()), rows_two)

    combined_csv = tmp_path / "combined.csv"
    summary_csv = tmp_path / "summary.csv"
    summary_md = tmp_path / "summary.md"

    aggregate = subprocess.run(
        [
            sys.executable,
            str(script),
            "aggregate",
            "--key-csv",
            str(key_csv),
            "--ratings-csv",
            str(rater_one),
            str(rater_two),
            "--output-combined",
            str(combined_csv),
            "--output-summary-csv",
            str(summary_csv),
            "--output-summary-md",
            str(summary_md),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert aggregate.returncode == 0, aggregate.stderr
    assert combined_csv.exists()
    assert summary_csv.exists()
    assert summary_md.exists()

    summary_rows = _read_csv(summary_csv)
    assert {row["config_id"] for row in summary_rows} == {"A", "B", "C"}
    assert sum(int(row["n_ratings"]) for row in summary_rows) == 12
