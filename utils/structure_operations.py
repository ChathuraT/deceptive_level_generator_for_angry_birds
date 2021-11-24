import itertools
from utils.block_operations import BlockOperations


class StructureOperations:

	def __init__(self):
		self.block_operations = BlockOperations()

	# shift the coordinates of the objects in a structure by a given value
	def shift_coordinates_of_structure(self, structure_data, axis, shift_value):
		# shift coordinates of all_blocks, all_pigs, all_tnts
		if axis == 'x':
			for game_object in itertools.chain(structure_data[0], structure_data[1], structure_data[2]):
				game_object.x += shift_value

		if axis == 'y':
			for game_object in itertools.chain(structure_data[0], structure_data[1], structure_data[2]):
				game_object.y += shift_value

	# find the bounding box of the structure (including the platforms), bounding box is enlarged with a value of bounding_box_offset
	def find_bounding_box_of_structure(self, blocks_considered, bounding_box_offset):
		# find vertical and horizontal coordinates of all the blocks
		x_coordinates = []
		y_coordinates = []
		# print(blocks_considered)
		for block in blocks_considered:
			# exclude platforms to get the correct bounding box of the structure
			# if block.type == 'Platform':
			#   continue
			# print(block)

			horizontal_span, vertical_span = self.block_operations.get_horizontal_and_vertical_span(block)
			x_coordinates.extend([block.x + horizontal_span / 2, block.x - horizontal_span / 2])
			y_coordinates.extend([block.y + vertical_span / 2, block.y - vertical_span / 2])

		# find the min and max x and y values as the bounding box of the blocks
		return [min(x_coordinates) - bounding_box_offset, max(x_coordinates) + bounding_box_offset,
				min(y_coordinates) - bounding_box_offset,
				max(y_coordinates) + bounding_box_offset]

	# check if given set of bounding boxes overlap each other
	def do_bounding_boxes_overlap(self, bounding_boxes):
		for i in range(0, len(bounding_boxes)):
			for j in range(i + 1, len(bounding_boxes)):
				# print(i, j)
				if self.check_interval_overlap(bounding_boxes[i][:2], bounding_boxes[j][:2]) and self.check_interval_overlap(bounding_boxes[i][2:], bounding_boxes[j][2:]):
					print('structures overlapped!')
					return True
		return False

	# for bounding_box_1 in bounding_boxes:
	# 	if check_interval_overlap(space[:2], candidate_horizontal_width) and check_interval_overlap(space[2:],candidate_vertical_width):
	# 		location_occupied = True

	# check whether 2 intervals overlap
	def check_interval_overlap(self, interval_1, interval_2, interval_overlap_offset_value=0.0):
		# print('check_interval_overlap', interval_1, interval_2)
		interval_width_1 = interval_1[1] - interval_1[0]
		interval_1_centre = interval_1[0] + interval_width_1 / 2
		interval_width_2 = interval_2[1] - interval_2[0]
		interval_2_centre = interval_2[0] + interval_width_2 / 2

		# check whether given 2 intervals overlap

		return (max(interval_1_centre + interval_width_1 / 2, interval_2_centre + interval_width_2 / 2) - min(
			interval_1_centre - interval_width_1 / 2, interval_2_centre - interval_width_2 / 2)) < (interval_width_1 + interval_width_2 - interval_overlap_offset_value)

	# classify all the game objects into separate types
	def get_all_game_objects_filtered(self, all_structures_data):
		all_blocks = []
		all_pigs = []
		all_tnts = []
		all_birds = []

		# combine data in all the structures
		for structure in all_structures_data:
			all_blocks += structure[0]
			all_pigs += structure[1]
			all_tnts += structure[2]
			all_birds += structure[3]

		return all_blocks, all_pigs, all_tnts, all_birds

	# returns the blocks which are cut by a horizontal line
	def find_blocks_which_cut_a_horizontal_line(self, structure, line):
		selected_blocks = []

		for block in structure:
			vertical_span = self.block_operations.get_horizontal_and_vertical_span(block)[1]

			# check if the block lies on the line
			# print('line, min mid max', line, block.y - vertical_span / 2, block.y, block.y + vertical_span / 2)
			if block.y - vertical_span / 2 < line and line < block.y + vertical_span / 2:
				# print('added')
				selected_blocks.append(block)

		return selected_blocks
