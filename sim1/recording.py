import collections.abc
import json
from typing import NoReturn

import attr
import numpy as np
from attr import validators
import time

import storage


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class Recorder:
	"""
	Attributes:
		memory: Contains all blocks of memory
	"""
	memory = attr.ib(
		type=storage.Memory, validator=validators.instance_of(storage.Memory))
	file = attr.ib(
		type=str, validator=validators.instance_of(str), kw_only=True)
	start = attr.ib(default=None)
	stop = attr.ib(default=None)

	def start_timer(self):
		self.start = time.time()

	def stop_timer(self):
		self.stop = time.time()

	def record(self, *args, **kwargs) -> NoReturn:
		with open(self.file, 'a') as f:
			f.write(f'{self.memory.fragmented(as_pages=True)}\n')

	def summarize(self) -> NoReturn:
		name, ext = self.file.split('.')
		file = ''.join((name, '_summary.', ext))
		with open(file, 'w') as f:
			data = np.loadtxt(self.file)
			summary = {
				'moving_avg': self._moving_avg(data),
				'duration': round(self.stop - self.start, 4),
				'mean': np.mean(data),
				'std': np.std(data),
				'max': max(data),
				'min': min(data)}
			json.dump(summary, f)

	@staticmethod
	def _moving_avg(x, *, window=None):
		"""Returns the moving average of x using window w.

		References:
			https://stackoverflow.com/questions/14313510/how-to-calculate
			-rolling-moving-average-using-numpy-scipy
		"""
		window = int(np.ceil(len(x) / 10)) if window is None else window
		return (np.convolve(x, np.ones(window), 'valid') / window).tolist()

	def clear(self):
		open(self.file, 'w').close()
