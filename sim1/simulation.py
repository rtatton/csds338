import io
import sys
from typing import NoReturn, Optional, TextIO, Union

import attr
from attr import validators

import allocation
import recording
import requests
import storage

NoneType = type(None)
StdOut = Optional[Union[TextIO, io.TextIOBase]]


@attr.s(slots=True, frozen=True)
class Simulator:
	stream = attr.ib(
		type=requests.RequestStream,
		validator=validators.instance_of(requests.RequestStream),
		kw_only=True,
		repr=False)
	allocator = attr.ib(
		type=allocation.Allocator,
		validator=validators.instance_of(allocation.Allocator),
		kw_only=True,
		repr=False)
	defragmentor = attr.ib(
		type=Optional[storage.Defragmentor],
		default=None,
		validator=validators.optional(
			validators.instance_of(storage.Defragmentor)),
		kw_only=True,
		repr=False)
	recorder = attr.ib(
		type=Optional[recording.Recorder],
		default=None,
		validator=validators.optional(
			validators.instance_of(recording.Recorder)),
		kw_only=True,
		repr=False)
	std_out = attr.ib(
		type=StdOut,
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, NoneType)),
		repr=False,
		kw_only=True)

	def run(self, steps: int = 100) -> NoReturn:
		"""Runs the simulation"""
		if self.recorder:
			self.recorder.clear()
			self.recorder.start_timer()
		for i, request in zip(range(steps), self.stream):
			if self.recorder:
				self.recorder.record()
			if self.std_out:
				print('-' * 80, file=self.std_out)
				print(f'{i + 1}:', file=self.std_out)
			self.allocator(request)
			if self.defragmentor:
				self.defragmentor()
		if self.recorder:
			self.recorder.stop_timer()
			self.recorder.summarize()


if __name__ == '__main__':
	memory = storage.Memory(10)
	stream = requests.RequestStream(memory)
	allocator = allocation.BestFit(memory)
	defragmentor = storage.ThresholdDefragmentor(memory)
	simulator = Simulator(
		stream=stream, allocator=allocator, defragmentor=defragmentor)
	simulator.run(1000)
