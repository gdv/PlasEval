"""Domain services: best-match search and evaluation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from plaseval.eval.domain.scores import (
    BinEvalStats,
    EvalStat,
    Evaluation,
    Statistic,
    StatisticReport,
)

if TYPE_CHECKING:
    from plaseval.eval.domain.model import Bin, BinCollection


def find_best_match(subject: Bin, opposites: BinCollection) -> BinEvalStats:
    """Find the opposite bin that covers most of `subject`'s contigs."""
    totals = subject.totals()
    unweighted = EvalStat.unmatched(totals.count)
    weighted = EvalStat.unmatched(totals.length)
    for opposite in opposites:
        common = subject.common_totals(opposite)
        unweighted = unweighted.challenged_by(opposite.id, common.count)
        weighted = weighted.challenged_by(opposite.id, common.length)
    return BinEvalStats(subject.id, unweighted, weighted)


def evaluate_bins(
    ground_truth: BinCollection,
    predictions: BinCollection,
) -> Evaluation:
    """Recall: ground-truth bins vs predictions. Precision: the reverse."""
    recalls = StatisticReport(
        Statistic.RECALL,
        tuple(find_best_match(bin_, predictions) for bin_ in ground_truth),
    )
    precisions = StatisticReport(
        Statistic.PRECISION,
        tuple(find_best_match(bin_, ground_truth) for bin_ in predictions),
    )
    return Evaluation(precisions=precisions, recalls=recalls)
