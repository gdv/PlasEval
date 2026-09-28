# Description of test cases

The folder `tests/artifacts/inputs` contains several "test" plasmid bins.
Pairs of these test bins have been to compared against each other to test different functionalities of PlasEval.
Given below is the list of comparisons made along with the significance of each comparison.

| Prediction | Ground truth | Particularity                                            | Expected                                 |
| ---------- | ------------ | -------------------------------------------------------- | ---------------------------------------- |
| `0`        | `1`          | Empty prediction                                         | Missing cost 1 so dissimilarity score 1  |
| `1`        | `0`          | Empty ground truth                                       | Extra cost 1 so dissimilarity score 1    |
| `0`        | `0`          | Both collections are empty                               | Dissimilarity score 0                    |
| `1`        | `1`          | Same bins                                                | Dissimilarity score 0                    |
| `1`        | `1`          | Same bins with $\alpha = 0$                              | Dissimilarity score 0                    |
| `2`        | `2`          | Same bins with copies                                    | Dissimilarity score 0                    |
| `2`        | `2`          | Same bins with copies and $\alpha = 0$                   | Dissimilarity score 0                    |
| `1`        | `2`          | Same bins with extra copies (in `2`)                     | Only positive missing cost               |
| `3`        | `4`          | Same bins with extra copies *in the same bins* (in both) | Positive extra and missing costs         |
| `1`        | `5`          | Same bins with extra copies *in the same bin* (in `5`)   | Only positive missing cost               |
| `1`        | `6`          | Completely different bins                                | Dissimilarity score 1                    |
| `1`        | `7`          | Simple split                                             | Only cut cost                            |
| `1`        | `8`          | Simple join                                              | Only join cost                           |
| `1`        | `9`          | Simple split + missing contigs                           | Cut and missing costs                    |
| `1`        | `10`         | Simple split + extra contigs                             | Cut and extra costs                      |
| `1`        | `11`         | Splits + missing copies                                  | Cut and missing costs                    |
| `7`        | `8`          | Join into multiple bins.                                 | Only positive join cost                  |
| `8`        | `7`          | Split into multiple bins.                                | Only positive cut cost                   |
| `7`        | `12`         | Multiple splits and joins.                               | Only positive cut and join costs         |
| `9`        | `14`         | Multiple joins with extra contigs on both sides.         | Positive join, missing and extra costs   |
| `2`        | `11`         | Extra copies on both side                                | Illustrates branch-n-bound functionality |
| `2`        | `13`         | Extra copies on both side                                | Illustrates branch-n-bound functionality |

> [!NOTE]
> Tests `2 vs 11` and `2 vs 13` were designed to test cases with splits and joins with extra copies on both sides.
> However, they ended up without any splits (both tests `2 vs 11`, `2 vs 13`) or joins (test `2 vs 11`).
> Interestingly, the algorithm matched the contig copies in such a way that the splits / joins were not required to transform one set of bins into the other.
