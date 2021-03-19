import abc
import collections.abc
import io
import sys
from typing import Any, NoReturn, Optional, TextIO, Union

import attr
from attr import validators

import memory
import requests
from requests import Request

NO_BLOCK = None
NoneType = type(None)
StdOut = Optional[Union[TextIO, io.TextIOBase]]


# noinspection PyUnresolvedReferences
@attr.s(slots=True, frozen=True)
class Allocator(abc.ABC, collections.abc.Callable):
	"""
	Attributes:
		memory: Contains all blocks of memory
		std_out: Stream to which request results should be written. If None,
			results will not be written to any stream.
	"""
	memory = attr.ib(
		type=memory.Memory, validator=validators.instance_of(memory.Memory))
	std_out = attr.ib(
		type=StdOut,
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, NoneType)),
		repr=False)

	def __call__(self, request: Request) -> NoReturn:
		self.call(request)

	@abc.abstractmethod
	def call(self, request: Request) -> NoReturn:
		pass


class FirstFit(Allocator):

	def __init__(self, *args, **kwargs):
		super(FirstFit, self).__init__(*args, **kwargs)

	def call(self, request: Request) -> NoReturn:
		# TODO Add defragmentation
		requested, request_type = request
		if request_type == requests.RequestType.FREE:
			self.memory.free(requested)
		elif request_type == requests.RequestType.ALLOCATE:
			fit = self.memory.get_first_fit(requested)
			self.memory.allocate(fit)
		else:
			fit = self.memory.get_first_fit(requested[0])
			self.memory.allocate(fit)


class BestFit(Allocator):

	def __init__(self, *args, **kwargs):
		super(BestFit, self).__init__(*args, **kwargs)

	def call(self, request: Request) -> NoReturn:
		# TODO Add defragmentation
		requested, request_type = request
		if request_type == requests.RequestType.FREE:
			self.memory.free(requested)
		elif request_type == requests.RequestType.ALLOCATE:
			fit = self.memory.get_first_fit(requested)
			self.memory.allocate(fit)
		else:
			fit = self.memory.get_first_fit(requested[0])
			self.memory.allocate(fit)

	def _print(self, request_type: str, params: Any) -> NoReturn:
		if self.std_out:
			print(f'{request_type}({params})', file=self.std_out)


if __name__ == '__main__':
	m = memory.Memory(10)
	f = FirstFit(m)
