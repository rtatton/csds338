import random
from collections import abc
from typing import Any, Callable, Sequence, Set, Tuple, Union

import attr
import numpy as np
from attr import validators

Block = int
Result = bool


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class RequestStream(abc.Iterator, abc.Callable):
	"""A stream of memory block requests.

	Attributes:
		blocks: Number of memory blocks.
		seed: Element to set the random seed.
		pages: Number of pages for each block of memory.
		allocated: Contains all memory blocks that have been allocated.
	"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	seed = attr.ib(type=Any, default=None)
	pages = attr.ib(type=Union[Sequence[int], np.ndarray], init=False)
	allocated = attr.ib(type=Set, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False)

	def __attrs_post_init__(self):
		super(RequestStream, self).__init__()
		if self.seed is None:
			self._rng = np.random.default_rng()
		else:
			self._rng = np.random.default_rng(self.seed)
			random.seed(self.seed)
		self.allocated = set()
		self.pages = np.array([self.sample_page() for _ in range(self.blocks)])

	def __call__(self, *args, **kwargs) -> Result:
		return next(self)

	def __next__(self) -> Result:
		request = self.sample_request()
		blocks, result = request()
		if request == self.me_too:
			print(f'MeToo({blocks[0]}|{blocks[1]}) -> {result}')
		elif request == self.allocate:
			print(f'Allocate({blocks}) -> {result}')
		else:
			print(f'Free({blocks}) -> {result}')
		return result

	# noinspection PyMethodMayBeStatic
	def sample_page(self):
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def sample_request(self) -> Callable:
		"""A discrete probability distribution over request types."""
		return random.choice((self.allocate, self.me_too, self.free))

	def allocate(self) -> Tuple[Block, Result]:
		"""Samples a block and determines if it should be allocated.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be allocated. A block is
			never allocated if it is already allocated.

			The co-domain of the distribution is {True, False}.

		See Also:
			allocate_sample() - defines the probability distribution.
		"""
		if (block := self.sample_block()) in self.allocated:
			result = False
		elif result := self.sample_allocate(block):
			self.allocated.add(block)
		return block, result

	# noinspection PyMethodMayBeStatic
	def sample_allocate(self, b: Block) -> Result:
		"""A discrete, bimodal, unconditional probability distribution.

		See Also:
			allocate() - implements the remaining sampling logic.
		"""
		return random.choice((True, False))

	def free(self) -> Tuple[Block, Result]:
		"""Samples a block and determines if it should be freed.

		Notes:
			Mathematically, the distribution is defined as p(b), which
			represents the probability that b will be freed/deallocated,
			A block is never freed if it is already free.

			The co-domain of the distribution is {True, False}.

		See Also:
			free_sample() - defines the probability distribution.
		"""
		if (block := self.sample_block()) in self.allocated:
			if result := self.sample_free(block):
				self.allocated.remove(block)
		else:
			result = False
		return block, result

	# noinspection PyMethodMayBeStatic
	def sample_free(self, b: Block) -> Result:
		"""A discrete, bimodal, unconditional probability distribution.

		See Also:
			free() - implements the remaining sampling logic.
		"""
		return random.choice((True, False))

	def me_too(self) -> Tuple[Tuple[Block, Block], Result]:
		"""Samples 2 blocks and determines if the first should be allocated.

		Notes:
			Mathematically, the distribution is defined as p(b1 | b2), which
			represents the probability that b1 will be allocated, given b2 is
			allocated. The first block is never allocated if either (1) it is
			already allocated or (2) the second block is free.

			The co-domain of the distribution is {True, False}.

		See Also:
			me_to_sample() - defines the probability distribution.
		"""
		b1, b2 = self.sample_block(2)
		if b2 in self.allocated:
			if b1 in self.allocated:
				result = False
			elif result := self.sample_me_too(b1, b2):
				self.allocated.add(b1)
		else:
			result = False
		return (b1, b2), result

	# noinspection PyMethodMayBeStatic
	def sample_me_too(self, b1: Block, b2: Block) -> Result:
		"""A discrete, conditional, bimodal probability distribution.

		See Also:
			me_too() - implements the remaining sampling logic.
		"""
		return random.choice((True, False))

	def sample_block(self, n: int = 1) -> Union[Block, Tuple[Block]]:
		def sample():
			return self._rng.integers(self.blocks)

		if n == 1:
			block = sample()
		else:
			block = tuple(sample() for _ in range(n))
		return block


if __name__ == '__main__':
	requests = RequestStream(blocks=5)
	for _ in range(25):
		requests()
	print(requests.allocated)
