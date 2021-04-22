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
		self.philosophers = [philosopher.Philosopher()]

	def get_left(self, p) -> bool:
		"""Check if the chopstick to the left of a philosopher is present."""
		return self.chopsticks[p]

	def get_right(self, p) -> bool:
		"""Check if the chopstick to the right of a philosopher is present."""
		return (self.chopsticks[p] - 1) % p

	def pick_up(self, *c, atomic: bool = False) -> bool:
		"""Pick up one or more chopsticks.
			Args:
				*c: Chopsticks to pick up.
				atomic: If True, no operation will complete if any of the
					chopsticks are already picked up. Otherwise, all specified
					chopsticks will be picked up, regardless if they are
					already picked up.

			Returns:
				True if the operation succeeded and False otherwise.
			"""
		if atomic:
			if not (failed := not np.all(self.chopsticks[c])):
				self.chopsticks[c] = False
		else:
			self.chopsticks[c] = False
			failed = False
		return not failed

	def put_down(self, *c, atomic: bool = False) -> bool:
		"""Put down one or more chopsticks.
		Args:
			*c: Chopsticks to put down.
			atomic: If True, no operation will complete if any of the
				chopsticks are already put down. Otherwise, all specified
				chopsticks will be put down, regardless if they are already
				put down.

		Returns:
			True if the operation succeeded and False otherwise.
		"""
		if atomic:
			if not (failed := np.any(self.chopsticks[c])):
				self.chopsticks[c] = True
		else:
			self.chopsticks[c] = True
			failed = False
		return not failed
