from utils.io_handler import IOHandler
from utils.data_classes import *
from utils.strategy_utils import StrategyUtils


class TestingResultAnalyzer:

	def is_level_passed(self, structure_data: Structure, strategies_to_analyze, utils: StrategyUtils):
		print('## find_structure_solving_strategies of structure', structure_data.id, '##')
		number_of_attempts_to_consider = 100

		# strategy_attempts_solved_the_structure = []

		# for all the strategies_to_analyze of the structure
		for strategy in structure_data.strategies:
			if strategy.index not in strategies_to_analyze:
				continue
			else:
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

	def count_passed_levels(self, structures_data: [Structure], strategies_to_analyze, utils: StrategyUtils):

		passed_count = 0
		passed_levels_ids = []
		for structure_data in structures_data:
			if self.is_level_passed(structure_data, strategies_to_analyze, utils):
				passed_count += 1
				passed_levels_ids.append(structure_data.id)

		total_levels = len(structures_data)
		print('total levels tested: ', total_levels)
		print('total levels passed: ', passed_count)
		print('passing rate:', passed_count * 100 / total_levels)

		return passed_levels_ids

	def main(self):
		# read the input files
		io_handler = IOHandler()

		structures = io_handler.read_all_structure_files()
		testing_results_agent = io_handler.read_structure_analyzer_json_file(testing_results_agent_file)
		testing_results_game = io_handler.read_structure_analyzer_json_file(testing_results_game_file)
		testing_data = io_handler.process_structure_data(testing_results_agent, testing_results_game)

		#print('testing_results_agent', testing_results_agent)
		#print('testing_results_game', testing_results_game)
		#print('combined_testing_data', testing_data)

		# find the number of passed levels
		utils = StrategyUtils(structures)
		passed_levels_ids = self.count_passed_levels(testing_data, [1], utils)

		# write the passed levels ids
		io_handler.write_passed_levels_ids(passed_levels_ids)

		# filter passed levels
		io_handler.filter_passed_levels()


if __name__ == "__main__":
	testing_results_analyzer = TestingResultAnalyzer()
	testing_results_analyzer.main()
