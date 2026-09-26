"""PlasEval (Plasmids Evaluator), a method for evaluating the predictions from plasmid binning tools.

Two modes of PlasEval:
- eval: evaluates plasmid bins against a set of ground truth bins to provide precision-recall statistics
- compare: compares two sets of plasmid bins to quantify the dissimilarity between the two given sets
"""  # noqa: E501

from plaseval.cli import APP


def main() -> None:
    """Compute the main CLI entry point."""
    APP()
