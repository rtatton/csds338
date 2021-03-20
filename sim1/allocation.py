import abc
import collections.abc
import io
import sys
from typing import Iterable, NoReturn, Optional, TextIO, Union

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
		kw_only=True,
		repr=False)

	def __call__(self, request: Request) -> NoReturn:
		result = self.call(request)
		self.print_result(request, result)

	@abc.abstractmethod
	def call(self, request: Request) -> requests.Result:
		pass

	def print_result(
			self,
			request: requests.Request,
			result: requests.Result) -> NoReturn:
		if self.std_out:
			rtype = self.format_rtype(request.rtype)
			pages = result.pages
			if isinstance(block := request.block, Iterable):
				params = f'blocks={tuple(b for b in block)}, pages={pages}'
			else:
				params = f'block={block}, pages={pages}'
			print(f'Request: {rtype}({params})', file=self.std_out)
			if result.success:
				block = f'block={result.block}'
				start = f'start={result.start}'
				pages = f'pages={result.pages}'
				before = f'before={result.before}'
				after = f'after={result.after}'
				params = f'{block}, {start}, {pages}, {before}, {after}'
				result = f'SuccessfulRequest({params})'
			else:
				result = 'FailedRequest'
			print(f'Result: {result}', file=self.std_out)

	@staticmethod
	def format_rtype(rtype: requests.RequestType) -> str:
		rtype = str(rtype.value)
		rtype = (s.capitalize() for s in rtype.split('_'))
		return ''.join(rtype)


class FirstFit(Allocator):

	def __init__(self, *args, **kwargs):
		super(FirstFit, self).__init__(*args, **kwargs)

	def call(self, request: requests.Request) -> requests.Result:
		# TODO Add defragmentation
		block, rtype = request.block, request.rtype
		if rtype == requests.RequestType.FREE:
			self.memory.free(block)
			fit = block
			start, before, after = None, None, None
		elif rtype == requests.RequestType.ALLOCATE:
			fit = self.memory.first_fit(block)
			start = self.memory.get_page_address(fit)
			before, after = self.memory.allocate(fit)
		else:
			to_allocate, _ = block
			fit = self.memory.first_fit(to_allocate)
			start = self.memory.get_page_address(fit)
			before, after = self.memory.allocate(fit)
		return requests.Result(
			success=True,
			block=fit,
			pages=self.memory.get_num_pages(fit),
			start=start,
			before=before,
			after=after)


class BestFit(Allocator):

	def __init__(self, *args, **kwargs):
		super(BestFit, self).__init__(*args, **kwargs)

	def call(self, request: requests.Request) -> requests.Result:
		# TODO Add defragmentation
		block, rtype = request.block, request.rtype
		if rtype == requests.RequestType.FREE:
			self.memory.free(block)
			fit = block
			start, before, after = None, None, None
		elif rtype == requests.RequestType.ALLOCATE:
			fit = self.memory.best_fit(block)
			start = self.memory.get_page_address(fit)
			before, after = self.memory.allocate(fit)
		else:
			to_allocate, _ = block
			fit = self.memory.best_fit(to_allocate)
			start = self.memory.get_page_address(fit)
			before, after = self.memory.allocate(fit)
		return requests.Result(
			success=True,
			block=fit,
			pages=self.memory.get_num_pages(fit),
			start=start,
			before=before,
			after=after)
