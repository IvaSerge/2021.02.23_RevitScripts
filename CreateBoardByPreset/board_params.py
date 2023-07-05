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
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
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
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2A = [
	["RBS_ELEC_MAINS", 1600],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "65kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "FD"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2C = [
	["RBS_ELEC_MAINS", 1600],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "65kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "FD"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2E_main = [
	["RBS_ELEC_MAINS", 200],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 200],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "36,8kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0F"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2E_sub = [
	["RBS_ELEC_MAINS", 200],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 200],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "36,8kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2E1_main = [
	["RBS_ELEC_MAINS", 250],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 250],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0F"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2E1_sub = [
	["RBS_ELEC_MAINS", 250],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 250],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2H = [
	["RBS_ELEC_MAINS", 400],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 400],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "32kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2I = [
	["RBS_ELEC_MAINS", 630],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 630],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "35kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2J_main = [
	["RBS_ELEC_MAINS", 250],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 250],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "20kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2J_sub = [
	["RBS_ELEC_MAINS", 250],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 250],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "20kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2R_main = [
	["RBS_ELEC_MAINS", 315],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 315],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "32kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2R_sub = [
	["RBS_ELEC_MAINS", 315],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 315],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "32kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2R2_main = [
	["RBS_ELEC_MAINS", 400],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 400],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "45kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2R2_sub = [
	["RBS_ELEC_MAINS", 400],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 400],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "45kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2S_main = [
	["RBS_ELEC_MAINS", 400],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "BOTTOM"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 400],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "55kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "F"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2S_sub = [
	["RBS_ELEC_MAINS", 400],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "BOTTOM"],
	["RBS_ELEC_ENCLOSURE", "IP55"],
	["Protection Class", "IP55"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 400],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "55kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]

preset_2T_main = [
	["RBS_ELEC_MAINS", 800],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "BOTTOM"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 800],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "Q"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2T_sub = [
	["RBS_ELEC_MAINS", 800],
	["RBS_ELEC_MOUNTING", "FLOOR"],
	["RBS_ELEC_PANEL_FEED_PARAM", "BOTTOM"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 800],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "2F"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2U_main = [
	["RBS_ELEC_MAINS", 100],
	["RBS_ELEC_MOUNTING", "WALL"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", "0F"],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000010)],  # Prefixed
]

preset_2U_sub = [
	["RBS_ELEC_MAINS", 100],
	["RBS_ELEC_MOUNTING", "WALL"],
	["RBS_ELEC_PANEL_FEED_PARAM", "TOP"],
	["RBS_ELEC_ENCLOSURE", "IP54"],
	["Protection Class", "IP54"],
	["RBS_ELEC_PANEL_MCB_RATING_PARAM", 100],
	["RBS_ELEC_SHORT_CIRCUIT_RATING", "50kA"],
	["RBS_ELEC_CIRCUIT_PREFIX", ""],
	["RBS_ELEC_CIRCUIT_NAMING", Autodesk.Revit.DB.ElementId(-7000011)],  # Standard
]
