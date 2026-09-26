"""Use case and entry point of the "eval" mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from plaseval.eval.domain.services import evaluate_bins
from plaseval.eval.infra.bins_repository import PlasevalBinsRepository
from plaseval.eval.infra.log_publisher import LoggingPublisher
from plaseval.eval.infra.tsv_publisher import TsvPublisher
from plaseval.utils import check_file, create_directories

if TYPE_CHECKING:
    from pathlib import Path

    from plaseval.eval.adapters import BinsRepository, EvaluationPublisher
    from plaseval.eval.domain.scores import Evaluation


@dataclass(frozen=True)
class EvaluateBins:
    """Use case of the "eval" mode."""

    repository: BinsRepository
    publishers: tuple[EvaluationPublisher, ...]

    def execute(
        self,
        gt_file: Path,
        pred_file: Path,
        min_contig_length: int,
    ) -> Evaluation:
        """Execute the use case of the "eval" mode."""
        ground_truth, predictions = self.repository.load(
            gt_file,
            pred_file,
            min_contig_length,
        )
        evaluation = evaluate_bins(ground_truth, predictions)
        for publisher in self.publishers:
            publisher.publish(evaluation)
        return evaluation


def eval_mode(
    pred_tsv: Path,
    gt_tsv: Path,
    min_contig_length: int,
    eval_file: Path,
    log_file: Path,
) -> None:
    """Compute "eval" evaluation mode (composition root)."""
    for in_file in (pred_tsv, gt_tsv):
        check_file(in_file)

    create_directories([eval_file.parent, log_file.parent])

    EvaluateBins(
        repository=PlasevalBinsRepository(),
        publishers=(LoggingPublisher(), TsvPublisher(eval_file)),
    ).execute(gt_tsv, pred_tsv, min_contig_length)
