import copy
import math
import itertools

from utils.data_classes import *
from utils.constants import *
from utils.structure_operations import StructureOperations
from utils.trajectory_planner import SimpleTrajectoryPlanner
from utils.strategy_utils import StrategyUtils
from utils.io_handler import IOHandler


class RollingFallingDeception:

	def __init__(self, analysis_data, structures):
		self.analysis_data = analysis_data
		self.structures = structures
		self.structure_operations = StructureOperations()
		self.trajectory_planner = SimpleTrajectoryPlanner()
		self.utils = StrategyUtils(structures)
		self.io_handler = IOHandler()

	# returns the block with highest impact when throwing (considering the velocity and the object type)
	def get_object_with_highest_impact(self, objects_thrown_out: [SelectedObjectGoneOut]):

		# if there are circular objects give priority to them
		objects_considered = [obj for obj in objects_thrown_out if obj.object_gone_out.object_type == 'Circle' or obj.object_gone_out.object_type == 'CircleSmall']
		# if no circular objects equal priority for other objects todo:consider giving priority for objects with higher health points
		if not objects_considered:
			print('no circular objects found')
			objects_considered = objects_thrown_out

		# calculate the velocities of objects_considered
		velocities_of_objects_considered = []

		for object_considered in objects_considered:
			velocities_of_objects_considered.append(math.sqrt(object_considered.object_gone_out.velocity[0] ** 2 + object_considered.object_gone_out.velocity[1] ** 2))

		# print('velocities_of_objects_considered', velocities_of_objects_considered)

		# rank objects_considered according to velocity
		sort_indexes = sorted(range(len(velocities_of_objects_considered)), key=lambda k: velocities_of_objects_considered[k])
		objects_considered = [objects_considered[i] for i in sort_indexes]  # todo: verify the ranking

		# return the object with the highest rank
		return objects_considered[0]

	def get_object_with_highest_impact_old(self, objects_thrown_out):

		# if there are circular objects give priority to them
		objects_considered = [obj for obj in objects_thrown_out if obj.object_type == 'Circle' or obj.object_type == 'CircleSmall']
		# if no circular objects equal priority for other objects todo:consider giving priority for objects with higher health points
		if not objects_considered:
			print('no circular objects found')
			objects_considered = objects_thrown_out

		# calculate the velocities of objects_considered
		velocities_of_objects_considered = []

		for object_considered in objects_considered:
			velocities_of_objects_considered.append(math.sqrt(object_considered.velocity[0] ** 2 + object_considered.velocity[1] ** 2))

		print('velocities_of_objects_considered', velocities_of_objects_considered)

		# rank objects_considered according to velocity
		sort_indexes = sorted(range(len(velocities_of_objects_considered)), key=lambda k: velocities_of_objects_considered[k])
		objects_considered = [objects_considered[i] for i in sort_indexes]  # todo: verify the ranking

		# return the object with the highest rank
		return objects_considered[0]

	def get_best_location_of_the_object_going_out(self, object_data_sequence):

		# return the entry closest to the ground (with of the object/2 + threshold is taken as the closest point to the ground)
		# modification: return the entry closer to the center of the 2nd and 4th  of the quarters
		y_level_considered = level_height_min + (level_height_max - level_height_min) / 2
		for entry in object_data_sequence:
			# if entry.centre[1] < ground_level + blocks[entry.object_type][1] / 2 + 0.2:
			if entry.centre[1] < y_level_considered:
				return entry

	# returns the most impacting object (and its location)
	def analyze_dynamic_data(self, shot_data: ShotData):

		objects_gone_out = []

		# for all the dynamic data elements of the shot
		for dynamic_data_element in shot_data.dynamic_data:
			# print('time:', dynamic_data_element.time)
			# for all the objects gone out
			for object_gone_out in dynamic_data_element.objects_gone_out:
				# disregard birds going out
				if 'bird' in object_gone_out.object_type:
					continue
				# record the object gone out
				objects_gone_out.append(object_gone_out)
		# print(object_gone_out)

		# for the same object recorded multiple times get the object location closest to the ground(assuming that object has the highest velocity close to the ground)
		objects_considered = []
		unique_objects_gone_out = []
		for object_gone_out in objects_gone_out:
			if object_gone_out.object_id not in objects_considered:
				objects_considered.append(object_gone_out.object_id)
				# get all the entries of the same object
				# same_object_entries = filter(lambda obj: obj.object_id == object_gone_out.object_id, objects_gone_out)
				same_object_entries = [obj for obj in objects_gone_out if obj.object_id == object_gone_out.object_id]
				print('same_object_entries', same_object_entries)
				# get the best entry to the ground
				best_location_entry_of_object_going_out = self.get_best_location_of_the_object_going_out(same_object_entries)
				if best_location_entry_of_object_going_out is not None:
					print('best_location_entry_of_object_going_out', best_location_entry_of_object_going_out)
					unique_objects_gone_out.append(best_location_entry_of_object_going_out)

		# from the unique objects going out get the object with the highest impact
		# object_selected = self.get_object_with_highest_impact(unique_objects_gone_out)

		print('unique_objects_gone_out', unique_objects_gone_out)
		# from all the objects going out select the one with the highest impact (velocity and type)
		return unique_objects_gone_out

	def find_objects_going_out(self, structure_data):
		print('## find_objects_going_out of structure', structure_data.id, '##')
		objects_going_out = []  # record the strategy, attempt, shot, ObjectGoneOut
		# for all the strategies of the structure
		for strategy in structure_data.strategies:
			# if strategy.index not in strategies_to_analyze:
			# 	continue
			# else:
			# for all the attempts of the same strategy
			for strategy_attempt in strategy.strategy_data:
				# for all the shots of the same attempt
				for shot_data in strategy_attempt.shots_data:

					print('strategy', strategy.index, 'attempt', strategy_attempt.attempt, 'shot', shot_data.shot_number)

					# skip if the shot has no any impact or objects gone out is empty
					if not shot_data.static_data_end.shot_has_impact:
						print('shot has no impact')
						continue
					if not shot_data.dynamic_data:
						print('shot has no dynamic_data')
						continue

					unique_objects_going_out = self.analyze_dynamic_data(shot_data)
					for unique_object_going_out in unique_objects_going_out:
						objects_going_out.append(
							SelectedObjectGoneOut(structure_data.id, strategy.index, strategy_attempt.attempt, shot_data.shot_number, unique_object_going_out))

		print('objects_going_out', objects_going_out)
		# if no object is going out from the structure return
		if not objects_going_out:
			return

		# from all the objects going out get the one with the most impact
		highest_impact_object_going_out = self.get_object_with_highest_impact(objects_going_out)

		print('highest_impact_object_going_out', highest_impact_object_going_out)

		return highest_impact_object_going_out

	# find strategies which solve a given structure
	def find_best_structure_solving_strategy(self, structure_data: Structure, strategies_to_analyze):
		print('## find_structure_solving_strategies of structure', structure_data.id, '##')
		strategy_attempts_solved_the_structure = []

		# for all the strategies_to_analyze of the structure
		for strategy in structure_data.strategies:
			if strategy.index not in strategies_to_analyze:
				continue
			else:
				# for all the attempts of the same strategy
				for strategy_attempt in strategy.strategy_data:
					print('strategy', strategy.index, 'attempt', strategy_attempt.attempt)
					if self.utils.does_attempt_solves_the_structure(strategy_attempt):
						strategy_attempts_solved_the_structure.append(StrategyAttemptSolvedStructure(structure_data.id, strategy.index, strategy_attempt))

					# check if the structure does not have any pigs (structure which is not needed to solve) by checking the number of pigs at the start of the first strategy
					if strategy_attempt.shots_data:
						if strategy_attempt.shots_data[0].static_data_start.pig_count == 0:
							return

		# if no strategy attempt solves the structure return
		if not strategy_attempts_solved_the_structure:
			return

		# from all the strategies which solves the structure find the one with least shots
		minimal_strategy_attempts_solved_the_structure = []
		for strategy_attempt in strategy_attempts_solved_the_structure:
			minimal_strategy_attempts_solved_the_structure.append(self.utils.get_mandatory_shots_for_solving_the_structure(strategy_attempt))

		print('minimal_strategy_attempts_solved_the_structure', minimal_strategy_attempts_solved_the_structure)

		# from the optimal strategies get the number of shots needed for each strategy attempt
		shot_count_of_strategy_attempt = []
		for strategy_attempt in minimal_strategy_attempts_solved_the_structure:
			shot_count_of_strategy_attempt.append(len(strategy_attempt.strategy_data.shots_data))
		print('shot_count_of_strategy_attempt', shot_count_of_strategy_attempt)

		# order the strategies in minimal_strategy_attempts_solved_the_structure according to the number of shots
		sort_indexes = sorted(range(len(shot_count_of_strategy_attempt)), key=lambda k: shot_count_of_strategy_attempt[k])
		ordered_minimal_strategy_attempts_solved_the_structure = [minimal_strategy_attempts_solved_the_structure[i] for i in sort_indexes]  # todo: verify the ranking

		# the selected strategy should contain a higher trajectory shot to be paired with a falling object
		# only consider the strategies that has number of shots equal to the strategy with minimum number of shots
		selected_strategy_attempt = None
		for strategy_attempt in ordered_minimal_strategy_attempts_solved_the_structure:
			if len(strategy_attempt.strategy_data.shots_data) > min(shot_count_of_strategy_attempt):  # only consider strategies with minimum number of shots
				continue
			for shot_data in strategy_attempt.strategy_data.shots_data:
				if shot_data.trajectory_selection == 2:  # higher trajectory
					selected_strategy_attempt = strategy_attempt
					break
		# if no shot with higher trajectory is found in any of the strategy attempts return
		if not selected_strategy_attempt:
			print('no higher trajectory shot found in the solving strategy attempt')
			return

		# least_shot_strategy =  minimal_strategy_attempts_solved_the_structure[min(range(len(shot_count_of_strategy_attempt)), key=shot_count_of_strategy_attempt.__getitem__)]

		return selected_strategy_attempt

	# find a gameobject in TargetObject version in the original structure (blocks and pigs and tnt)
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

	def match_inputs_and_outputs_of_sender_and_receiver(self, sender, receiver, sender_falling_object, receiver_solving_strategy: StrategyAttemptSolvedStructure):
		# get the falling object location of the sender structure
		sender_output_location = sender_falling_object.object_gone_out.centre

		# get the target objects location of the solving strategy of receiver structure (shots with a higher trajectory is selected : because a falling object resembles to a higher trajectory shot)
		# if the structures can not place without overlapping with the selected target try with the next target
		matching_shot_number = None
		checked_target_objects = []
		successfully_matched_sender_and_receiver = False
		receiver_tmp = None
		sender_tmp = None
		receiver_x_shift = 0
		receiver_y_shift = 0
		ground_overlap_adjust_y_shift = 0
		for shot_data in receiver_solving_strategy.strategy_data.shots_data:
			if shot_data.trajectory_selection == 2:  # consider only high trajectory targets
				receiver_target_object = shot_data.target_object
				matching_shot_number = shot_data.shot_number
				print('receiver_target_object', receiver_target_object)

				# find the receiver target object in the structure
				receiver_target_object = self.find_game_object_in_the_structure(receiver, receiver_target_object)
				# if it is an already selected target, try with the next target
				if receiver_target_object.identifier in checked_target_objects:
					print('already selected target, going to the next target')
					continue

				checked_target_objects.append(receiver_target_object.identifier)

				# check if the receiver target object is directly reachable with the high trajectory (if not rolling/falling deception might not visible in the final level)
				# if not try with the next target
				if not self.trajectory_planner.find_reachability_of_object([receiver], receiver_target_object, 'high', 'direct', None, None):
					# plt.show()

					print('target object is not directly reachable with the higher trajectory, going to the next target')
					continue

				# plt.show()

				# shift the coordinates of the receiver to the output of the sender
				sender_tmp = copy.deepcopy(sender)
				receiver_tmp = copy.deepcopy(receiver)
				receiver_x_shift = sender_output_location[0] - receiver_target_object.x
				receiver_y_shift = sender_output_location[1] - receiver_target_object.y
				self.structure_operations.shift_coordinates_of_structure(receiver_tmp, 'x', receiver_x_shift)
				self.structure_operations.shift_coordinates_of_structure(receiver_tmp, 'y', receiver_y_shift)

				# check if the structures overlap each other or with the ground and try to fix it. If can not be fixed, select the next target from the receiver_solving_strategy and retry.
				# If not matching succeeded, break the loop
				fix_any_structure_overlap = self.fix_structures_overlap([sender_tmp, receiver_tmp])
				if fix_any_structure_overlap[0]:  # matching succeeded
					successfully_matched_sender_and_receiver = True
					ground_overlap_adjust_y_shift = fix_any_structure_overlap[1]
					break

		# check with the final layout the target object of the sender is reachable (not necessarily directly)
		# if not self.trajectory_planner.find_reachability_of_object([sender_tmp + receiver_tmp], receiver_target_object, 2):
		# 	print('target object is not directly reachable with the higher trajectory, going to the next target')
		# 	continue

		# if none of the targets matched successfully return
		if not successfully_matched_sender_and_receiver:
			return

		# determine the number of birds
		birds_needed, solving_strategy = self.determine_number_of_birds_for_falling_objects_deception(sender_falling_object, receiver_solving_strategy, matching_shot_number)
		# if it returns none (sender is not solved by the time it sends something out) stop
		if not birds_needed:
			return

		# shift the coordinates of the solving strategy accordingly
		solving_strategy = self.adjust_coordinates_of_solving_strategy(solving_strategy, receiver_x_shift, receiver_y_shift + ground_overlap_adjust_y_shift, 0, ground_overlap_adjust_y_shift,
																	   sender_falling_object.structure_id, receiver_solving_strategy.structure_id)

		# check if all the target objects are reachable in the solving strategy (not necessarily directly)
		if not self.check_the_solution_target_reachability(solving_strategy, [sender_tmp, receiver_tmp]):
			print('all the targets are not reachable')
			# shift the structures close to the slingshot
			x_shift, y_shift = self.shift_structures_close_to_slingshot([sender_tmp, receiver_tmp])
			# adjust the coordinates of the solving_strategy
			solving_strategy = self.adjust_coordinates_of_solving_strategy(solving_strategy, x_shift, y_shift, x_shift, y_shift, sender_falling_object.structure_id,
																		   receiver_solving_strategy.structure_id)

			# now again check whether all the targets are reachable
			if not self.check_the_solution_target_reachability(solving_strategy, [sender_tmp, receiver_tmp]):
				return

		return [receiver_tmp, sender_tmp], birds_needed, solving_strategy

	def adjust_coordinates_of_solving_strategy(self, solving_strategy, receiver_x_shift, receiver_y_shift, sender_x_shift, sender_y_shift, sender_id, receiver_id):
		# adjust the original locations of the targets in the solving_strategy by the coordinate shifts done when matching the sender and receiver

		solving_strategy = copy.deepcopy(solving_strategy)  # stop propagating the changes to the original data structures
		for solution_shot_data in solving_strategy:
			shot_data = solution_shot_data.shot_data
			if shot_data.target_object.object_type == 'any_pig':  # skip any pig selection
				continue
			elif solution_shot_data.structure_id == sender_id:  # sender's shot targets should shift by ground_overlap_adjust_y_shift
				shot_data.target_object.centre[1] += sender_y_shift
			elif solution_shot_data.structure_id == receiver_id:  # receiver's shot targets should shift by receiver_x_shift, receiver_y_shift and ground_overlap_adjust_y_shift
				shot_data.target_object.centre[0] += receiver_x_shift
				shot_data.target_object.centre[1] += receiver_y_shift

		return solving_strategy

	def check_the_solution_target_reachability(self, solving_strategy, selected_structures):
		print('selected_structures', selected_structures)
		selected_structures_combined = self.structure_operations.get_all_game_objects_filtered(selected_structures)
		for solution_shot_data in solving_strategy:
			shot_data = solution_shot_data.shot_data

			# if target object is 'any_pig' which is not included in the strategy skip it
			if shot_data.target_object.object_type == 'any_pig':
				continue

			# find the target object in the structure
			target_object = self.find_game_object_in_the_structure(selected_structures_combined, shot_data.target_object)
			# check the reachability of the object
			if not self.trajectory_planner.find_reachability_of_object(selected_structures, target_object, 'any', 'any', None, None):
				return False
		print('all targets are reachable')
		return True

	def shift_structures_close_to_slingshot(self, structures):
		# shifts the structures' x coordinates to the level_width_min and y coordinates to the level_height_min
		structures_combined = self.structure_operations.get_all_game_objects_filtered(structures)
		bounding_box = self.structure_operations.find_bounding_box_of_structure(itertools.chain(structures_combined[0], structures_combined[1], structures_combined[2]), 0)

		x_shift_value = bounding_box[0] - level_width_min
		y_shift_value = bounding_box[2] - level_height_min

		for structure in structures:
			self.structure_operations.shift_coordinates_of_structure(structure, 'x', x_shift_value)
			self.structure_operations.shift_coordinates_of_structure(structure, 'y', y_shift_value)

		return x_shift_value, y_shift_value

	def fix_structures_overlap(self, structures):
		# for each structure calculate the bounding box
		bounding_boxes = []
		for structure in structures:
			bounding_boxes.append(self.structure_operations.find_bounding_box_of_structure(itertools.chain(structure[0], structure[1], structure[2]), 0))

		print('bounding_boxes', bounding_boxes)

		# check whether the structures overlap themselves
		do_bounding_boxes_overlap = self.structure_operations.do_bounding_boxes_overlap(bounding_boxes)

		# if bounding boxes do not overlap, check whether the whole level(all the structures) overlap with the ground and get the value that all the structures should shift upwards
		if not do_bounding_boxes_overlap:
			y_coordinate_shift_value = 0
			for bounding_box in bounding_boxes:
				if bounding_box[2] - ground_level < y_coordinate_shift_value:
					y_coordinate_shift_value = bounding_box[2] - ground_level

			y_coordinate_shift_value = y_coordinate_shift_value * -1  # making the shift value positive

			if y_coordinate_shift_value > 0:
				print('structures overlap with the ground, recommended shift up:', y_coordinate_shift_value)
				# check whether the structures do not go out of the level space after shifting
				for bounding_box in bounding_boxes:
					if bounding_box[3] + y_coordinate_shift_value > level_height_max:
						print('structures can not be shifted up - going out of the level space')
						return False, 0

				# if none of the structures goes out of the level space shift them
				for structure in structures:
					self.structure_operations.shift_coordinates_of_structure(structure, 'y', y_coordinate_shift_value)

				print('all structures lifted up')
				return True, y_coordinate_shift_value

			print('structures do not overlap each other or with ground')
			# structures do not overlap each other or with ground
			return True, 0

		else:
			print('structures overlap with each other')
			return False, 0

	def determine_number_of_birds_for_falling_objects_deception(self, sender_falling_object: SelectedObjectGoneOut, receiver_solving_strategy: StrategyAttemptSolvedStructure,
																receiver_connecting_shot_number):
		birds_needed = []
		solving_strategy = []

		## birds needed for the sender ##
		# get the corresponding strategy attempt and shot
		strategy_attempt = self.get_strategy_attempt(sender_falling_object.structure_id, sender_falling_object.strategy_index, sender_falling_object.attempt)
		print('shot_number', sender_falling_object.shot_number)

		# get the birds needed upto the specific shot
		for shot_data in strategy_attempt.shots_data:
			if shot_data.shot_number > sender_falling_object.shot_number:  # only upto the specific shot
				break
			elif shot_data.shot_number == sender_falling_object.shot_number:  # save bird for the specific shot
				birds_needed.append(shot_data.bird_type)
				solving_strategy.append(SolutionShotData(sender_falling_object.structure_id, shot_data))
			elif shot_data.static_data_end.shot_has_impact:  # for the shots before the specific shot save bird if the shot has an impact on the structure
				birds_needed.append(shot_data.bird_type)
				solving_strategy.append(SolutionShotData(sender_falling_object.structure_id, shot_data))

		# check if the structure is not solved at the shot which throws away the sender_falling_object
		sender_falling_object_shot_data = next((shot_data for shot_data in strategy_attempt.shots_data if shot_data.shot_number == sender_falling_object.shot_number), None)
		if sender_falling_object_shot_data.static_data_end.pig_count != 0:  # structure not solved
			# birds_needed += ['bird_red'] * sender_falling_object_shot_data.static_data_end.pig_count  # add red birds equal to the number of pigs remaining
			# add similar number of shots to the solution
			# solving_strategy += [SolutionShotData(sender_falling_object.structure_id, ShotData(-1, None, None, None, 'bird_red', None, None, TargetObject('any_pig', '', [])))] * sender_falling_object_shot_data.static_data_end.pig_count

			# modification: return non if the sender is not solved without adding extra birds
			return None, None

		# print('birds_needed', birds_needed)
		# print('solving_strategy', solving_strategy)

		## birds needed for the receiver ##
		# receiver_solving_strategy is already the best strategy, therefore get all the birds for the shots except for the receiver_connecting_shot_number
		for shot_data in receiver_solving_strategy.strategy_data.shots_data:
			if shot_data.shot_number == receiver_connecting_shot_number:
				continue
			birds_needed.append(shot_data.bird_type)
			solving_strategy.append(SolutionShotData(receiver_solving_strategy.structure_id, shot_data))

		print('birds_needed', birds_needed)
		print('solving_strategy', solving_strategy)

		return birds_needed, solving_strategy

	def get_strategy_attempt(self, structure_id, strategy_index, attempt):
		print('structure_id, strategy_index, attempt', structure_id, strategy_index, attempt)
		analysis_data = self.get_analysis_data_of_structure(structure_id)
		strategy = next((strategy for strategy in analysis_data.strategies if strategy.index == strategy_index), None)
		# print('strategy_data', strategy)
		attempt_data = next((attempt_data for attempt_data in strategy.strategy_data if attempt_data.attempt == attempt), None)
		# print('attempt_data', attempt_data)
		return attempt_data

	# returns analysis data with structure id
	def get_analysis_data_of_structure(self, structure_id):
		# for structure_analysis_data in self.analysis_data:
		# 	#print('structure_analysis_data.id == structure_id', type(structure_analysis_data.id), type(structure_id))
		# 	if structure_analysis_data.id == structure_id:
		# 		return structure_analysis_data
		# 	#print('not match')
		return next((structure_analysis_data for structure_analysis_data in self.analysis_data if structure_analysis_data.id == structure_id), None)

	# returns structure with structure id
	def get_structure(self, structure_id):
		# for structure in self.structures:
		# 	if structure[0] == structure_id:
		# 		return structure[1]
		return next((structure[1] for structure in self.structures if structure[0] == structure_id), None)

	# create a game level with rolling_falling_objects_deception for given 2 structures
	def generate_rolling_falling_objects_deception(self):

		for structure_1_index in range(0, len(self.analysis_data)):
			count = 0
			for structure_2_index in range(0, len(self.analysis_data)):

				# ids of the selected structures
				structure_1_id = int(self.structures[structure_1_index][0])
				structure_2_id = int(self.structures[structure_2_index][0])

				# check the compatibility of the structures considering the quarter of the level space which they located at
				# sender should be in the quarter 1 and 3 while receiver should be in quarter 2 and 4
				if structure_1_id % 10 != 1 and structure_1_id % 10 != 3:
					continue
				if structure_2_id % 10 != 2 and structure_2_id % 10 != 4:
					continue

				print('rolling_falling_objects deception of structures', structure_1_id, 'and', structure_2_id)

				sender = self.get_structure(structure_1_id)
				receiver = self.get_structure(structure_2_id)
				sender_analysis_data = self.get_analysis_data_of_structure(structure_1_id)
				receiver_analysis_data = self.get_analysis_data_of_structure(structure_2_id)

				print('sender', sender)
				print('receiver', receiver)
				print('sender_analysis_data', sender_analysis_data)
				print('receiver_analysis_data', receiver_analysis_data)
				# if any of the above data are null then there is an issue with the input data
				if sender is None or receiver is None or sender_analysis_data is None or receiver_analysis_data is None:
					print('Issue with gathering required data, check the inputs')
					continue
				# structure_1 is the sender and structure_2 is the receiver
				falling_object = self.find_objects_going_out(sender_analysis_data)
				solving_strategy = self.find_best_structure_solving_strategy(receiver_analysis_data, [1, 2, 3, 4, 5, 6])  # only strategies with high trajectories

				if not falling_object:
					print('No falling objects in structure', structure_1_id)
					continue
				if not solving_strategy:
					print('Structure', structure_2_id, 'can not be solved')
					continue

				# check whether the receiver is in the right quarter to accept the falling_object
				if level_width_min < falling_object.object_gone_out.centre[0] < level_width_min + (level_width_max - level_width_min) / 2:
					if structure_2_id % 10 != 2:
						print('receiver not in the correct quarter to accept the falling_object')
						continue
				elif level_width_min + (level_width_max - level_width_min) / 2 < falling_object.object_gone_out.centre[0] < level_width_max:
					if structure_2_id % 10 != 4:
						print('receiver not in the correct quarter to accept the falling_object')
						continue

				print('sender', falling_object, 'solving_strategy', solving_strategy)

				# match the sender and receiver considering the inputs and outputs
				level_data = self.match_inputs_and_outputs_of_sender_and_receiver(sender, receiver, falling_object, solving_strategy)

				# write the level file and the solution
				if level_data:
					# io_handler.write_the_level_file_and_solution(output_data, "{0:05d}".format(level_index_start))
					self.io_handler.write_the_level_file_and_solution(level_data, str(structure_1_id) + '_' + str(structure_2_id))

					# get only one level from same structure todo:remove this
					# count += 1
					# if count == 3: # get only 3 levels from the same structure
					#	break

		print('level generation reached end')

# return level_data
