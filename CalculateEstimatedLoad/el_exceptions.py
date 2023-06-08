# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import math
import toolsrvt


def test_exceptions(_elSys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> bool
	"""
		Analise of electrical system if it is an "exception"
		all
	"""
	el_sys_elements = [i for i in _elSys.Elements]  # type: list[Autodesk.Revit.DB.FamilyInstance]
	first_elem = el_sys_elements[0]  # type: Autodesk.Revit.DB.FamilyInstance
	doc = first_elem.Document

	# The fisrst element of the system is electrical board and
	board_category = toolsrvt.category_by_bic_name(doc, "OST_ElectricalEquipment").Id
	test_board = first_elem.Category.Id == board_category

	# if the first element is Quasi point
	if "QUASI" in str(first_elem.Symbol.FamilyName):
		# that is not exception
		return False

	any_tests = any([test_board])

	return any_tests
