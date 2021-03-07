import itertools
from collections import abc
from typing import Any, NoReturn

import attr
import numpy as np
from attr import validators

NoneType = type(None)


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class Memory(abc.Sized):
	"""A stream of memory block requests.

	Attributes:
		blocks: Number of memory blocks.
		page_size: Size of each page in units of bytes.
		seed: Element to set the random seed.
		pages: Number of pages for each block of memory.
		available: Indicator array that tracks if a block is allocated or free.
		_rng: Random generator.
		"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	page_size = attr.ib(type=int, default=4_000)
	seed = attr.ib(type=Any, default=None, repr=False)
	pages = attr.ib(type=np.ndarray, init=False)
	available = attr.ib(type=np.ndarray, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

	@page_size.validator
	def _check_page_size(self, attribute, value):
		if not isinstance(value, int):
			raise TypeError("'page_size' must be type int")
		elif not 0 < value:
			raise ValueError("'page_size' must be at least 1")

	def __attrs_post_init__(self):
		super(Memory, self).__init__()
		if self.seed is None:
			self._rng = np.random.default_rng()
		else:
			self._rng = np.random.default_rng(self.seed)
		self.pages = np.array([self.sample_page() for _ in range(self.blocks)])
		self.available = np.ones(self.blocks, dtype=bool)

	def __len__(self) -> int:
		return self.blocks * self.page_size

	@property
	def allocated(self) -> np.ndarray:
		return np.flatnonzero(~self.available)

	@property
	def num_allocated(self) -> int:
		"""Returns the number of memory blocks allocated."""
		return self.available.size - self.num_free

	@property
	def free(self) -> np.ndarray:
		return np.flatnonzero(self.available)

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

	def sample_page(self) -> int:
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def reset(self) -> NoReturn:
		"""Frees all memory blocks."""
		self.available = np.ones(self.blocks, dtype=bool)
