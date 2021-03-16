import attr
from attr import validators

import memory
from requests import Block, Request

NO_BLOCK = None
NoneType = type(None)


# noinspection PyUnresolvedReferences
@attr.s(slots=True)
class Algorithm:
	"""
	Attributes:
		memory: Contains all blocks of memory
	"""
	memory = attr.ib(
		type=memory.Memory, validator=validators.instance_of(memory.Memory))
	std_out = attr.ib(
		type=Optional[Union[TextIO, io.TextIOBase]],
		default=sys.stdout,
		validator=validators.instance_of((io.TextIOBase, TextIO, NoneType)),
		repr=False)

	def decide(self, request: Request):
		pass

	def allocate(self, block: Block):
		self.memory.allocate(block)
		self._print('Allocate', block)

	def free(self, block: Block):
		self.memory.free(block)
		self._print('Free', block)

	def _print(self, request_type: str, params: Any) -> NoReturn:
		if self.std_out:
			print(f'{request_type}({params})', file=self.std_out)


# Function to allocate memory to
# blocks as per First fit algorithm
def firstFit(blockSize, m, processSize, n):
	# Stores block id of the
	# block allocated to a process
	allocation = [-1] * n

	# Initially no block is assigned to any process

	# pick each process and find suitable blocks
	# according to its size ad assign to it
	for i in range(n):
		for j in range(m):
			if blockSize[j] >= processSize[i]:
				# allocate block j to p[i] process
				allocation[i] = j

				# Reduce available memory in this block.
				blockSize[j] -= processSize[i]

				break

	print(" Process No. Process Size      Block no.")
	for i in range(n):
		print(" ", i + 1, "         ", processSize[i],
			  "         ", end=" ")
		if allocation[i] != -1:
			print(allocation[i] + 1)
		else:
			print("Not Allocated")


# Function to allocate memory to blocks
# as per Best fit algorithm
def bestFit(blockSize, m, processSize, n):
	# Stores block id of the block
	# allocated to a process
	allocation = [-1] * n

	# pick each process and find suitable
	# blocks according to its size ad
	# assign to it
	for i in range(n):

		# Find the best fit block for
		# current process
		bestIdx = -1
		for j in range(m):
			if blockSize[j] >= processSize[i]:
				if bestIdx == -1:
					bestIdx = j
				elif blockSize[bestIdx] > blockSize[j]:
					bestIdx = j

		# If we could find a block for
		# current process
		if bestIdx != -1:
			# allocate block j to p[i] process
			allocation[i] = bestIdx

			# Reduce available memory in this block.
			blockSize[bestIdx] -= processSize[i]

	print("Process No. Process Size     Block no.")
	for i in range(n):
		print(i + 1, "         ", processSize[i],
			  end="         ")
		if allocation[i] != -1:
			print(allocation[i] + 1)
		else:
			print("Not Allocated")
