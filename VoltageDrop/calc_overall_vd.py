# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import circuit_voltage_drop
from circuit_voltage_drop import calc_circuit_vd

import cable_catalogue
from cable_catalogue import get_cable


def elsys_by_brd(_brd):
	"""Get all systems of electrical board.
		args:
		_brd - electrical board FamilyInstance
		return list(1, 2) where:
		1 - main electrical circuit
		2 - list of connectet low circuits
	"""
	allsys = _brd.MEPModel.ElectricalSystems
	lowsys = _brd.MEPModel.AssignedElectricalSystems
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
	if not(param):
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
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def category_by_bic_name(_bicString):
	global doc
	bicList = System.Enum.GetValues(BuiltInCategory)
	bic = [i for i in bicList if _bicString == i.ToString()][0]
	return Category.GetCategory(doc, bic)  # type: ignore


def get_low_elem(_up_elem):
	"""Get the next lower element of the net"""

	# check what is it
	cat_el_sys = category_by_bic_name("OST_ElectricalCircuit").Id
	cat_brd = category_by_bic_name("OST_ElectricalEquipment").Id

	# it is electrical system
	if _up_elem.Category.Id == cat_el_sys:
		return _up_elem.BaseEquipment

	# it is board
	if _up_elem.Category.Id == cat_brd:
		return elsys_by_brd(_up_elem)[0]

	return None


def get_vd(_el_sys):
	# type: (Autodesk.Revit.DB.Electrical.ElectricalSystem) -> list
	"""Calculate total voltage drop of circuit.

		args:
			_el_sys: electrical system

		return:
			list()
	"""

	low_elem_list = list()
	low_elem_list.append(_el_sys)
	low_elem = _el_sys

	while True:
		low_elem = get_low_elem(low_elem)
		if low_elem:
			low_elem_list.append(low_elem)
		else:
			break
	cat_el_sys = category_by_bic_name("OST_ElectricalCircuit").Id
	low_nets = [i for i in low_elem_list if i.Category.Id == cat_el_sys]

	vd_list = [calc_circuit_vd(i) for i in low_nets]
	# vd_list = [get_cable(i.WireSizeString) for i in low_nets]

	# el_sys_cable_size = _el_sys.WireSizeString
	# cable_info = get_cable(el_sys_cable_size)
	vd_overall = sum(vd_list)

	return low_elem_list, vd_list, vd_overall
