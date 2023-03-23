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
	parameters_to_set = [
		"RBS_ELEC_CIRCUIT_NAME",
		"RBS_ELEC_NUMBER_OF_POLES",
		"RBS_ELEC_CIRCUIT_FRAME_PARAM"
	]

	preset_3A_sub = [
		["6C / F123 Section 0F1", 3, 6],
		["6C / F456 Section 0F1", 3, 6],
		["6C / F789 Section 0F1", 3, 6],
		["6C / F101112 Section 0F1", 3, 6],
		["6C / F131415 Section 0F1", 3, 6],

		["6C / F161718 Section 0F2", 3, 6],
		["6C / F192021 Section 0F2", 3, 6],
		["6C / F222324 Section 0F2", 3, 6],
		["6C / F252627 Section 0F2", 3, 6],
		["6C / F282930 Section 0F2", 3, 6],

		["6C / F313233 Section 0F3", 3, 6],
		["6C / F343536 Section 0F3", 3, 6],
		["6C / F373839 Section 0F3", 3, 6],
		["6C / F404142 Section 0F3", 3, 6],
		["6C / F434445 Section 0F3", 3, 6],

		["6C / F464748 Section 0F4", 3, 6],
		["6C / F495051 Section 0F4", 3, 6],
		["6C / F525354 Section 0F4", 3, 6],
		["6C / F555657 Section 0F4", 3, 6],
		["6C / F585969 Section 0F4", 3, 6],

		["6C / F61 Section 0F5", 1, 6],
		["6C / F62 Section 0F5", 1, 6],
		["6C / F63 Section 0F5", 1, 6],
		["6C / F64 Section 0F5", 1, 6],
		["6C / F65 Section 0F5", 1, 6],
		["6C / F66 Section 0F5", 1, 6],
		["6C / F67 Section 0F5", 1, 6],
		["6C / F68 Section 0F5", 1, 6],
		["6C / F69 Section 0F5", 1, 6],
		["6C / F70 Section 0F5", 1, 6],
		["6C / F71 Section 0F5", 1, 6],
		["6C / F72 Section 0F5", 1, 6],
	]

	preset_3B_sub = [
		# Description | n_of_poles
		["6C / F1 Section 0F1", 1, 6],
		["6C / F2 Section 0F1", 1, 6],
		["6C / F3 Section 0F1", 1, 6],
		["6C / F4 Section 0F1", 1, 6],
		["6C / F5 Section 0F1", 1, 6],
		["6C / F6 Section 0F1", 1, 6],
		["6C / F7 Section 0F1", 1, 6],
		["6C / F8 Section 0F1", 1, 6],

		["6C / F9 Section 0F2", 1, 6],
		["6C / F10 Section 0F2", 1, 6],
		["6C / F11 Section 0F2", 1, 6],
		["6C / F12 Section 0F2", 1, 6],
		["6C / F13 Section 0F2", 1, 6],
		["6C / F14 Section 0F2", 1, 6],
		["6C / F15 Section 0F2", 1, 6],
		["6C / F16 Section 0F2", 1, 6],

		["6C / F17 Section 0F3", 1, 6],
		["6C / F18 Section 0F3", 1, 6],
		["6C / F19 Section 0F3", 1, 6],
		["6C / F20 Section 0F3", 1, 6],
		["6C / F21 Section 0F3", 1, 6],
		["6C / F22 Section 0F3", 1, 6],
		["6C / F23 Section 0F3", 1, 6],
		["6C / F24	Section 0F3", 1, 6],

		["6C / F25 Section 0F4", 1, 6],
		["6C / F26 Section 0F4", 1, 6],
		["6C / F27 Section 0F4", 1, 6],
		["6C / F28 Section 0F4", 1, 6],
		["6C / F29 Section 0F4", 1, 6],
		["6C / F30 Section 0F4", 1, 6],
		["6C / F31 Section 0F4", 1, 6],
		["6C / F32	Section 0F4", 1, 6],

		["6C / F33 Section 0F5", 1, 6],
		["6C / F34 Section 0F5", 1, 6],
		["6C / F35 Section 0F5", 1, 6],
		["6C / F36 Section 0F5", 1, 6],
		["6C / F37 Section 0F5", 1, 6],
		["6C / F38 Section 0F5", 1, 6],
		["6C / F39 Section 0F5", 1, 6],
		["6C / F40	Section 0F5", 1, 6],

		["6C / F33 Section 0F6", 1, 6],
		["6C / F34 Section 0F6", 1, 6],
		["6C / F35 Section 0F6", 1, 6],
		["6C / F36 Section 0F6", 1, 6],
		["6C / F37 Section 0F6", 1, 6],
		["6C / F38 Section 0F6", 1, 6],
		["6C / F39 Section 0F6", 1, 6],
		["6C / F40	Section 0F6", 1, 6],

		["6C / F49 Section 0F7", 1, 6],
		["6C / F50 Section 0F7", 1, 6],
		["6C / F51 Section 0F7", 1, 6],
		["6C / F52 Section 0F7", 1, 6],
		["6C / F53 Section 0F7", 1, 6],
		["6C / F54 Section 0F7", 1, 6],
		["6C / F55 Section 0F7", 1, 6],
		["6C / F56	Section 0F7", 1, 6],

		["6C / F57 Section 0F8", 1, 6],
		["6C / F58 Section 0F8", 1, 6],
		["6C / F59 Section 0F8", 1, 6],
		["6C / F60 Section 0F8", 1, 6],
		["6C / F61 Section 0F8", 1, 6],
		["6C / F62 Section 0F8", 1, 6],
		["6C / F63 Section 0F8", 1, 6],
		["6C / F64	Section 0F8", 1, 6],
	]

	preset_2A = [
		["250ETU / FD1 / 1xd150mm", 3, 250],
		["250ETU / FD2 / 1xd150mm", 3, 250],
		["160ETU / FD3 / 1xd150mm", 3, 160],
		["160ETU / FD4 / 1xd150mm", 3, 160],
		["160ETU / FD5 / 1xd150mm", 3, 160],
		["160ETU / FD6 / 1xd150mm", 3, 160],
		["160ETU / FD7 / 1xd150mm", 3, 160],
		["160ETU / FD8 / 1xd150mm", 3, 160],
		["160ETU / FD9 / 1xd150mm", 3, 160],
		["160ETU / FD10 / 1xd150mm", 3, 160],
		["160ETU / FD11 / 1xd150mm", 3, 160],
		["160ETU / FD12 / 1xd150mm", 3, 160],
		["160ETU / FD13 / 1xd150mm", 3, 160],
		["160ETU / FD14 / 1xd150mm", 3, 160],
	]

	preset_2C = [
		# Description | n_of_poles
		["630ETU / FD1 / 3xd150mm", 3, 630],
		["630ETU / FD2 / 3xd150mm", 3, 630],
		["630ETU / FD3 / 3xd150mm", 3, 630],
		["630ETU / FD4 / 3xd150mm", 3, 630],
	]

	preset_2E_main = [
		# Description | n_of_poles
		["63C / Section F1 / 1xd16mm", 3, 63],
		["63C / Section F2 / 1xd16mm", 3, 63],
		["63C / Section F3 / 1xd16mm", 3, 63],
		["63C / Section F4 / 1xd16mm", 3, 63],
		["63C / Section F5 / 1xd16mm", 3, 63],
		["63C / Section F6 / 1xd16mm", 3, 63],
		["Empty", 1],
		["Empty", 1],
	]

	preset_2E_sub = [
		# Description | n_of_poles
		["32B / F123 / 1xd6mm", 3, 32],
		["32B / F456 / 1xd6mm", 3, 32],
		["32B / F789 / 1xd6mm", 3, 32],
		["32B / F101112 / 1xd6mm", 3, 32],
		["32B / F131415 / 1xd6mm", 3, 32],
		["63B / F161718 / 1xd16mm", 3, 63],
		["63B / F192021 / 1xd16mm", 3, 63],

		["16B / 0,03 A / F22 Section F1", 1, 16],
		["16B / 0,03 A / F23 Section F1", 1, 16],
		["16B / 0,03 A / F24 Section F1", 1, 16],
		["16B / 0,03 A / F25 Section F1", 1, 16],
		["16B / 0,03 A / F26 Section F1", 1, 16],
		["16B / 0,03 A / F27 Section F1", 1, 16],
		["16B / 0,03 A / F28 Section F1", 1, 16],
		["16B / 0,03 A / F29 Section F1", 1, 16],
		["16B / 0,03 A / F30 Section F1", 1, 16],

		["16B / 0,03 A / F31 Section F2", 1, 16],
		["16B / 0,03 A / F32 Section F2", 1, 16],
		["16B / 0,03 A / F33 Section F2", 1, 16],
		["16B / 0,03 A / F34 Section F2", 1, 16],
		["16B / 0,03 A / F35 Section F2", 1, 16],
		["16B / 0,03 A / F36 Section F2", 1, 16],
		["16B / 0,03 A / F37 Section F2", 1, 16],
		["16B / 0,03 A / F38 Section F2", 1, 16],
		["16B / 0,03 A / F39 Section F2", 1, 16],

		["16B / 0,03 A / F40 Section F3", 1, 16],
		["16B / 0,03 A / F41 Section F3", 1, 16],
		["16B / 0,03 A / F42 Section F3", 1, 16],
		["16B / 0,03 A / F43 Section F3", 1, 16],
		["16B / 0,03 A / F44 Section F3", 1, 16],
		["16B / 0,03 A / F45 Section F3", 1, 16],
		["16B / 0,03 A / F46 Section F3", 1, 16],
		["16B / 0,03 A / F47 Section F3", 1, 16],
		["16B / 0,03 A / F48 Section F3", 1, 16],

		["16B / F495051 Section F4", 3, 16],
		["16B / F525354 Section F4", 3, 16],
		["16B / F555657 Section F4", 3, 16],
		["16B / F585960 Section F4", 3, 16],
		["16B / F616263 Section F4", 3, 16],

		["16B / 0,03 A / F646566 Section F5", 3, 16],
		["16B / 0,03 A / F676869 Section F5", 3, 16],
		["16B / 0,03 A / F707172 Section F5", 3, 16],

		["10C / F73 Section F6", 1, 10],
		["10C / F74 Section F6", 1, 10],
		["10C / F75 Section F6", 1, 10],
		["10C / F76 Section F6", 1, 10],
	]

	preset_2E1_main = [
		# Description | n_of_poles
		["63FUSE / Section F1 / 1xd16mm", 3, 63],
		["63FUSE / Section F2 / 1xd16mm", 3, 63],
		["63FUSE / Section F3 / 1xd16mm", 3, 63],
		["63FUSE / Section F4 / 1xd16mm", 3, 63],
		["63FUSE / Section F5 / 1xd16mm", 3, 63],
		["63FUSE / Section F6 / 1xd16mm", 3, 63],
		["63FUSE / Section F7 / 1xd16mm", 3, 63],
		["63FUSE / Section F8 / 1xd16mm", 3, 63],
		["63FUSE / Section F9 / 1xd16mm", 3, 63],
		["63FUSE / Section F10 / 1xd16mm", 3, 63],
	]

	preset_2E1_sub = [
		# Description | n_of_poles
		["32FUSE / F123 / 1xd6mm", 3, 32],
		["32FUSE / F456 / 1xd6mm", 3, 32],
		["32FUSE / F789 / 1xd6mm", 3, 32],
		["32FUSE / F101112 / 1xd6mm", 3, 32],
		["32FUSE / F131415 / 1xd6mm", 3, 32],
		["63FUSE / F161718 / 1xd16mm", 3, 63],
		["63FUSE / F192021 / 1xd16mm", 3, 63],

		["16B / 0,03 A / F22 Section F1", 1, 16],
		["16B / 0,03 A / F23 Section F1", 1, 16],
		["16B / 0,03 A / F24 Section F1", 1, 16],
		["16B / 0,03 A / F25 Section F1", 1, 16],
		["16B / 0,03 A / F26 Section F1", 1, 16],
		["16B / 0,03 A / F27 Section F1", 1, 16],
		["16B / 0,03 A / F28 Section F1", 1, 16],
		["16B / 0,03 A / F29 Section F1", 1, 16],
		["16B / 0,03 A / F30 Section F1", 1, 16],

		["16B / 0,03 A / F31 Section F2", 1, 16],
		["16B / 0,03 A / F32 Section F2", 1, 16],
		["16B / 0,03 A / F33 Section F2", 1, 16],
		["16B / 0,03 A / F34 Section F2", 1, 16],
		["16B / 0,03 A / F35 Section F2", 1, 16],
		["16B / 0,03 A / F36 Section F2", 1, 16],
		["16B / 0,03 A / F37 Section F2", 1, 16],
		["16B / 0,03 A / F38 Section F2", 1, 16],
		["16B / 0,03 A / F39 Section F2", 1, 16],

		["16B / 0,03 A / F40 Section F3", 1, 16],
		["16B / 0,03 A / F41 Section F3", 1, 16],
		["16B / 0,03 A / F42 Section F3", 1, 16],
		["16B / 0,03 A / F43 Section F3", 1, 16],
		["16B / 0,03 A / F44 Section F3", 1, 16],
		["16B / 0,03 A / F45 Section F3", 1, 16],
		["16B / 0,03 A / F46 Section F3", 1, 16],
		["16B / 0,03 A / F47 Section F3", 1, 16],
		["16B / 0,03 A / F48 Section F3", 1, 16],

		["16B / 0,03 A / F49 Section F4", 1, 16],
		["16B / 0,03 A / F50 Section F4", 1, 16],
		["16B / 0,03 A / F51 Section F4", 1, 16],
		["16B / 0,03 A / F52 Section F4", 1, 16],
		["16B / 0,03 A / F53 Section F4", 1, 16],
		["16B / 0,03 A / F54 Section F4", 1, 16],
		["16B / 0,03 A / F55 Section F4", 1, 16],
		["16B / 0,03 A / F56 Section F4", 1, 16],
		["16B / 0,03 A / F57 Section F4", 1, 16],

		["16B / 0,03 A / F58 Section F5", 1, 16],
		["16B / 0,03 A / F59 Section F5", 1, 16],
		["16B / 0,03 A / F60 Section F5", 1, 16],
		["16B / 0,03 A / F61 Section F5", 1, 16],
		["16B / 0,03 A / F62 Section F5", 1, 16],
		["16B / 0,03 A / F63 Section F5", 1, 16],
		["16B / 0,03 A / F64 Section F5", 1, 16],
		["16B / 0,03 A / F65 Section F5", 1, 16],
		["16B / 0,03 A / F66 Section F5", 1, 16],

		["16B / 0,03 A / F67 Section F6", 1, 16],
		["16B / 0,03 A / F68 Section F6", 1, 16],
		["16B / 0,03 A / F69 Section F6", 1, 16],
		["16B / 0,03 A / F70 Section F6", 1, 16],
		["16B / 0,03 A / F71 Section F6", 1, 16],
		["16B / 0,03 A / F72 Section F6", 1, 16],
		["16B / 0,03 A / F73 Section F6", 1, 16],
		["16B / 0,03 A / F74 Section F6", 1, 16],
		["16B / 0,03 A / F75 Section F6", 1, 16],

		["16B / 0,03 A / F76 Section F7", 1, 16],
		["16B / 0,03 A / F77 Section F7", 1, 16],
		["16B / 0,03 A / F78 Section F7", 1, 16],
		["16B / 0,03 A / F79 Section F7", 1, 16],
		["16B / 0,03 A / F80 Section F7", 1, 16],
		["16B / 0,03 A / F81 Section F7", 1, 16],
		["16B / 0,03 A / F82 Section F7", 1, 16],
		["16B / 0,03 A / F83 Section F7", 1, 16],
		["16B / 0,03 A / F84 Section F7", 1, 16],

		["16B / F858687 Section F8", 3, 16],
		["16B / F888990 Section F8", 3, 16],
		["16B / F919293 Section F8", 3, 16],

		["16B / 0,03 A / F949596 Section F9", 3, 16],
		["16B / 0,03 A / F979899 Section F9", 3, 16],
		["16B / 0,03 A / F100101102 Section F9", 3, 16],

		["10C / F103 Section F10", 1, 10],
		["10C / F104 Section F10", 1, 10],
		["10C / F105 Section F10", 1, 10],
		["10C / F106 Section F10", 1, 10],
	]

	preset_2H = [
		# Description | n_of_poles
		["N/A", 3],
		["100ETU / Q3 / 1xd35mm", 3, 160],
		["100ETU / Q4 / 1xd35mm", 3, 160],
		["100ETU / Q5 / 1xd35mm", 3, 160],
		["100ETU / Q6 / 1xd35mm", 3, 160],
		["100ETU / Q7 / 1xd35mm", 3, 160],
		["100ETU / Q8 / 1xd35mm", 3, 160],
		["100ETU / Q9 / 1xd35mm", 3, 160],
		["100ETU / Q10 / 1xd35mm", 3, 160],
		["100ETU / Q11 / 1xd35mm", 3, 160],
		["100ETU / Q12 / 1xd35mm", 3, 160],
		["100ETU / Q13 / 1xd35mm", 3, 160],
		["100ETU / Q14 / 1xd35mm", 3, 160],
	]

	preset_2I = [
		# Description | n_of_poles
		["630ETU / Main switch Q01 / 3xd150mm", 3, 630],
		["Internal circuits", 3],
		["250ETU / Q3 / 1xd120mm", 3, 250],
		["250ETU / Q4 / 1xd120mm", 3, 250],
		["160ETU / Q5 / 1xd70mm", 3, 160],
		["160ETU / Q6 / 1xd70mm", 3, 160],
		["100ETU / Q7 / 1xd35mm", 3, 160],
		["100ETU / Q8 / 1xd35mm", 3, 160],
		["100ETU / Q9 / 1xd35mm", 3, 160],
	]

	# list of preset options
	preset_2J_main = [
		# Description | n_of_poles
		["160ETU / 0Q2 / 1xd70mm", 3, 160],
		["160ETU / 0Q3 / 1xd70mm", 3, 160],
		["160ETU / 0Q4 / 1xd70mm", 3, 160],
		["160ETU / 0Q5 / 1xd70mm", 3, 160],
		["160ETU / 0Q6 / 1xd70mm", 3, 160],
		["63C / Section Q7 / 1xd16mm", 3, 63],
		["63C / Section Q8 / 1xd16mm", 3, 63],
	]

	# list of preset options
	preset_2J_sub = [
		# Description | n_of_poles
		["16B / 0,03 A / Q123 Section Q7", 3, 16],
		["16B / 0,03 A / Q456 Section Q7", 3, 16],
		["16B / 0,03 A / Q789 Section Q7", 3, 16],
		["16B / 0,03 A / Q101112 Section Q7", 3, 16],
		["16B / 0,03 A / Q131415 Section Q7", 3, 16],
		["16B / 0,03 A / Q161718 Section Q7", 3, 16],
		["16B / 0,03 A / Q192021 Section Q7", 3, 16],
		["16B / 0,03 A / Q222324 Section Q7", 3, 16],

		["16B / 0,03 A / Q252627 Section Q8", 3, 16],
		["16B / 0,03 A / Q282930 Section Q8", 3, 16],
		["16B / 0,03 A / Q313233 Section Q8", 3, 16],
		["16B / 0,03 A / Q343536 Section Q8", 3, 16],
		["16B / 0,03 A / Q373839 Section Q8", 3, 16],
		["16B / 0,03 A / Q404142 Section Q8", 3, 16],
		["16B / 0,03 A / Q434445 Section Q8", 3, 16],
		["16B / 0,03 A / Q464748 Section Q8", 3, 16],
	]

	# list of preset options
	preset_2R_main = [
		["63TMTU / Section 0Q2 / 1xd16mm", 3, 160],
		["63TMTU / Section 0Q3 / 1xd16mm", 3, 160],
		["63TMTU / Section 0Q4 / 1xd16mm", 3, 160],
		["63TMTU / Section 0Q5 / 1xd16mm", 3, 160],
		["63TMTU / Section 0Q6 / 1xd16mm", 3, 160],
		["63TMTU / Section 0Q7 / 1xd16mm", 3, 160],
		["160TMTU/ 0Q8 / 1xd70mm", 3, 160],
	]

	preset_2R_sub = [
		# Description | n_of_poles
		["16B / F123 Section Q2", 3, 16],
		["16B / F456 Section Q2", 3, 16],
		["16B / F789 Section Q2", 3, 16],
		["16B / F101112 Section Q2", 3, 16],
		["16B / F131415 Section Q2", 3, 16],
		["16B / F161718 Section Q2", 3, 16],
		["16B / F192021 Section Q2", 3, 16],
		["16B / F222324 Section Q2", 3, 16],
		["16B / F252627 Section Q2", 3, 16],

		["16B / F282930 Section Q3", 3, 16],
		["16B / F313233 Section Q3", 3, 16],
		["16B / F343536 Section Q3", 3, 16],
		["16B / F373839 Section Q3", 3, 16],
		["16B / F404142 Section Q3", 3, 16],
		["16B / F434445 Section Q3", 3, 16],
		["16B / F464748 Section Q3", 3, 16],
		["16B / F495051 Section Q3", 3, 16],
		["16B / F525354 Section Q3", 3, 16],

		["16B / F55 Section Q4", 1, 16],
		["16B / F56 Section Q4", 1, 16],
		["16B / F57 Section Q4", 1, 16],
		["16B / F58 Section Q4", 1, 16],
		["16B / F59 Section Q4", 1, 16],
		["16B / F60 Section Q4", 1, 16],

		["16B / 0,03 A / F61 Section Q5", 1, 16],
		["16B / 0,03 A / F62 Section Q5", 1, 16],
		["16B / 0,03 A / F63 Section Q5", 1, 16],
		["16B / 0,03 A / F64 Section Q5", 1, 16],
		["16B / 0,03 A / F65 Section Q5", 1, 16],
		["16B / 0,03 A / F66 Section Q5", 1, 16],

		["32B / 0,03 A / F676869 Section Q6 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F707172 Section Q6 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F7837475 Section Q6 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F767778 Section Q6 / 1xd6mm", 3, 32],

		["16B / 0,03 A / F798081 Section Q7", 3, 16],
		["16B / 0,03 A / F828384 Section Q7", 3, 16],
		["16B / 0,03 A / F858687 Section Q7", 3, 16],
		["16B / 0,03 A / F888990 Section Q7", 3, 16],

	]

	# list of preset options
	preset_2R2_main = [
		# Description | n_of_poles
		["100TMTU / Section 0Q2 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q3 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q4 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q5 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q6 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q7 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q8 / 1xd35mm", 3, 160],
		["100TMTU / Section 0Q9 / 1xd35mm", 3, 160],
		["160ETU / 0Q10 / 1xd120mm", 3, 160],
	]

	preset_2R2_sub = [
		# Description | n_of_poles
		["40FUSE / F123, 1xd10mm", 3, 40],
		["40FUSE / F456, 1xd10mm", 3, 40],
		["40FUSE / F789, 1xd10mm", 3, 40],
		["40FUSE / F101112, 1xd10mm", 3, 40],
		["40FUSE / F131415, 1xd10mm", 3, 40],
		["40FUSE / F161718, 1xd10mm", 3, 40],

		["63FUSE / F192021, 1xd16mm", 3, 63],
		["63FUSE / F222324, 1xd16mm", 3, 63],
		["63FUSE / F252627, 1xd16mm", 3, 63],
		["63FUSE / F282930, 1xd16mm", 3, 63],
		["63FUSE / F313233, 1xd16mm", 3, 63],
		["63FUSE / F343536, 1xd16mm", 3, 63],

		["32B / 0,03 A / F373839 Section Q2 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F404142 Section Q2 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F434445 Section Q2 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F464748 Section Q2 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F495051 Section Q2 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F525354 Section Q2 / 1xd6mm", 3, 32],

		["32B / 0,03 A / F555657 Section Q3 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F585960 Section Q3 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F616263 Section Q3 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F646566 Section Q3 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F676869 Section Q3 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F707172 Section Q3 / 1xd6mm", 3, 32],

		["16B / F73 Section Q4", 1, 16],
		["16B / F74 Section Q4", 1, 16],
		["16B / F75 Section Q4", 1, 16],
		["16B / F76 Section Q4", 1, 16],
		["16B / F77 Section Q4", 1, 16],
		["16B / F78 Section Q4", 1, 16],
		["16B / F79 Section Q4", 1, 16],
		["16B / F80 Section Q4", 1, 16],
		["16B / F81 Section Q4", 1, 16],
		["16B / F82 Section Q4", 1, 16],
		["16B / F83 Section Q4", 1, 16],
		["16B / F84 Section Q4", 1, 16],
		["16B / F85 Section Q4", 1, 16],
		["16B / F86 Section Q4", 1, 16],
		["16B / F87 Section Q4", 1, 16],
		["16B / F88 Section Q4", 1, 16],
		["16B / F89 Section Q4", 1, 16],
		["16B / F90 Section Q4", 1, 16],


		["32B / F91 Section Q5 / 1xd4mm", 1, 32],
		["32B / F92 Section Q5 / 1xd4mm", 1, 32],
		["32B / F93 Section Q5 / 1xd4mm", 1, 32],
		["32B / F94 Section Q5 / 1xd4mm", 1, 32],
		["32B / F95 Section Q5 / 1xd4mm", 1, 32],
		["32B / F96 Section Q5 / 1xd4mm", 1, 32],
		["32B / F97 Section Q5 / 1xd4mm", 1, 32],
		["32B / F98 Section Q5 / 1xd4mm", 1, 32],
		["32B / F99 Section Q5 / 1xd4mm", 1, 32],

		["16B / F100101102 Section Q6", 3, 16],
		["16B / F103104105 Section Q6", 3, 16],
		["16B / F106107108 Section Q6", 3, 16],
		["16B / F109110111 Section Q6", 3, 16],
		["16B / F112113114 Section Q6", 3, 16],
		["16B / F115116117 Section Q6", 3, 16],
		["16B / F118119120 Section Q6", 3, 16],
		["16B / F121122123 Section Q6", 3, 16],
		["16B / F124125126 Section Q6", 3, 16],

		["16B / F127128129 Section Q7", 3, 16],
		["16B / F130131132 Section Q7", 3, 16],
		["16B / F133134135 Section Q7", 3, 16],
		["16B / F136137138 Section Q7", 3, 16],
		["16B / F139140141 Section Q7", 3, 16],
		["16B / F142143144 Section Q7", 3, 16],
		["16B / F145146147 Section Q7", 3, 16],
		["16B / F148149150 Section Q7", 3, 16],
		["16B / F151152153 Section Q7", 3, 16],

		["16B / 0,03 A / F154 Section Q8", 1, 16],
		["16B / 0,03 A / F155 Section Q8", 1, 16],
		["16B / 0,03 A / F156 Section Q8", 1, 16],
		["16B / 0,03 A / F157 Section Q8", 1, 16],
		["16B / 0,03 A / F158 Section Q8", 1, 16],
		["16B / 0,03 A / F159 Section Q8", 1, 16],
		["16B / 0,03 A / F160 Section Q8", 1, 16],
		["16B / 0,03 A / F161 Section Q8", 1, 16],
		["16B / 0,03 A / F162 Section Q8", 1, 16],
		["16B / 0,03 A / F163 Section Q8", 1, 16],
		["16B / 0,03 A / F164 Section Q8", 1, 16],
		["16B / 0,03 A / F165 Section Q8", 1, 16],
		["16B / 0,03 A / F166 Section Q8", 1, 16],
		["16B / 0,03 A / F167 Section Q8", 1, 16],
		["16B / 0,03 A / F168 Section Q8", 1, 16],
		["16B / 0,03 A / F169 Section Q8", 1, 16],
		["16B / 0,03 A / F170 Section Q8", 1, 16],
		["16B / 0,03 A / F171 Section Q8", 1, 16],
		["16B / 0,03 A / F172 Section Q8", 1, 16],
		["16B / 0,03 A / F173 Section Q8", 1, 16],
		["16B / 0,03 A / F174 Section Q8", 1, 16],

		["16B / 0,03 A / F175 Section Q9", 1, 16],
		["16B / 0,03 A / F176 Section Q9", 1, 16],
		["16B / 0,03 A / F177 Section Q9", 1, 16],
		["16B / 0,03 A / F178 Section Q9", 1, 16],
		["16B / 0,03 A / F179 Section Q9", 1, 16],
		["16B / 0,03 A / F180 Section Q9", 1, 16],
		["16B / 0,03 A / F181 Section Q9", 1, 16],
		["16B / 0,03 A / F182 Section Q9", 1, 16],
		["16B / 0,03 A / F183 Section Q9", 1, 16],
		["16B / 0,03 A / F184 Section Q9", 1, 16],
		["16B / 0,03 A / F185 Section Q9", 1, 16],
		["16B / 0,03 A / F186 Section Q9", 1, 16],
		["16B / 0,03 A / F187 Section Q9", 1, 16],
		["16B / 0,03 A / F188 Section Q9", 1, 16],
		["16B / 0,03 A / F189 Section Q9", 1, 16],
		["16B / 0,03 A / F190 Section Q9", 1, 16],
		["16B / 0,03 A / F191 Section Q9", 1, 16],
		["16B / 0,03 A / F192 Section Q9", 1, 16],
		["16B / 0,03 A / F193 Section Q9", 1, 16],
		["16B / 0,03 A / F194 Section Q9", 1, 16],
		["16B / 0,03 A / F195 Section Q9", 1, 16],
	]

	# list of preset options
	preset_2S_main = [
		# Description | n_of_poles
		["63TMTU / Section Q1 / 1xd16mm", 3, 63],
		["95/160ETU / F456 / 1xd35mm", 3, 160],
		["95/160ETU / F789 / 1xd35mm", 3, 160],
		["95/160ETU / F101112 / 1xd35mm", 3, 160],
		["95/160ETU / F131415 / 1xd35mm", 3, 160],
		["95/160ETU / F161718 / 1xd35mm", 3, 160],
		["95/160ETU / F192021 / 1xd35mm", 3, 160],
		["95/160ETU / F222324 / 1xd35mm", 3, 160],
		["95/160ETU / F252627 / 1xd35mm", 3, 160],
	]

	preset_2S_sub = [
		# Description | n_of_poles
		["16B / 0,03 A / F1 Section Q1", 1, 16],
		["16B / 0,03 A / F2 Section Q1", 1, 16],
		["16B / 0,03 A / F3 Section Q1", 1, 16],
	]

	preset_2T_main = [
		# Description | n_of_poles
		["800ETU / Main switch Q1 / 4xd150mm", 3, 800],
		["63ETU / Section Q2 / 1xd16mm", 3, 100],
		["400ETU / Q3 / cu30x10mm", 3, 400],
		["100ETU / Q4 / cu25x5mm", 3, 160],
		["100ETU / Q5 / cu25x5mm", 3, 160],
		["100ETU / Q6 / cu25x5mm", 3, 160],
		["100ETU / Q7 / cu25x5mm", 3, 160],
		["100ETU / Q8 / cu25x5mm", 3, 160],
		["100ETU / Q9 / cu25x5mm", 3, 160],
		["100ETU / Q10 / cu25x5mm", 3, 160],
		["100ETU / Q11 / cu25x5mm", 3, 160],
		["100ETU / Q12 / cu25x5mm", 3, 160],
	]

	# TODO
	preset_2T_sub = [
		# Description | n_of_poles
		["16C / 2F1 Section Q2", 1, 16],
		["16C / 2F2 Seciton Q2", 1, 16],
		["16C / 2F3 Seciton Q2", 1, 16],
	]

	preset_2U_main = [
		# Description | n_of_poles
		["63C / 0F1 Seciton F1 / 1xd16mm", 3, 63],
		["63C / 0F2 Seciton F2 / 1xd16mm", 3, 63],
		["63C / 0F3 Seciton F3 / 1xd16mm", 3, 63],
		["63C / 0F4 Seciton F4 / 1xd16mm", 3, 63],
		["63C / 0F5 Seciton F5 / 1xd16mm", 3, 63],
		["63C / 0F6 Seciton F6 / 1xd16mm", 3, 63],
		["63ETU / Q7 Seciton F7 / 1xd16mm", 3, 63],
	]

	preset_2U_sub = [
		# Description | n_of_poles
		["16B / F1 Section 0F1", 1, 16],
		["16B / F2 Seciton 0F1", 1, 16],
		["16B / F3 Seciton 0F1", 1, 16],

		["16B / 0,03 A / F4 Section 0F2", 1, 16],
		["16B / 0,03 A / F5 Section 0F2", 1, 16],
		["16B / 0,03 A / F6 Section 0F2", 1, 16],
		["16B / 0,03 A / F7 Section 0F2", 1, 16],
		["16B / 0,03 A / F8 Section 0F2", 1, 16],
		["16B / 0,03 A / F9 Section 0F2", 1, 16],
		["16B / 0,03 A / F10 Section 0F2", 1, 16],

		["16B / 0,03 A / F11 Section 0F3", 1, 16],
		["16B / 0,03 A / F12 Section 0F3", 1, 16],
		["16B / 0,03 A / F13 Section 0F3", 1, 16],
		["16B / 0,03 A / F14 Section 0F3", 1, 16],
		["16B / 0,03 A / F15 Section 0F3", 1, 16],
		["16B / 0,03 A / F16 Section 0F3", 1, 16],
		["16B / 0,03 A / F17 Section 0F3", 1, 16],

		["16B / 0,03 A / F18 Section 0F4", 1, 16],
		["16B / 0,03 A / F19 Section 0F4", 1, 16],
		["16B / 0,03 A / F20 Section 0F4", 1, 16],
		["16B / 0,03 A / F21 Section 0F4", 1, 16],
		["16B / 0,03 A / F22 Section 0F4", 1, 16],
		["16B / 0,03 A / F23 Section 0F4", 1, 16],
		["16B / 0,03 A / F24 Section 0F4", 1, 16],

		["16B / F252627 Section 0F5", 3, 16],
		["16B / F282930 Section 0F5", 3, 16],
		["16B / F313233 Section 0F5", 3, 16],

		["16B / F343536 Section 0F6", 3, 16],
		["16B / F373839 Section 0F6", 3, 16],
		["32B / F404142 Section 0F6 / 1xd6mm", 3, 32],
		["63B / F434445 Section 0F6 / 1xd16mm", 3, 63],

		["32B / 0,03 A / F464748 Section Q7 / 1xd6mm", 3, 32],
		["32B / 0,03 A / F495051 Section Q7 / 1xd6mm", 3, 32],
	]
