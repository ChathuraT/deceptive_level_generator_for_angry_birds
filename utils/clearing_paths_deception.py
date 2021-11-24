import copy
import itertools

from utils.data_classes import *
from utils.constants import *
from utils.structure_operations import StructureOperations
from utils.block_operations import BlockOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.io_handler import IOHandler


class ClearingPathsDeception:

	def __init__(self, analysis_data, structures):
		self.analysis_data = analysis_data
		self.structures = structures
		self.structure_operations = StructureOperations()
		self.block_operations = BlockOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()
		self.utils = StrategyUtils(structures)

	# get the best strategy attempt with highest bounding box reduction from all the attempts of the strategy
	def find_best_strategy_attempt_of_strategy(self, structure_id, strategy: Strategy):
		# criteria to select a strategy
		# min_bounding_box_change_needed = 20  # 50% change should be there to consider the strategy is feasible

		print('## finding the best shot which affected the bounding box most for structure:', structure_id, 'strategy index:', strategy.index, '##')
		print('strategy', strategy)
		change_percentages_of_bounding_box = []

		# for all the attempts of the same strategy
		for strategy_attempt in strategy.strategy_data:

			# skip the strategy attempts with zero shots
			if not strategy_attempt.shots_data:
				change_percentages_of_bounding_box.append(0)
				continue

			# print('strategy_attempt', strategy_attempt)
			# print('target object', strategy_attempt.shots_data[0].target_object)

			# get the static_data_start bounding box of the first shot of the strategy attempt
			bounding_box_start = strategy_attempt.shots_data[0].static_data_start.bounding_box
			# get the static_data_end bounding box of the last shot of the strategy attempt (currently only one shot is done per strategy attempt)
			bounding_box_end = strategy_attempt.shots_data[-1].static_data_end.bounding_box

			# calculate the bounding box change
			bounding_box_base = bounding_box_start[2] if bounding_box_end[2] < bounding_box_start[2] else bounding_box_end[2]  # to exclude the objects falling onto the ground (which expands the bb)

			# height change percentage of the bounding box
			initial_height = bounding_box_start[3] - bounding_box_start[2]
			end_height = bounding_box_end[3] - bounding_box_base
			height_change = round((initial_height - end_height) / initial_height, 2) * 100

			# print('height_change', height_change, 'bounding_box_start', bounding_box_start, 'bounding_box_end', bounding_box_end)
			change_percentages_of_bounding_box.append(height_change)

		# check if there are attempts which satisfies the minimum change requirements and outperform others, if not return none
		# if max(change_percentages_of_bounding_box) < min_bounding_box_change_needed:
		# 	return []

		# sort the strategy attempts according to the change percentage of the bounding box
		sort_indexes = sorted(range(len(change_percentages_of_bounding_box)), key=lambda k: change_percentages_of_bounding_box[k])
		ordered_strategy_attempts = [strategy.strategy_data[i] for i in sort_indexes]
		# print('ordered_strategy_attempts', ordered_strategy_attempts[-1])
		best_strategy_attempt = StrategyAttemptDamagedStructure(structure_id, strategy.index, ordered_strategy_attempts[-1])

		return [max(change_percentages_of_bounding_box), best_strategy_attempt]

	# with the given best attempts of each strategy, find the attempt which outperforms the others in reducing the bounding box
	def get_attempt_which_outperforms_others_in_structure_clearing(self, selected_attempts_of_strategies):
		# criteria to select a strategy
		min_bounding_box_change_needed = 50  # 50% change should be there to consider the strategy is feasible
		maximum_percentage_of_shots_above_min_bounding_box_change = 20  # the maximum percentage of shots that can be above the min_bounding_box_change_needed
		candidate_attempts = []

		for attempt in selected_attempts_of_strategies:
			print('attempt', attempt)
			if attempt[0] < min_bounding_box_change_needed:  # check least bb change is satisfied
				continue
			else:
				candidate_attempts.append(attempt)

		if len(candidate_attempts) * 100 / len(selected_attempts_of_strategies) > maximum_percentage_of_shots_above_min_bounding_box_change:
			# large number of strategies exceeds the min_bounding_box_change_needed, therefore the structure is not feasible for clearing paths deception
			print('more than', maximum_percentage_of_shots_above_min_bounding_box_change, '% of shots do a', min_bounding_box_change_needed, '% change to the bounding box')
			return
		else:
			# only few shots make a considerable amount of change to the bb; structure is feasible for the deception.
			# return the best (most bb change percentage) strategy attempt
			maximum_bounding_box_change = 0
			best_strategy_attempt = None
			for attempt in candidate_attempts:
				if attempt[0] > maximum_bounding_box_change:
					best_strategy_attempt = attempt[1]
					maximum_bounding_box_change = attempt[0]

			return best_strategy_attempt

	def find_candidate_structures_for_clearing_paths_deception(self, strategy_id_start):
		candidate_structure_clearing_strategies = []
		print('self.analysis_data', self.analysis_data)

		# for all the structures
		for structure_data in self.analysis_data:

			# best_attempt_of strategies_to_analyze
			best_attempts_of_strategies_to_analyze = []

			# for all the strategies in the structure
			for strategy in structure_data.strategies[strategy_id_start - 1:]:
				# get the best strategy attempt which reduces the bounding box the most
				best_strategy_attempt_of_strategy = self.find_best_strategy_attempt_of_strategy(structure_data.id, strategy)

				best_attempts_of_strategies_to_analyze.append(best_strategy_attempt_of_strategy)

			# print('best_attempts_of_strategies_to_analyze', best_attempts_of_strategies_to_analyze)
			# from the 	best strategy attempt of each of the strategy, check whether if there is an attempt which outperform others
			outperforming_strategy = self.get_attempt_which_outperforms_others_in_structure_clearing(best_attempts_of_strategies_to_analyze)
			if outperforming_strategy:
				candidate_structure_clearing_strategies.append(outperforming_strategy)
			# print('outperforming_strategy', outperforming_strategy)

		print('number_of_candidate structures', len(candidate_structure_clearing_strategies))
		# print('candidate_structure_clearing_strategies', candidate_structure_clearing_strategies)

		return candidate_structure_clearing_strategies

	# find strategies which solve a given structure
	def find_best_structure_solving_strategy_attempt(self, structure_id, strategy: Strategy):
		print('## find_structure_solving_strategies of structure', structure_id, '##')
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

	# with the given best attempts of all the strategies returns the strategy which outperforms other
	def get_attempt_which_outperforms_other_in_solving(self, best_attempts_of_strategies):
		no_of_shots_in_strategies = []
		attempt_index = 0
		for attempt in best_attempts_of_strategies:
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
			elif no_of_shots_in_strategy[1] == least_number_of_shots:
				# there are more than one strategy with least number of shots
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
			# none of the strategies solves the structure
			print('none of the strategies solves the structure')
			return

		print('strategy_with_least_number_of_shots', strategy_with_least_number_of_shots)
		# return the strategy which outperform others
		return best_attempts_of_strategies[strategy_with_least_number_of_shots[0]]

	def find_candidate_structures_for_behind_structure(self):
		# structures with an outperforming strategy is only selected as a candidate structure
		candidate_structure_solving_strategies = []

		# for all the structures
		for structure_data in self.analysis_data:
			# best_attempt_of strategies_to_analyze
			best_attempts_of_strategies_to_analyze = []

			# check if the structure contains pigs
			if not self.utils.does_structure_contain_pigs(structure_data):
				print('structure', structure_data.id, ' does not contain pigs')
				continue

			# get the best strategy attempts of all the strategies
			for strategy in structure_data.strategies:
				best_solving_strategy_attempt_of_strategy = self.find_best_structure_solving_strategy_attempt(structure_data.id, strategy)

				best_attempts_of_strategies_to_analyze.append(best_solving_strategy_attempt_of_strategy)

			# find results of one strategy outperforms another
			outperforming_strategy = self.get_attempt_which_outperforms_other_in_solving(best_attempts_of_strategies_to_analyze)

			if outperforming_strategy:
				candidate_structure_solving_strategies.append(outperforming_strategy)

		print('number_of_candidate structures', len(candidate_structure_solving_strategies))
		# print('candidate_structure_solving_strategies', candidate_structure_solving_strategies)
		return candidate_structure_solving_strategies

	def get_the_solution_for_clearing_paths_deception(self, candidate_structures_strategies: [StrategyAttemptSolvedStructure]):
		birds_needed = []
		solving_strategy = []

		# determine the birds needed for each candidate strategy attempt
		for strategy_attempt in candidate_structures_strategies:
			for shot_data in strategy_attempt.strategy_data.shots_data:
				birds_needed.append(shot_data.bird_type)
				solving_strategy.append(SolutionShotData(strategy_attempt.structure_id, shot_data))

		# print('birds_needed', birds_needed)
		# print('solving_strategy', solving_strategy)

		return birds_needed, solving_strategy

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
		# print('candidate_objects', candidate_objects)
		closest_object = self.utils.find_closest_object_considering_location(object_to_find, candidate_objects)

		# print('closest_object', closest_object)
		return closest_object

	def find_the_y_location_of_the_front_structure(self, trajectory_points, front_structure_x_location):
		# returns the y coordinate of the closest x coordinate

		# get all the x coordinates of the trajectory path
		x_coordinates_of_trajectory_path = [trajectory_point[0] for trajectory_point in trajectory_points]
		# get the index of the closest coordinate to front_structure_x_location
		trajectory_point_index = min(range(len(x_coordinates_of_trajectory_path)), key=lambda i: abs(x_coordinates_of_trajectory_path[i] - front_structure_x_location))

		# print('closest trajectory coordinate to x coordinate', front_structure_x_location, 'is', trajectory_points[trajectory_point_index])

		return trajectory_points[trajectory_point_index][1]

	def find_bounding_box_change(self, strategy):
		# get the static_data_start bounding box of the first shot of the strategy attempt
		bounding_box_start = strategy.strategy_data.shots_data[0].static_data_start.bounding_box
		# get the static_data_end bounding box of the last shot of the strategy attempt (currently only one shot is done per strategy attempt)
		bounding_box_end = strategy.strategy_data.shots_data[-1].static_data_end.bounding_box

		# calculate the bounding box change
		bounding_box_base = bounding_box_start[2] if bounding_box_end[2] < bounding_box_start[2] else bounding_box_end[2]  # to exclude the objects falling onto the ground (which expands the bb)

		# height change percentage of the bounding box
		initial_height = bounding_box_start[3] - bounding_box_start[2]
		end_height = bounding_box_end[3] - bounding_box_base
		height_change = initial_height - end_height

		return height_change

	def check_the_solution_target_reachability(self, solving_strategy, front_structure, back_structure, front_structure_id, back_structure_id, front_structure_max_y_after_clearing):
		y_limit_of_a_lower_trajectory_target = 2.8  # the highest y position a lower trajectory target can be placed (otherwise effeect of lower trajectory is not there)
		# print('selected_structures', selected_structures)
		selected_structures_combined = self.structure_operations.get_all_game_objects_filtered([front_structure, back_structure])
		for solution_shot_data in solving_strategy:
			shot_data = solution_shot_data.shot_data

			# if target object is 'any_pig' which is not included in the strategy skip it
			if shot_data.target_object.object_type == 'any_pig':
				continue

			# find the target object in the structure
			target_object = self.find_game_object_in_the_structure(selected_structures_combined, shot_data.target_object)
			# trajectory used for the solution
			trajectory_selection_for_reachability = 'low' if solution_shot_data.shot_data.trajectory_selection == 1 else 'high'

			# if the target object is reached by a lower trajectory and its location is above the y_limit_of_a_lower_trajectory_target then return false
			if solution_shot_data.structure_id == front_structure_id:  # only done for the front structure. o.w. a very few levels are obtained
				if target_object.y > y_limit_of_a_lower_trajectory_target:
					print('a lower trajectory target is placed in a higher position, aborting...')
					return False

			# if the target object is from the back structure, make sure that is not blocked by front structure blocks after destroying the front structure (o.w. strategy to solve it might not work)
			if solution_shot_data.structure_id == back_structure_id:
				print('target from back structure')
				if not self.trajectory_planner.find_reachability_of_object([front_structure, back_structure], target_object, trajectory_selection_for_reachability, 'cleared_path', None,
																		   [front_structure_id, front_structure_max_y_after_clearing]):
					return False
			else:  # front structure targets
				print('target from front structure')
				# check the reachability of the object
				if not self.trajectory_planner.find_reachability_of_object([front_structure, back_structure], target_object, trajectory_selection_for_reachability, 'any', None, None):
					return False
		print('all targets are reachable')
		return True

	def remove_pigs_from_structure(self, structure):
		# print('structure', structure)

		return [structure[0], [], structure[2], structure[3]]

	def place_structures_on_level(self, front_strategy, back_strategy):
		# max number of attempts to create the level layout
		max_attempts_to_create_level_layout = 100

		# get the strategy to solve the generating level
		birds_needed, solving_strategy = self.get_the_solution_for_clearing_paths_deception([front_strategy, back_strategy])
		layout_successfully_generated = False
		attempts_to_create_level_layout = 0
		complete_level_layout = []
		front_structure = None
		back_structure = None
		centre_of_the_level_space = [level_width_min + (level_width_max - level_width_min) / 2, level_height_min + (level_height_max - level_height_min) / 2]

		while not layout_successfully_generated:
			# exceeding the maximum attempts, return
			if attempts_to_create_level_layout >= max_attempts_to_create_level_layout:
				return []

			# get a copy of the structures
			front_structure = copy.deepcopy(self.utils.get_structure(front_strategy.structure_id))
			back_structure = copy.deepcopy(self.utils.get_structure(back_strategy.structure_id))

			# calculate the width and height of the 2 structures
			bounding_box_of_front_structure = self.structure_operations.find_bounding_box_of_structure(itertools.chain(front_structure[0], front_structure[1], front_structure[2]), 0)
			bounding_box_of_back_structure = self.structure_operations.find_bounding_box_of_structure(itertools.chain(back_structure[0], back_structure[1], back_structure[2]), 0)

			back_structure_half_width = (bounding_box_of_back_structure[1] - bounding_box_of_back_structure[0]) / 2
			back_structure_half_height = (bounding_box_of_back_structure[3] - bounding_box_of_back_structure[2]) / 2
			front_structure_half_width = (bounding_box_of_front_structure[1] - bounding_box_of_front_structure[0]) / 2
			front_structure_half_height = (bounding_box_of_front_structure[3] - bounding_box_of_front_structure[2]) / 2

			# place the back structure first
			print('placing the back structure')

			# consider the quarter of the screen which the structure is located when placing (PLACED AT THE SAME LOCATION AS TESTING)
			back_structure_space_location = None
			if back_strategy.structure_id % 10 == 3:
				# back_structure_space_location = [uniform(centre_of_the_level_space[0] + back_structure_half_width, level_width_max - back_structure_half_width),
				# 								 uniform(centre_of_the_level_space[1] + back_structure_half_height, level_height_max - back_structure_half_height)]
				back_structure_space_location = [level_width_min + 3 * (level_width_max - level_width_min) / 4, level_height_min + 3 * (level_height_max - level_height_min) / 4]
			if back_strategy.structure_id % 10 == 4:
				# back_structure_space_location = [uniform(centre_of_the_level_space[0] + back_structure_half_width, level_width_max - back_structure_half_width),
				# 								 uniform(level_height_min + back_structure_half_height, centre_of_the_level_space[1] - back_structure_half_height)]
				back_structure_space_location = [level_width_min + 3 * (level_width_max - level_width_min) / 4, level_height_min + (level_height_max - level_height_min) / 4]

			back_structure_horizontal_width = [back_structure_space_location[0] - back_structure_half_width, back_structure_space_location[0] + back_structure_half_width]
			back_structure_vertical_width = [back_structure_space_location[1] - back_structure_half_height, back_structure_space_location[1] + back_structure_half_height]

			# shift the coordinates of the back structure and the solving strategy
			# adjust x coordinates
			x_shift_value = back_structure_space_location[0] - (bounding_box_of_back_structure[0] + (bounding_box_of_back_structure[1] - bounding_box_of_back_structure[0]) / 2)
			# print('x_shift_value', x_shift_value)
			self.structure_operations.shift_coordinates_of_structure(back_structure, 'x', x_shift_value)
			# adjust y coordinates
			y_shift_value = back_structure_space_location[1] - (bounding_box_of_back_structure[2] + (bounding_box_of_back_structure[3] - bounding_box_of_back_structure[2]) / 2)
			# print('y_shift_value', y_shift_value)
			self.structure_operations.shift_coordinates_of_structure(back_structure, 'y', y_shift_value)
			# shift the coordinates of the target object of the strategy
			solving_strategy = self.adjust_coordinates_of_solving_strategy(solving_strategy, x_shift_value, y_shift_value, back_strategy.structure_id)

			trajectory_paths = None
			trajectory_selection_to_the_target = None
			attempts_to_get_a_reachable_target = 0
			while not trajectory_paths:  # loop until a reachable target is found in the back structure todo: if any of the targets is not reachable then no point of proceeding?
				# get the target of the back structure
				target_object_of_back_structure = copy.deepcopy(back_strategy.strategy_data.shots_data[attempts_to_get_a_reachable_target].target_object)
				trajectory_selection_to_the_target = back_strategy.strategy_data.shots_data[attempts_to_get_a_reachable_target].trajectory_selection

				# find the target object in the structure
				target_object = self.find_game_object_in_the_structure(back_structure, target_object_of_back_structure)
				# find trajectory path to the target object
				trajectory_paths = self.trajectory_planner.get_trajectory_paths(target_object)

				attempts_to_get_a_reachable_target += 1
				# if no trajectory path is found for any target, try from the beginning
				if attempts_to_get_a_reachable_target >= len(back_strategy.strategy_data.shots_data):
					break
				continue

			# no any reachable targets in the solver structure; try creating the layout again
			if not trajectory_paths:
				attempts_to_create_level_layout += 1
				continue

			# get the trajectory needed for the target in the solution strategy
			selected_trajectory_path_in_wc = self.block_operations.convert_trajectory_to_wc_from_usc(trajectory_paths[trajectory_selection_to_the_target - 1])

			# place the front structure next
			print('placing the front structure')

			# get a random x location for the front structure (-2*front_structure_half_width is to keep a space of front_structure_half_width between the 2 structures)
			# front_structure_x_location = uniform(level_width_min + front_structure_half_width, back_structure_horizontal_width[0] - 2 * front_structure_half_width)
			front_structure_x_location = centre_of_the_level_space[0] - front_structure_half_width  # determine the x location considering the structures original quarter
			# front_structure_x_location = level_width_min + (level_width_max - level_width_min) / 4  # (PLACED AT THE SAME LOCATION AS TESTING)

			# decide the y location from the trajectory points of the low trajectory
			y_location_trajectory_crosses_the_structure = self.find_the_y_location_of_the_front_structure(selected_trajectory_path_in_wc, front_structure_x_location)
			# top of the structure should be (y_location_trajectory_crosses_the_structure + change in bb - threshold to avoid colliding with leftmost blocks)
			bounding_box_change = self.find_bounding_box_change(front_strategy)
			collision_avoiding_threshold = bounding_box_change * 0.5  # (this is to shift the front structure down to avoid bird colliding with left most blocks of the structure even after clearing the path)
			front_structure_y_location = y_location_trajectory_crosses_the_structure + bounding_box_change - collision_avoiding_threshold - front_structure_half_height

			# from the y coordinate of the front structure determine whether the selected front structure in the suitable quarter
			if front_structure_y_location > centre_of_the_level_space[1] and front_strategy.structure_id % 10 != 1:
				print('front structure is not in the correct quarter')
				attempts_to_create_level_layout += 1
				continue
			elif front_structure_y_location < centre_of_the_level_space[1] and front_strategy.structure_id % 10 != 2:
				print('front structure is not in the correct quarter')
				attempts_to_create_level_layout += 1
				continue

			# shift the coordinates of the front structure and the solving strategy
			# adjust x coordinates
			x_shift_value = front_structure_x_location - (bounding_box_of_front_structure[0] + (bounding_box_of_front_structure[1] - bounding_box_of_front_structure[0]) / 2)
			# print('x_shift_value', x_shift_value)
			self.structure_operations.shift_coordinates_of_structure(front_structure, 'x', x_shift_value)
			# adjust y coordinates
			y_shift_value = front_structure_y_location - (bounding_box_of_front_structure[2] + (bounding_box_of_front_structure[3] - bounding_box_of_front_structure[2]) / 2)
			# print('y_shift_value', y_shift_value)
			self.structure_operations.shift_coordinates_of_structure(front_structure, 'y', y_shift_value)
			# shift the coordinates of the target object of the strategy
			solving_strategy = self.adjust_coordinates_of_solving_strategy(solving_strategy, x_shift_value, y_shift_value, front_strategy.structure_id)

			# check if the other targets of the back structure are within the reachable range
			attempts_to_create_level_layout += 1

			# check whether all the target objects are reachable
			if self.check_the_solution_target_reachability(solving_strategy, front_structure, back_structure, front_strategy.structure_id, back_strategy.structure_id,
														   front_structure_y_location + front_structure_half_height - bounding_box_change):
				layout_successfully_generated = True
			else:
				print('## Generated layout does not satisfy meta constraints! ##')

		# remove pigs from the front structure (front structure is just to block the trajectory)
		front_structure = self.remove_pigs_from_structure(front_structure)

		return [front_structure, back_structure], birds_needed, solving_strategy

	def match_candidate_structures(self, front_strategies, back_strategies):

		levels_data = []
		level_index_start = 20
		io_handler = IOHandler()

		for back_strategy_index in range(0, len(back_strategies)):
			for front_strategy_index in range(0, len(front_strategies)):

				back_strategy = back_strategies[back_strategy_index]
				front_strategy = front_strategies[front_strategy_index]

				print('front_structure id', front_strategy.structure_id, 'back_structure id', back_strategy.structure_id)

				# only pair structures in the first 2 quarters as front structure with structure in the last 2 quarters as back structures
				level_data = None
				if (front_strategy.structure_id % 10 == 1 or front_strategy.structure_id % 10 == 2) and (back_strategy.structure_id % 10 == 3 or back_strategy.structure_id % 10 == 4):
					print('matching structures')
					level_data = self.place_structures_on_level(front_strategy, back_strategy)

				if level_data:
					levels_data.append(level_data)
					# write the level file on the go
					io_handler.write_the_level_file_and_solution(level_data, str(front_strategy.structure_id) + '_' + str(back_strategy.structure_id))
					level_index_start += 1

		return levels_data

	def generate_clearing_paths_deception(self):
		candidate_structure_clearing_strategies = self.find_candidate_structures_for_clearing_paths_deception(7)  # strategies starting 7 are considered (shooting at reachable objects)
		candidate_behind_structure_strategies = self.find_candidate_structures_for_behind_structure()  # all strategies are considered
		print('candidate_structure_clearing_strategies', len(candidate_structure_clearing_strategies))
		print('candidate_behind_structure_strategies', len(candidate_behind_structure_strategies))
		# print('candidate_structure_clearing_strategies', candidate_structure_clearing_strategies)
		# print('candidate_behind_structure_strategies', candidate_behind_structure_strategies)

		print('### Creating levels with selected strategies### ')
		self.match_candidate_structures(candidate_structure_clearing_strategies, candidate_behind_structure_strategies)
