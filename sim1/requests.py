from collections import abc
from typing import (
	Any, Callable, Tuple, Union)

import attr
import numpy as np
from attr import validators

import memory

Block = int
Blocks = Union[Block, Tuple[Block, ...]]
Request = Callable[[], Blocks]


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
	seed = attr.ib(type=Any, default=None, repr=False)
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
		return self.sample_request()

	def sample_request(self) -> Request:
		"""A discrete probability distribution over request types.

		Returns:
			A request callable.
		"""
		if not self.memory.num_allocated:
			request = self.allocate
		elif not self.memory.num_free:
			request = self.free
		else:
			request = self._rng.choice((self.allocate, self.free, self.me_too))
		return request

	def allocate(self) -> Block:
		"""Samples a free block and determines if it should be allocated.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be allocated. A block is
			never allocated if it is already allocated.

			The co-domain of the distribution is {True, False}.

		Returns:
			The sampled block and the result if the sampling occurred.
		"""
		return self.sample_block(allocated=False)

	def free(self) -> Block:
		"""Samples an allocated block and determines if it should be freed.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be freed/deallocated,
			A block is never freed if it is already free.

			The co-domain of the distribution is {True, False}.

		Returns:
			The sampled block and the result if the sampling occurred.
		"""
		return self.sample_block(allocated=True)

	def me_too(self) -> Tuple[Block, Block]:
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
			The 2 sampled blocks and the result if the sampling occurred.
		"""
		allocated = self.sample_block(allocated=True)
		to_allocate = self.sample_block(allocated=False)
		return to_allocate, allocated

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
			block = block[0]
		return block


if __name__ == '__main__':
	print()
