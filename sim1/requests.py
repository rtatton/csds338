import io
import random
import sys
from collections import abc
from typing import (
	Any, Callable, NoReturn, Optional, Sequence, Set, TextIO,
	Tuple, Union)

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
		std_out: Stream to which request results should be written. If None,
			results will not be written to any stream.
	"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	seed = attr.ib(type=Any, default=None, repr=False)
	std_out = attr.ib(
		type=Optional[Union[TextIO, io.TextIOBase]],
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, type(None))),
		repr=False)
	pages = attr.ib(type=Union[Sequence[int], np.ndarray], init=False)
	allocated = attr.ib(type=Set, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

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
		_, result = request()
		return result

	# noinspection PyMethodMayBeStatic
	def sample_page(self) -> int:
		"""A discrete probability distribution over memory block pages."""
		return self._rng.integers(1, 21)

	def sample_request(self) -> Callable[[], Tuple[..., Result]]:
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
			sample_allocate() - defines the probability distribution.
		"""
		if (block := self.sample_block()) in self.allocated:
			result = False
		elif result := self.sample_allocate(block):
			self.allocated.add(block)
		self._print('Allocate', block, result)
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
			sample_free() - defines the probability distribution.
		"""
		if (block := self.sample_block()) in self.allocated:
			if result := self.sample_free(block):
				self.allocated.remove(block)
		else:
			result = False
		self._print('Free', block, result)
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
			sample_me_too() - defines the probability distribution.
		"""
		b1, b2 = self.sample_block(2)
		if b2 in self.allocated:
			if b1 in self.allocated:
				result = False
			elif result := self.sample_me_too(b1, b2):
				self.allocated.add(b1)
		else:
			result = False
		self._print('MeToo', f'{b1}|{b2}', result)
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

	def _print(self, request_type: str, params: Any, result: Any) -> NoReturn:
		if self.std_out:
			print(f'{request_type}({params}) -> {result}', file=self.std_out)


if __name__ == '__main__':
	requests = RequestStream(5)
	for _ in range(25):
		requests()
	print(requests.allocated)
