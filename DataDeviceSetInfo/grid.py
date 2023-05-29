"""modue to represent architectural grid"""
import clr

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import math

# ================ local imports
import toolsrvt


class grid:
	def __init__(self, _rvt_grid):
		# type: (Autodesk.Revit.DB.Grid) -> None
		"""
		Extended electrical panel class
		"""
		self.rvt_grid = _rvt_grid  # type: Autodesk.Revit.DB.Grid
		self.angle = grid.get_angle(_rvt_grid)
		self.intersections = dict()

	@staticmethod
	def get_angle(_rvt_grid):
		# type: (Autodesk.Revit.DB.Grid) -> float
		"""
		get angle rotation fo the grid
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
