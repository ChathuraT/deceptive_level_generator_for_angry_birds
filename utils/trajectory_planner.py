from math import atan2, acos, sqrt, sin, cos
from utils.block_operations import BlockOperations
from utils.structure_operations import StructureOperations
from utils.data_classes import *
# changes to the original trajectory planner:
# 25/09/2020 adjusted _a and xn in the set_trajectory function to cross the 2 trajectories correctly at the pig when plotting the trajectory path

# TODO change geometric libs to shapely
# from computer_vision.cv_utils import Rectangle
from utils.point2D import Point2D


class SimpleTrajectoryPlanner:
	"""a simple trajectory planner, reimplementation of the java code"""

	def __init__(self):

		# for calculating reference point
		self.X_OFFSET = 0.45
		self.Y_OFFSET = 0.35
		self.scale_factor = 2.7
		# STRETCH factor for shooting a bird relative to the sling size
		self.STRETCH = 0.4
		self.X_MAX = 640

		# unit velocity
		self._velocity = 9.5 / self.scale_factor

		# conversion between the trajectory time and actual time in milliseconds
		self._time_unit = 815

		# boolean flag on set trajectory
		self._traj_set = False

		# parameters of the set trajectory
		self._release = None
		self._theta = None
		self._ux = None
		self._uy = None
		self._a = None
		self._b = None

		# the trajectory points
		self._trajectory = []

		# reference point and current scale
		self._ref = None
		self._scale = None

		self.block_operations = BlockOperations()
		self.structure_operations = StructureOperations()
		self.slingshot = Slingshot(79, 152, 32, 10)

	def plotTrajectory(self, slingshot, release_point, target_object):
		"""Plot a trajectory
		 *
		 * @param   canvas - the canvas to draw onto
		 *          slingshot - bounding rectangle of the slingshot
		 *          release_point - point where the mouse click was released from
		 * @return  the canvas with trajectory drawn
		 *
		 """
		# width = canvas.size[0]
		# height = canvas.size[1]
		self._trajectory = []  # clean the previous trajectories
		self._traj_set = False

		trajectory = self.predictTrajectory(slingshot, release_point)
		trajectory_points_usc = []

		# draw = ImageDraw.Draw(canvas)
		# dot_radius = 3
		# draw estimated trajectory
		for p in trajectory:
			# get only the trajectory points until the target_object and above the ground
			if p.X <= target_object.X and 480 - p.Y > 300:
				# if 480 - p.Y > 300:
				trajectory_points_usc.append([p.X, p.Y])
		# plt.scatter(p.X, 480 - p.Y, color='blue')

		# print('trajectory_points', trajectory_points_usc)
		return trajectory_points_usc

	def predictTrajectory(self, slingshot, launch_point):
		"""predicts a trajectory"""
		self.set_trajectory(slingshot, launch_point)
		return self._trajectory

	def get_reference_point(self, sling):
		"""find the reference point given the sling"""

		p = Point2D(int(sling.X + self.X_OFFSET * sling.width), int(sling.Y + self.Y_OFFSET * sling.width))
		return p

	def set_trajectory(self, sling, release_point):
		""" Choose a trajectory by specifying the sling location and release point
		 * Derive all related parameters (angle, velocity, equation of the parabola, etc)
		 *
		 * @param   sling - bounding rectangle of the slingshot
		 *          release_point - point where the mouse click was released from
		 *
		"""

		# don't update parameters if the ref point and release point are the same
		if self._traj_set and self._ref != None and self._ref == self.get_reference_point(sling) and \
				self._release != None and self._release == release_point:
			return

		# set the scene parameters
		self._scale = sling.height + sling.width
		self._ref = self.get_reference_point(sling)

		# set parameters for the trajectory
		self._release = Point2D(release_point.X, release_point.Y)

		# find the launch angle
		self._theta = atan2(self._release.Y - self._ref.Y, self._ref.X - self._release.X)

		# work out initial velocities and coefficients of the parabola
		self._ux = self._velocity * cos(self._theta)
		self._uy = self._velocity * sin(self._theta)
		# self._a = -0.9 / (self._ux * self._ux)
		self._a = -0.9 / (self._ux * self._ux)
		self._b = self._uy / self._ux

		# work out points of the trajectory
		for x in range(0, self.X_MAX):
			# xn = x / (self._scale + 2)
			xn = x / (self._scale + 2)
			y = self._ref.Y - (int)((self._a * xn * xn + self._b * xn) * self._scale)
			self._trajectory.append(Point2D(x + self._ref.X, y))

		# turn on the setTraj flag
		self._traj_set = True

	def estimate_launch_point(self, slingshot, targetPoint):
		# calculate relative position of the target (normalised)
		scale = self.get_scene_scale(slingshot)
		# print ('scale ', scale)
		# System.out.println("scale " + scale)
		ref = self.get_reference_point(slingshot)
		x = (targetPoint.X - ref.X)
		y = -(targetPoint.Y - ref.Y)

		# gravity
		g = 0.48 * 9.81 / self.scale_factor * scale

		# launch speed
		v = self._velocity * scale
		#        print ('launch speed ', v)
		pts = []

		solution_existence_factor = v ** 4 - g ** 2 * x ** 2 - 2 * y * g * v ** 2

		# the target point cannot be reached
		if solution_existence_factor < 0:
			return None

		# solve cos theta from projectile equation

		cos_theta_1 = sqrt((x ** 2 * v ** 2 - x ** 2 * y * g + x ** 2 * sqrt(v ** 4 - g ** 2 * x ** 2 - 2 * y * g * v ** 2)) / (2 * v ** 2 * (x ** 2 + y ** 2)))
		cos_theta_2 = sqrt((x ** 2 * v ** 2 - x ** 2 * y * g - x ** 2 * sqrt(v ** 4 - g ** 2 * x ** 2 - 2 * y * g * v ** 2)) / (2 * v ** 2 * (x ** 2 + y ** 2)))
		#        print ('cos_theta_1 ', cos_theta_1, ' cos_theta_2 ', cos_theta_2)

		distance_between = sqrt(x ** 2 + y ** 2)  # ad-hoc patch

		theta_1 = acos(cos_theta_1) + distance_between * 0.0001  # compensate the rounding error
		theta_2 = acos(cos_theta_2) + distance_between * 0.00005  # compensate the rounding error
		pts.append(self.find_release_point(slingshot, theta_1))
		pts.append(self.find_release_point(slingshot, theta_2))

		return pts

	def get_scene_scale(self, sling):
		"""return scene scale determined by the sling size"""
		return sling.height + sling.width

	def find_release_point(self, sling, theta):
		"""find the release point given the sling location and launch angle, using maximum velocity
		 *
		 * @param   sling - bounding rectangle of the slingshot
		 *          theta - launch angle in radians (anticlockwise from positive direction of the x-axis)
		 * @return  the release point on screen
		 *
		"""

		mag = sling.height * 5
		# print('mag ', mag)
		ref = self.get_reference_point(sling)
		# print('ref ', ref)
		# print('cos theta ', cos(theta))
		#        print('sin theta ',sin(theta))
		release = Point2D(int(ref.X - mag * cos(theta)), int(ref.Y + mag * sin(theta)))

		return release

	def get_trajectory_points_to_object(self, slingshot, object_location):
		# print('object_location')

		# pprint(vars(object_location))
		possible_launch_points = self.estimate_launch_point(slingshot, object_location)
		trajectory_points = []
		# possible_launch_points = [Point2D(-100, 450)]

		if possible_launch_points:
			for launch_point in possible_launch_points:
				# plt.scatter(launch_point.X, 480 - launch_point.Y, color='red')
				# print('possible_launch_points', launch_point)
				trajectory_points.append(self.plotTrajectory(slingshot, launch_point, object_location))
		else:
			print('no release point found!')

		return trajectory_points

	# returns the trajectory paths (as a list of points) to reach a given objects
	def get_trajectory_paths(self, game_object):
		# convert the object coordinates to usc
		object_location_usc = self.block_operations.convert_wc_to_usc([game_object.x, game_object.y])
		object_location = Point2D(object_location_usc[0], object_location_usc[1])
		# plt.scatter(object_location.X, 480 - object_location.Y, color='red')

		# get the trajectory points of possible trajectories
		# slingshot_position x, y, height, width
		possible_trajectories = self.get_trajectory_points_to_object(self.slingshot, object_location)

		return possible_trajectories

	# find the reachability of an object (of the center point) considering the trajectory given (1: low, 2: high,  3: any) and
	# reachability_criteria (1: directly reachable, 2: partially reachable (not blocked by other structure except partial_reachability_structure_id), 3: anyhow reachable, 4: cleared path
	# (when the front structure is cleared)). cleared_path_data is a array with  [front_structure_id, front_structure_max_y_after_clearing]
	def find_reachability_of_object(self, structures_data, object_considered, trajectory_considered, reachability_criteria, partial_reachability_structure_id, cleared_path_data):
		all_blocks, all_pigs, all_tnts, all_birds = self.structure_operations.get_all_game_objects_filtered(structures_data)

		# plot the objects in the screen coordinate
		for block in all_blocks:
			block_coordinates = self.block_operations.convert_wc_to_usc([block.x, block.y])
		# plt.scatter(block_coordinates[0], 480 - block_coordinates[1], color='brown')

		for pig in all_pigs:
			pig_coordinates = self.block_operations.convert_wc_to_usc([pig.x, pig.y])
		# plt.scatter(pig_coordinates[0], 480 - pig_coordinates[1], color='green')

		# get possible trajectory paths to the game_object
		trajectory_paths = self.get_trajectory_paths(object_considered)

		# if no trajectory path is found, the object is unreachable
		if not trajectory_paths:
			print('target object is unreachable')
			return False

		# find the objects in trajectory path to the game_object
		# get the blocks laying on the trajectory path
		objects_on_ways = []
		for trajectory_points in trajectory_paths:
			# find the objects on the each trajectory path
			objects_on_ways.append(self.find_objects_on_way(all_blocks, trajectory_points))

		# remove the object considered from the objects_on_way
		for objects_on_way in objects_on_ways:
			if object_considered in objects_on_way:
				objects_on_way.remove(object_considered)

		# objects_on_ways.reverse()
		print('object_considered', object_considered)
		print('objects_on_way to the target object', objects_on_ways)

		# check the direct reachability of the block considering the trajectory
		if reachability_criteria == 'direct':
			if trajectory_considered == 'low':  # low trajectory
				for game_object in objects_on_ways[0]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						return False  # if there is any block in the trajectory path object is not directly reachable
				return True
			elif trajectory_considered == 'high':  # high trajectory
				for game_object in objects_on_ways[1]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						return False  # if there is any block in the trajectory path object is not directly reachable
				return True
			elif trajectory_considered == 'any':  # any trajectory
				for objects_on_way in objects_on_ways:
					path_blocked = False
					for game_object in objects_on_way:
						if '<class \'data_classes.Block\'>' == str(type(game_object)):
							# if game_object.type == 'Platform':
							path_blocked = True
							print('path blocked')
							break
					if not path_blocked:
						return True

		# check the reachability (block is in bird's range) of the block considering any trajectory
		elif reachability_criteria == 'any':  # direct or indirect
			if trajectory_considered == 'any':  # any trajectory
				for objects_on_way in objects_on_ways:
					path_blocked = False
					for game_object in objects_on_way:
						if '<class \'data_classes.Block\'>' == str(type(game_object)):
							if game_object.type == 'Platform':
								path_blocked = True
								print('path blocked')
								break
					if not path_blocked:
						print('object is reachable')
						return True
			if trajectory_considered == 'low':  # any trajectory
				for game_object in objects_on_ways[0]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
				return True
			if trajectory_considered == 'high':  # high trajectory
				for game_object in objects_on_ways[1]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
				return True
		# check the direct reachability of the block considering the given trajectory excluding blocks of partial_reachability_structure_id
		elif reachability_criteria == 'partial':  # direct or indirect
			if trajectory_considered == 'low':  # low trajectory
				for game_object in objects_on_ways[0]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
						elif game_object.structure_id != partial_reachability_structure_id:  # exclude gameobject of partial_reachability_structure_id
							# print('low path blocked by objects of other structures')
							# print('game_object.structure_id', game_object.structure_id)
							# print('partial_reachability_structure_id', partial_reachability_structure_id)
							return False
				return True
			if trajectory_considered == 'high':  # high trajectory
				for game_object in objects_on_ways[1]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
						elif game_object.structure_id != partial_reachability_structure_id:  # exclude gameobject of partial_reachability_structure_id
							# print('high path blocked by objects of other structures')
							# print('game_object.structure_id', game_object.structure_id)
							# print('partial_reachability_structure_id', partial_reachability_structure_id)
							return False
				return True
		# check the direct reachability of the block considering the given trajectory after clearing the front structure (clearing paths deception)
		elif reachability_criteria == 'cleared_path':  # any block in the cleared front structure shouldn't block the trajectory
			if trajectory_considered == 'low':  # low trajectory
				for game_object in objects_on_ways[0]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
						elif game_object.structure_id == cleared_path_data[0]:  # only check the blocks of front structure
							# print(reachability_criteria, trajectory_considered, 'found candidate block in front structure', game_object)
							# print('max y of cleared structure', cleared_path_data[1])
							# check if the path blocking block is below the maximum y coordinate of the front structure after clearing it (clearing path does not make access to the target)
							if game_object.y + self.block_operations.get_horizontal_and_vertical_span(game_object)[1]/2 < cleared_path_data[1]:
								return False
				return True
			if trajectory_considered == 'high':  # high trajectory
				for game_object in objects_on_ways[1]:
					if '<class \'data_classes.Block\'>' == str(type(game_object)):
						if game_object.type == 'Platform':  # consider platform of any structure
							print('path blocked by platform')
							return False
						elif game_object.structure_id == cleared_path_data[0]:  # only check the blocks of front structure
							# print(reachability_criteria, trajectory_considered, 'found candidate block in front structure')
							# check if the path blocking block is below the maximum y coordinate of the front structure after clearing it (clearing path does not make access to the target)
							if game_object.y + self.block_operations.get_horizontal_and_vertical_span(game_object)[1]/2 < cleared_path_data[1]:
								return False
				return True

		return False

	# return objects which lie in the trajectory path
	def find_objects_on_way(self, objects_considered, trajectory_path):
		objects_on_way = []
		for i in range(len(trajectory_path) - 1):
			for game_object in objects_considered:
				if self.block_operations.line_intersects_object([trajectory_path[i], trajectory_path[i + 1]], game_object):
					# print('trajectory point', trajectory_path[i], trajectory_path[i + 1])
					# print('object on way: ', game_object)

					if game_object not in objects_on_way:  # save only the unsaved objects
						objects_on_way.append(game_object)

		# print('objects_on_way', objects_on_way)

		return objects_on_way
