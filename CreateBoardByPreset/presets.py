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


class presets():

	# list of preset options
	preset_2R_main = [
		# Description | n_of_poles | TripRating | Remarks
		[5, 4, 2],
		[
			["Empty", "3", "0 A", ""],
			["63 A / Section Q2", "3", "63 A"],
			["63 A / Section Q3", "3", "63 A"],
			["63 A / Section Q4", "3", "63 A"],
			["63 A / Section Q5", "3", "63 A"],
			["63 A / Section Q6", "3", "63 A"],
			["63 A / Section Q7", "3", "63 A"],
			["160 A / Section Q8", "3", "160 A"]
		]
	]

	preset_2R_sub = [
		# Description | n_of_poles | TripRating | Remarks
		[5, 4],
		[
			["16 A / F123 Section Q2", "3"],
			["16 A / F456 Section Q2", "3"],
			["16 A / F789 Section Q2", "3"],
			["16 A / F101112 Section Q2", "3"],
			["16 A / F131415 Section Q2", "3"],
			["16 A / F161718 Section Q2", "3"],
			["16 A / F192021 Section Q2", "3"],
			["16 A / F222324 Section Q2", "3"],
			["16 A / F252627 Section Q2", "3"],

			["16 A / F282930 Section Q3", "3"],
			["16 A / F313233 Section Q3", "3"],
			["16 A / F343536 Section Q3", "3"],
			["16 A / F373839 Section Q3", "3"],
			["16 A / F404142 Section Q3", "3"],
			["16 A / F434445 Section Q3", "3"],
			["16 A / F464748 Section Q3", "3"],
			["16 A / F495051 Section Q3", "3"],
			["16 A / F525354 Section Q3", "3"],

			["16 A / F55 Section Q4", "1"],
			["16 A / F56 Section Q4", "1"],
			["16 A / F57 Section Q4", "1"],
			["16 A / F58 Section Q4", "1"],
			["16 A / F59 Section Q4", "1"],
			["16 A / F60 Section Q4", "1"],

			["16 A / 0,03 A / F61 Section Q5", "1"],
			["16 A / 0,03 A / F62 Section Q5", "1"],
			["16 A / 0,03 A / F63 Section Q5", "1"],
			["16 A / 0,03 A / F64 Section Q5", "1"],
			["16 A / 0,03 A / F65 Section Q5", "1"],
			["16 A / 0,03 A / F66 Section Q5", "1"],

			["40 A / 0,03 A / F676869 Section Q6", "3"],
			["40 A / 0,03 A / F707172 Section Q6", "3"],
			["40 A / 0,03 A / F7837475 Section Q6", "3"],
			["40 A / 0,03 A / F767778 Section Q6", "3"],

			["25 A / 0,03 A / F798081 Section Q7", "3"],
			["25 A / 0,03 A / F828384 Section Q7", "3"],
			["25 A / 0,03 A / F858687 Section Q7", "3"],
			["25 A / 0,03 A / F888990 Section Q7", "3"],
		]
	]
