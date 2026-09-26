"""Core domain model: contigs, bins and the length threshold."""

from __future__ import annotations

from collections.abc import Collection, Iterable, Iterator
from dataclasses import dataclass
from typing import NewType, final

ContigID = NewType("ContigID", str)
BinID = NewType("BinID", str)


@dataclass(frozen=True)
class Contig:
    """A contig with its length."""

    id: ContigID
    length: int


@dataclass(frozen=True)
class ContigTotals:
    """Number of contigs and their cumulative length."""

    count: int
    length: int

    @classmethod
    def of(cls, contigs: Iterable[Contig]) -> ContigTotals:
        """Create totals from an iterable of contigs."""
        lengths = [contig.length for contig in contigs]
        return cls(count=len(lengths), length=sum(lengths))


@dataclass(frozen=True)
class Bin:
    """A bin: an identified, ordered list of contigs."""

    id: BinID
    contigs: tuple[Contig, ...]

    def totals(self) -> ContigTotals:
        """Totals of the contigs of this bin."""
        return ContigTotals.of(self.contigs)

    def common_totals(self, other: Bin) -> ContigTotals:
        """Totals of the (distinct) contigs shared with `other`."""
        shared = set(self.contigs) & set(other.contigs)
        return ContigTotals.of(shared)


@final
@dataclass(frozen=True)
class BinCollection(Collection[Bin]):
    """An ordered collection of bins (ground truth or prediction)."""

    bins: tuple[Bin, ...]

    def __iter__(self) -> Iterator[Bin]:
        """Return an iterator over the bins."""
        return iter(self.bins)

    def __len__(self) -> int:
        """Return the number of bins."""
        return len(self.bins)

    def __contains__(self, bin_id: BinID) -> bool:
        """Return whether the bin is in the collection."""
        return any(bin_id == b.id for b in self.bins)
