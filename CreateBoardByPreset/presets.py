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
		# Description | n_of_poles
		[5, 4],
		[
			["Empty", "3", "0 A"],
			["63 A / Section Q2", "3"],
			["63 A / Section Q3", "3"],
			["63 A / Section Q4", "3"],
			["63 A / Section Q5", "3"],
			["63 A / Section Q6", "3"],
			["63 A / Section Q7", "3"],
			["160 A / Section Q8", "3"]
		]
	]

	preset_2R_sub = [
		# Description | n_of_poles
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

	preset_2E_main = [
		# Description | n_of_poles
		[5, 4],
		[
			["63 A / Section F1", "3"],
			["63 A / Section F2", "3"],
			["63 A / Section F3", "3"],
			["63 A / Section F4", "3"],
			["63 A / Section F5", "3"],
			["63 A / Section F6", "3"],
			["Empty", "1"],
			["Empty", "1"],
		]
	]

	preset_2E_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["32 A / F123", "3"],
			["32 A / F456", "3"],
			["32 A / F789", "3"],
			["32 A / F101112", "3"],
			["32 A / F131415", "3"],
			["63 A / F161718", "3"],
			["63 A / F192021", "3"],

			["16 A / 0,03 A / F22 Section F1", "1"],
			["16 A / 0,03 A / F23 Section F1", "1"],
			["16 A / 0,03 A / F24 Section F1", "1"],
			["16 A / 0,03 A / F25 Section F1", "1"],
			["16 A / 0,03 A / F26 Section F1", "1"],
			["16 A / 0,03 A / F27 Section F1", "1"],
			["16 A / 0,03 A / F28 Section F1", "1"],
			["16 A / 0,03 A / F29 Section F1", "1"],
			["16 A / 0,03 A / F30 Section F1", "1"],

			["16 A / 0,03 A / F31 Section F2", "1"],
			["16 A / 0,03 A / F32 Section F2", "1"],
			["16 A / 0,03 A / F33 Section F2", "1"],
			["16 A / 0,03 A / F34 Section F2", "1"],
			["16 A / 0,03 A / F35 Section F2", "1"],
			["16 A / 0,03 A / F36 Section F2", "1"],
			["16 A / 0,03 A / F37 Section F2", "1"],
			["16 A / 0,03 A / F38 Section F2", "1"],
			["16 A / 0,03 A / F39 Section F2", "1"],

			["16 A / 0,03 A / F40 Section F3", "1"],
			["16 A / 0,03 A / F41 Section F3", "1"],
			["16 A / 0,03 A / F42 Section F3", "1"],
			["16 A / 0,03 A / F43 Section F3", "1"],
			["16 A / 0,03 A / F44 Section F3", "1"],
			["16 A / 0,03 A / F45 Section F3", "1"],
			["16 A / 0,03 A / F46 Section F3", "1"],
			["16 A / 0,03 A / F47 Section F3", "1"],
			["16 A / 0,03 A / F48 Section F3", "1"],

			["16 A / F495051 Section F4", "3"],
			["16 A / F525354 Section F4", "3"],
			["16 A / F555657 Section F4", "3"],
			["16 A / F585960 Section F4", "3"],
			["16 A / F616263 Section F4", "3"],

			["25 A / 0,03 A / F646566 Section F5", "3"],
			["25 A / 0,03 A / F676869 Section F5", "3"],
			["25 A / 0,03 A / F707172 Section F5", "3"],

			["10 A / F73 Section F6", "1"],
			["10 A / F74 Section F6", "1"],
			["10 A / F75 Section F6", "1"],
			["10 A / F76 Section F6", "1"],
		]
	]
