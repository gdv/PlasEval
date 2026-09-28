#!/usr/bin/env bash

pred_idx=(
    0
    1
    0
    1
    2
    1
)

gt_idx=(
    1
    0
    0
    1
    2
    2
)

n_tests=${#pred_idx[@]}

if [ $n_tests -ne ${#gt_idx[@]} ]; then
    echo "Error: expected the same number of tests, found $n_tests and ${#gt_idx[@]}."
    exit 1
fi

input_dir=tests/artifacts/inputs
output_dir=tests/eval/artifacts/outputs

for i in $(seq 0 $(($n_tests - 1))); do
    pred_tsv=$input_dir/test_bins_${pred_idx[$i]}.tsv
    gt_tsv=$input_dir/test_bins_${gt_idx[$i]}.tsv

    out_prefix=test_${pred_idx[$i]}v${gt_idx[$i]}
    out_tsv=$output_dir/$out_prefix.tsv
    out_log=$output_dir/$out_prefix.log

    uv run plaseval eval --pred $pred_tsv --gt $gt_tsv --out $out_tsv --log $out_log
done
