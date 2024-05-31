"""modue to represent architectural grid"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import math
from operator import itemgetter


class grid:
	# class variables
	all_intersection_points = list()

	@classmethod
	def find_grid_intersection_points(cls, doc):
		# type: (Autodesk.Revit.DB.Document) -> list

		view = doc.ActiveView
		view_temp_prop = doc.GetElement(view.GetTemporaryViewPropertiesId())
		if view_temp_prop:
			is_temp_view = True
		else:
			is_temp_view = False

		all_grids = FilteredElementCollector(doc).\
			OfCategory(BuiltInCategory.OST_Grids).\
			WhereElementIsNotElementType().\
			ToElements()
		
		# filter elements, that not visible on temporary view
		filtered_grids = []
		for rvt_grd in all_grids:
			grid_is_hidden = rvt_grd.IsHidden(view)
			if is_temp_view:
				grid_temporary_hidden = not(view.IsElementVisibleInTemporaryViewMode(
					TemporaryViewMode.TemporaryHideIsolate, rvt_grd.Id))
			else:
				grid_temporary_hidden = False
			if grid_temporary_hidden or grid_is_hidden:
				continue
			filtered_grids.append(rvt_grd)

		all_intersection_points = dict()
		obj_grids = [grid(i) for i in filtered_grids]
		for grd in obj_grids:
			grid_intersections = grd.get_intersection_points(obj_grids)
			all_intersection_points.update(grid_intersections)

		cls.all_intersection_points = all_intersection_points
		return cls.all_intersection_points

	def __init__(self, _rvt_grid):
		# type: (Autodesk.Revit.DB.Grid) -> None
		self.rvt_grid = _rvt_grid  # type: Autodesk.Revit.DB.Grid
		self.angle = grid.get_angle(_rvt_grid)
		self.intersections = dict()

	@staticmethod
	def get_angle(_rvt_grid):
		# type: (Autodesk.Revit.DB.Grid) -> float
		"""
		Get angle rotation fo the grid
		"""
		vector = _rvt_grid.Curve.Direction
		direction = round(math.degrees(math.acos(_rvt_grid.Curve.Direction.X)))
		# rotating vector in upper direction
		if direction == 180 or direction == 0:
			direction = 0
		elif vector.Y < 0:
			direction = 180 - direction
		else:
			pass
		return direction

	def get_intersection_points(self, _grids):
		# type: (grid, list[grid]) -> None
		grids = [i for i in _grids
			if i.angle != self.angle]

		curve_current = self.rvt_grid.Curve

		for grid_next in grids:
			curve_next = grid_next.rvt_grid.Curve
			# define naming priority
			# name with smalest angle is first as example ("A" = 0, "1" = 90) -> A1
			if self.angle < grid_next.angle:
				point_name = self.rvt_grid.Name + grid_next.rvt_grid.Name
			else:
				point_name = grid_next.rvt_grid.Name + self.rvt_grid.Name

			# find intersection point
			results = Autodesk.Revit.DB.IntersectionResultArray()
			comparation_result = curve_current.Intersect(curve_next, results)
			if comparation_result[0] == SetComparisonResult.Overlap:
				point = comparation_result[1][0].XYZPoint
				# add point to dictionary
				self.intersections.update({point_name: point})

		return self.intersections

	@classmethod
	def get_nearest_grid_by_instance(cls, rvt_inst: FamilyInstance) -> str:
		"""
			Get nearest grid string for family
		"""
		rvt_inst_point = rvt_inst.Location.Point
		# # get all distances list
		distance_list = list()
		all_intersect_points = cls.all_intersection_points.items()
		for key, value in all_intersect_points:
			distance = rvt_inst_point.DistanceTo(value)
			distance_list.append([key, distance])
		distance_list.sort(key=itemgetter(1))
		shortest_grid_name = distance_list[0][0]
		return shortest_grid_name
