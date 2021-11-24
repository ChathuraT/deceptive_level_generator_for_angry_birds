from utils.data_classes import *
from utils.structure_operations import StructureOperations
from utils.block_operations import BlockOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.material_analysis_deception import MaterialAnalysisDeception
from utils.io_handler import IOHandler


class NonGreedyActionsDeception:

	def __init__(self, analysis_data, structures):
		self.analysis_data = analysis_data
		self.structures = structures
		self.structure_operations = StructureOperations()
		self.block_operations = BlockOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()
		self.utils = StrategyUtils(structures)
		self.material_analysis_deception = MaterialAnalysisDeception(analysis_data, structures)

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
			elif no_of_shots_in_strategy[0] == 3 or no_of_shots_in_strategy[0] == 4:
				# skip white or black bird strategies
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
			# none of the strategies solved the structure check white and black birds strategies
			if no_of_shots_in_strategies[3][1] != -1:
				# white bird strategy solves the structure: return it
				strategy_with_least_number_of_shots = no_of_shots_in_strategies[3]
			elif no_of_shots_in_strategies[4][1] != -1:
				# black bird strategy solves the structure: return it
				strategy_with_least_number_of_shots = no_of_shots_in_strategies[4]
			else:
				# none of the strategies solves the structure
				print('none of the strategies solves the structure')
				return

		print('strategy_with_least_number_of_shots', strategy_with_least_number_of_shots)
		# return the strategy which outperform others
		return attempts_of_different_birds[strategy_with_least_number_of_shots[0]]

	def match_candidate_structures(self, candidate_structures_strategies: [[StrategyAttemptSolvedStructure]]):
		levels_data = []
		level_index_start = 0
		io_handler = IOHandler()

		for structure_1_strategies_index in range(0, len(candidate_structures_strategies)):
			for structure_2_strategies_index in range(structure_1_strategies_index + 1, len(candidate_structures_strategies)):
				print('structure_1_strategies_index, structure_2_strategies_index', structure_1_strategies_index, structure_2_strategies_index)
				# if both the structures are in the same quarter skip them
				# get the structure ids using the first non empty attempt of the structures
				if next(structure_1_attempt for structure_1_attempt in candidate_structures_strategies[structure_1_strategies_index] if structure_1_attempt).structure_id % 10 == next(
						structure_2_attempt for structure_2_attempt in candidate_structures_strategies[structure_2_strategies_index] if structure_2_attempt).structure_id % 10:
					print('both the structure are in the same quarter, skip to next structure')
					continue

				# get the shot count for the red bird
				struct_1_red_bird_shot_count = -1
				struct_2_red_bird_shot_count = -1
				if candidate_structures_strategies[structure_1_strategies_index][0]:
					struct_1_red_bird_shot_count = len(candidate_structures_strategies[structure_1_strategies_index][0].strategy_data.shots_data)
				if candidate_structures_strategies[structure_2_strategies_index][0]:
					struct_2_red_bird_shot_count = len(candidate_structures_strategies[structure_2_strategies_index][0].strategy_data.shots_data)
				print('struct_1_red_bird_shot_count', struct_1_red_bird_shot_count)
				print('struct_2_red_bird_shot_count', struct_2_red_bird_shot_count)

				# determining the greedy and non greedy structures
				greedy_structure_strategy = None
				non_greedy_structure_strategy = None
				greedy_structure_name = None

				# if both the structures can be solved by a single red bird the deception can not be created with the selected structures
				if struct_1_red_bird_shot_count == 1 and struct_2_red_bird_shot_count == 1:
					print('both structures can be solved by the red birds')
					continue
				# # if none of the structures can be solved by a single red bird the deception can not be created with the selected structures
				# if struct_1_red_bird_shot_count != 1 or struct_2_red_bird_shot_count != 1:
				# 	print('none of the structures can be solved by a single red bird')
				# 	continue

				# select the structure that can be solved by a single red bird, then that structure is suitable for the greedy structure
				if struct_1_red_bird_shot_count == 1:
					greedy_structure_strategy = candidate_structures_strategies[structure_1_strategies_index][0]
					greedy_structure_name = 1
				elif struct_2_red_bird_shot_count == 1:
					greedy_structure_strategy = candidate_structures_strategies[structure_2_strategies_index][0]
					greedy_structure_name = 2
				else:
					print('none of the structures can be solved by a single red bird')
					continue

				# get the other structure as the non greedy structure, select the strategy with least number of shots as the non_greedy strategy
				if greedy_structure_name == 1:
					non_greedy_structure_strategy = self.get_attempt_which_outperforms_other(candidate_structures_strategies[structure_2_strategies_index])
				if greedy_structure_name == 2:
					non_greedy_structure_strategy = self.get_attempt_which_outperforms_other(candidate_structures_strategies[structure_1_strategies_index])

				print('greedy structure', greedy_structure_strategy)
				print('non greedy structure', non_greedy_structure_strategy)

				# if 2 structures are selected successfully, then place the structures in the level
				if greedy_structure_strategy is not None and non_greedy_structure_strategy is not None:

					# number of pigs in the greedy structure should be higher than the number of pigs in the non greedy structure
					if non_greedy_structure_strategy.strategy_data.shots_data[0].static_data_start.pig_count >= greedy_structure_strategy.strategy_data.shots_data[0].static_data_start.pig_count:
						print('pigs in the non greedy structure is higher or similar than the pigs in the greedy structure')
						continue

					print('matching strategies found, creating the level')
					level_data = self.material_analysis_deception.place_structures_on_level([non_greedy_structure_strategy, greedy_structure_strategy])

					if level_data:
						levels_data.append(level_data)
						# write the level file on the go
						io_handler.write_the_level_file_and_solution(level_data, str(non_greedy_structure_strategy.structure_id) + '_' + str(greedy_structure_strategy.structure_id))

						# get only one level from same structure todo:remove this
						break
		# for bird_type_1_index in range(0, 5):  # for all 5 types of birds
		# 	if not candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index] and not candidate_structures_strategies[structure_2_strategies_index][
		# 		bird_type_1_index]:  # if non of the structures can be solved by the bird_type_1 goto next bird
		# 		continue
		# 	for bird_type_2_index in range(bird_type_1_index + 1, 5):
		# 		if not candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index] and not candidate_structures_strategies[structure_2_strategies_index][
		# 			bird_type_2_index]:  # if non of the structures can be solved by the bird_type_2 goto next bird
		# 			continue
		# 		elif bird_type_1_index == bird_type_2_index:  # same bird go to next bird
		# 			continue
		# 		elif bird_type_1_index == 3 or bird_type_2_index == 3:  # a trick to remove specific bird strategies (testing)
		# 			continue
		# 		else:  # 2 different bird types
		# 			if candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]:
		# 				struct_1_bird_type_1_shot_count = len(candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index].strategy_data.shots_data)
		# 			else:
		# 				struct_1_bird_type_1_shot_count = -1  # structure can not be solved by bird_type_1
		# 			if candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]:
		# 				struct_2_bird_type_1_shot_count = len(candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index].strategy_data.shots_data)
		# 			else:
		# 				struct_2_bird_type_1_shot_count = -1  # structure can not be solved by bird_type_1
		# 			if candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]:
		# 				struct_1_bird_type_2_shot_count = len(candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index].strategy_data.shots_data)
		# 			else:
		# 				struct_1_bird_type_2_shot_count = -1  # structure can not be solved by bird_type_2
		# 			if candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]:
		# 				struct_2_bird_type_2_shot_count = len(candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index].strategy_data.shots_data)
		# 			else:
		# 				struct_2_bird_type_2_shot_count = -1  # structure can not be solved by bird_type_2
		#
		# 			# checking conditions for the matching
		# 			# if any of the 2 structures is not solvable by the selected 2 bird types goto next bird
		# 			if (struct_1_bird_type_1_shot_count == -1 and struct_1_bird_type_2_shot_count == -1) or (struct_2_bird_type_1_shot_count == -1 and struct_2_bird_type_2_shot_count == -1):
		# 				continue
		# 			# if performance of the 2 structures are equal, deception is not that strong since swapping bird types also works
		# 			if struct_1_bird_type_1_shot_count == struct_2_bird_type_1_shot_count and struct_1_bird_type_2_shot_count == struct_2_bird_type_2_shot_count:
		# 				continue
		#
		# 			# determining the strategies #
		# 			structure_1_strategy = None
		# 			structure_2_strategy = None
		# 			# cases where the bird type can't solve a structure
		# 			if struct_1_bird_type_1_shot_count == -1 or struct_2_bird_type_2_shot_count == -1:
		# 				structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]
		# 				structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]  # irrespective of the bird count bird type 1 should use
		# 			elif struct_1_bird_type_2_shot_count == -1 or struct_2_bird_type_1_shot_count == -1:
		# 				structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]
		# 				structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]  # irrespective of the bird count bird type 2 should use
		# 			else:  # all the other cases bird type with minimum shots should use, and 2 structures should get different bird types
		# 				if struct_1_bird_type_1_shot_count < struct_2_bird_type_1_shot_count:
		# 					if struct_2_bird_type_2_shot_count < struct_1_bird_type_2_shot_count:
		# 						# at least one of the bird counts of the 2 structures should be 1, to avoid solutions with mixed birds type (which are not tested)
		# 						if struct_1_bird_type_1_shot_count == 1 or struct_2_bird_type_2_shot_count == 1:
		# 							structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_1_index]
		# 							structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_2_index]
		# 				elif struct_2_bird_type_1_shot_count < struct_1_bird_type_1_shot_count:
		# 					if struct_1_bird_type_2_shot_count < struct_2_bird_type_2_shot_count:
		# 						# at least one of the bird counts of the 2 structures should be 1, to avoid solutions with mixed birds type (which are not tested)
		# 						if struct_2_bird_type_1_shot_count == 1 or struct_1_bird_type_2_shot_count == 1:
		# 							structure_1_strategy = candidate_structures_strategies[structure_1_strategies_index][bird_type_2_index]
		# 							structure_2_strategy = candidate_structures_strategies[structure_2_strategies_index][bird_type_1_index]
		#
		# 			# if 2 strategies were found successfully generate the game level
		# 			if structure_1_strategy is not None and structure_2_strategy is not None:
		# 				print('matching strategies found, creating the level')
		# 				level_data = self.place_structures_on_level([structure_1_strategy, structure_2_strategy])
		#
		# 				if level_data:
		# 					levels_data.append(level_data)
		#
		# 					# write the level file on the go
		# 					io_handler.write_the_level_file_and_solution(level_data,
		# 																 str(structure_1_strategy.structure_id) + '_' + str(structure_2_strategy.structure_id + '_' + str(level_index_start)))
		# 					level_index_start += 1
		#
		# 			print(struct_1_bird_type_1_shot_count, struct_2_bird_type_1_shot_count, struct_1_bird_type_2_shot_count, struct_2_bird_type_2_shot_count)

		return levels_data

	def generate_non_greedy_actions_deception(self):
		candidate_structures_strategies = self.material_analysis_deception.find_candidate_structures_for_material_deception([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
		# print('candidate_structures_strategies', candidate_structures_strategies)

		output_levels = self.match_candidate_structures(candidate_structures_strategies)

# structure_1, structure_2, birds_needed, solving_strategy
# return output_levels
