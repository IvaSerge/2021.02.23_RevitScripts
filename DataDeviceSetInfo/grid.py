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
		# type: (Autodesk.Revit.DB.Grid) -> any
		"""
		Extended electrical panel class
		"""
		self.rvt_grid = _rvt_grid  # type: Autodesk.Revit.DB.Grid
		self.angle = float

	def get_angle(self):
		round(math.degrees(math.acos(self.rvt_grid.Curve.Direction.X)))
		vector = self.rvt_grid.Curve.Direction
		direction = round(math.degrees(math.acos(self.rvt_grid.Curve.Direction.X)))
		# rotating vector in upper direction
		if direction == 180 or direction == 0:
			direction = 0
		elif vector.Y < 0:
			direction = 180 - direction
		else:
			pass
		self.angle = direction
		return direction
