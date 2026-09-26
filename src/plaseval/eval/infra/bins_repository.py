"""Anti-corruption layer between plaseval.bins and the domain model."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from plaseval.bins import BinMap, ContigLengthMap, read_gt_and_pred_bins
from plaseval.eval.adapters import BinsRepository
from plaseval.eval.domain.model import Bin, BinCollection, BinID, Contig, ContigID

if TYPE_CHECKING:
    from pathlib import Path


@final
class PlasevalBinsRepository(BinsRepository):
    """Load bins from Plaseval format files."""

    def load(
        self,
        gt_file: Path,
        pred_file: Path,
        min_contig_length: int,
    ) -> tuple[BinCollection, BinCollection]:
        """Return (ground truth bins, predicted bins)."""
        gt_bins, pred_bins, ctg_lengths = read_gt_and_pred_bins(
            gt_file,
            pred_file,
            min_contig_length,
        )
        return (
            self._to_collection(gt_bins, ctg_lengths),
            self._to_collection(pred_bins, ctg_lengths),
        )

    @staticmethod
    def _to_collection(bin_map: BinMap, ctg_lengths: ContigLengthMap) -> BinCollection:
        return BinCollection(
            tuple(
                Bin(
                    id=BinID(bin_id),
                    contigs=tuple(
                        Contig(ContigID(ctg), ctg_lengths[ctg]) for ctg in ctgs
                    ),
                )
                for bin_id, ctgs in bin_map.items()
            ),
        )
