import enum
from collections import abc
from typing import Any, Optional, Tuple

import attr
import numpy as np
from attr import validators

import memory
from memory import (
	Block, BlockTypes, BlocksTypes, Blocks, NO_BLOCK, Page, PageTypes, Pages,
	PagesTypes)

OPTIONAL_PAGE_VALIDATOR = validators.optional(
	validators.instance_of(PageTypes))
OPTIONAL_BLOCK_VALIDATOR = validators.optional(
	validators.instance_of(BlockTypes))
OPTIONAL_PAGES_VALIDATOR = validators.optional(
	validators.instance_of(PagesTypes))


class RequestType(enum.Enum):
	ALLOCATE = 'allocate'
	FREE = 'free'
	ME_TOO = 'me_too'


@attr.s(frozen=True, slots=True)
class Result:
	success = attr.ib(
		type=bool,
		validator=validators.instance_of(bool),
		kw_only=True)
	block = attr.ib(
		type=Optional[Block],
		default=True,
		validator=OPTIONAL_BLOCK_VALIDATOR,
		kw_only=True)
	pages = attr.ib(
		type=Optional[Page],
		default=None,
		validator=OPTIONAL_PAGE_VALIDATOR,
		kw_only=True)
	start = attr.ib(
		type=Optional[Block],
		default=None,
		validator=OPTIONAL_BLOCK_VALIDATOR,
		kw_only=True)
	before = attr.ib(
		type=Page,
		default=None,
		validator=OPTIONAL_PAGE_VALIDATOR,
		kw_only=True)
	after = attr.ib(
		type=Optional[Pages],
		default=None,
		validator=OPTIONAL_PAGES_VALIDATOR,
		kw_only=True)


@attr.s(frozen=True, slots=True)
class Request:
	block = attr.ib(
		type=BlocksTypes,
		validator=validators.instance_of(BlocksTypes),
		kw_only=True)
	pages = attr.ib(
		type=Page,
		validator=validators.instance_of(PageTypes),
		kw_only=True)
	rtype = attr.ib(
		type=RequestType,
		validator=validators.instance_of(RequestType),
		kw_only=True)


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class RequestStream(abc.Iterator, abc.Callable):
	"""A stream of memory block requests.

	Attributes:
		memory: Contains all blocks of memory
		seed: Element to set the random seed.
		_rng: Random generator.
	"""
	memory = attr.ib(
		type=memory.Memory, validator=validators.instance_of(memory.Memory))
	seed = attr.ib(type=Any, default=None, kw_only=True, repr=False)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

	def __attrs_post_init__(self):
		super(RequestStream, self).__init__()
		if self.seed is None:
			self._rng = np.random.default_rng()
		else:
			self._rng = np.random.default_rng(self.seed)

	def __call__(self, *args, **kwargs) -> Request:
		return next(self)

	def __next__(self) -> Request:
		return self.request()

	def request(self) -> Request:
		"""A discrete probability distribution over request types.

		Returns:
			The requested block, corresponding pages, and request type.
		"""
		if not self.memory.num_allocated:
			block, pages = self.allocate()
			request = Request(
				block=block, pages=pages, rtype=RequestType.ALLOCATE)
		elif not self.memory.num_free:
			block, pages = self.free()
			request = Request(block=block, pages=pages, rtype=RequestType.FREE)
		else:
			(block, pages), rtype = self._rng.choice(np.array((
				(self.allocate(), RequestType.ALLOCATE),
				(self.free(), RequestType.FREE),
				(self.me_too(), RequestType.ME_TOO)),
				dtype=object))
			request = Request(block=block, pages=pages, rtype=rtype)
		return request

	def allocate(self) -> Tuple[Block, Page]:
		"""Samples a free block and determines if it should be allocated.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be allocated. A block is
			never allocated if it is already allocated.

			The co-domain of the distribution is {True, False}.

		Returns:
			The sampled block and the corresponding number of pages.
		"""
		block = self.sample_block(allocated=False)
		pages = self.memory.pages[block]
		return block, pages

	def free(self) -> Tuple[Block, Page]:
		"""Samples an allocated block and determines if it should be freed.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be freed/deallocated,
			A block is never freed if it is already free.

			The co-domain of the distribution is {True, False}.

		Returns:
			The sampled block and the corresponding number of pages.
		"""
		block = self.sample_block(allocated=True)
		pages = self.memory.pages[block]
		return block, pages

	def me_too(self) -> Tuple[Tuple[Block, Block], Page]:
		"""Samples 2 blocks and determines if the first should be allocated.

		Notes:
			The first (given) block is sampled is allocated, while the second
			block sampled is free. If either all blocks are allocated or no
			blocks are free, then the result is always False.

			Mathematically, the distribution is defined as p(b1 | b2), which
			represents the probability that b1 will be allocated, given b2 is
			allocated. The first block is never allocated if either (1) it is
			already allocated or (2) the second block is free.

			The co-domain of the distribution is {True, False}.

		Returns:
			The 2 sampled blocks and the corresponding number of pages.
		"""
		allocated = self.sample_block(allocated=True)
		to_allocate = self.sample_block(allocated=False)
		blocks = (to_allocate, allocated)
		if to_allocate is NO_BLOCK:
			pages = 0
		else:
			pages = self.memory.pages[to_allocate]
		return blocks, pages

	# noinspection PyIncorrectDocstring
	def sample_block(self, n: int = 1, *, allocated: bool = True) -> Blocks:
		"""Samples either allocated or free blocks.

		Args:
			n: Number of blocks to sample. Sampling is done without
				replacement, so the number of blocks sampled is
				min(n, pool_size).

		Keyword Args:
			allocated: True only samples from allocated blocks. False only
				samples from free blocks.

		Returns:
			None or > 0 blocks.
		"""
		if allocated:
			pool = self.memory.get_allocated()
		else:
			pool = self.memory.get_free()
		block = self._rng.choice(pool, size=min(n, pool.size), replace=False)
		if block.size < 1:
			block = NO_BLOCK
		elif n == 1:
			block = int(block[0])
		return block
