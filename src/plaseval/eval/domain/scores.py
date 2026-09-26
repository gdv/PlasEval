"""Value objects describing the scores produced by an evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from plaseval.eval.domain.model import BinID

DEFAULT_REPORTED_DECIMALS = 4
PERFECT_SCORE = 1.0
ZERO_SCORE = 0.0


def round_score(
    value: float,
    reported_decimal: int = DEFAULT_REPORTED_DECIMALS,
) -> float:
    """Round `value` to `REPORTED_DECIMALS` decimal places."""
    return round(value, reported_decimal)


def safe_ratio(numerator: float, denominator: float, undefined: float) -> float:
    """Divide `numerator` by `denominator` if non-zero, otherwise return `undefined`."""
    return numerator / denominator if denominator else undefined


class Statistic(StrEnum):
    """Measures of performance."""

    PRECISION = "Precision"
    RECALL = "Recall"
    F1 = "F1"


@dataclass(frozen=True)
class EvalStat:
    """Best match found for a bin, on one measure (contig count or length)."""

    value: float
    best_bin: BinID | None
    common: int
    total: int

    @classmethod
    def unmatched(cls, total: int) -> EvalStat:
        """Return evaluation statistics when no match is found."""
        return cls(value=0.0, best_bin=None, common=0, total=total)

    def challenged_by(self, candidate: BinID, common: int) -> EvalStat:
        """Return the better of `self` and the candidate (ties keep `self`).

        A zero total (nothing admitted by the length threshold) leaves the
        candidate value equal to `self.value`, so `self` is kept.
        """
        candidate_value = safe_ratio(common, self.total, undefined=self.value)
        if candidate_value > self.value:
            return EvalStat(candidate_value, candidate, common, self.total)
        return self

    def reported_value(self) -> float:
        """Return the reported formatted value."""
        return round_score(self.value)


@dataclass(frozen=True)
class BinEvalStats:
    """Evaluation statistics for a bin."""

    bin_id: BinID
    unweighted: EvalStat
    weighted: EvalStat


@dataclass(frozen=True)
class ScorePair:
    """The same score computed on contig counts and on contig lengths."""

    unweighted: float
    weighted: float

    @classmethod
    def undefined(cls) -> ScorePair:
        """Score of a statistic with nothing to evaluate (vacuously perfect)."""
        return cls(unweighted=PERFECT_SCORE, weighted=PERFECT_SCORE)

    def f1_with(self, other: ScorePair) -> ScorePair:
        """F1 of `self` (precision) and `other` (recall), on rounded inputs."""
        return ScorePair(
            unweighted=_harmonic_mean(self.unweighted, other.unweighted),
            weighted=_harmonic_mean(self.weighted, other.weighted),
        )


def _harmonic_mean(first: float, second: float) -> float:
    return round_score(safe_ratio(2 * first * second, first + second, ZERO_SCORE))


def _pooled_ratio(stats: Sequence[EvalStat]) -> float:
    common = sum(stat.common for stat in stats)
    total = sum(stat.total for stat in stats)
    return round_score(safe_ratio(common, total, ZERO_SCORE))


@dataclass(frozen=True)
class StatisticReport:
    """Per-bin statistics of a single statistic (precision or recall)."""

    statistic: Statistic
    per_bin: tuple[BinEvalStats, ...]

    def overall(self) -> ScorePair:
        """Pooled score; undefined (so perfect) when there are no bins to score.

        Recall is undefined when the ground truth is empty, and precision is
        undefined when the prediction is empty.
        """
        if not self.per_bin:
            return ScorePair.undefined()
        return ScorePair(
            unweighted=_pooled_ratio([s.unweighted for s in self.per_bin]),
            weighted=_pooled_ratio([s.weighted for s in self.per_bin]),
        )


@dataclass(frozen=True)
class OverallScore:
    """Score for a single statistic."""

    statistic: Statistic
    scores: ScorePair


@dataclass(frozen=True)
class Evaluation:
    """Aggregate root: the full result of comparing predictions to ground truth."""

    precisions: StatisticReport
    recalls: StatisticReport

    def overall_scores(self) -> tuple[OverallScore, ...]:
        """Precision, recall, and F1 scores."""
        precision = self.precisions.overall()
        recall = self.recalls.overall()
        return (
            OverallScore(Statistic.PRECISION, precision),
            OverallScore(Statistic.RECALL, recall),
            OverallScore(Statistic.F1, precision.f1_with(recall)),
        )
