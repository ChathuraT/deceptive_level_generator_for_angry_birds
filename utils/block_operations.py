import math
from utils.constants import *


class BlockOperations:
	def get_horizontal_and_vertical_span(self, block_considered):
		# returns the horizontal and vertical span of a given object

		location_offset_x = 0.1  # used to reduce the horizontal span of the round blocks (which's base is not fully touched)

		horizontal_span_of_the_block = 0
		vertical_span_of_the_block = 0

		# print('block_considered', type(block_considered))
		# print('xxx', '<class \'__main__.Pig\'>' == str(type(block_considered)))
		# print('xxx', '<class \'__main__.Block\'>' == str(type(block_considered)))

		block_rotation = self.get_adjusted_block_rotation(block_considered)

		# if isinstance(block_considered, Block):
		if '<class \'utils.data_classes.Block\'>' == str(type(block_considered)):
			vertical_span_of_the_block = abs(
				(blocks[block_considered.type][0] * block_considered.scale_x) * math.sin(
					math.radians(block_rotation))) + abs(
				(blocks[block_considered.type][1] * block_considered.scale_y) * math.cos(
					math.radians(block_rotation)))
			horizontal_span_of_the_block = abs(
				(blocks[block_considered.type][0] * block_considered.scale_x) * math.cos(
					math.radians(block_rotation))) + abs(
				(blocks[block_considered.type][1] * block_considered.scale_y) * math.sin(
					math.radians(block_rotation)))
		# elif isinstance(block_considered, Pig):
		elif '<class \'utils.data_classes.Pig\'>' == str(type(block_considered)):
			vertical_span_of_the_block = abs(
				(pigs[block_considered.type][0]) * math.sin(math.radians(block_rotation))) + abs(
				(pigs[block_considered.type][1]) * math.cos(math.radians(block_rotation)))
			horizontal_span_of_the_block = abs(
				(pigs[block_considered.type][0]) * math.cos(math.radians(block_rotation))) + abs(
				(pigs[block_considered.type][1]) * math.sin(math.radians(block_rotation))) - location_offset_x
		elif '<class \'utils.data_classes.Tnt\'>' == str(type(block_considered)):
			vertical_span_of_the_block = abs(
				(tnts[block_considered.type][0]) * math.sin(math.radians(block_rotation))) + abs(
				(tnts[block_considered.type][1]) * math.cos(math.radians(block_rotation)))
			horizontal_span_of_the_block = abs(
				(tnts[block_considered.type][0]) * math.cos(math.radians(block_rotation))) + abs(
				(tnts[block_considered.type][1]) * math.sin(math.radians(block_rotation))) - location_offset_x
		else:
			print('Unknown Object!')

		return horizontal_span_of_the_block, vertical_span_of_the_block

	# check the rotation of the block and return the round offed rotation if not slanted
	def get_adjusted_block_rotation(self, block):
		# the threshold degree by which the object's rotation is ignored
		slanting_threshold = 5

		if self.is_slanted_block(block):
			return block.rotation
		else:
			rotation = abs(block.rotation)
			if rotation < slanting_threshold:
				return 0
			elif abs(block.rotation - 90) < slanting_threshold:
				return 90
			elif abs(block.rotation - 180) < slanting_threshold:
				return 180
			elif abs(block.rotation - 270) < slanting_threshold:
				return 270
			elif abs(block.rotation - 360) < slanting_threshold:
				return 360

	# check if the block is slanted
	def is_slanted_block(self, block):
		# the threshold degree by which the object's rotation is ignored
		slanting_threshold = 5

		if abs(block.rotation) < slanting_threshold or abs(block.rotation - 90) < slanting_threshold or abs(
				block.rotation - 180) < slanting_threshold or abs(block.rotation - 270) < slanting_threshold or abs(
			block.rotation - 360) < slanting_threshold or abs(block.rotation + 90) < slanting_threshold or abs(
			block.rotation + 180) < slanting_threshold or abs(block.rotation + 270) < slanting_threshold or abs(
			block.rotation + 360) < slanting_threshold:
			return False

		return True

	# check whether a given line (in USC coordinates) intersects an object (in LGSC coordinate), slanted game objects are not precisely handled
	def line_intersects_object(self, line, game_object):
		# get the bounding box of the game object
		bounding_box = self.find_bounding_box_of_object(game_object)

		# get the line segments of the bounding box and convert them to USC
		bounding_box_line_segments = [[self.convert_wc_to_usc([bounding_box[0], bounding_box[2]]), self.convert_wc_to_usc([bounding_box[0], bounding_box[3]])],
									  [self.convert_wc_to_usc([bounding_box[0], bounding_box[3]]), self.convert_wc_to_usc([bounding_box[1], bounding_box[3]])],
									  [self.convert_wc_to_usc([bounding_box[1], bounding_box[3]]), self.convert_wc_to_usc([bounding_box[1], bounding_box[2]])],
									  [self.convert_wc_to_usc([bounding_box[1], bounding_box[2]]), self.convert_wc_to_usc([bounding_box[0], bounding_box[2]])]]

		return (self.line_intersects_line(line, bounding_box_line_segments[0]) or self.line_intersects_line(line, bounding_box_line_segments[1]) or
				self.line_intersects_line(line, bounding_box_line_segments[2]) or self.line_intersects_line(line, bounding_box_line_segments[3]))

	# returns the bounding box of a given object (min_x, max_x, min_y, max_y)
	def find_bounding_box_of_object(self, game_object):
		horizontal_span, vertical_span = self.get_horizontal_and_vertical_span(game_object)
		return [game_object.x - horizontal_span / 2, game_object.x + horizontal_span / 2, game_object.y - vertical_span / 2, game_object.y + vertical_span / 2]

	# ccw -> counter-clockwise
	def counter_clock_wise(self, p1, p2, p3):
		return (p3[1] - p1[1]) * (p2[0] - p1[0]) > (p2[1] - p1[1]) * (p3[0] - p1[0])

	# determines if two lines intersect (line1 2 points: l1p1, l1p2 and line2 2 points:  l2p1, l2p2)
	def line_intersects_line(self, line_1, line_2):
		l1p1, l1p2 = line_1[0], line_1[1]
		l2p1, l2p2 = line_2[0], line_2[1]
		return self.counter_clock_wise(l1p1, l2p1, l2p2) != self.counter_clock_wise(l1p2, l2p1, l2p2) and self.counter_clock_wise(l1p1, l1p2, l2p1) != self.counter_clock_wise(l1p1, l1p2, l2p2)

	# convert a given coordinate from science birds(world) coordinates to unity screen coordinate
	def convert_wc_to_usc(self, coordinate):
		# print('sbc_coordinate', sbc_coordinate)
		usc_coordinate = [usc_x_offset + coordinate[0] * usc_x_scale, usc_y_offset - coordinate[1] * usc_y_scale]
		# usc_coordinate = [292 + sbc_coordinate[0] * 16, 126.5 - sbc_coordinate[1] * 16]
		# print('usc_coordinate', usc_coordinate)

		return usc_coordinate

	# convert the trajectory path in usc to wc
	def convert_trajectory_to_wc_from_usc(self, trajectory_points):
		for point in trajectory_points:
			point[0] = (point[0] - usc_x_offset) / usc_x_scale
			point[1] = (usc_y_offset - point[1]) / usc_y_scale

		return trajectory_points
