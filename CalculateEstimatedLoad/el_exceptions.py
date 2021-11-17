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


def test_exceptions(_elSys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> bool
	"""Analise of electrical system if it is an "excepgion" """
	el_sys_elements = [i for i in _elSys.Elements]  # type: list[Autodesk.Revit.DB.FamilyInstance]
	first_elem = el_sys_elements[0]  # type: Autodesk.Revit.DB.FamilyInstance

	# The fisrst element of the system is electrical board and
	# board name begins with CP1
	test_board_CP1 = str(first_elem.Name).startswith("CP1")

	# if the first element of the circuit type contains "ELECTRICAL_RCPT"
	test_RCPT = "ELECTRICAL_RCPT" in str(first_elem.Name)

	any_tests = any([
		test_board_CP1,
		test_RCPT])

	return any_tests
