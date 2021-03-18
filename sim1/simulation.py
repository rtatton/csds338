from typing import NoReturn

import attr
from attr import validators

import allocation
import requests


@attr.s(slots=True, frozen=True)
class Simulator:
	request_stream = attr.ib(
		type=requests.RequestStream,
		validator=validators.instance_of(requests.RequestStream))
	allocator = attr.ib(
		type=allocation.Allocator,
		validator=validators.instance_of(allocation.Allocator))

	def run(self, steps: int = 100) -> NoReturn:
		"""Runs the simulation"""
		for _ in range(steps):
			request = self.request_stream()
			self.allocator(request)
