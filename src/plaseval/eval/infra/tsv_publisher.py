"""Write an Evaluation to the TSV evaluation file."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    from pathlib import Path

    from plaseval.eval.domain.model import BinID
    from plaseval.eval.domain.scores import (
        BinEvalStats,
        Evaluation,
        OverallScore,
        Statistic,
    )


class Level(StrEnum):
    """Header levels."""

    INDIVIDUAL = "Individual"
    OVERALL = "Overall"


class Column(StrEnum):
    """Header columns, in file order."""

    LEVEL = "Level"
    STATISTIC = "Statistic"
    BIN = "Bin"
    UNWTD_STAT = "Unwtd_Stat"
    UNWTD_MATCH = "Unwtd_Match"
    WTD_STAT = "Wtd_Stat"
    WTD_MATCH = "Wtd_Match"


class TsvPublisher:
    """Write an Evaluation to a TSV file."""

    FIELD_SEPARATOR: ClassVar = "\t"
    LINE_END: ClassVar = "\n"

    @classmethod
    def _header_line(cls) -> str:
        return (
            cls.FIELD_SEPARATOR.join(str(column.value) for column in Column)
            + cls.LINE_END
        )

    @classmethod
    def _line(  # noqa: PLR0913, PLR0917
        cls,
        level: Level,
        statistic: Statistic,
        bin_id: BinID | None,
        unweighted_value: float,
        unweighted_match: BinID | None,
        weighted_value: float,
        weighted_match: BinID | None,
    ) -> str:
        return (
            cls.FIELD_SEPARATOR.join(
                map(
                    str,
                    (
                        level,
                        statistic,
                        bin_id,
                        unweighted_value,
                        unweighted_match,
                        weighted_value,
                        weighted_match,
                    ),
                ),
            )
            + cls.LINE_END
        )

    def __init__(self, path: Path) -> None:
        self._path = path

    def publish(self, evaluation: Evaluation) -> None:
        """Write an Evaluation to a TSV file."""
        with self._path.open("w") as out:
            out.write(self._header_line())

            for report in (evaluation.precisions, evaluation.recalls):
                for stats in report.per_bin:
                    out.write(self._individual_line(report.statistic, stats))

            for overall in evaluation.overall_scores():
                out.write(self._overall_line(overall))

    def _individual_line(self, statistic: Statistic, stats: BinEvalStats) -> str:
        return self._line(
            Level.INDIVIDUAL,
            statistic,
            stats.bin_id,
            stats.unweighted.reported_value(),
            stats.unweighted.best_bin,
            stats.weighted.reported_value(),
            stats.weighted.best_bin,
        )

    def _overall_line(self, overall: OverallScore) -> str:
        return self._line(
            Level.OVERALL,
            overall.statistic,
            None,
            overall.scores.unweighted,
            None,
            overall.scores.weighted,
            None,
        )
