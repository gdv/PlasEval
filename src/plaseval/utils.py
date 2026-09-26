"""Handling errors."""

import logging
import sys
from pathlib import Path

import typer

_LOGGER = logging.getLogger(__name__)


def check_file(in_file: Path, msg: str = "FILE") -> None:
    """Check if file exists and is not empty."""
    if not in_file.exists():
        _err_msg = f"File {in_file} does not exist"
        _LOGGER.critical(_err_msg)
        print_err(_err_msg)
        raise typer.Exit(1)

    if not in_file.is_file():
        _err_msg = f"Object {in_file} is not a file"
        _LOGGER.critical(_err_msg)
        print_err(_err_msg)
        raise typer.Exit(1)

    if in_file.stat().st_size == 0:
        _warn_msg = f"{msg}\t{in_file}: is empty"
        _LOGGER.warning(_warn_msg)
        print_warning(_warn_msg)


# ==================================================================================== #
#                                   STANDARD OUTPUTS                                   #
# ==================================================================================== #


def print_err(err_msg: str) -> None:
    """Print error message."""
    print(f"ERROR\t{err_msg}", file=sys.stderr)  # noqa: T201


def print_warning(warn_msg: str) -> None:
    """Print warning message."""
    print(f"WARNING\t{warn_msg}", file=sys.stderr)  # noqa: T201


# ==================================================================================== #
#                                        LOGGING                                       #
# ==================================================================================== #
def init_logging(log_file: Path) -> None:
    """Initialize logging."""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        filemode="w",
        level=logging.INFO,
        format="%(name)s - %(levelname)s - %(message)s",
    )


# ==================================================================================== #
#                                          IO                                          #
# ==================================================================================== #
def create_directories(in_dir_list: list[Path]) -> None:
    """Create directories."""
    for in_dir in in_dir_list:
        in_dir.mkdir(parents=True, exist_ok=True)
