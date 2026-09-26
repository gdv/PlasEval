"""PlasEval (Plasmids Evaluator), a method for evaluating the predictions from plasmid binning tools.

Two modes of PlasEval:
- eval: evaluates plasmid bins against a set of ground truth bins to provide precision-recall statistics
- compare: compares two sets of plasmid bins to quantify the dissimilarity between the two given sets
"""  # noqa: E501

# Due to typer
# ruff: noqa: PLR0913, PLR0917

from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from plaseval.comp.main import comp_mode
from plaseval.eval.app import eval_mode
from plaseval.utils import init_logging

APP = typer.Typer(
    help=(
        "PlasEval (Plasmids binning Evaluator):"
        " compare two collections of plasmid bins."
    ),
    add_completion=False,
    rich_help_panel="rich",
)


DEFAULT_MIN_CONTIG_LENGTH = 0
DEFAULT_ALPHA = 0.5


class CLISection(StrEnum):
    """CLI section."""

    INPUTS = "Inputs"
    OUTPUTS = "Outputs"
    PARAMETERS = "Parameters"


@APP.command("eval")
def eval_cmd(
    pred_tsv: Annotated[
        Path,
        typer.Option(
            "--pred",
            help="Predicted bins filepath",
            rich_help_panel=CLISection.INPUTS,
        ),
    ],
    gt_tsv: Annotated[
        Path,
        typer.Option(
            "--gt",
            help="Ground truth bins filepath",
            rich_help_panel=CLISection.INPUTS,
        ),
    ],
    out_file: Annotated[
        Path,
        typer.Option(
            "--out",
            help="Path of file contaning the evaluation measures",
            rich_help_panel=CLISection.OUTPUTS,
        ),
    ],
    log_file: Annotated[
        Path,
        typer.Option("--log", help="Log filepath", rich_help_panel=CLISection.OUTPUTS),
    ],
    min_len: Annotated[
        int,
        typer.Option(
            "--min-len",
            help="Minimum length of contigs",
            rich_help_panel=CLISection.PARAMETERS,
        ),
    ] = DEFAULT_MIN_CONTIG_LENGTH,
) -> None:
    """Compute the recall, precision and F1 statistics for plasmid binning."""
    init_logging(log_file)
    eval_mode(pred_tsv, gt_tsv, min_len, out_file, log_file)


@APP.command("comp")
def comp_cmd(
    pred_tsv: Annotated[
        Path,
        typer.Option(
            "--pred",
            help="Predicted bins filepath",
            rich_help_panel=CLISection.INPUTS,
        ),
    ],
    gt_tsv: Annotated[
        Path,
        typer.Option(
            "--gt",
            help="Ground truth bins filepath",
            rich_help_panel=CLISection.INPUTS,
        ),
    ],
    out_file: Annotated[
        Path,
        typer.Option(
            "--out",
            help="Path of file contaning the evaluation measures",
            rich_help_panel=CLISection.OUTPUTS,
        ),
    ],
    log_file: Annotated[
        Path,
        typer.Option("--log", help="Log filepath", rich_help_panel=CLISection.OUTPUTS),
    ],
    alpha: Annotated[
        float,
        typer.Option(
            "--alpha",
            help="Weight exponent alpha",
            rich_help_panel=CLISection.PARAMETERS,
        ),
    ] = DEFAULT_ALPHA,
    min_len: Annotated[
        int,
        typer.Option(
            "--min-len",
            help="Minimum length of contigs",
            rich_help_panel=CLISection.PARAMETERS,
        ),
    ] = DEFAULT_MIN_CONTIG_LENGTH,
) -> None:
    """Compute dissimilarity measure between two collections of plasmid bins."""
    init_logging(log_file)
    comp_mode(pred_tsv, gt_tsv, alpha, min_len, out_file, log_file)
