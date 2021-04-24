from typing import Any

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
	seed = attr.ib(type=Any, default=None)
	_rng = attr.ib(type=np.random.Generator, init=False, repr=False)

	def __attrs_post_init__(self):
		self._rng = np.random.default_rng(self.seed)
		self.chopsticks = np.ones(self.n_chairs, dtype=bool)
		self.philosophers = [
			philosopher.Philosopher(philosopher.PhilosopherState.THINKING, 0)
			for _ in range(self.n_chairs)]

	def get_left(self, p: int, return_idx: bool = False) -> bool:
		"""Check if the chopstick to the left of a philosopher is present."""
		result = self.chopsticks[p]
		return (result, p) if return_idx else result

	def get_right(self, p: int, return_idx: bool = False) -> bool:
		"""Check if the chopstick to the right of a philosopher is present."""
		idx = (p - 1) % len(self.chopsticks)
		result = self.chopsticks[idx]
		return (result, idx) if return_idx else result

	def pick_up(self, p: int, any_chop: bool=False) -> bool:
		"""Attempts to have the philosopher pick up a chopstick. If successful, changes chopstick[index] to False and Philosopher.right/left to True
			Args:
				p: Index of philosopher picking up the chopstick
				pr: Probability that the picking up will actually occur
			Returns:
				True if the operation succeeded and False otherwise.
			"""
		phil = self.philosophers[p]
		if not(any_chop):
			left_on_table, left_idx = self.get_left(p, return_idx=True)
			right_on_table, right_idx = self.get_right(p, return_idx=True)
			if result := left_on_table and phil.left_chop == -1:
				self.chopsticks[left_idx] = False
				phil.left_chop = left_idx
			elif result := right_on_table and phil.right_chop == -1:
				self.chopsticks[right_idx] = False
				phil.right_chop = right_idx
			return result
		else:
			free = np.flatnonzero(self.chopsticks)
			if free.size > 0:
				chop = random.choice(free)
				self.chopsticks[chop] = False
				result = True
				if phil.right_chop == -1:
					phil.right_chop = chop
				else:
					phil.left_chop = chop
			else:
				result = False
			return result

		

	def put_down(self, p: int) -> bool:
		"""Attempts to have the philosopher pick up a chopstick. If successful, changes chopstick[index] to True and Philosopher.right/left to False
			Args:
				p: Index of philosopher picking up the chopstick
				pr: Probability that the putting down will actually occur
			Returns:
				True if the operation succeeded and False otherwise.
		"""
		phil = self.philosophers[p]
		if result := phil.left_chop >= 0:
			self.chopsticks[phil.left_chop] = True
			phil.left_chop = -1
		elif result := phil.right_chop >= 0:
			self.chopsticks[phil.right_chop] = True
			phil.right_chop = -1
		return result
			
