#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import random
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Iterable

REQUIRED_BENCHMARK_COLUMNS = {
    "task_id",
    "domain",
    "query",
    "expected_role",
    "config_id",
    "config",
    "ranked_ids",
}

RATER_TEMPLATE_COLUMNS = [
    "item_id",
    "task_id",
    "domain",
    "query",
    "variant_code",
    "ranked_ids",
    "rater_id",
    "quality_score",
    "notes",
]

KEY_COLUMNS = [
    "item_id",
    "task_id",
    "variant_code",
    "config_id",
    "config",
    "expected_role",
]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [dict(row) for row in reader]


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _normalize_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    cleaned: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in rows:
        task_id = row.get("task_id", "").strip()
        config_id = row.get("config_id", "").strip()
        if not task_id or not config_id:
            continue
        key = (task_id, config_id)
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(row)

    cleaned.sort(key=lambda r: (r.get("task_id", ""), r.get("config_id", "")))
    return cleaned


def _prepare(args: argparse.Namespace) -> int:
    input_csv = Path(args.input_csv).expanduser().resolve()
    rows = _read_csv(input_csv)
    if not rows:
        raise SystemExit(f"No rows found in benchmark CSV: {input_csv}")

    missing = REQUIRED_BENCHMARK_COLUMNS - set(rows[0].keys())
    if missing:
        raise SystemExit(
            "Benchmark CSV is missing required columns: " + ", ".join(sorted(missing))
        )

    rows = _normalize_rows(rows)
    if args.config_ids:
        requested = {cfg.strip() for cfg in args.config_ids.split(",") if cfg.strip()}
        rows = [row for row in rows if row.get("config_id", "").strip() in requested]

    task_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        task_groups[row["task_id"].strip()].append(row)

    rng = random.Random(args.seed)
    template_rows: list[dict[str, object]] = []
    key_rows: list[dict[str, object]] = []

    for task_id in sorted(task_groups):
        group = list(task_groups[task_id])
        if args.blind:
            rng.shuffle(group)
        else:
            group.sort(key=lambda r: r.get("config_id", ""))

        for idx, row in enumerate(group, start=1):
            variant_code = f"V{idx}"
            item_id = f"{task_id}_{variant_code}"

            template_rows.append(
                {
                    "item_id": item_id,
                    "task_id": task_id,
                    "domain": row.get("domain", ""),
                    "query": row.get("query", ""),
                    "variant_code": variant_code,
                    "ranked_ids": row.get("ranked_ids", ""),
                    "rater_id": "",
                    "quality_score": "",
                    "notes": "",
                }
            )

            key_rows.append(
                {
                    "item_id": item_id,
                    "task_id": task_id,
                    "variant_code": variant_code,
                    "config_id": row.get("config_id", ""),
                    "config": row.get("config", ""),
                    "expected_role": row.get("expected_role", ""),
                }
            )

    output_template = Path(args.output_template).expanduser().resolve()
    output_key = Path(args.output_key).expanduser().resolve()

    _write_csv(output_template, RATER_TEMPLATE_COLUMNS, template_rows)
    _write_csv(output_key, KEY_COLUMNS, key_rows)

    print(f"Wrote rater template: {output_template}")
    print(f"Wrote key file: {output_key}")
    print(f"Items: {len(template_rows)} ({len(task_groups)} tasks)")
    return 0


def _safe_float(value: str) -> float | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _load_key(path: Path) -> dict[str, dict[str, str]]:
    rows = _read_csv(path)
    if not rows:
        raise SystemExit(f"Key CSV has no rows: {path}")
    mapping: dict[str, dict[str, str]] = {}
    for row in rows:
        item_id = row.get("item_id", "").strip()
        if item_id:
            mapping[item_id] = row
    return mapping


def _aggregate(args: argparse.Namespace) -> int:
    key_path = Path(args.key_csv).expanduser().resolve()
    key_map = _load_key(key_path)

    ratings_input = [Path(p).expanduser().resolve() for p in args.ratings_csv]
    all_rows: list[dict[str, object]] = []

    for path in ratings_input:
        rows = _read_csv(path)
        if not rows:
            continue
        fallback_rater = path.stem
        for row in rows:
            item_id = row.get("item_id", "").strip()
            if not item_id or item_id not in key_map:
                continue
            score = _safe_float(row.get("quality_score", ""))
            if score is None:
                continue

            key = key_map[item_id]
            rater_id = (row.get("rater_id", "") or "").strip() or fallback_rater
            all_rows.append(
                {
                    "item_id": item_id,
                    "task_id": key.get("task_id", ""),
                    "variant_code": key.get("variant_code", ""),
                    "config_id": key.get("config_id", ""),
                    "config": key.get("config", ""),
                    "rater_id": rater_id,
                    "quality_score": score,
                    "notes": row.get("notes", ""),
                }
            )

    if not all_rows:
        raise SystemExit("No scored ratings found. Fill quality_score values (1-5) first.")

    by_config: dict[str, list[float]] = defaultdict(list)
    by_item: dict[str, list[float]] = defaultdict(list)

    for row in all_rows:
        cfg = str(row["config_id"])
        score = float(row["quality_score"])
        by_config[cfg].append(score)
        by_item[str(row["item_id"])].append(score)

    summary_rows: list[dict[str, object]] = []
    for config_id in sorted(by_config):
        scores = by_config[config_id]
        label = next((r["config"] for r in all_rows if r["config_id"] == config_id), config_id)
        summary_rows.append(
            {
                "config_id": config_id,
                "config": label,
                "n_ratings": len(scores),
                "avg_quality": round(statistics.mean(scores), 3),
                "median_quality": round(statistics.median(scores), 3),
                "stdev_quality": round(statistics.pstdev(scores), 3),
                "top_box_rate_pct": round(100.0 * (sum(1 for s in scores if s >= 4.0) / len(scores)), 1),
            }
        )

    exact_agreement = 0
    within_one = 0
    comparable_items = 0
    for _, scores in by_item.items():
        if len(scores) < 2:
            continue
        comparable_items += 1
        if max(scores) == min(scores):
            exact_agreement += 1
        if (max(scores) - min(scores)) <= 1.0:
            within_one += 1

    combined_output = Path(args.output_combined).expanduser().resolve()
    summary_output = Path(args.output_summary_csv).expanduser().resolve()
    report_output = Path(args.output_summary_md).expanduser().resolve()

    _write_csv(
        combined_output,
        [
            "item_id",
            "task_id",
            "variant_code",
            "config_id",
            "config",
            "rater_id",
            "quality_score",
            "notes",
        ],
        all_rows,
    )
    _write_csv(
        summary_output,
        [
            "config_id",
            "config",
            "n_ratings",
            "avg_quality",
            "median_quality",
            "stdev_quality",
            "top_box_rate_pct",
        ],
        summary_rows,
    )

    report_output.parent.mkdir(parents=True, exist_ok=True)
    with report_output.open("w", encoding="utf-8") as fh:
        fh.write("# SkillMesh Human Eval Summary\n\n")
        fh.write(f"Ratings files: {len(ratings_input)}\n\n")
        fh.write("## Config Scores\n\n")
        fh.write("| Config ID | Config | N Ratings | Avg Quality | Median | Std Dev | Top-Box (>=4) |\n")
        fh.write("|---|---|---:|---:|---:|---:|---:|\n")
        for row in summary_rows:
            fh.write(
                f"| {row['config_id']} | {row['config']} | {row['n_ratings']} | "
                f"{row['avg_quality']} | {row['median_quality']} | {row['stdev_quality']} | "
                f"{row['top_box_rate_pct']}% |\n"
            )

        fh.write("\n## Inter-Rater Agreement\n\n")
        fh.write(f"- Comparable items (>=2 ratings): {comparable_items}\n")
        if comparable_items:
            fh.write(
                f"- Exact agreement: {exact_agreement}/{comparable_items} "
                f"({(100.0 * exact_agreement / comparable_items):.1f}%)\n"
            )
            fh.write(
                f"- Within 1 point: {within_one}/{comparable_items} "
                f"({(100.0 * within_one / comparable_items):.1f}%)\n"
            )
        else:
            fh.write("- Not enough overlapping ratings yet.\n")

    print(f"Wrote combined ratings: {combined_output}")
    print(f"Wrote summary CSV: {summary_output}")
    print(f"Wrote summary report: {report_output}")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepare and aggregate human ratings for SkillMesh benchmark runs.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    prep = sub.add_parser("prepare", help="Create blinded rating template and key file")
    prep.add_argument("--input-csv", required=True, help="Benchmark run CSV")
    prep.add_argument(
        "--output-template",
        required=True,
        help="Output CSV for raters to fill",
    )
    prep.add_argument(
        "--output-key",
        required=True,
        help="Output CSV mapping variant codes to real config IDs",
    )
    prep.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Shuffle seed for blinded order",
    )
    prep.add_argument(
        "--config-ids",
        default="",
        help="Optional comma-separated config IDs to include (example: A,B,C)",
    )
    prep.add_argument(
        "--no-blind",
        action="store_false",
        dest="blind",
        default=True,
        help="Disable shuffling and keep config order deterministic (A/B/C)",
    )

    agg = sub.add_parser("aggregate", help="Aggregate completed rating sheets")
    agg.add_argument("--key-csv", required=True, help="Key file from prepare step")
    agg.add_argument(
        "--ratings-csv",
        required=True,
        nargs="+",
        help="One or more completed ratings CSV files",
    )
    agg.add_argument(
        "--output-combined",
        required=True,
        help="Output combined ratings CSV",
    )
    agg.add_argument(
        "--output-summary-csv",
        required=True,
        help="Output aggregate summary CSV",
    )
    agg.add_argument(
        "--output-summary-md",
        required=True,
        help="Output aggregate summary Markdown",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "prepare":
        return _prepare(args)
    return _aggregate(args)


if __name__ == "__main__":
    raise SystemExit(main())
