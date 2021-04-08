import attr
import numpy as np
from attr import validators


@attr.s(slots=True)
class DiningPhilosophers:
	"""
	Attributes:
		philosophers: Number of philosophers at the dining table.
		chopsticks: Boolean array indicating which chopsticks are available.
			Note that when saturated is False, indexing is performed clockwise
			such that the ith chopstick is to the left (from the perspective
			of sitting at the table) of the ith philosopher.
		saturated: If True, each philosopher has two chopsticks. Otherwise,
			a chopstick exists between every pair of philosophers.
	"""
	philosophers = attr.ib(type=int, validator=validators.instance_of(int))
	chopsticks = attr.ib(type=np.ndarray, init=False)
	saturated = attr.ib(type=bool, default=False, kw_only=True)

	def __attrs_post_init__(self):
		if self.saturated:
			self.chopsticks = np.ones((self.philosophers, 2), dtype=bool)
		else:
			self.chopsticks = np.ones(self.philosophers, dtype=bool)

	def get_left(self, p) -> bool:
		"""Check if the chopstick to the left of a philosopher is present."""
		return self.chopsticks[p][0] if self.saturated else self.chopsticks[p]

	def get_right(self, p) -> bool:
		"""Check if the chopstick to the right of a philosopher is present."""
		chops = self.chopsticks
		return chops[p][1] if self.saturated else (chops[p] - 1) % p

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


if __name__ == '__main__':
	dp = DiningPhilosophers(3)
	print(dp)
