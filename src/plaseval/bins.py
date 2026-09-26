"""Bins."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

BinMap = dict[str, list[str]]
ContigLengthMap = dict[str, int]


def read_bin_data(bins_file: Path, min_length: int) -> tuple[BinMap, ContigLengthMap]:
    """Read bins and contigs data.

    Argument
    --------
    bins_file: Path
        Path to file containing bins details
    min_length: int
        Minimum length of contigs

    Returns
    -------
    BinMap
        Map bin ID to list of contig IDs
    ContigLengthMap
        Map contig ID to their length
    """
    bin_map = BinMap()
    ctg_len_map = ContigLengthMap()

    pls_ctg_df = pd.read_csv(bins_file, sep="\t")
    for row in pls_ctg_df.itertuples(index=False, name=None):
        plasmid, contig, length = str(row[0]), str(row[1]), int(row[2])

        if length < min_length:
            continue

        ctg_len_map[contig] = length
        if plasmid not in bin_map:
            bin_map[plasmid] = []
        if contig not in set(bin_map[plasmid]):
            bin_map[plasmid].append(contig)

    return bin_map, ctg_len_map


def read_gt_and_pred_bins(
    gt_bins_file: Path,
    pred_bins_file: Path,
    min_length: int,
) -> tuple[BinMap, BinMap, ContigLengthMap]:
    """Read ground truth and prediction bins data.

    Raises
    ------
    ValueError
        If a contig has different lengths in the ground truth and prediction bins

    Arguments
    ---------
    gt_bins_file: Path
        Path to file containing ground truth bins details
    pred_bins_file: Path
        Path to file containing prediction bins details

    Returns
    -------
    gt_bin_map: BinMap
        Map ground truth bin ID to list of contig IDs
    pred_bin_map: BinMap
        Map prediction bin ID to list of contig IDs
    ctg_len_map: ContigLengthMap
        Map contig ID to their length
    """
    gt_bin_map, gt_ctg_len = read_bin_data(gt_bins_file, min_length)
    pred_bin_map, pred_ctg_len = read_bin_data(pred_bins_file, min_length)

    for ctg_id in set(gt_ctg_len).intersection(set(pred_ctg_len)):
        gt_len = gt_ctg_len[ctg_id]
        pred_len = pred_ctg_len[ctg_id]
        if gt_len != pred_len:
            _err_msg = (
                f"Contig {ctg_id} has different lengths"
                f" in the ground truth ({gt_len})"
                f" and prediction bins ({pred_len})"
            )
            raise ValueError(_err_msg)

    ctg_len_map = {**gt_ctg_len, **pred_ctg_len}
    return gt_bin_map, pred_bin_map, ctg_len_map
