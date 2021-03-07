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

