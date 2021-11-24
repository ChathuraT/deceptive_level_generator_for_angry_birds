import copy
import itertools
from random import randint, uniform

from utils.data_classes import *
from utils.constants import *
from utils.structure_operations import StructureOperations
from utils.block_operations import BlockOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.io_handler import IOHandler


class MaterialAnalysisDeception:

	def __init__(self, analysis_data, structures):
		self.analysis_data = analysis_data
		self.structures = structures
		self.structure_operations = StructureOperations()
		self.block_operations = BlockOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()
		self.utils = StrategyUtils(structures)

	# with the given best 10 attempts of the 5 birds types returns the strategy which outperforms other
	def get_attempt_which_outperforms_other(self, attempts_of_different_birds):
		no_of_shots_in_strategies = []
		attempt_index = 0
		for attempt in attempts_of_different_birds:
			if not attempt:  # when the structure is not solved by the attempt
				no_of_shots_in_strategies.append([attempt_index, -1])
			else:
				no_of_shots_in_strategies.append([attempt_index, len(attempt.strategy_data.shots_data)])

			attempt_index += 1

		# no_of_shots_in_strategies = [-1,-1,-1,-1]
		# no_of_shots_in_strategies_copy = no_of_shots_in_strategies.copy()

		print('no_of_shots_in_strategies', no_of_shots_in_strategies)
		# get the strategy with the least shot count (disregard black bird strategies)
		least_number_of_shots = 99999
		strategy_with_least_number_of_shots = None
		more_than_one_strategy_with_least_number_of_shots = False

		for no_of_shots_in_strategy in no_of_shots_in_strategies:
			# skip strategies which do not solve the strategy
			if no_of_shots_in_strategy[1] == -1:
				continue
			elif no_of_shots_in_strategy[0] == 4 or no_of_shots_in_strategy[0] == 9:
				# skip black bird strategies
				continue
			elif no_of_shots_in_strategy[1] == least_number_of_shots:
				# there are more than one strategy with least number of shots
				# if it is from the same bird strategy, then it is ok
				if strategy_with_least_number_of_shots[0] + 5 == no_of_shots_in_strategy[0]:
					continue
				more_than_one_strategy_with_least_number_of_shots = True
			# print('strategy_with_least_number_of_shots[0] no_of_shots_in_strategy[0]', strategy_with_least_number_of_shots[0], no_of_shots_in_strategy[0])

			elif no_of_shots_in_strategy[1] < least_number_of_shots:
				strategy_with_least_number_of_shots = no_of_shots_in_strategy
				least_number_of_shots = no_of_shots_in_strategy[1]
				more_than_one_strategy_with_least_number_of_shots = False

		# if there are more than one strategy with least number of shots: no birds outperforms all the other birds
		if more_than_one_strategy_with_least_number_of_shots:
			print('there are more than one strategy with least number of shots', least_number_of_shots)
			return

		if least_number_of_shots == 99999:
			print('none of the non-black bird strategy solves the structure')
			# none of the strategies solved the structure check black birds strategies
			if no_of_shots_in_strategies[4][1] != -1:
				# black bird lower strategy solves the structure: return it
				strategy_with_least_number_of_shots = no_of_shots_in_strategies[4]
			elif no_of_shots_in_strategies[9][1] != -1:
				# black bird higher strategy solves the structure: return it
				strategy_with_least_number_of_shots = no_of_shots_in_strategies[9]
			else:
				# none of the strategies solves the structure
				print('none of the strategies solves the structure')
				return

		print('strategy_with_least_number_of_shots', strategy_with_least_number_of_shots)
		# return the strategy which outperform others
		return attempts_of_different_birds[strategy_with_least_number_of_shots[0]]

	# # check if one attempt outperforms others
	# no_of_shots_in_strategies_copy.sort()
	# try:
	# 	least_valid_shot_count = [i for i, i in enumerate(no_of_shots_in_strategies_copy) if i > 0][0]
	# except:  # first 3 birds do not solve the structure
	# 	least_valid_shot_count = -1
	# 	return
	#
	# print('no_of_shots_in_strategies_copy', no_of_shots_in_strategies_copy)
	# print('least_valid_shot_count', least_valid_shot_count)
	#
	# if least_valid_shot_count > 0:  # there are strategies which solves the structure
	# 	# check if it is a blackbird strategy (4 and 9 are black birds low and high strategies)
	# 	# if no_of_shots_in_strategies.index(least_valid_shot_count) == 4 or no_of_shots_in_strategies.index(least_valid_shot_count) == 9:
	# 	# 	# if so check the next least shot strategy
	# 	#
	# 	# if there are other strategies with the same shot count, no strategy outperforms the other
	# 	if no_of_shots_in_strategies_copy.count(least_valid_shot_count) > 1:
	# 		print('none of the birds outperforms others')
	# 		return
	#
	# elif least_valid_shot_count == -1:  # none of the strategies solved the structure, check whether the black bird could solve it
	# 	if no_of_shots_in_strategies[-1] > -1:
	# 		print('black bird outperforms others')
	# 		return attempts_of_different_birds[-1]
	# 	else:
	# 		print('no any bird has solved the structure')
	# 		return  # none of the strategies including the black bird did not solve the structure

	# return the outperforming strategy
	# return attempts_of_different_birds[no_of_shots_in_strategies.index(least_valid_shot_count)]

	def find_candidate_structures_for_material_deception_old(self, strategies_to_analyze):
		candidate_structure_solving_strategies = []

		# for all the structures
		for structure_data in self.analysis_data:
			# best_attempt_of strategies_to_analyze
			best_attempts_of_strategies_to_analyze = []

			# check if the structure contains pigs
			if not self.utils.does_structure_contain_pigs(structure_data):
				print('structure', structure_data.id, ' does not contain pigs or pigs are unreachable')
				continue

			# get the best strategy attempt of strategies_to_analyze
			for strategy in structure_data.strategies:
				if strategy.index not in strategies_to_analyze:
					continue

				best_solving_strategy_attempt_of_strategy = self.find_best_strategy_attempt_of_strategy(structure_data.id, strategy)

				best_attempts_of_strategies_to_analyze.append(best_solving_strategy_attempt_of_strategy)

			# find results of one strategy (bird type) outperforms another
			outperforming_strategy = self.get_attempt_which_outperforms_other(best_attempts_of_strategies_to_analyze)

			if outperforming_strategy:
				candidate_structure_solving_strategies.append(outperforming_strategy)

		print('number_of_candidate structures', len(candidate_structure_solving_strategies))
		print('candidate_structure_solving_strategies', candidate_structure_solving_strategies)
		return candidate_structure_solving_strategies

	# given the best attempts of 10 strategies (2 for each 5 birds), get the best trajectory selection for the bird (return 5 strategies)
	def find_best_trajectory_attempts(self, best_attempt_of_each_strategy):
		best_trajectory_attempts = []

		# get the shot count of each attempt
		no_of_shots_in_strategies = []
		attempt_index = 0
		for attempt in best_attempt_of_each_strategy:
			if not attempt:  # when the structure is not solved by the attempt
				no_of_shots_in_strategies.append(-1)
			else:
				no_of_shots_in_strategies.append(len(attempt.strategy_data.shots_data))

			attempt_index += 1
		print('no_of_shots_in_strategies', no_of_shots_in_strategies)

		# trajectory with least shots is considered as the best trajectory attempt, get the best attempt from high and low trajectories for each bird
		for i in range(0, 5):
			if no_of_shots_in_strategies[i] == -1:
				best_trajectory_attempts.append(best_attempt_of_each_strategy[i + 5])
			elif no_of_shots_in_strategies[i + 5] == -1:
				best_trajectory_attempts.append(best_attempt_of_each_strategy[i])
			else:
				if no_of_shots_in_strategies[i] <= no_of_shots_in_strategies[i + 5]:
					best_trajectory_attempts.append(best_attempt_of_each_strategy[i])
				else:
					best_trajectory_attempts.append(best_attempt_of_each_strategy[i + 5])
		print('best_trajectory_attempts', best_trajectory_attempts)
		return best_trajectory_attempts

	def find_candidate_structures_for_material_deception(self, strategies_to_analyze):
		candidate_structure_solving_strategies = []

		# for all the structures
		for structure_data in self.analysis_data:
			# best_attempt_of strategies_to_analyze
			best_attempts_of_strategies_to_analyze = []

			# check if the structure contains pigs
			if not self.utils.does_structure_contain_pigs(structure_data):
				print('structure', structure_data.id, ' does not contain pigs or pigs are unreachable')
				continue

			# get the best strategy attempt of strategies_to_analyze
			for strategy in structure_data.strategies:
				if strategy.index not in strategies_to_analyze:
					continue

				best_solving_strategy_attempt_of_strategy = self.find_best_strategy_attempt_of_strategy(structure_data.id, strategy)

				best_attempts_of_strategies_to_analyze.append(best_solving_strategy_attempt_of_strategy)

			# print('best_attempts_of_strategies_to_analyze', best_attempts_of_strategies_to_analyze)

			# find the best trajectory selection for each bird (strategy) (combine 10 strategies to 5)
			best_attempts_of_birds = self.find_best_trajectory_attempts(best_attempts_of_strategies_to_analyze)

			candidate_structure_solving_strategies.append(best_attempts_of_birds)

		print('number_of_candidate structures', len(candidate_structure_solving_strategies))
		# print('candidate_structure_solving_strategies', candidate_structure_solving_strategies)
		return candidate_structure_solving_strategies

	def find_best_strategy_attempt_of_strategy(self, structure_id, strategy: Strategy):
		# find best solving strategy attempt which solves a given structure
		print('## find_structure_solving_strategies of structure:', structure_id, 'index:', strategy.index, '##')
		strategy_attempts_solved_the_structure = []

		# for all the attempts of the same strategy
		for strategy_attempt in strategy.strategy_data:
			# print('strategy', strategy.index, 'attempt', strategy_attempt.attempt)
			if self.utils.does_attempt_solves_the_structure(strategy_attempt):
				strategy_attempts_solved_the_structure.append(StrategyAttemptSolvedStructure(structure_id, strategy.index, strategy_attempt))

			# check if the structure does not have any pigs (structure which is not needed to solve) by checking the number of pigs at the start of the first strategy
			if strategy_attempt.shots_data:
				if strategy_attempt.shots_data[0].static_data_start.pig_count == 0:
					return []

		# if no strategy attempt solves the structure return
		if not strategy_attempts_solved_the_structure:
			print('None of the attempts of the strategy solved the structure')
			return []

		# from all the strategies which solves the structure find the one with least shots
		minimal_strategy_attempts_solved_the_structure = []
		for strategy_attempt in strategy_attempts_solved_the_structure:
			minimal_strategy_attempts_solved_the_structure.append(self.utils.get_mandatory_shots_for_solving_the_structure(strategy_attempt))

		# print('minimal_strategy_attempts_solved_the_structure', minimal_strategy_attempts_solved_the_structure)

		# from the optimal strategies get the number of shots needed for each strategy attempt
		shot_count_of_strategy_attempt = []
		for strategy_attempt in minimal_strategy_attempts_solved_the_structure:
			shot_count_of_strategy_attempt.append(len(strategy_attempt.strategy_data.shots_data))
		print('shot_count_of successful strategy_attempts', shot_count_of_strategy_attempt)

		# order the strategies in minimal_strategy_attempts_solved_the_structure according to the number of shots
		sort_indexes = sorted(range(len(shot_count_of_strategy_attempt)), key=lambda k: shot_count_of_strategy_attempt[k])
		ordered_minimal_strategy_attempts_solved_the_structure = [minimal_strategy_attempts_solved_the_structure[i] for i in sort_indexes]

		# return the first strategy with minimal number of shots
		return ordered_minimal_strategy_attempts_solved_the_structure[0]

	def place_structures_on_level(self, structure_solving_strategies: [StrategyAttemptSolvedStructure]):
		# get the strategy to solve the generating level
		birds_needed, solving_strategy = self.determine_number_of_birds_for_material_deception(structure_solving_strategies)
		all_structures = []
		structure_ids_of_all_structures = []

		for structure_solving_strategy in structure_solving_strategies:
			# get a copy of the structures
			print('structure_solving_strategy.structure_id', structure_solving_strategy.structure_id)
			all_structures.append(copy.deepcopy(self.utils.get_structure(structure_solving_strategy.structure_id)))
			structure_ids_of_all_structures.append(structure_solving_strategy.structure_id)

		# calculate the bounding box of the structure
		print('structure_data', all_structures)
		bounding_box_of_structures = []
		for structure_data in all_structures:
			bounding_box_of_structures.append(self.structure_operations.find_bounding_box_of_structure(itertools.chain(structure_data[0], structure_data[1], structure_data[2]), 0))

		print('bounding_box_of_structures', bounding_box_of_structures)

		# check if bounding boxes of the 2 structures overlap
		if self.structure_operations.check_interval_overlap([bounding_box_of_structures[0][0], bounding_box_of_structures[0][1]],
															[bounding_box_of_structures[1][0], bounding_box_of_structures[1][1]]) and self.structure_operations.check_interval_overlap(
			[bounding_box_of_structures[0][2], bounding_box_of_structures[0][3]], [bounding_box_of_structures[1][2], bounding_box_of_structures[1][3]]):
			return []

		# check whether all the target objects are reachable
		if not self.check_the_solution_target_reachability(solving_strategy, all_structures):
			print('## Generated layout does not satisfy meta constraints! ##')
			return []

		return all_structures, birds_needed, solving_strategy

	def place_structures_on_level_old(self, structure_solving_strategies: [StrategyAttemptSolvedStructure]):  # todo: only tested for 2 structures

		# place the first structure on ground
		# bounding_box_structure_1 = self.structure_operations.find_bounding_box_of_structure(itertools.chain(structure_1[0], structure_1[1], structure_1[2]), 0)
		# shift_value = ground_level - bounding_box_structure_1[2]
		# self.structure_operations.shift_coordinates_of_structure(structure_1, 'y', shift_value)
		# # update the bounding box of the structure
		# bounding_box_structure_1[2] += shift_value
		# bounding_box_structure_1[3] += shift_value
		# # place the second structure in a place which does not overlap with the already placed structure

		# max number of attempts to create the level layout
		max_attempts_to_create_level_layout = 10
		# number of attempts to place a structure
		max_attempts_to_place_ground_structure = 100
		max_attempts_to_place_platform_structure = 100

		number_of_all_structures = len(structure_solving_strategies)
		layout_successfully_generated = False
		attempts_to_create_level_layout = 0
		complete_level_layout = []
		solving_strategy_tmp = None

		# get the strategy to solve the generating level
		birds_needed, solving_strategy = self.determine_number_of_birds_for_material_deception(structure_solving_strategies)

		while not layout_successfully_generated:
			all_structures = []
			structure_ids_of_all_structures = []
			for structure_solving_strategy in structure_solving_strategies:
				# get a copy of the structures
				print('structure_solving_strategy.structure_id', structure_solving_strategy.structure_id)
				all_structures.append(copy.deepcopy(self.utils.get_structure(structure_solving_strategy.structure_id)))
				structure_ids_of_all_structures.append(structure_solving_strategy.structure_id)

			# dividing the total number of structures randomly to the ground and platforms
			number_of_ground_structures = randint(1, number_of_all_structures)
			number_of_platform_structures = randint(1, number_of_all_structures)
			sum_of_ground_and_platform = number_of_ground_structures + number_of_platform_structures
			number_of_ground_structures = round(number_of_ground_structures * number_of_all_structures / sum_of_ground_and_platform)
			number_of_platform_structures = round(number_of_platform_structures * number_of_all_structures / sum_of_ground_and_platform)
			number_of_ground_structures = number_of_ground_structures + (number_of_all_structures - number_of_ground_structures - number_of_platform_structures)
			print('number_of_ground_structures', number_of_ground_structures)
			print('number_of_platform_structures', number_of_platform_structures)

			# calculate the width and height of all the structures
			print('structure_data', all_structures)
			bounding_box_of_structures = []
			for structure_data in all_structures:
				print('structure_data', structure_data)
				bounding_box_of_structures.append(self.structure_operations.find_bounding_box_of_structure(itertools.chain(structure_data[0], structure_data[1], structure_data[2]), 0))

			print('bounding_box_of_structures', bounding_box_of_structures)

			checked_structure_indexes = []
			ground_structure_indexes = []
			platform_structure_indexes = []
			ground_locations_occupied = [0] * number_of_all_structures  # (x)
			platform_locations_occupied = [[0, 0]] * number_of_all_structures  # (x,y)
			spaces_occupied = [[0, 0, 0, 0]] * number_of_all_structures  # (x_min,x_max,y_min,y_max)

			# place the ground structures randomly
			print('## placing', number_of_ground_structures, 'ground structures ##')

			for i in range(number_of_ground_structures):
				# get the index of a random structure to place on ground
				selected_structure_index = randint(0, number_of_all_structures - 1)
				while selected_structure_index in checked_structure_indexes:
					selected_structure_index = randint(0, number_of_all_structures - 1)

				checked_structure_indexes.append(selected_structure_index)
				print('checked_structure_indexes', checked_structure_indexes)

				structure_half_width = (bounding_box_of_structures[selected_structure_index][1] - bounding_box_of_structures[selected_structure_index][0]) / 2

				# find a random ground location (x) which is not already occupied
				location_occupied = True
				candidate_ground_location = None
				candidate_ground_width = None
				number_of_attempts = 0

				while location_occupied:
					location_occupied = False

					# get a random location on the ground
					candidate_ground_location = uniform(level_width_min + structure_half_width, level_width_max - structure_half_width)
					# candidate_ground_location = uniform(structure_half_width, (level_width_max - level_width_min) - structure_half_width)
					candidate_ground_width = [candidate_ground_location - structure_half_width, candidate_ground_location + structure_half_width]

					# print('candidate_ground_location', candidate_ground_location)

					# check whether the space is already occupied
					for space in spaces_occupied:
						# checking only the horizontal overlap is enough
						if self.structure_operations.check_interval_overlap(space[:2], candidate_ground_width):
							location_occupied = True
							break

					number_of_attempts += 1
					# disregard the structure if the number of attempts exceeds the max_attempts_to_place_structure
					if number_of_attempts >= max_attempts_to_place_ground_structure:
						print('# structure placing failed', selected_structure_index, ' #')
						break

				# save the location of the structure if it was successful to find a place
				if not location_occupied:
					print('# structure placed successfully', selected_structure_index, ' #')

					ground_locations_occupied[selected_structure_index] = candidate_ground_location
					spaces_occupied[selected_structure_index] = candidate_ground_width + [bounding_box_of_structures[selected_structure_index][2],
																						  bounding_box_of_structures[selected_structure_index][3]]
					ground_structure_indexes.append(selected_structure_index)

				print('ground_locations_occupied', ground_locations_occupied)
				print('spaces_occupied', spaces_occupied)

			# place platform structures randomly
			print('## placing', number_of_platform_structures, 'platform structures ##')

			for i in range(number_of_platform_structures):
				# get the index of a random structure to place on a platform
				selected_structure_index = randint(0, number_of_all_structures - 1)
				while selected_structure_index in checked_structure_indexes:
					selected_structure_index = randint(0, number_of_all_structures - 1)

				checked_structure_indexes.append(selected_structure_index)
				print('checked_structure_indexes', checked_structure_indexes)

				structure_half_width = (bounding_box_of_structures[selected_structure_index][1] - bounding_box_of_structures[selected_structure_index][0]) / 2
				structure_half_height = (bounding_box_of_structures[selected_structure_index][3] - bounding_box_of_structures[selected_structure_index][2]) / 2

				# get a random space location which is not already occupied
				location_occupied = True
				candidate_space_location = None
				candidate_horizontal_width = None
				candidate_vertical_width = None
				number_of_attempts = 0

				while location_occupied:
					location_occupied = False

					# get a random space location (x,y)
					# candidate_space_location = [uniform(structure_half_width, (level_width_max - level_width_min) - structure_half_width),
					# 							uniform(structure_half_height, (level_height_max - level_height_min) - structure_half_height)]
					# print('candidate_space_location', candidate_space_location)
					candidate_space_location = [uniform(level_width_min + structure_half_width, level_width_max - structure_half_width),
												uniform(level_height_min + structure_half_height, level_height_max - structure_half_height)]
					candidate_horizontal_width = [candidate_space_location[0] - structure_half_width, candidate_space_location[0] + structure_half_width]
					candidate_vertical_width = [candidate_space_location[1] - structure_half_height, candidate_space_location[1] + structure_half_height]

					# print('candidate_ground_location', candidate_ground_location)

					# check whether the space is already occupied
					for space in spaces_occupied:
						# checking the horizontal and vertical intervals overlap with already placed structures
						if self.structure_operations.check_interval_overlap(space[:2], candidate_horizontal_width) and self.structure_operations.check_interval_overlap(space[2:],
																																										candidate_vertical_width):
							location_occupied = True
							break

					number_of_attempts += 1
					# disregard the structure if the number of attempts exceeds the max_attempts_to_place_structure
					if number_of_attempts >= max_attempts_to_place_platform_structure:
						print('# structure placing failed', selected_structure_index, ' #')
						break

				# save the location of the structure if it was successful to find a place
				if not location_occupied:
					print('# structure placed successfully', selected_structure_index, ' #')

					platform_locations_occupied[selected_structure_index] = candidate_space_location
					spaces_occupied[selected_structure_index] = candidate_horizontal_width + candidate_vertical_width
					platform_structure_indexes.append(selected_structure_index)

				print('platform_locations_occupied', platform_locations_occupied)
				print('spaces_occupied', spaces_occupied)

			# solving_strategy_tmp is used to save the adjusted coordinates when structures are shifting
			solving_strategy_tmp = solving_strategy

			# adjust the coordinates of ground structures
			for i in range(len(all_structures)):

				# get only the ground structures
				if i not in ground_structure_indexes:
					continue

				# adjust x and y coordinates
				x_shift_value = ground_locations_occupied[i] - (bounding_box_of_structures[i][0] + (bounding_box_of_structures[i][1] - bounding_box_of_structures[i][0]) / 2)
				# print('x_shift_value', x_shift_value)
				self.structure_operations.shift_coordinates_of_structure(all_structures[i], 'x', x_shift_value)

				# for ground structures keep the base platform under the ground
				y_shift_value = self.utils.find_y_shift_value_of_ground_structure(all_structures[i][0], bounding_box_of_structures[i][2])
				# print('y_shift_value', y_shift_value)

				self.structure_operations.shift_coordinates_of_structure(all_structures[i], 'y', y_shift_value)

				# shift the coordinates of the target object of the strategy
				solving_strategy_tmp = self.adjust_coordinates_of_solving_strategy(solving_strategy, x_shift_value, y_shift_value, structure_ids_of_all_structures[i])

			# adjust the coordinates of platform structures
			for i in range(len(all_structures)):

				# get only the platform structures
				if i not in platform_structure_indexes:
					continue

				# adjust x coordinates
				x_shift_value = platform_locations_occupied[i][0] - (bounding_box_of_structures[i][0] + (bounding_box_of_structures[i][1] - bounding_box_of_structures[i][0]) / 2)
				# print('x_shift_value', x_shift_value)
				self.structure_operations.shift_coordinates_of_structure(all_structures[i], 'x', x_shift_value)

				# adjust y coordinates
				y_shift_value = platform_locations_occupied[i][1] - (bounding_box_of_structures[i][2] + (bounding_box_of_structures[i][3] - bounding_box_of_structures[i][2]) / 2)
				# print('y_shift_value', y_shift_value)

				self.structure_operations.shift_coordinates_of_structure(all_structures[i], 'y', y_shift_value)

				# shift the coordinates of the target object of the strategy
				solving_strategy_tmp = self.adjust_coordinates_of_solving_strategy(solving_strategy_tmp, x_shift_value, y_shift_value, structure_ids_of_all_structures[i])

			# filter out all the ground and platform structures and return
			ground_structures = [all_structures[i] for i in ground_structure_indexes]
			platform_structures = [all_structures[i] for i in platform_structure_indexes]
			complete_level_layout = ground_structures + platform_structures

			# attempts_to_create_level_layout += 1

			# check whether all the target objects are reachable
			if self.check_the_solution_target_reachability(solving_strategy_tmp, all_structures):
				layout_successfully_generated = True
			else:
				print('## Generated layout does not satisfy meta constraints! ##')
				if attempts_to_create_level_layout + 1 == max_attempts_to_create_level_layout:
					return []

			attempts_to_create_level_layout += 1

		# print('ground_structures', ground_structures)
		# print('platform_structures', platform_structures)
		# print('complete_level_layout inside ', complete_level_layout)
		return complete_level_layout, birds_needed, solving_strategy_tmp

	def adjust_coordinates_of_solving_strategy(self, solving_strategy, x_shift_value, y_shift_value, structure_id):
		# adjust the original locations of the targets in the solving_strategy by the coordinate shifts done when matching the structures

		solving_strategy = copy.deepcopy(solving_strategy)  # stop propagating the changes to the original data structures

		for solution_shot_data in solving_strategy:
			shot_data = solution_shot_data.shot_data
			if shot_data.target_object.object_type == 'any_pig':  # skip any pig selection
				continue
			elif solution_shot_data.structure_id == structure_id:  # shift the coordinates of other targets
				shot_data.target_object.centre[0] += x_shift_value
				shot_data.target_object.centre[1] += y_shift_value

		return solving_strategy

	def check_the_solution_target_reachability(self, solving_strategy, selected_structures):
		# print('selected_structures', selected_structures)
		selected_structures_combined = self.structure_operations.get_all_game_objects_filtered(selected_structures)
		for solution_shot_data in solving_strategy:
			shot_data = solution_shot_data.shot_data

			# if target object is 'any_pig' which is not included in the strategy skip it
			if shot_data.target_object.object_type == 'any_pig':
				continue

			# find the target object in the structure
			target_object = self.find_game_object_in_the_structure(selected_structures_combined, shot_data.target_object)
			# check the reachability of the object
			trajectory_selection_for_reachability = 'low' if solution_shot_data.shot_data.trajectory_selection == 1 else 'high'
			if not self.trajectory_planner.find_reachability_of_object(selected_structures, target_object, trajectory_selection_for_reachability, 'partial', solution_shot_data.structure_id, None):
				return False
		print('all targets are reachable')
		return True

	# find a gameobject in TargetObject version in the original structure (only blocks and pigs)
	def find_game_object_in_the_structure(self, structure, object_to_find):
		candidate_objects = []
		# print(structure[0])
		# print(structure[1])
		# print(structure[2])
		# get all objects of the same type
		if object_to_find.object_type == 'BasicSmall' or object_to_find.object_type == 'BasicMedium':
			candidate_objects = structure[1]
		else:
			for game_object in itertools.chain(structure[0], structure[1], structure[2]):
				# print(game_object.type, object_to_find.object_type)
				if game_object.type == object_to_find.object_type:
					candidate_objects.append(game_object)

		# from the same type objects get the object with the closest location
		print('candidate_objects', candidate_objects)
		closest_object = self.utils.find_closest_object_considering_location(object_to_find, candidate_objects)

		# print('closest_object', closest_object)
		return closest_object

	def determine_number_of_birds_for_material_deception(self, candidate_structures_strategies: [StrategyAttemptSolvedStructure]):
		birds_needed = []
		solving_strategy = []

		# determine the birds needed for each candidate strategy attempt
		# get the birds needed upto the specific shot
		for strategy_attempt in candidate_structures_strategies:
			for shot_data in strategy_attempt.strategy_data.shots_data:
				birds_needed.append(shot_data.bird_type)
				solving_strategy.append(SolutionShotData(strategy_attempt.structure_id, shot_data))

		print('birds_needed', birds_needed)
		print('solving_strategy', solving_strategy)

		return birds_needed, solving_strategy

	def match_candidate_structures_old(self, candidate_structures_strategies: [[StrategyAttemptSolvedStructure]]):
		levels_data = []
		level_index_start = 0
		io_handler = IOHandler()

		# print('structure_1_strategy_index', structure_1_strategy_index, 'structure_2_strategy_index', structure_2_strategy_index)

		for prospective_strategy_index in range(0, len(candidate_structures_strategies)):
			for matching_strategy_index in range(prospective_strategy_index + 1, len(candidate_structures_strategies)):
				print('prospective_strategy_index, matching_strategy_index', prospective_strategy_index, matching_strategy_index)

				prospective_strategy = candidate_structures_strategies[prospective_strategy_index]
				matching_strategy = candidate_structures_strategies[matching_strategy_index]

				# if they have the 2 candidate structure solving strategies use the same type of bird, then skip
				# print('prospective_strategy.strategy_data.shots_data[0].bird_type', prospective_strategy.strategy_data.shots_data[0].bird_type)
				# print('matching_strategy.strategy_data.shots_data[0].bird_type', matching_strategy.strategy_data.shots_data[0].bird_type)
				if prospective_strategy.strategy_data.shots_data[0].bird_type == matching_strategy.strategy_data.shots_data[0].bird_type:
					print("both the solving strategies of selected structures use the same type of birds, skipping...")
					continue

				print('prospective_strategy', prospective_strategy)
				level_data = self.place_structures_on_level([prospective_strategy, matching_strategy])

				# print('complete_level_layout', level_layout)
				# for structure in level_layout:
				# 	print('structure in level_layout', structure)
				if level_data:
					levels_data.append(level_data)

					# write the level file on the go
					io_handler.write_the_level_file_and_solution(level_data, str(prospective_strategy.structure_id) + '_' + str(matching_strategy.structure_id))
					level_index_start += 1

		return levels_data

	def match_candidate_structures(self, candidate_structures_strategies: [[StrategyAttemptSolvedStructure]]):
		levels_data = []
		level_index_start = 0
		io_handler = IOHandler()

		for structure_1_strategies_index in range(0, len(candidate_structures_strategies)):
			one_level_generated = False
			for structure_2_strategies_index in range(structure_1_strategies_index + 1, len(candidate_structures_strategies)):
				print('structure_1_strategies_index, structure_2_strategies_index', structure_1_strategies_index, structure_2_strategies_index)
				# if both the structures are in the same quarter skip them
				# get the structure ids using the first non empty attempt of the structures
				if next(structure_1_attempt for structure_1_attempt in candidate_structures_strategies[structure_1_strategies_index] if structure_1_attempt).structure_id % 10 == next(
						structure_2_attempt for structure_2_attempt in candidate_structures_strategies[structure_2_strategies_index] if structure_2_attempt).structure_id % 10:
					print('both the structure are in the same quarter, skip to next structure')
					continue

				for bird_type_1_index in range(0, 5):  # for all 5 types of birds
					if not candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index] and not candidate_structures_strategies[structure_2_strategies_index][
						bird_type_1_index]:  # if non of the structures can be solved by the bird_type_1 goto next bird
						continue
					for bird_type_2_index in range(bird_type_1_index + 1, 5):
						if not candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index] and not candidate_structures_strategies[structure_2_strategies_index][
							bird_type_2_index]:  # if non of the structures can be solved by the bird_type_2 goto next bird
							continue
						elif bird_type_1_index == bird_type_2_index:  # same bird go to next bird
							continue
						elif bird_type_1_index == 3 or bird_type_2_index == 3:  # a trick to remove specific bird strategies (testing)
							continue
						else:  # 2 different bird types
							if candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]:
								struct_1_bird_type_1_shot_count = len(candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index].strategy_data.shots_data)
							else:
								struct_1_bird_type_1_shot_count = -1  # structure can not be solved by bird_type_1
							if candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]:
								struct_2_bird_type_1_shot_count = len(candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index].strategy_data.shots_data)
							else:
								struct_2_bird_type_1_shot_count = -1  # structure can not be solved by bird_type_1
							if candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]:
								struct_1_bird_type_2_shot_count = len(candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index].strategy_data.shots_data)
							else:
								struct_1_bird_type_2_shot_count = -1  # structure can not be solved by bird_type_2
							if candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]:
								struct_2_bird_type_2_shot_count = len(candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index].strategy_data.shots_data)
							else:
								struct_2_bird_type_2_shot_count = -1  # structure can not be solved by bird_type_2

							# checking conditions for the matching
							# if any of the 2 structures is not solvable by the selected 2 bird types goto next bird
							if (struct_1_bird_type_1_shot_count == -1 and struct_1_bird_type_2_shot_count == -1) or (struct_2_bird_type_1_shot_count == -1 and struct_2_bird_type_2_shot_count == -1):
								continue
							# if performance of the 2 structures are equal, deception is not that strong since swapping bird types also works
							if struct_1_bird_type_1_shot_count == struct_2_bird_type_1_shot_count and struct_1_bird_type_2_shot_count == struct_2_bird_type_2_shot_count:
								continue

							# determining the strategies #
							structure_1_strategy = None
							structure_2_strategy = None
							# cases where the bird type can't solve a structure
							if struct_1_bird_type_1_shot_count == -1 or struct_2_bird_type_2_shot_count == -1:
								structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]
								structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]  # irrespective of the bird count bird type 1 should use
							elif struct_1_bird_type_2_shot_count == -1 or struct_2_bird_type_1_shot_count == -1:
								structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]
								structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]  # irrespective of the bird count bird type 2 should use
							else:  # all the other cases bird type with minimum shots should use, and 2 structures should get different bird types
								if struct_1_bird_type_1_shot_count < struct_2_bird_type_1_shot_count:
									if struct_2_bird_type_2_shot_count < struct_1_bird_type_2_shot_count:
										# at least one of the bird counts of the 2 structures should be 1, to avoid solutions with mixed birds type (which are not tested)
										if struct_1_bird_type_1_shot_count == 1 or struct_2_bird_type_2_shot_count == 1:
											structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]
											structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]
								elif struct_2_bird_type_1_shot_count < struct_1_bird_type_1_shot_count:
									if struct_1_bird_type_2_shot_count < struct_2_bird_type_2_shot_count:
										# at least one of the bird counts of the 2 structures should be 1, to avoid solutions with mixed birds type (which are not tested)
										if struct_2_bird_type_1_shot_count == 1 or struct_1_bird_type_2_shot_count == 1:
											structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]
											structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]

							# if 2 strategies were found successfully generate the game level
							if structure_1_strategy is not None and structure_2_strategy is not None:
								print('matching strategies found, creating the level')
								level_data = self.place_structures_on_level([structure_1_strategy, structure_2_strategy])

								if level_data:
									levels_data.append(level_data)

									# write the level file on the go
									io_handler.write_the_level_file_and_solution(level_data,
																				 str(structure_1_strategy.structure_id) + '_' + str(structure_2_strategy.structure_id) + '_' + str(level_index_start))
									level_index_start += 1

									# create only one level from one structure
									one_level_generated = True
									break
							print(struct_1_bird_type_1_shot_count, struct_2_bird_type_1_shot_count, struct_1_bird_type_2_shot_count, struct_2_bird_type_2_shot_count)
					if one_level_generated:
						break
				if one_level_generated:
					break

		return levels_data

	def generate_material_analysis_deception(self):
		# candidate_structures_strategies = self.find_candidate_structures_for_material_deception([4, 5, 6, 7, 8])
		candidate_structures_strategies = self.find_candidate_structures_for_material_deception([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
		# print('candidate_structures_strategies', candidate_structures_strategies)

		output_levels = self.match_candidate_structures(candidate_structures_strategies)

		# structure_1, structure_2, birds_needed, solving_strategy
		return output_levels
