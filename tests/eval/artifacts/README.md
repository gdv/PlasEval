# Description of test cases

The folder `tests/artifacts/inputs` contains several "test" plasmid bins.
Pairs of these test bins have been to compared against each other to test different functionalities of PlasEval.
Given below is the list of comparisons made along with the significance of each comparison.

By default, if a statistic value is not noted in the `Expected` column, the value equals 1 (perfect).

| Prediction | Ground truth | Particularity                                            | Expected                         |
| ---------- | ------------ | -------------------------------------------------------- | -------------------------------- |
| `0`        | `1`          | Empty prediction                                         | Recall 0, prec 1 so F1 0         |
| `1`        | `0`          | Empty ground truth                                       | Recall 1, prec 0 so F1 0         |
| `0`        | `0`          | Both collections are empty                               | Recall 1, prec 1 so F1 1         |
| `1`        | `1`          | Same bins                                                | Recall 1, prec 1 so F1 1         |
| `2`        | `2`          | Same bins with copies                                    | Recall 1, prec 1 so F1 1         |
| `1`        | `2`          | Same bins with extra copies (in `2`)                     | Recall $< 1$ so F1 $<1$          |
| `3`        | `4`          | Same bins with extra copies *in the same bins* (in both) | Positive extra and missing costs |
| `1`        | `5`          | Same bins with extra copies *in the same bin* (in `5`)   | Recall, prec and F1 1            |
| `1`        | `6`          | Completely different bins                                | Recall, prec and F1 0            |
| `1`        | `7`          | Simple split                                             | Prec and F1 $<1$                 |
| `1`        | `8`          | Simple join                                              | Recall and F1 $<1$               |
| `1`        | `9`          | Simple split + missing contigs                           | Recall, prec and F1 $<1$         |
| `1`        | `10`         | Simple split + extra contigs                             | Prec and F1 $<1$                 |
| `1`        | `11`         | Splits + missing copies                                  | Prec and F1 $<1$                 |
| `7`        | `8`          | Join into multiple bins.                                 | Recall and F1 $<1$               |
| `8`        | `7`          | Split into multiple bins.                                | Prec and F1 $<1$                 |
| `7`        | `12`         | Multiple splits and joins.                               | Recall, prec and F1 $<1$         |
| `9`        | `14`         | Multiple joins with extra contigs on both sides.         | Recall, prec and F1 $<1$         |
| `2`        | `11`         | Extra copies on both side                                | Prec and F1 $<1$                 |
| `2`        | `13`         | Extra copies on both side                                | Recall and F1 $<1$               |
