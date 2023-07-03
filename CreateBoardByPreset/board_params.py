# ================ system imports
import clr
import System

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import BuiltInCategory

# ================ Python imports
import operator
from operator import itemgetter, attrgetter

preset_3A_sub = [
	["RBS_ELEC_MAINS", 100],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "10kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
]

preset_3B_sub = [
	["RBS_ELEC_MAINS", 100],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "10kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
]

preset_2A = [
	["RBS_ELEC_MAINS", 1600],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "65kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
]

preset_2C = [
	["RBS_ELEC_MAINS", 1600],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "65kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
]

preset_2E_main = [
	["RBS_ELEC_MAINS", 200],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 200],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "36,8kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "Q"],
]

	# preset_2E_sub = [
	# ]

	# preset_2E1_main = [
	# ]

	# preset_2E1_sub = [
	# ]

	# preset_2H = [
	# ]

	# preset_2I = [
	# ]

	# preset_2J_main = [
	# ]

	# preset_2J_sub = [
	# ]

	# preset_2R_main = [
	# ]

	# preset_2R_sub = [
	# ]

	# preset_2R2_main = [
	# ]

	# preset_2R2_sub = [
	# ]

	# preset_2S_main = [
	# ]

	# preset_2S_sub = [
	# ]

	# preset_2T_main = [
	# ]

	# preset_2T_sub = [
	# ]

	# preset_2U_main = [
	# ]

	# preset_2U_sub = [
	# ]
