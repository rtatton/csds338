import io
import sys
from collections import abc
from typing import (
	Any, Callable, NoReturn, Optional, TextIO, Tuple, Union)

import attr
import numpy as np
from attr import validators

NoneType = type(None)
Block = int
Blocks = Union[Block, Tuple[Block, ...]]
Result = bool
TRUE_OR_FALSE = (True, False)
NO_BLOCK = None


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class RequestStream(abc.Iterator, abc.Callable):
	"""A stream of memory block requests.

	Attributes:
		blocks: Number of memory blocks.
		seed: Element to set the random seed.
		pages: Number of pages for each block of memory.
		available: Indicator array that tracks if a block is allocated or free.
		std_out: Stream to which request results should be written. If None,
			results will not be written to any stream.
		_rng: Random generator.
	"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	seed = attr.ib(type=Any, default=None, repr=False)
	std_out = attr.ib(
		type=Optional[Union[TextIO, io.TextIOBase]],
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, NoneType)),
		repr=False)
	pages = attr.ib(type=np.ndarray, init=False)
	available = attr.ib(type=np.ndarray, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

	def __attrs_post_init__(self):
		super(RequestStream, self).__init__()
		if self.seed is None:
			self._rng = np.random.default_rng()
		else:
			self._rng = np.random.default_rng(self.seed)
		self.pages = np.array([self.sample_page() for _ in range(self.blocks)])
		self.available = np.ones(self.blocks, dtype=bool)

	def __call__(self, *args, **kwargs) -> Result:
		return next(self)

	def __next__(self) -> Result:
		request = self.sample_request()
		_, result = request()
		return result

	def sample_page(self) -> int:
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def sample_request(self) -> Callable[[], Tuple[Blocks, Result]]:
		"""A discrete probability distribution over request types.

		Returns:
			A request callable.
		"""
		if all(self.available):
			request = self.allocate
		elif not any(self.available):
			request = self.free
		else:
			request = self._rng.choice((self.allocate, self.free, self.me_too))
		return request

	def allocate(self) -> Tuple[Block, Result]:
		"""Samples a free block and determines if it should be allocated.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be allocated. A block is
			never allocated if it is already allocated.

			The co-domain of the distribution is {True, False}.

		See Also:
			sample_allocate() - defines the probability distribution.

		Returns:
			The sampled block and the result if the sampling occurred.
		"""
		if (block := self.sample_block(allocated=False)) is NO_BLOCK:
			result = False
		elif result := self.sample_allocate(block):
			self.available[block] = False
		self._print('Allocate', block, result)
		return block, result

	def sample_allocate(self, b: Block) -> Result:
		"""A discrete, bimodal, unconditional probability distribution.

		See Also:
			allocate() - implements the remaining sampling logic.

		Returns:
			True if the sampling should occur and False otherwise.
		"""
		return self._rng.choice(TRUE_OR_FALSE)

	def free(self) -> Tuple[Block, Result]:
		"""Samples an allocated block and determines if it should be freed.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be freed/deallocated,
			A block is never freed if it is already free.

			The co-domain of the distribution is {True, False}.

		See Also:
			sample_free() - defines the probability distribution.

		Returns:
			The sampled block and the result if the sampling occurred.
		"""
		if (block := self.sample_block(allocated=True)) is NO_BLOCK:
			result = False
		elif result := self.sample_free(block):
			self.available[block] = True
		self._print('Free', block, result)
		return block, result

	def sample_free(self, b: Block) -> Result:
		"""A discrete, bimodal, unconditional probability distribution.

		See Also:
			free() - implements the remaining sampling logic.

		Returns:
			True if the sampling should occur and False otherwise.
		"""
		return self._rng.choice(TRUE_OR_FALSE)

	def me_too(self) -> Tuple[Tuple[Block, Block], Result]:
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

		See Also:
			sample_me_too() - defines the probability distribution.

		Returns:
			The 2 sampled blocks and the result if the sampling occurred.
		"""
		allocated = self.sample_block(allocated=True)
		to_allocate = self.sample_block(allocated=False)
		if allocated is NO_BLOCK or to_allocate is NO_BLOCK:
			result = False
		elif result := self.sample_me_too(allocated, to_allocate):
			self.available[to_allocate] = False
		self._print('MeToo', f'{to_allocate}|{allocated}', result)
		return (allocated, to_allocate), result

	def sample_me_too(self, allocated: Block, to_allocate: Block) -> Result:
		"""A discrete, conditional, bimodal probability distribution.

		See Also:
			me_too() - implements the remaining sampling logic.

		Returns:
			True if the sampling should occur and False otherwise.
		"""
		return self._rng.choice(TRUE_OR_FALSE)

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
			0 or more sampled blocks.
		"""
		pool = np.flatnonzero(~self.available if allocated else self.available)
		block = self._rng.choice(pool, size=min(n, pool.size), replace=False)
		if block.size < 1:
			block = NO_BLOCK
		elif n == 1:
			block = block[0]
		return block

	def _print(self, request_type: str, params: Any, result: Any) -> NoReturn:
		if self.std_out:
			print(f'{request_type}({params}) -> {result}', file=self.std_out)


if __name__ == '__main__':
	requests = RequestStream(5)
	for _ in range(20):
		requests()
	print(np.flatnonzero(requests.available))
