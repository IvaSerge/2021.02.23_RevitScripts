# ================ system imports
import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

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


def setup_param_value(elem, name, pValue):

	# check element staus
	elem_status = WorksharingUtils.GetCheckoutStatus(doc, elem.Id)

	if elem_status == CheckoutStatus.OwnedByOtherUser:
		return None

	# custom parameter
	param = elem.LookupParameter(name)
	# check is it a BuiltIn parameter if not found
	if not(param):
		try:
			param = elem.get_Parameter(get_bip(name)).Set(pValue)
		except:
			pass

	if param:
		try:
			param.Set(pValue)
		except:
			pass
	return elem


def get_bip(paramName):
	builtInParams = System.Enum.GetValues(BuiltInParameter)
	param = []
	for i in builtInParams:
		if i.ToString() == paramName:
			param.append(i)
			return i


def get_sys_by_selection(sel_obj):
		"""
		Get system by selected object
		"""
		el_sys_list = list()
		# get system by selected object

		# check if selection is electrical board
		# OST_ElectricalEquipment.Id == -2001040
		if sel_obj.Category.Id == ElementId(-2001040):
			sys_el = sel_obj.MEPModel.ElectricalSystems
			sys_all = [x.Id for x in sel_obj.MEPModel.AssignedElectricalSystems]
			el_sys_list = [x for x in sys_el if x.Id not in sys_all]
			# filter out electrical circuit only
			el_sys_list = [
				x for x in el_sys_list
				if x.SystemType == Electrical.ElectricalSystemType.PowerCircuit]
		else:
			el_sys_list = [x for x in sel_obj.MEPModel.ElectricalSystems]
		return el_sys_list


def get_circuit_info(_el_circuit, _param_list):
	outlist = list()
	search_list = zip([_el_circuit] * len(_param_list), _param_list)
	found_list = [get_parval(i[0], i[1]) for i in search_list]
	set_list = zip(_param_list, found_list)
	elem_list = [i for i in circuit.Elements]
	for elem in elem_list:
		for info in set_list:
			outlist.append([elem, info[0], info[1]])
	return outlist


doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application

reload = IN[1]  # type: ignore
calc_all = IN[2]  # type: ignore

params_dat = [
	"TO Grid",
	"TO Level",
	"TO Panel",
	"TO Rack",
	"TO Rack Floor",
	"TO Rack Grid"]

if calc_all:
	all_systems = FilteredElementCollector(doc)\
		.OfCategory(BuiltInCategory.OST_ElectricalCircuit)\
		.WhereElementIsNotElementType()\
		.ToElements()
	circuit_list = [sys for sys in all_systems if sys.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.Data]

if not calc_all:
	test_elem = UnwrapElement(IN[3])  # type: ignore
	circuit_list = get_sys_by_selection(test_elem)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for circuit in circuit_list:
	elem_list = get_circuit_info(circuit, params_dat)
	for elem in elem_list:
		setup_param_value(elem[0], elem[1], elem[2])

TransactionManager.Instance.TransactionTaskDone()
# =========End transaction

OUT = circuit_list
