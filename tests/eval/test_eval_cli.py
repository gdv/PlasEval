"""Pytest suite for the `plaseval eval` CLI.

Layout (relative to this file, adjust ARTIFACTS_ROOT below if needed):

    tests/
      artifacts/
        inputs/
          test_bins_0.tsv
          test_bins_1.tsv
        ...
      eval/
        artifacts/
          outputs/
            test_0v0.out
            test_0v0.log
            test_1v1_alpha_0.out
            test_1v1_alpha_0.log
            ...

Only a subset of possible (pred, gt) combinations are exercised -- the exact
couples to test are declared explicitly in TEST_CASES below rather than
discovered by globbing, since the artifacts directory may contain files that
aren't meant to be run.

The CLI is invoked in-process via typer.testing.CliRunner against
plaseval.cli.APP rather than shelled out to as a subprocess, so that
coverage tools correctly attribute execution to the plaseval source.
"""

import math
import os
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner, Result

from plaseval.cli import APP

# ==================================================================================== #
#                                     CONFIGURATION                                    #
# ==================================================================================== #
ARTIFACTS_ROOT = Path(__file__).parent.parent / "artifacts"
COMP_ARTIFACTS = Path(__file__).parent / "artifacts"
INPUT_DIR = ARTIFACTS_ROOT / "inputs"
OUTPUT_DIR = COMP_ARTIFACTS / "outputs"

PLASEVAL_BIN = os.environ.get("PLASEVAL_BIN", "plaseval")

# Numeric columns are compared with a relative tolerance rather than an exact
# string match, since the tool's floating-point formatting can differ in the
# last few significant digits between runs/platforms (e.g. 0.206712673421253
# vs 0.20671267342125307) without the underlying value being meaningfully
# different. Override via env vars if needed:
#   PLASEVAL_NUMERIC_REL_TOLERANCE - relative tolerance (default 1e-6)
#   PLASEVAL_NUMERIC_ABS_TOLERANCE - absolute tolerance floor for
#                                    near-zero values (default 1e-9)
NUMERIC_REL_TOLERANCE = float(os.environ.get("PLASEVAL_NUMERIC_REL_TOLERANCE", "1e-6"))
NUMERIC_ABS_TOLERANCE = float(os.environ.get("PLASEVAL_NUMERIC_ABS_TOLERANCE", "1e-9"))


# ------------------------------------------------------------------------------------ #
# The (gt, pred) couples to test.
#
# Each entry is (gt_idx, pred_idx)
#
# The expected output/log filename prefix is derived as:
#   test_<pred>v<gt>
# ------------------------------------------------------------------------------------ #
TEST_CASES = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
    (1, 1),
    (1, 2),
    (1, 5),
    (1, 6),
    (1, 7),
    (1, 8),
    (1, 9),
    (1, 10),
    (1, 11),
    (2, 2),
    (2, 2),
    (2, 11),
    (2, 13),
    (3, 4),
    (7, 8),
    (7, 12),
    (8, 7),
    (9, 14),
]


def _prefix_for(gt_idx: int, pred_idx: int) -> str:
    return f"test_{pred_idx}v{gt_idx}"


def build_cases() -> list[tuple[Path, Path, Path, Path]]:
    """Build (gt, pred, alpha) cases from TEST_CASES."""
    cases = []
    for pred_idx, gt_idx in TEST_CASES:
        prefix = _prefix_for(gt_idx, pred_idx)
        pred_path = INPUT_DIR / f"test_bins_{pred_idx}.tsv"
        gt_path = INPUT_DIR / f"test_bins_{gt_idx}.tsv"
        expected_out = OUTPUT_DIR / f"{prefix}.tsv"
        expected_log = OUTPUT_DIR / f"{prefix}.log"
        cases.append(
            (
                pred_path,
                gt_path,
                expected_out,
                expected_log,
            ),
        )
    return cases


CASES = build_cases()


# ==================================================================================== #
#                                       FIXTURES                                       #
# ==================================================================================== #
@pytest.fixture(scope="session", autouse=True)
def ensure_plaseval_available() -> None:
    if shutil.which(PLASEVAL_BIN) is None:
        pytest.skip(
            f"'{PLASEVAL_BIN}' not found on PATH; set PLASEVAL_BIN to its "
            f"location or install it before running these tests.",
        )


@pytest.fixture(scope="session", autouse=True)
def ensure_test_data_present() -> None:
    if not INPUT_DIR.is_dir() or not OUTPUT_DIR.is_dir():
        pytest.skip(f"Test data not found under {ARTIFACTS_ROOT}")


@pytest.fixture(scope="session")
def runner() -> CliRunner:
    return CliRunner()


# ==================================================================================== #
#                                        HELPERS                                       #
# ==================================================================================== #
def run_plaseval_eval(
    runner: CliRunner,
    gt_path: Path,
    pred_path: Path,
    out_path: Path,
    log_path: Path,
) -> Result:
    args = [
        "eval",
        "--gt",
        str(gt_path),
        "--pred",
        str(pred_path),
        "--out",
        str(out_path),
        "--log",
        str(log_path),
    ]
    return runner.invoke(APP, args)


def _is_number(token: str) -> bool:
    try:
        float(token)
    except ValueError:
        return False
    else:
        return True


def compare_with_tolerance(
    actual: str,
    expected: str,
    rel_tolerance: float = NUMERIC_REL_TOLERANCE,
    abs_tolerance: float = NUMERIC_ABS_TOLERANCE,
) -> None:
    """Compare numerics.

    Line-by-line, tab-split comparison; numeric tokens are compared with
    `tolerance`, everything else must match exactly.
    """
    actual_lines = actual.splitlines()
    expected_lines = expected.splitlines()

    assert len(actual_lines) == len(expected_lines), (
        f"line count mismatch: actual={len(actual_lines)} "
        f"expected={len(expected_lines)}"
    )

    for lineno, (a_line, e_line) in enumerate(
        zip(actual_lines, expected_lines, strict=True),
        start=1,
    ):
        a_tokens = a_line.split("\t")
        e_tokens = e_line.split("\t")
        assert len(a_tokens) == len(e_tokens), (
            f"line {lineno}: column count mismatch\n  actual:   {a_line!r}\n"
            f"  expected: {e_line!r}"
        )
        for col, (a_tok, e_tok) in enumerate(
            zip(a_tokens, e_tokens, strict=True),
            start=1,
        ):
            if _is_number(a_tok) and _is_number(e_tok):
                assert math.isclose(
                    float(a_tok),
                    float(e_tok),
                    rel_tol=rel_tolerance,
                    abs_tol=abs_tolerance,
                ), (
                    f"line {lineno}, col {col}: {a_tok} != {e_tok} "
                    f"(rel_tol={rel_tolerance}, abs_tol={abs_tolerance})"
                )
            else:
                assert a_tok == e_tok, (
                    f"line {lineno}, col {col}: {a_tok!r} != {e_tok!r}"
                )


# ==================================================================================== #
#                                         TESTS                                        #
# ==================================================================================== #
@pytest.mark.parametrize(
    ("pred_path", "gt_path", "expected_out", "expected_log"),
    CASES,
)
def test_eval_matches_expected_output(  # noqa: PLR0913, PLR0917
    runner: CliRunner,
    pred_path: Path,
    gt_path: Path,
    expected_out: Path,
    expected_log: Path,
    tmp_path: Path,
) -> None:
    assert gt_path.exists(), f"missing gt input file: {gt_path}"
    assert pred_path.exists(), f"missing pred input file: {pred_path}"
    assert expected_out.exists(), f"missing expected output file: {expected_out}"

    out_path = tmp_path / "result.tsv"
    log_path = tmp_path / "result.log"

    result = run_plaseval_eval(runner, gt_path, pred_path, out_path, log_path)

    log_contents = (
        log_path.read_text() if log_path.exists() else "<log file not created>"
    )
    assert result.exit_code == 0, (
        f"plaseval eval exited with {result.exit_code}\n"
        f"--- output ---\n{result.output}\n"
        f"--- exception ---\n{result.exception!r}\n"
        f"--- log ---\n{log_contents}"
    )

    assert out_path.exists(), (
        f"expected output file was not created at {out_path}\n"
        f"--- output ---\n{result.output}\n"
        f"--- log ---\n{log_contents}"
    )

    actual_text = out_path.read_text()
    expected_text = expected_out.read_text()

    compare_with_tolerance(actual_text, expected_text)


def test_missing_gt_file_fails_gracefully(runner: CliRunner, tmp_path: Path) -> None:
    """The CLI should fail cleanly (non-zero exit) on a missing --gt file.

    Rather than crashing without a useful message.
    """
    if not CASES:
        pytest.skip("no reference input files available to build this case")

    missing_gt = INPUT_DIR / "does_not_exist_bin.tsv"
    pred_path, _, _, _ = CASES[0]
    out_path = tmp_path / "result.tsv"
    log_path = tmp_path / "result.log"

    result = run_plaseval_eval(runner, missing_gt, pred_path, out_path, log_path)

    assert result.exit_code != 0, "expected a non-zero exit code for missing --gt file"
