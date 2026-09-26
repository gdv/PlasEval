"""Dissimilarity between plasmid sets."""

from pathlib import Path
from typing import Literal

import pandas as pd
from bidict import bidict

from plaseval.comp.compare_sets import run_compare_plasmids
from plaseval.utils import check_file, create_directories

CollectionRole = Literal["L", "R"]


def get_plasmid_details(
    contigs_dict: dict,
    filename: Path,
    side: CollectionRole,
    min_len: int,
) -> bidict:
    """Get plasmid details.

    Arguments
    ---------
    contigs_dict:
        Key: contig (str)
        Value: Nested dictionary:
            length (int)
            L_copies/R_copies (list of contig copies in plasmid set)
    path to input file
    side ('L' or 'R')

    Returns
    -------
    plasmids: list of list of contig ids
    updated contigs_dict
    plasmids_keys: bidict of plasmid indices <-> plasmid names/ids
    """
    plasmids: list[list[str]] = []
    plasmids_keys: bidict[str, int] = bidict()
    plasmid_idx = 0
    pls_ctg_df = pd.read_csv(filename, sep="\t")

    for row in pls_ctg_df.itertuples(index=False, name=None):
        plasmid, contig, length = (
            f"{side}_{row[0]}",
            str(row[1]),
            int(row[2]),
        )
        if length >= min_len:
            if contig not in contigs_dict:
                contigs_dict[contig] = {
                    "length": length,
                    "L_copies": [],
                    "R_copies": [],
                }
            if plasmid not in plasmids_keys:
                plasmids_keys[plasmid] = plasmid_idx
                plasmids.append([])
                plasmid_idx += 1
            pls_index = plasmids_keys[plasmid]
            plasmids[pls_index].append(contig)
            contigs_dict[contig][f"{side}_copies"].append(
                [contig, pls_index, len(plasmids[pls_index])],
            )
    return plasmids_keys


def comp_mode(
    pred_bins_tsv: Path,
    gt_bins_tsv: Path,
    p: float,
    min_len: int,
    output_file: Path,
    log_file: Path,
):
    """Compute "comp" evaluation mode.

    * Reads input files
    * Initializes plasmid dicts and stores plasmid bins for both sides
    * Calls compare_sets function to compute dissimilarity between the two sides
    """
    for in_file in [pred_bins_tsv, gt_bins_tsv]:
        check_file(in_file)

    output_dir = output_file.parent
    log_dir = log_file.parent
    create_directories([output_dir, log_dir])

    with output_file.open("w") as results_file:
        # Reading data and saving it to a dictionary with plasmids as keys
        # and a nested dictionary of contigs as values
        contigs_dict = {}
        pls_ids_dict = {"L": {}, "R": {}}
        pls_ids_dict["L"] = get_plasmid_details(
            contigs_dict,
            pred_bins_tsv,
            "L",
            min_len,
        )
        pls_ids_dict["R"] = get_plasmid_details(
            contigs_dict,
            gt_bins_tsv,
            "R",
            min_len,
        )
        run_compare_plasmids(
            contigs_dict,
            pls_ids_dict,
            p,
            results_file,
        )
