import sys
from utils.rolling_falling_deception import RollingFallingDeception
from utils.material_analysis_deception import MaterialAnalysisDeception
from utils.clearing_paths_deception import ClearingPathsDeception
from utils.tap_time_deception import TapTimeDeception
from utils.non_greedy_actions_deception import NonGreedyActionsDeception
from utils.TNT_deception import TNTDeception
from utils.io_handler import IOHandler
from utils.constants import *


class StrategyAnalyzer:
	analyzing_results_agent = []

	def main(self):

		# check the deception that needs to be generated 1: Rolling/falling objects deception, 2: Clearing paths deception, 3: Entity strength analysis deception,
		# 4: Non-greedy actions deception 5: Non-fixed tap time deception 6: TNT deception
		try:
			deception_index = int(sys.argv[1])
			print('user given deception index for the generation:', deception_index)
		except:
			print('the deception index provided is invalid, using the default deception 2: Clearing paths deception')
			deception_index = 2

		# read the input files
		io_handler = IOHandler()
		structures = io_handler.read_all_structure_files()
		analyzing_results_agent = io_handler.read_structure_analyzer_json_file(analyzing_results_agent_file)
		analyzing_results_game = io_handler.read_structure_analyzer_json_file(analyzing_results_game_file)
		analysis_data = io_handler.process_structure_data(analyzing_results_agent, analyzing_results_game)

		# generate game levels according to the deception
		if deception_index == '1':
			rolling_falling_deception = RollingFallingDeception(analysis_data, structures)
			rolling_falling_deception.generate_rolling_falling_objects_deception()
		elif deception_index == '2':
			clearing_paths_deception = ClearingPathsDeception(analysis_data, structures)
			clearing_paths_deception.generate_clearing_paths_deception()
		elif deception_index == '3':
			material_analysis_deception = MaterialAnalysisDeception(analysis_data, structures)
			material_analysis_deception.generate_material_analysis_deception()
		elif deception_index == '4':
			non_greedy_actions_deception = NonGreedyActionsDeception(analysis_data, structures)
			non_greedy_actions_deception.generate_non_greedy_actions_deception()
		elif deception_index == '5':
			tap_time_deception = TapTimeDeception(analysis_data, structures)
			tap_time_deception.generate_tap_time_deception()
		elif deception_index == '6':
			tnt_deception = TNTDeception(analysis_data, structures)
			tnt_deception.generate_TNT_deception()


if __name__ == "__main__":
	strategy_analyzer = StrategyAnalyzer()
	strategy_analyzer.main()
