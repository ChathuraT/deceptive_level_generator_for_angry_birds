import copy
import itertools

from utils.data_classes import *
from utils.structure_operations import StructureOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.io_handler import IOHandler


class TapTimeDeception:
	bird_type_indexes = {'bird_yellow': 0, 'bird_blue': 1, 'bird_white': 2, 'bird_black': 3, 'bird_red': 4}

	def __init__(self, analysis_data, structures):
		self.analysis_data = analysis_data
		self.structures = structures
		self.utils = StrategyUtils(structures)
		self.structure_operations = StructureOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()

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

		# count the number of least shots for each bird
		least_shot_count_for_birds = []
		candidate_strategies = []
		for i in range(1, 6):
			bird_counts_of_all_attempts_of_bird = no_of_shots_in_strategies[(i - 1) * 10: i * 10]
			bird_counts_for_passed_attempts = [item for item in bird_counts_of_all_attempts_of_bird if item[1] >= 0]

			# print(no_of_shots_in_strategies[(i-1)*10: i*10])
			print('bird_counts_of_all_attempts_of_bird', bird_counts_of_all_attempts_of_bird)
			print('bird_counts_for_passed_attempts', bird_counts_for_passed_attempts)
			if bird_counts_for_passed_attempts:  # if there is at least one passing attempt for the bird
				minimum_bird_count_for_passing_attempts = min(bird_counts_for_passed_attempts, key=lambda x: x[1])[1]
				least_shot_count_for_birds.append(minimum_bird_count_for_passing_attempts)

				# check if there is only one tap time (strategy) for the bird type which outperforms other tap times (strategy)
				if i == 5:  # skip red birds when checking the outperforming strategy (since no tap time is needed for the red bird, it is excluded from this deception)
					continue
				print('no of minimum(', minimum_bird_count_for_passing_attempts, ')bird attempts', [item[1] for item in bird_counts_for_passed_attempts].count(minimum_bird_count_for_passing_attempts))
				if [item[1] for item in bird_counts_for_passed_attempts].count(minimum_bird_count_for_passing_attempts) == 1:
					print('outperforming attempt available')
					print(best_attempts_of_strategies[min(bird_counts_for_passed_attempts, key=lambda x: x[1])[0]])
					candidate_strategies.append(best_attempts_of_strategies[min(bird_counts_for_passed_attempts, key=lambda x: x[1])[0]])

			else:
				least_shot_count_for_birds.append(-1)

		print('least_shot_count_for_birds', least_shot_count_for_birds)

		# get the strategy with the least shot count (disregard black bird strategies)
		# least_number_of_shots = 99999
		# strategy_with_least_number_of_shots = None
		# more_than_one_strategy_with_least_number_of_shots = False
		#
		# for no_of_shots_in_strategy in no_of_shots_in_strategies:
		# 	# skip strategies which do not solve the strategy
		# 	if no_of_shots_in_strategy[1] == -1:
		# 		continue
		# 	elif no_of_shots_in_strategy[1] == least_number_of_shots:
		# 		# there are more than one strategy with least number of shots
		# 		more_than_one_strategy_with_least_number_of_shots = True
		# 	# print('strategy_with_least_number_of_shots[0] no_of_shots_in_strategy[0]', strategy_with_least_number_of_shots[0], no_of_shots_in_strategy[0])
		# 	elif no_of_shots_in_strategy[1] < least_number_of_shots:
		# 		strategy_with_least_number_of_shots = no_of_shots_in_strategy
		# 		least_number_of_shots = no_of_shots_in_strategy[1]
		# 		more_than_one_strategy_with_least_number_of_shots = False
		#
		# # if there are more than one strategy with least number of shots: no birds outperforms all the other birds
		# if more_than_one_strategy_with_least_number_of_shots:
		# 	print('there are more than one strategy with least number of shots', least_number_of_shots)
		# 	return
		#
		# if least_number_of_shots == 99999:
		# 	# none of the strategies solves the structure
		# 	print('none of the strategies solves the structure')
		# 	return
		#
		# print('strategy_with_least_number_of_shots', strategy_with_least_number_of_shots)
		# return the strategy which outperform others
		# return best_attempts_of_strategies[strategy_with_least_number_of_shots[0]]

		return candidate_strategies, least_shot_count_for_birds

	def find_candidate_structures_for_tap_time_deception(self):
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
			outperforming_strategies = self.get_attempt_which_outperforms_other_in_solving(best_attempts_of_strategies_to_analyze)

			if outperforming_strategies[0]:
				candidate_structure_solving_strategies.append(outperforming_strategies)

		print('number_of_candidate structures', len(candidate_structure_solving_strategies))
		print('candidate_structure_solving_strategies', candidate_structure_solving_strategies)
		return candidate_structure_solving_strategies

	def determine_number_of_birds_for_solution(self, candidate_structures_strategies: [StrategyAttemptSolvedStructure]):
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

	def place_structures_on_level(self, structure_solving_strategies: [StrategyAttemptSolvedStructure]):
		# get the strategy to solve the generating level
		birds_needed, solving_strategy = self.determine_number_of_birds_for_solution(structure_solving_strategies)
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

	def match_candidate_structures(self, candidate_structures_data):
		levels_data = []
		level_index_start = 0
		io_handler = IOHandler()
		candidate_structures_strategies = [item[0] for item in candidate_structures_data]
		candidate_structures_shot_counts = [item[1] for item in candidate_structures_data]

		for structure_1_strategies_index in range(0, len(candidate_structures_strategies)):
			for structure_2_strategies_index in range(structure_1_strategies_index + 1, len(candidate_structures_strategies)):
				print('structure_1_strategies_index, structure_2_strategies_index', structure_1_strategies_index, structure_2_strategies_index)
				# if both the structures are in the same quarter skip them
				# get the structure ids using the first non empty attempt of the structures
				if next(structure_1_attempt for structure_1_attempt in candidate_structures_strategies[structure_1_strategies_index] if structure_1_attempt).structure_id % 10 == next(
						structure_2_attempt for structure_2_attempt in candidate_structures_strategies[structure_2_strategies_index] if structure_2_attempt).structure_id % 10:
					print('both the structures are in the same quarter, skip to next structure')
					continue

				print('structure 1', next(structure_1_attempt for structure_1_attempt in candidate_structures_strategies[structure_1_strategies_index] if structure_1_attempt).structure_id)
				print('structure 2', next(structure_2_attempt for structure_2_attempt in candidate_structures_strategies[structure_2_strategies_index] if structure_2_attempt).structure_id)
				# for all the tap time strategies in structure 1 and structure 2
				for candidate_strategy_structure_1 in candidate_structures_strategies[structure_1_strategies_index]:
					for candidate_strategy_structure_2 in candidate_structures_strategies[structure_2_strategies_index]:
						# get the outperforming bird types of the structures
						structure_1_bird_type = candidate_strategy_structure_1.strategy_data.shots_data[0].bird_type
						structure_2_bird_type = candidate_strategy_structure_2.strategy_data.shots_data[0].bird_type

						print('structure_1_bird_type', structure_1_bird_type)
						print('structure_2_bird_type', structure_2_bird_type)
						print('structure_1_shot_count', candidate_structures_shot_counts[structure_1_strategies_index])
						print('structure_2_shot_count', candidate_structures_shot_counts[structure_2_strategies_index])

						# # check if structure_1_bird_type is different from structure_2_bird_type
						# if structure_1_bird_type == structure_2_bird_type:
						# 	print('both structures are vulnerable for the same bird')
						# 	continue
						#
						# # check if structure_1_bird_type is not good at structure 2
						# if candidate_structures_shot_counts[structure_1_strategies_index][self.bird_type_indexes[structure_1_bird_type]] >= \
						# 		candidate_structures_shot_counts[structure_2_strategies_index][self.bird_type_indexes[structure_1_bird_type]] > 0:
						# 	print('structure 2 is also good at structure 1 bird type')
						# 	continue
						#
						# # check if structure_2_bird_type is not good at structure 1
						# if candidate_structures_shot_counts[structure_2_strategies_index][self.bird_type_indexes[structure_2_bird_type]] >= \
						# 		candidate_structures_shot_counts[structure_1_strategies_index][self.bird_type_indexes[structure_2_bird_type]] > 0:
						# 	print('structure 1 is also good at structure 2 bird type')
						# 	continue

						# check if the red bird can also solve the structure with a less number of shots, which means tap time doesn't matter
						if candidate_structures_shot_counts[structure_1_strategies_index][self.bird_type_indexes[structure_1_bird_type]] >= \
								candidate_structures_shot_counts[structure_1_strategies_index][-1] > 0:
							print('red bird is also good at structure 1') # no specific tap time is needed for the structure, can solve by just shooting at the pig
							continue

						if candidate_structures_shot_counts[structure_2_strategies_index][self.bird_type_indexes[structure_2_bird_type]] >= \
								candidate_structures_shot_counts[structure_2_strategies_index][-1] > 0:
							print('red bird is also good at structure 2') # no specific tap time is needed for the structure, can solve by just shooting at the pig
							continue

						print('feasible structures found, create the level')

						level_data = self.place_structures_on_level([candidate_strategy_structure_1, candidate_strategy_structure_2])

						if level_data:
							levels_data.append(level_data)

							# write the level file on the go
							io_handler.write_the_level_file_and_solution(level_data, str(candidate_strategy_structure_1.structure_id) + '_' + str(
								candidate_strategy_structure_2.structure_id) + '_' + str(level_index_start))
							level_index_start += 1

	def generate_tap_time_deception(self):
		candidate_structures_tap_time = self.find_candidate_structures_for_tap_time_deception()
		# candidate_solvable_structures = self.find_candidate_solvable_structures()
		# print('candidate_structures_tap_time', candidate_structures_tap_time)

		print('### Creating levels with selected strategies### ')
		self.match_candidate_structures(candidate_structures_tap_time)
