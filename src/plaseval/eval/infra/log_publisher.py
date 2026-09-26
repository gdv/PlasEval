"""Log an Evaluation in the legacy human-readable format."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plaseval.eval.domain.scores import (
        BinEvalStats,
        Evaluation,
        OverallScore,
        StatisticReport,
    )

_LOGGER = logging.getLogger(__name__)

FIELD_SEPARATOR = "\t"
BLANK_LINE = ""
FINAL_TITLE = "#Final statistics (Unwtd and Wtd)"
FINAL_SECTION = ">Overall details"
FINAL_HEADER = FIELD_SEPARATOR.join(
    ("#Overall_statistic", "Unwtd_statistic", "Wtd_statistic"),
)


@dataclass(frozen=True)
class _Section:
    """Log section."""

    title: str
    section: str
    header: str


_PRECISION_SECTION = _Section(
    title="#Precision: Proportion of correctly identified contigs for each prediction",
    section=">Precision details",
    header=FIELD_SEPARATOR.join(
        (
            "#Predicted_bin",
            "Unwtd_Precision",
            "Unwtd_Reference_plasmid",
            "Wtd_Precision",
            "Wtd_Reference_plasmid",
        ),
    ),
)
_RECALL_SECTION = _Section(
    title="#Recall: Proportion of correctly identified contigs for each reference",
    section=">Recall details",
    header=FIELD_SEPARATOR.join(
        (
            "#Reference_plasmid",
            "Unwtd_Recall",
            "Unwtd_Predicted_bin",
            "Wtd_Recall",
            "Wtd_Predicted_bin",
        ),
    ),
)


def _row(*fields: object) -> str:
    return FIELD_SEPARATOR.join(str(field) for field in fields)


class LoggingPublisher:
    """Log an Evaluation in the legacy human-readable format."""

    def publish(self, evaluation: Evaluation) -> None:
        """Log an Evaluation in the legacy human-readable format."""
        self._log_report(evaluation.precisions, _PRECISION_SECTION)
        self._log_report(evaluation.recalls, _RECALL_SECTION)
        _LOGGER.info(FINAL_TITLE)
        _LOGGER.info(FINAL_SECTION)
        _LOGGER.info(FINAL_HEADER)
        for overall in evaluation.overall_scores():
            _LOGGER.info(self._overall_row(overall))

    def _log_report(self, report: StatisticReport, section: _Section) -> None:
        _LOGGER.info(section.title)
        _LOGGER.info(section.section)
        _LOGGER.info(section.header)
        for stats in report.per_bin:
            _LOGGER.info(self._bin_row(stats))
        _LOGGER.info(BLANK_LINE)

    @staticmethod
    def _bin_row(stats: BinEvalStats) -> str:
        return _row(
            stats.bin_id,
            stats.unweighted.reported_value(),
            stats.unweighted.best_bin,
            stats.weighted.reported_value(),
            stats.weighted.best_bin,
        )

    @staticmethod
    def _overall_row(overall: OverallScore) -> str:
        return _row(
            overall.statistic,
            overall.scores.unweighted,
            overall.scores.weighted,
        )
