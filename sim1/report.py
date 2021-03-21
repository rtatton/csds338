import itertools
import json
import os

import numpy as np
from matplotlib import pyplot as plt

import allocation
import recording
import requests
import simulation
import storage


def parse(file: str):
	_, parts = file.split('\\')
	allocator, threshold = parts.split('-')
	return parts, allocator, threshold


def get_allocator_files():
	files = os.listdir('output')
	return itertools.groupby(files, key=lambda f: parse(f)[1])


if __name__ == '__main__':
	thresholds = (0.25, 0.5, 0.75)
	num_steps = 100_000
	num_blocks = 250
	std_out = None

	memory = storage.Memory(num_blocks)
	stream = requests.RequestStream(memory)
	best_fit = allocation.BestFit(memory, std_out=std_out)
	first_fit = allocation.FirstFit(memory, std_out=std_out)
	allocators = {'best_fit': best_fit, 'first_fit': first_fit}

	if not os.path.exists('output'):
		os.mkdir('output')

	for name, allocator in allocators.items():
		print(f'Allocator: {name}')
		for t in thresholds:
			print(f'Threshold: {t}')
			file = f"output\\{name}-{str(t).replace('.', '')}.txt"
			recorder = recording.Recorder(memory, file=file)
			defragmentor = storage.ThresholdDefragmentor(memory, threshold=t)

			simulator = simulation.Simulator(
				stream=stream,
				allocator=allocator,
				defragmentor=defragmentor,
				recorder=recorder,
				std_out=std_out)

			simulator.run(num_steps)

		memory.reset()

	groups = get_allocator_files()
	for group in groups:
		fig, ax = plt.subplots()
		summaries = ((a, s) for a, s in group if 'summary' in f)
		allocator_name = None
		str_thresh = None
		for allocator, summary in summaries:
			allocator_name = allocator
			_, _, str_thresh = parse(summary)
			with open(summary, 'r') as f:
				data = json.load(f)
			moving = data['moving_avg']
			plt.figure(figsize=(15, 4))
			x = np.arange(1, len(moving) + 1)
			ax.plot(x, moving)

		fig.set_size_inches(15, 4)
		ax.set_xlabel('Time')
		ax.set_ylabel('Fragmentation')
		allocator = f"allocator={allocator_name.replace('_', ' ')}"
		threshold = f'threshold={float(str_thresh) / 10}'
		blocks = f'blocks={num_blocks}'
		pages = f'pages={memory.total_pages}'
		params = f'{blocks}, {pages}, {allocator}, {threshold}'
		ax.set_title(f'Memory Fragmentation ({params})')
		ax.legend(thresholds)
		plt.savefig(f'{allocator}.png', dpi=400)
