# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory
from Autodesk.Revit.DB.Category import GetCategory  # type: ignore

# ================ Python imports
import operator
from operator import itemgetter, attrgetter

# list of preset options
preset_2R_main = list(
	# Description | n_of_poles | TripRating | Remarks
	["Empty", "3", "0A", ""],
	["Section Q2", "3", "63A", "0Q2"],
	["Section Q3", "3", "63A", "0Q3"],
	["Section Q4", "3", "63A", "0Q4"],
	["Section Q5", "3", "63A", "0Q5"],
	["Section Q6", "3", "63A", "0Q6"],
	["Section Q7", "3", "63A", "0Q7"],
	["Section Q8", "3", "160A", "0Q8"],
)
