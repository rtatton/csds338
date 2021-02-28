import random
from collections import abc
from typing import Any, Callable, Sequence, Set, Union

import attr
import numpy as np
from attr import validators


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class RequestGenerator(abc.Callable):
	"""
	Attributes:
		blocks: Number of memory blocks.
		page: Returns the number of pages for the ith memory block.
		request: Returns if the ith block should be requested by a process.
		seed: Element to set the random seed.
		pages: Number of pages for each block of memory.
		allocated: Contains all memory blocks that have been allocated.
	"""
	blocks = attr.ib(
		type=int, default=100, validator=validators.instance_of(int))
	page = attr.ib(
		type=Callable[[int], int],
		validator=validators.is_callable(),
		default=lambda: 10,
		repr=False)
	request = attr.ib(
		type=Callable[[int], bool],
		validator=validators.is_callable(),
		default=lambda x: random.choice((True, False)),
		repr=False)
	free = attr.ib(
		type=Callable[[int], bool],
		validator=validators.is_callable(),
		default=lambda x: random.choice((True, False)),
		repr=False)
	me_too = attr.ib(
		type=Callable[[int, int], bool],
		validator=validators.is_callable(),
		default=lambda x, y: random.choice((True, False)),
		repr=False)
	seed = attr.ib(type=Any, default=None)
	pages = attr.ib(type=Union[Sequence[int], np.ndarray], init=False)
	allocated = attr.ib(type=Set, init=False)
	_rng = attr.ib(type=np.random.Generator, init=False)

	def __attrs_post_init__(self):
		super(RequestGenerator, self).__init__()
		self.allocated = set()
		self.pages = np.array([self.page() for _ in range(self.blocks)])
		if self.seed is not None:
			self._rng = np.random.default_rng(self.seed)
		else:
			self._rng = np.random.default_rng()

	def __call__(self, *args, **kwargs):
		activity = random.choice((self.request, self.me_too, self.free))
		block1 = self._sample_block()
		if activity is self.me_too:
			block2 = self._sample_block()
			result = activity(block1, block2)
			print(f'MeTooRequest({block1}, {block2}) -> {result}')
		elif activity is self.request:
			result = activity(block1)
			print(f'StandardRequest({block1}) -> {result}')
		else:
			result = activity(block1)
			print(f'FreeRequest({block1}) -> {result}')
		return result

	def _sample_block(self) -> int:
		def sample():
			return self._rng.integers(self.blocks + 1)

		block = sample()
		while block in self.allocated:
			block = sample()
		return block


if __name__ == '__main__':
	stream = RequestGenerator(blocks=5)
	for _ in range(5):
		print(stream())
