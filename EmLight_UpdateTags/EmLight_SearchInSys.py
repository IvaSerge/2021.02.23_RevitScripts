import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

clr.AddReferenceByName('Microsoft.Office.Interop.Excel, Version=11.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c')
from Microsoft.Office.Interop import Excel  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

System.Threading.Thread.CurrentThread.CurrentCulture = System.Globalization.CultureInfo("en-US")
from System.Runtime.InteropServices import Marshal

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

# ================ Python imports
import operator
from operator import itemgetter, attrgetter


def sort_list_by_point(start_point, point_list, elems):
	list_len = len(point_list)
	start_pnt_list = [start_point] * list_len
	calc_dist = zip(point_list, start_pnt_list)
	sort_dist = [x[0].DistanceTo(x[1]) for x in calc_dist]
	sort_list = zip(elems, sort_dist)
	return [x[0] for x in sorted(sort_list, key=itemgetter(1))]


def getElemInSys(el_sys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list()
	"""Get elements is circuit and all Quasi boards
	"""
	elems = [i for i in el_sys.Elements]
	if len(elems) == 1:
		return elems

	# sort elems by location
	start_point = el_sys.BaseEquipment.Location.Point
	point_list = [i.Location.Point for i in elems]
	sorted_elems = sort_list_by_point(start_point, point_list, elems)
	return sorted_elems


def searchInDeep(el_sys):
		# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list()
	"""Check if Quasi elements are in circuit.
	Return list of elements in Quasi element
	"""
	pass
