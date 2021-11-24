# directory to write generated solution files
solution_files_directory = './output_levels/'

# directory for the structure files
structure_input_folder = './structure_files/'
level_output_folder = './output_levels/'

# block sizes in the game
blocks = {'SquareHole': [0.84, 0.84], 'RectFat': [0.85, 0.43], 'SquareSmall': [0.43, 0.43], 'SquareTiny': [0.22, 0.22], 'RectTiny': [0.43, 0.22], 'RectSmall': [0.85, 0.22],
		  'RectMedium': [1.68, 0.22], 'RectBig': [2.06, 0.22], 'TriangleHole': [0.82, 0.82], 'Triangle': [0.82, 0.82], 'Circle': [0.8, 0.8], 'CircleSmall': [0.45, 0.45], 'Platform': [0.64, 0.64]}

# pigs sizes in the game
pigs = {'BasicSmall': [0.47, 0.45], 'BasicMedium': [0.78, 0.76], 'BasicBig': [0.99, 0.97], 'novel_object_1': [1.29, 1.44]}

# tnt size in the game
tnts = {'TNT': [0.66, 0.66]}

# ground level in the level
ground_level = -3.5

# level area of SB
# level_width_min = -6.0
# level_width_max = 9.0
level_width_min = -9.0
level_width_max = 5.0
level_height_min = -3.5
level_height_max = 6.0  # 10.0

# scale of different coordinate systems
usc_x_offset = 274
usc_y_offset = 130.5
usc_x_scale = 16
usc_y_scale = 16

### input files from the structure analyzer ###

# analyzing_results_game_file = '..\\sciencebirds\\Bin\\analyzing_results_game.json'
# analyzing_results_game_file = '.\\analysis_output\\analyzing_results_game.json'
# analyzing_results_agent_file = '.\\analysis_output\\analyzing_results_agent.json'

# analyzing_results_game_file = '.\\analysis_output\\analyzing_results_material_game.json'
# analyzing_results_agent_file = '.\\analysis_output\\analyzing_results_material_agent.json'

analyzing_results_game_file = './analysis_output/analyzing_results_clearing_paths_game.json'
analyzing_results_agent_file = './analysis_output/analyzing_results_clearing_paths_agent.json'

# analyzing_results_game_file = '.\\analysis_output\\analyzing_results_tap_time_game.json'
# analyzing_results_agent_file = '.\\analysis_output\\analyzing_results_tap_time_agent.json'

### input files from the testing results analyzer ###

# testing_results_game_file = '.\\analysis_output\\analyzing_results_game.json'
# testing_results_agent_file = '.\\analysis_output\\analyzing_results_agent.json'

# testing_results_game_file = '..\\analysis_output\\testing_results_rolling_falling_game.json'
# testing_results_agent_file = '.\\analysis_output\\testing_results_rolling_falling_agent.json'

# testing_results_game_file = '.\\analysis_output\\testing_results_material_game.json'
# testing_results_agent_file = '.\\analysis_output\\testing_results_material_agent.json'

# testing_results_game_file = '.\\analysis_output\\testing_results_clearing_paths_game.json'
# testing_results_agent_file = '.\\analysis_output\\testing_results_clearing_paths_agent.json'

### input files from the hyper agent result analyzer ###
# hyper_results_game_file = '..\\sciencebirds - Yiwen\\Bin\\analyzing_results_game.json'
# hyper_results_agent_file = '..\\sciencebirdsframework_release\\analyzing_results_agent.json'
#
# # file to save passed levels indexes
# passed_levels_data_file = 'passed_level_ids.txt'
# # directory for filtering passed levels
# testing_levels_directory = '..\\sciencebirds - Yiwen\\Bin\\Science Birds_Data\\StreamingAssets\\Levels\\novelty_level_0\\type2\\Levels\\'
# # directory to save passed levels
# passed_levels_directory = './solved_levels/'
# # directory for non vulnerable levels
# non_vulnerable_levels_directory = './non_vulnerable_levels/'
