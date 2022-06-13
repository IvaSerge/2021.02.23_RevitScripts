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

	preset_3A_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["6 A / F123 Section 0F1", "3"],
			["6 A / F456 Section 0F1", "3"],
			["6 A / F789 Section 0F1", "3"],
			["6 A / F101112 Section 0F1", "3"],
			["6 A / F131415 Section 0F1", "3"],

			["6 A / F161718 Section 0F2", "3"],
			["6 A / F192021 Section 0F2", "3"],
			["6 A / F222324 Section 0F2", "3"],
			["6 A / F252627 Section 0F2", "3"],
			["6 A / F282930 Section 0F2", "3"],

			["6 A / F313233 Section 0F3", "3"],
			["6 A / F343536 Section 0F3", "3"],
			["6 A / F373839 Section 0F3", "3"],
			["6 A / F404142 Section 0F3", "3"],
			["6 A / F434445 Section 0F3", "3"],

			["6 A / F464748 Section 0F4", "3"],
			["6 A / F495051 Section 0F4", "3"],
			["6 A / F525354 Section 0F4", "3"],
			["6 A / F555657 Section 0F4", "3"],
			["6 A / F585969 Section 0F4", "3"],

			["6 A / F61 Section 0F5", "1"],
			["6 A / F62 Section 0F5", "1"],
			["6 A / F63 Section 0F5", "1"],
			["6 A / F64 Section 0F5", "1"],
			["6 A / F65 Section 0F5", "1"],
			["6 A / F66 Section 0F5", "1"],
			["6 A / F67 Section 0F5", "1"],
			["6 A / F68 Section 0F5", "1"],
			["6 A / F69 Section 0F5", "1"],
			["6 A / F70 Section 0F5", "1"],
			["6 A / F71 Section 0F5", "1"],
			["6 A / F72 Section 0F5", "1"],
		]
	]

	preset_3B_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["6 A / F1 Section 0F1", "1"],
			["6 A / F2 Section 0F1", "1"],
			["6 A / F3 Section 0F1", "1"],
			["6 A / F4 Section 0F1", "1"],
			["6 A / F5 Section 0F1", "1"],
			["6 A / F6 Section 0F1", "1"],
			["6 A / F7 Section 0F1", "1"],
			["6 A / F8 Section 0F1", "1"],

			["6 A / F9 Section 0F2", "1"],
			["6 A / F10 Section 0F2", "1"],
			["6 A / F11 Section 0F2", "1"],
			["6 A / F12 Section 0F2", "1"],
			["6 A / F13 Section 0F2", "1"],
			["6 A / F14 Section 0F2", "1"],
			["6 A / F15 Section 0F2", "1"],
			["6 A / F16 Section 0F2", "1"],

			["6 A / F17 Section 0F3", "1"],
			["6 A / F18 Section 0F3", "1"],
			["6 A / F19 Section 0F3", "1"],
			["6 A / F20 Section 0F3", "1"],
			["6 A / F21 Section 0F3", "1"],
			["6 A / F22 Section 0F3", "1"],
			["6 A / F23 Section 0F3", "1"],
			["6 A / F24	Section 0F3", "1"],

			["6 A / F25 Section 0F4", "1"],
			["6 A / F26 Section 0F4", "1"],
			["6 A / F27 Section 0F4", "1"],
			["6 A / F28 Section 0F4", "1"],
			["6 A / F29 Section 0F4", "1"],
			["6 A / F30 Section 0F4", "1"],
			["6 A / F31 Section 0F4", "1"],
			["6 A / F32	Section 0F4", "1"],

			["6 A / F33 Section 0F5", "1"],
			["6 A / F34 Section 0F5", "1"],
			["6 A / F35 Section 0F5", "1"],
			["6 A / F36 Section 0F5", "1"],
			["6 A / F37 Section 0F5", "1"],
			["6 A / F38 Section 0F5", "1"],
			["6 A / F39 Section 0F5", "1"],
			["6 A / F40	Section 0F5", "1"],

			["6 A / F33 Section 0F6", "1"],
			["6 A / F34 Section 0F6", "1"],
			["6 A / F35 Section 0F6", "1"],
			["6 A / F36 Section 0F6", "1"],
			["6 A / F37 Section 0F6", "1"],
			["6 A / F38 Section 0F6", "1"],
			["6 A / F39 Section 0F6", "1"],
			["6 A / F40	Section 0F6", "1"],

			["6 A / F49 Section 0F7", "1"],
			["6 A / F50 Section 0F7", "1"],
			["6 A / F51 Section 0F7", "1"],
			["6 A / F52 Section 0F7", "1"],
			["6 A / F53 Section 0F7", "1"],
			["6 A / F54 Section 0F7", "1"],
			["6 A / F55 Section 0F7", "1"],
			["6 A / F56	Section 0F7", "1"],

			["6 A / F57 Section 0F8", "1"],
			["6 A / F58 Section 0F8", "1"],
			["6 A / F59 Section 0F8", "1"],
			["6 A / F60 Section 0F8", "1"],
			["6 A / F61 Section 0F8", "1"],
			["6 A / F62 Section 0F8", "1"],
			["6 A / F63 Section 0F8", "1"],
			["6 A / F64	Section 0F8", "1"],
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

			["16 A / 0,03 A / F646566 Section F5", "3"],
			["16 A / 0,03 A / F676869 Section F5", "3"],
			["16 A / 0,03 A / F707172 Section F5", "3"],

			["10 A / F73 Section F6", "1"],
			["10 A / F74 Section F6", "1"],
			["10 A / F75 Section F6", "1"],
			["10 A / F76 Section F6", "1"],
		]
	]

	preset_2H = [
		# Description | n_of_poles
		[5, 4],
		[
			["400 A / Main switch", "3"],
			["N/A", "3"],
			["100 A / Q3", "3"],
			["100 A / Q4", "3"],
			["100 A / Q5", "3"],
			["100 A / Q6", "3"],
			["100 A / Q7", "3"],
			["100 A / Q8", "3"],
			["100 A / Q9", "3"],
			["100 A / Q10", "3"],
			["100 A / Q11", "3"],
			["100 A / Q12", "3"],
			["100 A / Q13", "3"],
			["100 A / Q14", "3"],
		]
	]

	preset_2I = [
		# Description | n_of_poles
		[5, 4],
		[
			["630 A / Main switch", "3"],
			["Internal circuits", "3"],
			["250 A / Q3", "3"],
			["250 A / Q4", "3"],
			["160 A / Q5", "3"],
			["160 A / Q6", "3"],
			["100 A / Q7", "3"],
			["100 A / Q8", "3"],
			["100 A / Q9", "3"],
		]
	]

	# list of preset options
	preset_2J_main = [
		# Description | n_of_poles
		[5, 4],
		[
			["Feeder switch 250 A", "3"],
			["160 A / 0Q2", "3"],
			["160 A / 0Q3", "3"],
			["160 A / 0Q4", "3"],
			["160 A / 0Q5", "3"],
			["160 A / 0Q6", "3"],
			["63 A / Section Q7", "3"],
			["63 A / Section Q8", "3"],
		]
	]

	# list of preset options
	preset_2J_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["16 A / 0,03 A / Q123 Section Q7", "3"],
			["16 A / 0,03 A / Q456 Section Q7", "3"],
			["16 A / 0,03 A / Q789 Section Q7", "3"],
			["16 A / 0,03 A / Q101112 Section Q7", "3"],
			["16 A / 0,03 A / Q131415 Section Q7", "3"],
			["16 A / 0,03 A / Q161718 Section Q7", "3"],
			["16 A / 0,03 A / Q192021 Section Q7", "3"],
			["16 A / 0,03 A / Q222324 Section Q7", "3"],

			["16 A / 0,03 A / Q252627 Section Q8", "3"],
			["16 A / 0,03 A / Q282930 Section Q8", "3"],
			["16 A / 0,03 A / Q313233 Section Q8", "3"],
			["16 A / 0,03 A / Q343536 Section Q8", "3"],
			["16 A / 0,03 A / Q373839 Section Q8", "3"],
			["16 A / 0,03 A / Q404142 Section Q8", "3"],
			["16 A / 0,03 A / Q434445 Section Q8", "3"],
			["16 A / 0,03 A / Q464748 Section Q8", "3"],
		]
	]

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

			["32 A / 0,03 A / F676869 Section Q6", "3"],
			["32 A / 0,03 A / F707172 Section Q6", "3"],
			["32 A / 0,03 A / F7837475 Section Q6", "3"],
			["32 A / 0,03 A / F767778 Section Q6", "3"],

			["16 A / 0,03 A / F798081 Section Q7", "3"],
			["16 A / 0,03 A / F828384 Section Q7", "3"],
			["16 A / 0,03 A / F858687 Section Q7", "3"],
			["16 A / 0,03 A / F888990 Section Q7", "3"],
		]
	]

	# # list of preset options
	preset_2S_main = [
		# Description | n_of_poles
		[5, 4],
		[
			["63 A / Section Q1", "3"],
			["95 A / F456", "3"],
			["95 A / F789", "3"],
			["95 A / F101112", "3"],
			["95 A / F131415", "3"],
			["95 A / F161718", "3"],
			["95 A / F192021", "3"],
			["95 A / F222324", "3"],
			["95 A / F252627", "3"],
		]
	]

	preset_2S_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["16 A / 0,03 A / F1 Section Q1", "1"],
			["16 A / 0,03 A / F2 Section Q1", "1"],
			["16 A / 0,03 A / F3 Section Q1", "1"],
		]
	]

	preset_2T_main = [
		# Description | n_of_poles
		[5, 4],
		[
			["800 A / Main circuit breaker Q1", "3"],
			["63 A / Section Q2", "3"],
			["400 A / Q3", "3"],
			["100 A / Q4", "3"],
			["100 A / Q5", "3"],
			["100 A / Q6", "3"],
			["100 A / Q7", "3"],
			["100 A / Q8", "3"],
			["100 A / Q9", "3"],
			["100 A / Q10", "3"],
			["100 A / Q11", "3"],
			["100 A / Q12", "3"],
		]
	]

	preset_2U_main = [
		# Description | n_of_poles
		[5, 4],
		[
			["63 A / 0F1 Seciton F1", "3"],
			["63 A / 0F2 Seciton F2", "3"],
			["63 A / 0F3 Seciton F3", "3"],
			["63 A / 0F4 Seciton F4", "3"],
			["63 A / 0F5 Seciton F5", "3"],
			["63 A / 0F6 Seciton F6", "3"],
			["63 A / 0F7 Seciton F7", "3"],
		]
	]

	preset_2U_sub = [
		# Description | n_of_poles
		[5, 4],
		[
			["16 A / F1 Section 0F1", "1"],
			["16 A / F2 Seciton 0F1", "1"],
			["16 A / F3 Seciton 0F1", "1"],

			["16 A / 0,03 A / F4 Section 0F2", "1"],
			["16 A / 0,03 A / F5 Section 0F2", "1"],
			["16 A / 0,03 A / F6 Section 0F2", "1"],
			["16 A / 0,03 A / F7 Section 0F2", "1"],
			["16 A / 0,03 A / F8 Section 0F2", "1"],
			["16 A / 0,03 A / F9 Section 0F2", "1"],
			["16 A / 0,03 A / F10 Section 0F2", "1"],

			["16 A / 0,03 A / F11 Section 0F3", "1"],
			["16 A / 0,03 A / F12 Section 0F3", "1"],
			["16 A / 0,03 A / F13 Section 0F3", "1"],
			["16 A / 0,03 A / F14 Section 0F3", "1"],
			["16 A / 0,03 A / F15 Section 0F3", "1"],
			["16 A / 0,03 A / F16 Section 0F3", "1"],
			["16 A / 0,03 A / F17 Section 0F3", "1"],

			["16 A / 0,03 A / F18 Section 0F4", "1"],
			["16 A / 0,03 A / F19 Section 0F4", "1"],
			["16 A / 0,03 A / F20 Section 0F4", "1"],
			["16 A / 0,03 A / F21 Section 0F4", "1"],
			["16 A / 0,03 A / F22 Section 0F4", "1"],
			["16 A / 0,03 A / F23 Section 0F4", "1"],
			["16 A / 0,03 A / F24 Section 0F4", "1"],

			["16 A / F252627 Section 0F5", "3"],
			["16 A / F282930 Section 0F5", "3"],
			["16 A / F313233 Section 0F5", "3"],

			["16 A / F343536 Section 0F6", "3"],
			["16 A / F373839 Section 0F6", "3"],
			["32 A / F404142 Section 0F6", "3"],
			["63 A / F434445 Section 0F6", "3"],

			["40 A / 0,03 A / F464748 Section 0F7", "3"],
			["40 A / 0,03 A / F495051 Section 0F7", "3"],
		]
	]
