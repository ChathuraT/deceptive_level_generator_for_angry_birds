from random import randint

import jsonpickle
import re
import os
from shutil import copyfile

from utils.data_classes import *
from utils.constants import *


class IOHandler:
	level_file_meta = '<?xml version="1.0" encoding="utf-16"?>\n<Level width="2">\n	<Camera x="0" y="-1" minWidth="25" maxWidth="35" />\n'
	rounding_digits = 4

	def read_solution_files(self):
		solution_files = os.listdir(solution_files_directory)
		solutions_read = []

		# read all the files in the directory
		for solution_file in solution_files:

			# do not read level files in the output directory
			if 'solution' not in solution_file:
				# print('skip', solution_file)
				continue

			solution_data = self.read_solution_file(solution_files_directory + solution_file)

			# check if the level id is a duplicate (multiple levels with same id), if so abort
			if solution_data[0] in [solution[0] for solution in solutions_read]:
				raise ValueError('Duplicate solutions for the same level id, possibly multiple levels with same id! level id:', solution_data[0], 'file name: ', solution_file)

			solutions_read.append(solution_data)

		return solutions_read

	def read_solution_file(self, solution_file_name):
		# read the level file and extract the objects
		print('reading the solution file', solution_file_name)

		shots_data = []
		level_id = None
		with open(solution_file_name) as level_file:
			for line in level_file:
				if 'levelID' in line:
					level_id = int(re.search('levelID="(.*?)"', line).group(1))
				elif '<Shot' in line:  # start of a new shot data element
					shot_number = int(re.search('shotNumber="(.*?)"', line).group(1))
				elif '<Bird' in line:
					bird_type = re.search('type="(.*?)"', line).group(1)
				elif '<Target' in line:
					target_type = re.search('type="(.*?)"', line).group(1)
					target_material = re.search('material="(.*?)"', line).group(1)
					target_center_x = float(re.search('x="(.*?)"', line).group(1))
					target_center_y = float(re.search('y="(.*?)"', line).group(1))
				elif '<Trajectory' in line:
					trajectory_selection = re.search('selection="(.*?)"', line).group(1)
					if trajectory_selection == 'low':
						trajectory_selection = 1
					elif trajectory_selection == 'high':
						trajectory_selection = 2
					else:  # any_pigs none selection; set it to low
						trajectory_selection = 1
				elif '<Tap' in line:
					tap_interval = int(re.search('interval="(.*?)"', line).group(1))
				elif '</Shot>' in line:  # end of the shot data element
					shots_data.append(
						ShotDataSolutionFile(shot_number, bird_type, tap_interval, trajectory_selection, TargetObject(target_type, target_material, [target_center_x, target_center_y])))

		solution = [level_id, shots_data]

		return solution

	def read_structure_analyzer_json_file(self, file_name):
		data_read = []
		with open(file_name) as file:
			# json_string = file.read()
			for structure_data in file:
				# print('structure_data', structure_data)
				# data_read = json.loads(json_string)
				data_read.append(jsonpickle.decode(structure_data))

		# print('data_read', data_read)
		return data_read

	def get_all_structure_indexes(self, analyzing_results_game):
		all_indexes = []
		for structure in analyzing_results_game:
			if structure['structureID'] not in all_indexes:
				all_indexes.append(int(structure['structureID']))

		return all_indexes

	def process_structure_data(self, analyzing_results_agent, analyzing_results_game):
		processed_data = []
		# get all the structure indexes in analyzing_results_game
		all_structure_ids = self.get_all_structure_indexes(analyzing_results_game)
		print('all_structure_ids', all_structure_ids)

		for structure_id in all_structure_ids:
			print('structure_id', structure_id)
			strategy_data_game = []
			strategy_data_agent = []
			all_structure_data = Structure(structure_id, list())

			# get all the game data elements associated with the same structure index (if there are multiple attempts)
			for structure_data in analyzing_results_game:
				if int(structure_data['structureID']) == structure_id:
					strategy_data_game += structure_data['strategyDatas']

			# get all the agent data elements associated with the same structure index (if there are multiple attempts)
			for structure_data in analyzing_results_agent:
				if int(structure_data['structure_id']) == structure_id:
					strategy_data_agent += structure_data['strategy_data']

			# print('strategy_data_game', strategy_data_game)
			# print('strategy_data_agent', strategy_data_agent)

			# get all the strategies attempted for the structure and create Strategy elements
			all_strategy_indexes = []
			for strategy in strategy_data_game:
				if strategy['strategyIndex'] not in all_strategy_indexes:
					# create Strategy data element
					all_structure_data.strategies.append(Strategy(strategy['strategyIndex'], list()))
					all_strategy_indexes.append(strategy['strategyIndex'])

			# print('all_strategy_indexes', all_strategy_indexes)

			# for all the strategies
			for attempt in range(0, len(strategy_data_game)):
				# get the corresponding StrategyData element from the all_structure_data
				# print('strategy_data_game[attempt]', strategy_data_game[attempt])
				strategy_data_element = next(strategy for strategy in all_structure_data.strategies if strategy.index == int(strategy_data_game[attempt]['strategyIndex']))

				# get the shot datas of the strategy
				print('attempt', attempt)
				shots_data_from_agent = strategy_data_agent[attempt]['shot_data']
				shots_data_from_game = strategy_data_game[attempt]['shotOutputDatas']
				shots_data = self.get_shots_data_processed(shots_data_from_agent, shots_data_from_game)
				strategy_data_element.strategy_data.append(StrategyData(len(strategy_data_element.strategy_data) + 1, shots_data))

			# print('strategy_data_element', strategy_data_element)

			# print('all_structure_data', all_structure_data)
			processed_data.append(all_structure_data)

		# print('processed_data', processed_data)
		return processed_data

	# for structure_data in analyzing_results_game:
	# 	# get all the data elements from the same structure
	#
	# 		print(structure_data)
	# 	print('structureID', structure_data['structureID'])

	# process the shots in a given shot_data/shotOutputDatas of a strategy data
	def get_shots_data_processed(self, shots_data_from_agent, shots_data_from_game):
		# print('shots_data_from_agent', shots_data_from_agent)
		# print('shots_data_from_game', shots_data_from_game)
		all_shots_data = []
		# for all the shots in the strategy
		for shot_index in range(0, len(shots_data_from_game)):

			static_data_start_not_valid = False
			dynamic_data_not_valid = False
			static_data_end_not_valid = False
			target_object_not_valid = False
			static_data_start = None
			dynamic_data = None
			static_data_end = None
			target_object = None

			shot_data_agent = shots_data_from_agent[shot_index]
			shot_data_game = shots_data_from_game[shot_index]
			try:
				# create static data before the shot
				static_data_start = StaticDataStart(shot_data_game['staticDataStart']['numberOfPigs'], shot_data_game['staticDataStart']['boundingBox'])
			except:
				static_data_start_not_valid = True
			try:
				# create the dynamic data list
				dynamic_data = []
				for dynamic_data_element in shot_data_game['dynamicData']['DynamicDataElements']:

					# create the objects gone out list
					objects_gone_out = []
					for object_gone_out in dynamic_data_element['objectsGoneOut']:
						objects_gone_out.append(ObjectGoneOut(object_gone_out['objectID'], object_gone_out['objectType'], object_gone_out['material'], object_gone_out['centre'],
															  object_gone_out['velocity']))

					dynamic_data.append(DynamicData(dynamic_data_element['time'], objects_gone_out))
			except:
				dynamic_data_not_valid = True
			try:
				# create static data after the shot
				static_data_end = StaticDataEnd(shot_data_game['staticDataEnd']['numberOfPigs'], shot_data_game['staticDataEnd']['boundingBox'],
												shot_data_game['staticDataEnd']['shotHasImpact'])
			except:
				static_data_end_not_valid = True
			try:
				# create agents target object
				target_object = TargetObject(shot_data_agent['target_object']['object_type'], shot_data_agent['target_object']['material'], shot_data_agent['target_object']['centre'])
			except:
				target_object_not_valid = True

			# if static data start or static data end is not valid, there is an issue with data recording of that shot. Don't save it (WARNING: this may leads to having wrong strategies, haven't tested)
			if static_data_start_not_valid or static_data_end_not_valid:
				print("A shot data skipped due to an issue with static data recording at the start or end...")
				continue
			# save the shot data
			all_shots_data.append(ShotData(shot_data_game['shotNumber'], static_data_start, dynamic_data, static_data_end, shot_data_agent['bird_type'], shot_data_agent['tap_interval'],
										   shot_data_agent['trajectory_selection'], target_object))
		# except:
		# 	# mostly when dynamic data is empty
		# 	print('NoneType detected:', shot_data_game)

		# print('all_shots_data', all_shots_data)
		return all_shots_data

	def read_structure_file(self, level_file_name):
		# read the level file and extract the objects
		print('reading the level file', level_file_name)

		all_blocks = []
		all_pigs = []
		all_tnts = []
		meta_data = ''
		structure_id = -2

		# use the count of the object as an identifier for the object
		object_count = 0

		with open(level_file_name) as level_file:
			for line in level_file:
				if 'Block' in line:
					object_count += 1
					type = re.search('type="(.*?)"', line).group(1)
					material = re.search('material="(.*?)"', line).group(1)
					x = re.search('x="(.*?)"', line).group(1)
					y = re.search('y="(.*?)"', line).group(1)
					rotation = re.search('rotation="(.*?)"', line).group(1)

					all_blocks.append(Block(object_count, type, material, float(x), float(y), float(rotation), 1, 1, structure_id))

				elif 'Platform' in line:
					object_count += 1

					type = re.search('type="(.*?)"', line).group(1)
					x = re.search('x="(.*?)"', line).group(1)
					y = re.search('y="(.*?)"', line).group(1)
					scale_x = re.search('scaleX="(.*?)"', line).group(1) if re.search('scaleX="(.*?)"',
																					  line) is not None else 1
					scale_y = re.search('scaleY="(.*?)"', line).group(1) if re.search('scaleY="(.*?)"',
																					  line) is not None else 1
					rotation = re.search('rotation="(.*?)"', line).group(1) if re.search('rotation="(.*?)"',
																						 line) is not None else 0

					all_blocks.append(
						Block(object_count, type, "", float(x), float(y), float(rotation), float(scale_x), float(scale_y), structure_id))

				elif 'Pig' in line:
					object_count += 1

					type = re.search('type="(.*?)"', line).group(1)
					x = re.search('x="(.*?)"', line).group(1)
					y = re.search('y="(.*?)"', line).group(1)
					rotation = re.search('rotation="(.*?)"', line).group(1)

					all_pigs.append(Pig(object_count, type, float(x), float(y), float(rotation), structure_id))

				elif 'TNT' in line:
					object_count += 1

					x = re.search('x="(.*?)"', line).group(1)
					y = re.search('y="(.*?)"', line).group(1)
					rotation = re.search('rotation="(.*?)"', line).group(1)

					all_tnts.append(Tnt(object_count, float(x), float(y), float(rotation), 'TNT', structure_id))

				else:
					if '<GameObjects>' in line or '</GameObjects>' in line or '</Level>' in line:
						continue
					elif '<Score' in line:
						structure_id = int(re.search('<Score highScore="(.* ?)"', line).group(1))
					else:
						meta_data += line

		return [structure_id, (all_blocks, all_pigs, all_tnts, meta_data)]

	def read_all_structure_files(self):
		structure_files = os.listdir(structure_input_folder)
		structures_read = []
		number_of_structures_read = 0
		# read all the files in the directory
		for structure_file in structure_files:
			structure_data = self.read_structure_file(structure_input_folder + structure_file)
			# convert_to_screen_coordinates(structure_data[0], structure_data[1])
			# number_of_structures_read += 1
			structures_read.append(structure_data)

		return structures_read

	def write_passed_levels_ids(self, passed_levels_ids):
		data_file = open(passed_levels_data_file, "w")

		for passed_level_id in passed_levels_ids:
			data_file.write(str(passed_level_id) + '\n')

		data_file.close()

	def filter_passed_levels(self):
		passed_levels_ids = []

		# read passed levels indexes
		with open(passed_levels_data_file) as passed_levels_data:
			for line in passed_levels_data:
				passed_levels_ids.append(int(line[:-1]))

		print('passed_levels_ids', passed_levels_ids)
		level_files = os.listdir(testing_levels_directory)
		structures_read = []
		pass_count = 0
		# read all the files in the directory
		for level_file in level_files:
			level_id = self.read_structure_file(testing_levels_directory + level_file)[0]
			# print('level id', level_id)
			if level_id in passed_levels_ids:
				# print('passed level', level_id)
				pass_count += 1
				# copy the level file to
				copyfile(testing_levels_directory + level_file, passed_levels_directory + level_file)

		print('pass_count', pass_count)

	def filter_non_vulnerable_levels(self, vulnerable_level_ids):

		print('vulnerable_level_ids', vulnerable_level_ids)
		level_files = os.listdir(passed_levels_directory)
		structures_read = []
		non_vulnerable_count = 0
		# read all the files in the directory
		for level_file in level_files:
			level_id = self.read_structure_file(passed_levels_directory + level_file)[0]
			# print('level id', level_id)
			if level_id in vulnerable_level_ids:
				continue
			# print('passed level', level_id)
			non_vulnerable_count += 1
			# copy the level file to
			copyfile(passed_levels_directory + level_file, non_vulnerable_levels_directory + level_file)

		print('non vulnerable levels filtered', non_vulnerable_count)

	def write_the_level_file(self, structures, birds_data, level_id, file_name):

		all_blocks = []
		all_pigs = []
		all_tnts = []

		for structure in structures:
			all_blocks += structure[0]
			all_pigs += structure[1]
			all_tnts += structure[2]

		level_file = open(level_output_folder + file_name, "w")

		# write meta data
		level_file.write(self.level_file_meta)

		# write the unique ID in the highscore tag
		level_file.write('	<Score highScore="%s" />\n' % str(level_id))

		# write birds data
		level_file.write('	<Birds>\n')
		for bird in birds_data:
			bird_name = 'unknown'
			if bird == 'bird_red':
				bird_name = 'BirdRed'
			if bird == 'bird_yellow':
				bird_name = 'BirdYellow'
			if bird == 'bird_blue':
				bird_name = 'BirdBlue'
			if bird == 'bird_white':
				bird_name = 'BirdWhite'
			if bird == 'bird_black':
				bird_name = 'BirdBlack'
			level_file.write('		<Bird type="' + bird_name + '" />\n')
		level_file.write('	</Birds>\n')

		# write slingshot and all game objects
		level_file.write('	<Slingshot x="-12.0" y="-2.5" />\n')
		level_file.write('	<GameObjects>\n')

		# write pigs
		for pig in all_pigs:
			# unchanged pigs
			level_file.write('		<Pig type="%s" material="" x="%s" y="%s" rotation="%s" />\n' % (
				pig.type, str(round(pig.x, self.rounding_digits)), str(round(pig.y, self.rounding_digits)),
				str(round(pig.rotation, self.rounding_digits))))

		# write TNTs
		for tnt in all_tnts:
			level_file.write('		<TNT type="" x="%s" y="%s" rotation="%s" />\n' % (
				str(round(tnt.x, self.rounding_digits)), str(round(tnt.y, self.rounding_digits)), str(round(tnt.rotation, self.rounding_digits))))

		# write blocks
		for block in all_blocks:
			# check if platform
			if block.type == 'Platform':
				level_file.write('		<Platform type="%s" material="" x="%s" y="%s" rotation="%s" scaleX="%s" scaleY="%s" />\n' % (
					block.type, str(round(block.x, self.rounding_digits)), str(round(block.y, self.rounding_digits)),
					str(round(block.rotation, self.rounding_digits)),
					str(round(block.scale_x, self.rounding_digits)),
					str(round(block.scale_y, self.rounding_digits))))

			# normal blocks
			else:
				level_file.write('		<Block type="%s" material="%s" x="%s" y="%s" rotation="%s" />\n' % (
					block.type, block.material, str(round(block.x, self.rounding_digits)), str(round(block.y, self.rounding_digits)),
					str(round(block.rotation, self.rounding_digits))))

		# close the level file
		level_file.write('	</GameObjects>\n')
		level_file.write('</Level>\n')
		level_file.close()

	def write_the_solution_file(self, solution, level_id, file_name):
		solution_file = open(level_output_folder + file_name, "w")
		solution_file.write('<Solution levelID="%s">\n' % str(level_id))
		# write all the shots
		shot_number = 0
		for solution_shot_data in solution:
			shot_data = solution_shot_data.shot_data
			shot_number += 1
			solution_file.write('	<Shot shotNumber="' + str(shot_number) + '" structureID="' + str(solution_shot_data.structure_id) + '">\n')
			solution_file.write('		<Bird type="' + shot_data.bird_type + '" />\n')

			if shot_data.target_object.object_type == 'any_pig':  # pigs which were not there in the selected strategy
				solution_file.write('		<Target type="' + str(shot_data.target_object.object_type) + '" material="" x="" y="' + '" />\n')
			else:
				solution_file.write(
					'		<Target type="' + str(shot_data.target_object.object_type) + '" material="' + str(shot_data.target_object.material) + '" x="' + str(
						round(shot_data.target_object.centre[0], self.rounding_digits)) + '" y="' + str(round(shot_data.target_object.centre[1], self.rounding_digits)) + '" />\n')

			trajectory_selection = 'none'
			if shot_data.trajectory_selection == 1:
				trajectory_selection = 'low'
			elif shot_data.trajectory_selection == 2:
				trajectory_selection = 'high'

			solution_file.write('		<Trajectory selection="' + trajectory_selection + '" />\n')
			solution_file.write('		<Tap interval="' + str(shot_data.tap_time) + '" />\n')

			solution_file.write('	</Shot>\n')
		solution_file.write('</Solution>\n')
		solution_file.close()

	def write_the_level_file_and_solution(self, level_data, level_file_name):
		# level data should contain [[structure_1, structure_2, ...][bird_1, bird_2, ...][solution]]

		# create a unique ID based on the timestamp for the level and solution
		# level_id = int(time.mktime(datetime.now().timetuple()))
		level_id = randint(10000000, 99999999)

		# write the level file
		self.write_the_level_file(level_data[0], level_data[1], level_id, level_file_name + '.xml')

		# write the solution file
		self.write_the_solution_file(level_data[-1], level_id, level_file_name + '_solution.xml')
