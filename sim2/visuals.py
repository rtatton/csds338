from typing import Sequence

import numpy as np
from matplotlib import lines, pyplot as plt

import philosopher

State = philosopher.PhilosopherState
STATES = (State.THINKING, State.EATING, State.WAITING)
STATE_TO_IDX = {State.THINKING: 1, State.EATING: 2, State.WAITING: 3}
IDX_TO_STATE = {1: State.THINKING, 2: State.EATING, 3: State.WAITING}

COLORS = {
	State.WAITING: 'tomato',
	State.THINKING: 'deepskyblue',
	State.EATING: 'chartreuse'}


def to_numpy(seqs: Sequence[Sequence[State]], expand=False):
	seqs = np.array([[STATE_TO_IDX[s] for s in seq] for seq in seqs])
	if expand:
		seqs = np.array([[
			np.where(seq == STATE_TO_IDX[s], STATE_TO_IDX[s], 0)
			for s in STATES] for seq in seqs])
	return seqs


def event_plot(events: Sequence[Sequence[State]], save_as: str):
	def plot_phil(axis, phil_events):
		for y, row in enumerate(phil_events):
			cols = ((t, col) for t, col in enumerate(row) if col != 0)
			for t, col in cols:
				axis.fill_between(
					x=(t, t + 1),
					y1=(0, 0),
					y2=(1, 1),
					color=COLORS[IDX_TO_STATE[col]])

	events = to_numpy(events, expand=True)
	fig, axes = plt.subplots(events.shape[0], 1)
	axes[-1].set_xlabel('Time')
	axes[0].set_title('Dining Philosopher States')
	for p, (ax, phil) in enumerate(zip(axes, events)):
		ax.get_yaxis().set_visible(True)
		ax.set_yticks([])
		ax.set_ylabel(f'P{p}', rotation=0, position=(0, 0.5), labelpad=10)
		if p != len(events) - 1:
			ax.set_xticks([])
		plot_phil(ax, phil)
	legend = [lines.Line2D([0], [0], color=COLORS[s], lw=4) for s in STATES]
	plt.legend(legend, [s.value for s in STATES], bbox_to_anchor=(1.3, 3))
	plt.savefig(save_as, dpi=400, bbox_inches='tight')
