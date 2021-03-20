import itertools
from collections import abc
from typing import Any, NoReturn, Optional, Tuple, Union

import attr
import numpy as np
from attr import validators

BlockTypes = (int, np.integer)
Block = Union[int, np.integer]
Page = Union[int, np.integer]
PageTypes = (int, np.integer)
Blocks = Union[int, np.integer, np.ndarray]
BlocksTypes = (*BlockTypes, Tuple, np.ndarray)
Pages = Union[int, np.integer, np.ndarray]
PagesTypes = (*PageTypes, np.ndarray, Tuple)
Contiguous = Optional[Tuple[np.ndarray, ...]]
NO_BLOCK = None


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
		type=int, default=100, validator=validators.instance_of(BlockTypes))
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
		return (indices, self.pages[indices]) if with_pages else indices

	def get_page_address(self, b: Block) -> Page:
		return (np.cumsum(self.pages) - self.pages[0])[b]

	def get_num_pages(self, b: Block) -> Page:
		return self.pages[b]

	def first_fit(self, b: Block) -> Optional[Block]:
		"""Returns the first fitting block of memory."""
		choices = self.available * (self.pages >= self.pages[b])
		return min(np.flatnonzero(choices), default=None)

	def best_fit(self, b: Block) -> Optional[Block]:
		"""Returns the best fitting block of memory.

		References:
			https://stackoverflow.com/questions/55769522/how-to-find-maximum
			-negative-and-minimum-positive-number-in-a-numpy-array
		"""
		diff = self.pages - self.pages[b] + 1
		choices = diff * self.available * (self.pages >= self.pages[b])
		if choices.size > 0:
			fit = np.where(choices > 0, choices, np.inf).argmin()
		else:
			fit = None
		return fit

	def defragment(self) -> NoReturn:
		"""Defragments the memory."""
		indices = self.available.argsort()
		self.available = self.available[indices]
		self.pages = self.pages[indices]

	@property
	def num_allocated(self) -> int:
		"""Returns the number of memory blocks allocated."""
		return self.available.size - self.num_free

	def get_free(self, *, with_pages: bool = False) -> Blocks:
		"""Returns the indices of the free blocks and optional page values."""
		indices = np.flatnonzero(self.available)
		return (indices, self.pages[indices]) if with_pages else indices

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

	def allocate(self, b: Block) -> Tuple[Page, Optional[Pages]]:
		"""Allocates a block of memory.

		Returns:
			The size of the contiguous chunk of memory prior to allocating
			and, if the chunk is more than one block, the resulting two
			chunks of contiguous memory after allocating.
		"""
		contiguous = self.contiguous()
		chunk = np.argmax([b in sub for sub in contiguous])
		if (selected := contiguous[chunk]).size > 1:
			pages = self.pages[selected]
			idx = np.flatnonzero(selected == b)
			idx = idx.item()
			before = sum(pages)
			after = (sum(pages[:idx]), sum(pages[idx + 1:]))
		else:
			idx = selected.item()
			before, after = self.pages[idx], None
		self.available[b] = False
		return before, after

	def contiguous(
			self, *, with_pages: bool = False
	) -> Union[Contiguous, Tuple[Contiguous, Pages]]:
		"""Returns the indices (and pages) of contiguous blocks of free memory.

		References:
			https://stackoverflow.com/questions/7352684/how-to-find-the-groups
			-of-consecutive-elements-in-a-numpy-array
		"""
		available = np.flatnonzero(self.available)
		split_at = np.flatnonzero(np.diff(available) != 1)
		contiguous = np.split(available, split_at + 1)
		if len(contiguous) == 1 and contiguous[0].size == 0:
			contiguous = None
		if with_pages and contiguous:
			pages = np.array([sum(self.pages[c]) for c in contiguous])
			contiguous = (tuple(contiguous), pages)
		return contiguous

	def free(self, b: Block) -> NoReturn:
		"""Frees a block of memory."""
		self.available[b] = True

	def sample_page(self) -> int:
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def reset(self) -> NoReturn:
		"""Frees all memory blocks."""
		self.available = np.ones(self.blocks, dtype=bool)
