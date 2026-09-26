"""Adapters."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

    from plaseval.eval.domain.model import BinCollection
    from plaseval.eval.domain.scores import Evaluation


class BinsRepository(Protocol):
    """Bin repository protocol."""

    def load(
        self,
        gt_file: Path,
        pred_file: Path,
        min_contig_length: int,
    ) -> tuple[BinCollection, BinCollection]:
        """Return (ground truth bins, predicted bins)."""


class EvaluationPublisher(Protocol):
    """Evaluation publisher protocol."""

    def publish(self, evaluation: Evaluation) -> None:
        """Publish an Evaluation."""
