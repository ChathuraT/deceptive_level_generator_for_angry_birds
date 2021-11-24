from dataclasses import dataclass


# data classes for game objects in the level files
@dataclass
class Block:
	identifier: int
	type: str
	material: str
	x: float
	y: float
	rotation: float
	scale_x: float = 1.0
	scale_y: float = 1.0
	structure_id: int = -1


@dataclass
class Pig:
	identifier: int
	type: str
	x: float
	y: float
	rotation: float
	structure_id: int = -1


@dataclass
class Tnt:
	identifier: int
	x: float
	y: float
	rotation: float
	type: str = 'TNT'
	structure_id: int = -1


# data classes for storing structure analysis data
@dataclass
class TargetObject:
	object_type: str
	material: str
	centre: [float]


@dataclass
class ObjectGoneOut:
	object_id: int
	object_type: str
	material: str
	centre: [float]
	velocity: [float]


@dataclass
class DynamicData:
	time: int
	objects_gone_out: [ObjectGoneOut]


@dataclass
class StaticDataStart:
	pig_count: int
	bounding_box: [float]


@dataclass
class StaticDataEnd:
	pig_count: int
	bounding_box: [float]
	shot_has_impact: bool


@dataclass
class ShotData:
	# data from the game
	shot_number: int
	static_data_start: StaticDataStart
	dynamic_data: [DynamicData]
	static_data_end: StaticDataEnd

	# data from the agent
	bird_type: str
	tap_time: float
	trajectory_selection: int  # low = 1, high = 2
	target_object: TargetObject


@dataclass
class StrategyData:
	attempt: int
	shots_data: [ShotData]


@dataclass
class Strategy:
	index: int
	strategy_data: [StrategyData]


@dataclass
class Structure:
	id: int
	strategies: [Strategy]


# data classes for deceptions
@dataclass
class SelectedObjectGoneOut:
	structure_id: int
	strategy_index: int
	attempt: int
	shot_number: int
	object_gone_out: ObjectGoneOut


@dataclass
class StrategyAttemptSolvedStructure:
	structure_id: int
	strategy_index: int
	strategy_data: StrategyData


# clearing paths deception
@dataclass
class StrategyAttemptDamagedStructure:
	structure_id: int
	strategy_index: int
	strategy_data: StrategyData


@dataclass
class SolutionShotData:
	structure_id: int
	shot_data: ShotData


@dataclass
class ShotDataSolutionFile:
	shot_number: int
	bird_type: str
	tap_interval: int
	trajectory_selection: int
	target_object: TargetObject


@dataclass
class Slingshot:
	X: float
	Y: float
	height: float
	width: float
