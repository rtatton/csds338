import random

import attr
import numpy as np
from attr import validators

import philosopher


@attr.s(slots=True)
class DiningTable:
	"""
	Attributes:
		n_chairs: Number of chairs at the dining table.
		chopsticks: Boolean array indicating which chopsticks are available.
			Indexing is performed clockwise such that the ith chopstick is to
			the left (from the perspective of sitting at the table) of the
			ith philosopher.
	"""
	n_chairs = attr.ib(type=int, validator=validators.instance_of(int))
	chopsticks = attr.ib(type=np.ndarray, init=False)
	philosophers = attr.ib(
		type=philosopher.Philosopher, init=False, repr=False)

	def __attrs_post_init__(self):
		self.chopsticks = np.ones(self.n_chairs, dtype=bool)
		self.philosophers = [
			philosopher.Philosopher() for _ in range(self.n_chairs)]

	def get_left(self, p: int, return_idx: bool = False) -> bool:
		"""Check if the chopstick to the left of a philosopher is present."""
		result = self.chopsticks[p]
		return (result, p) if return_idx else result

	def get_right(self, p: int, return_idx: bool = False) -> bool:
		"""Check if the chopstick to the right of a philosopher is present."""
		result = (self.chopsticks[p] - 1) % p
		idx = (p - 1) % p
		return (result, idx) if return_idx else result

	def pick_up(self, p: int) -> bool:
		"""Attempts to have the philosopher pick up a chopstick.
			Args:
				p: Index of philosopher picking up the chopstick

			Returns:
				True if the operation succeeded and False otherwise.
			"""
		phil = self.philosophers[p]
		left_on_table, left_idx = self.get_left(p, return_idx=True)
		right_on_table, right_idx = self.get_right(p, return_idx=True)
		if result := left_on_table:
			self.chopsticks[left_idx] = False
			if phil.state == philosopher.PhilosopherState.WAITING_LEFT:
				phil.state = philosopher.PhilosopherState.EATING
			else:
				phil.state = philosopher.PhilosopherState.THINKING
		elif result := right_on_table:
			self.chopsticks[right_idx] = False
			if phil.state == philosopher.PhilosopherState.WAITING_RIGHT:
				phil.state = philosopher.PhilosopherState.EATING
			else:
				phil.state = philosopher.PhilosopherState.THINKING
		return result

	def put_down(self, p: int) -> bool:
		"""Attempts to have the philosopher pick up a chopstick.
			Args:
				p: Index of philosopher picking up the chopstick

			Returns:
				True if the operation succeeded and False otherwise.
		"""
		phil = self.philosophers[p]
		if result := phil.state == philosopher.PhilosopherState.EATING:
			# TODO Do we want to specify which chopstick to put down?
			if random.choice((True, False)):
				_, idx = self.get_left(p, return_idx=True)
				self.chopsticks[idx] = True
			else:
				_, idx = self.get_right(p, return_idx=True)
				self.chopsticks[idx] = True
			phil.state = philosopher.PhilosopherState.THINKING
		return result
