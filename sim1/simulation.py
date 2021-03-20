import io
import sys
from typing import NoReturn, Optional, TextIO, Union

import attr
from attr import validators

import allocation
import memory
import requests

NoneType = type(None)
StdOut = Optional[Union[TextIO, io.TextIOBase]]


@attr.s(slots=True, frozen=True)
class Simulator:
	stream = attr.ib(
		type=requests.RequestStream,
		validator=validators.instance_of(requests.RequestStream))
	allocator = attr.ib(
		type=allocation.Allocator,
		validator=validators.instance_of(allocation.Allocator))
	std_out = attr.ib(
		type=StdOut,
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, NoneType)),
		repr=False)

	def run(self, steps: int = 100) -> NoReturn:
		"""Runs the simulation"""
		for i, request in zip(range(steps), self.stream):
			if self.std_out:
				print('-' * 80, file=self.std_out)
				print(f'{i + 1}:', file=self.std_out)
			self.allocator(request)


if __name__ == '__main__':
	with open('output.txt', 'w') as f:
		mem = memory.Memory(10)
		stream = requests.RequestStream(mem)
		allocator = allocation.BestFit(mem)
		simulator = Simulator(stream, allocator)
		simulator.run(10_000)
