from utils.data_classes import *
from utils.structure_operations import StructureOperations
from utils.block_operations import BlockOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.io_handler import IOHandler


class HyperResultsAnalyzer:

	def __init__(self, hyper_data, solutions_data, structures):
		self.hyper_data = hyper_data
		self.solutions_data = solutions_data
		self.structure_operations = StructureOperations()
		self.block_operations = BlockOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()
		self.utils = StrategyUtils(structures)

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

	def find_structure_solving_strategies(self):
		candidate_structure_solving_strategies = []

		# for all the structures
		for structure_data in self.hyper_data:
			# best_attempt_of strategies_to_analyze
			best_attempts_of_strategies_to_analyze = []

			# check if the structure contains pigs
			if not self.utils.does_structure_contain_pigs(structure_data):
				print('structure', structure_data.id, ' does not contain pigs or pigs are unreachable')
				candidate_structure_solving_strategies.append([])
				continue

			# get the best strategy attempt of strategies_to_analyze
			for strategy in structure_data.strategies:
				# if strategy.index not in strategies_to_analyze:
				# 	continue

				best_solving_strategy_attempt_of_strategy = self.find_best_strategy_attempt_of_strategy(structure_data.id, strategy)
				# if best_solving_strategy_attempt_of_strategy:
				best_attempts_of_strategies_to_analyze.append(best_solving_strategy_attempt_of_strategy)

			print('best_attempts_of_strategies_to_analyze', best_attempts_of_strategies_to_analyze)
			candidate_structure_solving_strategies.append(best_attempts_of_strategies_to_analyze)

		print('number_of_tested structures', len(candidate_structure_solving_strategies))
		# print('candidate_structure_solving_strategies', candidate_structure_solving_strategies)
		return candidate_structure_solving_strategies

	def get_shots_of_the_strategy(self, level_id):
		return next((solution[1] for solution in self.solutions_data if solution[0] == level_id), None)

	def truncate(self, float_num, decimal_points):
		# return math.trunc(float_num * 10 ** decimal_points) / 10 ** decimal_points
		return round(float_num)

	def does_two_targets_similar(self, target_object_1, target_object_2):
		# compare the location only to one decimal place
		# print(self.truncate(target_object_1.centre[0], 1))

		if target_object_1.object_type == target_object_2.object_type:
			if self.truncate(target_object_1.centre[0], 1) == self.truncate(target_object_2.centre[0], 1):
				if self.truncate(target_object_1.centre[1], 1) == self.truncate(target_object_2.centre[1], 1):
					return True
		return False

	def does_strategy_attempt_is_solution_strategy(self, strategy_attempt: StrategyAttemptSolvedStructure):
		# get the solution strategy
		# print('##### checking the structure', strategy_attempt.structure_id, 'strategy index', strategy_attempt.strategy_index)
		# print('strategy_attempt', strategy_attempt)
		solution_strategy_shots = self.get_shots_of_the_strategy(strategy_attempt.structure_id)
		print('solution_strategy_shots', solution_strategy_shots)

		# if the shot numbers are equal then two strategies are different
		if len(solution_strategy_shots) != len(strategy_attempt.strategy_data.shots_data):
			print('different number of shot counts in the 2 strategies')
			return False
		for shot_number in range(0, len(solution_strategy_shots)):
			print('solution target', solution_strategy_shots[shot_number].target_object.object_type)
			print('solution target location', solution_strategy_shots[shot_number].target_object.centre)
			print('strategy_attempt target', strategy_attempt.strategy_data.shots_data[shot_number].target_object.object_type)
			print('strategy_attempt target location', strategy_attempt.strategy_data.shots_data[shot_number].target_object.centre)
			if not self.does_two_targets_similar(solution_strategy_shots[shot_number].target_object, strategy_attempt.strategy_data.shots_data[shot_number].target_object):
				print('two targets are different')
				return False

		return True

	def count_levels_passed_with_other_strategies_except_solution_strategy(self, structures_solving_strategies):
		print('structures_solving_strategies', structures_solving_strategies)
		all_levels_passed = 0
		levels_passed_with_other_strategies_except_solution_strategy = 0
		vulnerable_structures = []

		all_strategies_solved_the_structure = 0
		non_solution_strategies_solved_the_structure = 0
		deceptive_factor_calculation = 0

		for structure_data in structures_solving_strategies:
			all_strategies_solved_the_structure = 0
			non_solution_strategies_solved_the_structure = 0
			print('structure_data', structure_data)
			for strategy_attempt in structure_data:
				if strategy_attempt:
					# get the minimal shots needed for the strategy
					minimal_strategy = self.utils.get_mandatory_shots_for_solving_the_structure(strategy_attempt)
					if not self.does_strategy_attempt_is_solution_strategy(minimal_strategy):
						non_solution_strategies_solved_the_structure += 1

						# save the structure id as a vulnerable structure (can be solved by other strategies except the solution strategy)
						if minimal_strategy.structure_id not in vulnerable_structures:
							vulnerable_structures.append(minimal_strategy.structure_id)

					all_strategies_solved_the_structure += 1

			print('all_strategies_solved_the_structure', all_strategies_solved_the_structure)
			print('non_solution_strategies_solved_the_structure', non_solution_strategies_solved_the_structure)
			if non_solution_strategies_solved_the_structure != 0:
				levels_passed_with_other_strategies_except_solution_strategy += 1
				deceptive_factor_calculation += non_solution_strategies_solved_the_structure
			if all_strategies_solved_the_structure != 0:
				all_levels_passed += 1

		print('all levels tested', len(structures_solving_strategies))
		print('all passed levels: ', all_levels_passed)
		print('total levels passed with other strategies except the solution strategy: ', levels_passed_with_other_strategies_except_solution_strategy)
		print('vulnerable structures: ', vulnerable_structures)
		# filter the non vulnerable levels to a directory
		io_handler.filter_non_vulnerable_levels(vulnerable_structures)

		# deceptiveness factor = total number of passed strategies except the solution strategy/ total number of strategies tried
		print('deceptiveness factor', deceptive_factor_calculation / (len(structures_solving_strategies[0]) * len(structures_solving_strategies)))

	def is_level_passed(self, structure_data: Structure, utils: StrategyUtils):
		print('## find_structure_solving_strategies of structure', structure_data.id, '##')
		number_of_attempts_to_consider = 100

		# strategy_attempts_solved_the_structure = []

		# for all the strategies_to_analyze of the structure
		for strategy in structure_data.strategies:
			# if strategy.index not in strategies_to_analyze:
			# 	continue
			# else:
			attempts_checked = 0
			# for all the attempts of the same strategy
			for strategy_attempt in strategy.strategy_data:
				# print('strategy', strategy.index, 'attempt', strategy_attempt.attempt)
				if utils.does_attempt_solves_the_structure(strategy_attempt):
					# strategy_attempts_solved_the_structure.append(StrategyAttemptSolvedStructure(structure_data.id, strategy.index, strategy_attempt))
					print('structure solved!')
					return True
				attempts_checked += 1

				if attempts_checked >= number_of_attempts_to_consider:  # break id maximum number of attempts to consider is reached
					return False
		# check if the structure does not have any pigs (structure which is not needed to solve) by checking the number of pigs at the start of the first strategy
		# if strategy_attempt.shots_data:
		# 	if strategy_attempt.shots_data[0].static_data_start.pig_count == 0:
		# 		return

		# if no strategy attempt solves the structure return false
		return False

	def count_passed_levels(self, structures_data: [Structure], utils: StrategyUtils):

		passed_count = 0
		for structure_data in structures_data:
			if self.is_level_passed(structure_data, utils):
				passed_count += 1

		total_levels = len(structures_data)
		print('total levels tested: ', total_levels)
		print('total levels passed: ', passed_count)
		print('passing rate:', passed_count * 100 / total_levels)

	def main(self, testing_data):

		# print('testing_results_agent', testing_results_agent)
		# print('testing_results_game', testing_results_game)
		# print('combined_testing_data', testing_data)

		# find the number of passed levels
		# self.count_passed_levels(testing_data, self.utils)
		structures_solving_strategies = self.find_structure_solving_strategies()
		total_levels_passed = 0
		for structure_data in structures_solving_strategies:
			# print('structure_data', structure_data)
			for strategy in structure_data:
				if strategy:
					total_levels_passed += 1
					break
		print('total_levels_passed', total_levels_passed)

		self.count_levels_passed_with_other_strategies_except_solution_strategy(structures_solving_strategies)


if __name__ == "__main__":
	# read the input files
	io_handler = IOHandler()

	structures = io_handler.read_all_structure_files()
	hyper_results_agent = io_handler.read_structure_analyzer_json_file(hyper_results_agent_file)
	hyper_results_game = io_handler.read_structure_analyzer_json_file(hyper_results_game_file)
	solutions_data = io_handler.read_solution_files()
	hyper_data = io_handler.process_structure_data(hyper_results_agent, hyper_results_game)
	strategy_analyzer = HyperResultsAnalyzer(hyper_data, solutions_data, structures)
	strategy_analyzer.main(hyper_data)
