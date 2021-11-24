from utils.data_classes import *
import numpy as np
import itertools

from utils.structure_operations import StructureOperations
from utils.block_operations import BlockOperations


class StrategyUtils:

	def __init__(self, structures):
		self.structures = structures
		self.structure_operations = StructureOperations()
		self.block_operations = BlockOperations()

	# returns whether the attempt can solve the structure
	def does_attempt_solves_the_structure(self, strategy_attempt: StrategyData):
		# print('does_attempt_solves_the_structure', strategy_attempt)
		for shot_data in strategy_attempt.shots_data:
			# print('shot', shot_data.shot_number)
			if shot_data.static_data_end.pig_count == 0:
				# print('structure_solved')
				return True
		return False

	# returns only the shots (StrategyAttemptSolvedStructure) that are needed for the attempt to solve the structure(removes shots without impact)
	def get_mandatory_shots_for_solving_the_structure(self, strategy_attempt: StrategyAttemptSolvedStructure):
		# print('get_mandatory_shots_for_solving_the_structure', strategy_attempt)

		optimal_strategy = StrategyAttemptSolvedStructure(strategy_attempt.structure_id, strategy_attempt.strategy_index, StrategyData(strategy_attempt.strategy_data.attempt, list()))
		for shot_data in strategy_attempt.strategy_data.shots_data:
			# print('shot', shot_data.shot_number)
			if shot_data.static_data_end.shot_has_impact:
				# print('shot has impact')
				optimal_strategy.strategy_data.shots_data.append(shot_data)

		return optimal_strategy

	def does_structure_contain_pigs(self, structure):
		# check if the structure has any pigs: by checking the number of pigs at the static_data_start
		# print('structure', structure)
		for strategy in structure.strategies:
			# for all the attempts of same strategy
			for strategy_attempt in strategy.strategy_data:
				if strategy_attempt.shots_data:
					if strategy_attempt.shots_data[0].static_data_start.pig_count > 0:
						return True
		return False

	def does_structure_contain_TNTs(self, structure_data):
		# check if the structure has any TNTs: by checking the objects in the structure
		# print('structure', structure)
		structure = self.get_structure(structure_data.id)

		for game_object in itertools.chain(structure[0], structure[1], structure[2]):
			# print(game_object.type, object_to_find.object_type)
			if game_object.type == 'TNT':
				return True
		return False

	# returns structure with structure id
	def get_structure(self, structure_id):
		return next((structure[1] for structure in self.structures if structure[0] == structure_id), None)

	def find_closest_object_considering_location(self, object_to_find, candidate_objects):
		center_of_object_to_find = object_to_find.centre
		centers_of_candidate_objects = [[centre.x, centre.y] for centre in candidate_objects]
		# print('center_of_object_to_find', center_of_object_to_find)
		# print('centers_of_candidate_objects', centers_of_candidate_objects)

		nodes = np.asarray(centers_of_candidate_objects)
		dist_2 = np.sum((nodes - center_of_object_to_find) ** 2, axis=1)
		selected_object = candidate_objects[np.argmin(dist_2)]

		print('selected object', selected_object)
		return selected_object

	# find the value a ground structure can be shifted to place properly on the ground (hiding the bottom platforms)
	def find_y_shift_value_of_ground_structure(self, structure, bounding_box_min_y):
		topmost_points_of_bottom_layer = []

		# get the blocks in the bottom most layer of the structure
		bottom_layer = self.structure_operations.find_blocks_which_cut_a_horizontal_line(structure, bounding_box_min_y + 0.2)

		# check if all the objects in the bottom layer are platforms (if not structure can not be further pushed to the ground)
		for game_object in bottom_layer:
			if game_object.type != 'Platform':
				print('non platform objects found in the bottom layer, structure can not be pushed into the ground')
				return -bounding_box_min_y

		# get the topmost points of all the platforms
		for platform in bottom_layer:
			topmost_points_of_bottom_layer.append(platform.y + self.block_operations.get_horizontal_and_vertical_span(platform)[1] / 2)

		# order the topmost points in descending order and get the highest topmost point which does not cut any block
		topmost_points_of_bottom_layer.sort(reverse=True)
		# print('topmost_points_of_bottom_layer', topmost_points_of_bottom_layer)
		for topmost_point in topmost_points_of_bottom_layer:
			# get the blocks in the level of topmost_point
			blocks_in_level = self.structure_operations.find_blocks_which_cut_a_horizontal_line(structure, topmost_point)

			# check if all the objects in the level are platforms (if not try with the next value)
			for game_object in blocks_in_level:
				if game_object.type != 'Platform':
					continue

			# if all objects ate platforms use this value as the shift value
			return -topmost_point
