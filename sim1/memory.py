import itertools
from collections import abc
from typing import Any, NoReturn, Tuple, Union

import attr
import numpy as np
from attr import validators

NoneType = type(None)
Block = int
Blocks = Union[Tuple[np.ndarray, np.ndarray], np.ndarray]


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class Memory(abc.Sized):
	"""A stream of memory block requests.

	Attributes:
		blocks: Number of memory blocks.
		seed: Element to set the random seed.
		pages: Number of pages for each block of memory.
		available: Indicator array that tracks if a block is allocated or free.
		_rng: Random generator.
		"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	seed = attr.ib(type=Any, default=None, repr=False)
	pages = attr.ib(type=np.ndarray, init=False)
	available = attr.ib(type=np.ndarray, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

	def __attrs_post_init__(self):
		super(Memory, self).__init__()
		if self.seed is None:
			self._rng = np.random.default_rng()
		else:
			self._rng = np.random.default_rng(self.seed)
		self.pages = np.array([self.sample_page() for _ in range(self.blocks)])
		self.available = np.ones(self.blocks, dtype=bool)

	def __len__(self) -> int:
		return len(self.blocks)

	def get_allocated(self, *, with_pages: bool = False) -> Blocks:
		indices = np.flatnonzero(~self.available)
		return (indices, self.blocks[indices]) if with_pages else indices

	@property
	def num_allocated(self) -> int:
		"""Returns the number of memory blocks allocated."""
		return self.available.size - self.num_free

	def get_free(self, *, with_pages: bool = False) -> Blocks:
		indices = np.flatnonzero(self.available)
		return (indices, self.blocks[indices]) if with_pages else indices

	@property
	def num_free(self) -> int:
		"""Returns the number of memory blocks free."""
		return sum(self.available)

	@property
	def fragmented(self) -> float:
		"""Returns the percentage of memory fragmentation.

		References:
			http://stackoverflow.com/questions/4586972/ddg#4587077
		"""
		groups = itertools.groupby(self.available)
		max_free = max(sum(1 for _ in g) for _, g in groups)
		num_free = self.num_free
		return 0 if num_free == 0 else (num_free - max_free) / num_free

	def allocate(self, b: Block) -> NoReturn:
		self.available[b] = False

	def free(self, b: Block) -> NoReturn:
		self.available[b] = True

	def sample_page(self) -> int:
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def reset(self) -> NoReturn:
		"""Frees all memory blocks."""
		self.available = np.ones(self.blocks, dtype=bool)
