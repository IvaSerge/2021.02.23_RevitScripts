import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

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


def elsys_by_brd(_brd):
	"""Get all systems of electrical board.
		args:
		_brd - electrical board FamilyInstance
		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.GetElectricalSystems()
	lowsys = _brd.MEPModel.GetAssignedElectricalSystems()

	# filter out non Power circuits
	allsys = [i for i in allsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
	lowsys = [i for i in lowsys
		if i.SystemType == Electrical.ElectricalSystemType.PowerCircuit]

	# board have upper and lower circuits
	if lowsys and allsys:
		lowsysId = [i.Id for i in lowsys]
		mainboardsysLst = [i for i in allsys if i.Id not in lowsysId]
		# board have no main circuit
		if len(mainboardsysLst) == 0:
			mainboardsys = None
		else:
			mainboardsys = mainboardsysLst[0]
		lowsys = [i for i in allsys if i.Id in lowsysId]
		lowsys.sort(key=lambda x: get_parval(x, "RBS_ELEC_CIRCUIT_NUMBER"))
		return mainboardsys, lowsys

	# board have no circuits
	if not allsys and not lowsys:
		return None, None

	# board have only main circuit
	if not lowsys:
		return [i for i in allsys][0], None


def get_parval(elem, name):
	# type: (FamilyInstance, str) -> any
	"""Get parametr value

	args:
		elem - family instance or type
		name - parameter name
	return:
		value - parameter value
	"""

	value = None
	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not param:
		param = elem.get_Parameter(get_bip(name))

	# get paremeter Value if found
	try:
		storeType = param.StorageType
		# value = storeType
		if storeType == StorageType.String:
			value = param.AsString()
		elif storeType == StorageType.Integer:
			value = param.AsDouble()
		elif storeType == StorageType.Double:
			value = param.AsDouble()
		elif storeType == StorageType.ElementId:
			value = param.AsValueString()
	except:
		pass
	return value


def get_bip(paramName):
	builtInParams = [i for i in System.Enum.GetNames(BuiltInParameter)]
	param = None
	for i, i_name in enumerate(builtInParams):
		if i_name == paramName:
			param = System.Enum.GetValues(BuiltInParameter)[i]
			break
	return param


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


def searchInDeep(el_sys, elem_list=list()):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem, list()) -> list()
	"""Check if Quasi elements are in circuit. Return list of elements.
	"""

	# ATTENTION: 2 circuits in Quasi element not allowed
	# ATTENTION: only 1st circuit will be calculated
	elems = getElemInSys(el_sys)

	for elem in elems:
		if elem.Symbol.Family.Name == "QUASI_Connector":
			# get first circuit
			low_sys = elsys_by_brd(elem)[1]
			if low_sys:
				low_sys = low_sys[0]
				searchInDeep(low_sys, elem_list)

		else:
			elem_list.append(elem)

	return elem_list
