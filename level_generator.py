from utils.rolling_falling_deception import RollingFallingDeception
from utils.material_analysis_deception import MaterialAnalysisDeception
from utils.clearing_paths_deception import ClearingPathsDeception
from utils.tap_time_deception import TapTimeDeception
from utils.non_greedy_actions_deception import NonGreedyActionsDeception
from utils.TNT_deception import TNTDeception
from utils.io_handler import IOHandler
from utils.constants import *


class StrategyAnalyzer:
	deception_considered = 'clearing_paths'
	analyzing_results_agent = []

	def main(self):
		# read the input files
		io_handler = IOHandler()
		structures = io_handler.read_all_structure_files()
		analyzing_results_agent = io_handler.read_structure_analyzer_json_file(analyzing_results_agent_file)
		analyzing_results_game = io_handler.read_structure_analyzer_json_file(analyzing_results_game_file)
		analysis_data = io_handler.process_structure_data(analyzing_results_agent, analyzing_results_game)

		# generate game levels according to the deception
		if self.deception_considered == 'rolling_falling':
			rolling_falling_deception = RollingFallingDeception(analysis_data, structures)
			rolling_falling_deception.generate_rolling_falling_objects_deception()
		elif self.deception_considered == 'clearing_paths':
			clearing_paths_deception = ClearingPathsDeception(analysis_data, structures)
			clearing_paths_deception.generate_clearing_paths_deception()
		elif self.deception_considered == 'material_analysis':
			material_analysis_deception = MaterialAnalysisDeception(analysis_data, structures)
			material_analysis_deception.generate_material_analysis_deception()
		elif self.deception_considered == 'non_greedy_actions':
			non_greedy_actions_deception = NonGreedyActionsDeception(analysis_data, structures)
			non_greedy_actions_deception.generate_non_greedy_actions_deception()
		elif self.deception_considered == 'tap_time':
			tap_time_deception = TapTimeDeception(analysis_data, structures)
			tap_time_deception.generate_tap_time_deception()
		elif self.deception_considered == 'TnT':
			tnt_deception = TNTDeception(analysis_data, structures)
			tnt_deception.generate_TNT_deception()


if __name__ == "__main__":
	strategy_analyzer = StrategyAnalyzer()
	strategy_analyzer.main()
