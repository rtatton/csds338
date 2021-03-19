from typing import NoReturn

import attr
from attr import validators

import allocation
import memory
import requests


@attr.s(slots=True, frozen=True)
class Simulator:
	stream = attr.ib(
		type=requests.RequestStream,
		validator=validators.instance_of(requests.RequestStream))
	allocator = attr.ib(
		type=allocation.Allocator,
		validator=validators.instance_of(allocation.Allocator))

	def run(self, steps: int = 100) -> NoReturn:
		"""Runs the simulation"""
		for _, request in zip(range(steps), self.stream):
			self.allocator(request)


if __name__ == '__main__':
	mem = memory.Memory(5)
	stream = requests.RequestStream(mem)
	allocator = allocation.FirstFit(mem)
	simulator = Simulator(stream, allocator)
	simulator.run()
