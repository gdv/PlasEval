"""Edge cases: empty ground truth and/or empty prediction."""

from __future__ import annotations

import pytest

from plaseval.eval.domain.model import (
    Bin,
    BinCollection,
    BinID,
    Contig,
    ContigID,
)
from plaseval.eval.domain.scores import ScorePair, Statistic
from plaseval.eval.domain.services import evaluate_bins

ZERO = ScorePair(unweighted=0.0, weighted=0.0)
ONE = ScorePair(unweighted=1.0, weighted=1.0)


def _collection(*bins: tuple[str, tuple[str, ...]]) -> BinCollection:
    return BinCollection(
        tuple(
            Bin(BinID(bin_id), tuple(Contig(ContigID(c), 100) for c in contigs))
            for bin_id, contigs in bins
        ),
    )


EMPTY = _collection()
NON_EMPTY = _collection(("B1", ("c1", "c2")), ("B2", ("c3",)))


def _scores(gt: BinCollection, pred: BinCollection) -> dict[Statistic, ScorePair]:
    evaluation = evaluate_bins(gt, pred)
    return {o.statistic: o.scores for o in evaluation.overall_scores()}


@pytest.mark.parametrize(
    ("gt", "pred", "precision", "recall", "f1"),
    [
        pytest.param(EMPTY, NON_EMPTY, ZERO, ONE, ZERO, id="empty-gt"),
        pytest.param(NON_EMPTY, EMPTY, ONE, ZERO, ZERO, id="empty-pred"),
        pytest.param(EMPTY, EMPTY, ONE, ONE, ONE, id="both-empty"),
        pytest.param(NON_EMPTY, NON_EMPTY, ONE, ONE, ONE, id="identical"),
    ],
)
def test_overall_scores(
    gt: BinCollection,
    pred: BinCollection,
    precision: ScorePair,
    recall: ScorePair,
    f1: ScorePair,
) -> None:
    scores = _scores(gt, pred)
    assert scores[Statistic.PRECISION] == precision
    assert scores[Statistic.RECALL] == recall
    assert scores[Statistic.F1] == f1
