from argparse import ArgumentParser
from datetime import datetime, timezone
from json import dump
from pathlib import Path

from coverage import Coverage
from coverage.cmdline import FAIL_UNDER
from coverage.results import should_fail_under

_precision = 1


def report_n_get_total_coverage() -> float:
    cov = Coverage()
    cov.load()
    return cov.report(show_missing=True, precision=_precision)


def write_stats(workflow: str, run_id: int, total_coverage: float):
    p = Path(".") / ".github" / ".stats" / f".{workflow}.latest.json"
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)

    obj = {
        "run_id": run_id,
        "date_utc": now.isoformat(),
        "coverage_total": total_coverage,
    }

    with p.open("w") as f:
        dump(obj, fp=f)

    print(f"Wrote new stats to '{p}'.")


def rounded_coverage(total: float, min_cov: float) -> float:
    if (min_cov != 100.0) or (total == 100.0):
        return round(total, ndigits=_precision)

    for ndigits in range(_precision, 6):
        if (rd := round(total, ndigits=ndigits)) < min_cov:
            return rd

    return total


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("--workflow", type=str, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--min-coverage", type=float, required=True)

    args = parser.parse_args()

    total_cov = report_n_get_total_coverage()
    rounded_cov = rounded_coverage(total=total_cov, min_cov=args.min_coverage)

    write_stats(workflow=args.workflow, run_id=args.run_id, total_coverage=rounded_cov)

    if should_fail_under(total_cov, args.min_coverage, _precision):
        print(
            f"FAILURE: Coverage total of {rounded_cov}% is less than the required"
            f" minimum of {args.min_coverage}%."
        )
        raise SystemExit(FAIL_UNDER)
