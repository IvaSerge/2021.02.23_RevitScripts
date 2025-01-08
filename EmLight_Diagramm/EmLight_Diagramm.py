
"""
	All the tags need to be updated to draw dthe diagramm
	Quasi_Connecnors names need to be updated by "Update_subboard_name" script
	"E_Ligth_number" - need to be filled in manualy or by script ???
"""

from re import X
from this import d
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

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ python imports
import importlib
from importlib import reload
from operator import itemgetter
import re

# ================ local imports
import toolsrvt
reload(toolsrvt)
import diag
reload(diag)
from diag import Diagramm

def getByCatAndStrParam(_bic, _bip, _val, _isType):
	global doc
	if _isType:
		fnrvStr = FilterStringEquals()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsElementType().\
			WherePasses(filter).\
			ToElements()
	else:
		fnrvStr = FilterStringContains()
		pvp = ParameterValueProvider(ElementId(int(_bip)))
		frule = FilterStringRule(pvp, fnrvStr, _val)
		filter = ElementParameterFilter(frule)
		elem = FilteredElementCollector(doc).\
			OfCategory(_bic).\
			WhereElementIsNotElementType().\
			WherePasses(filter).\
			ToElements()
	return elem


global doc
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

Diagramm.doc = doc

board_inst = UnwrapElement(IN[3])  # type: ignore

# select view for diagramm
view_name = IN[2]  # type: ignore
Diagramm.view_diagramm = getByCatAndStrParam(
	BuiltInCategory.OST_Views,
	BuiltInParameter.VIEW_NAME,
	view_name,
	False)[0]

# type to install
Diagramm.type_first = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_NOT_1P",
	True)[0]

Diagramm.type_emergency = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_E01",
	True)[0]

Diagramm.type_exit = getByCatAndStrParam(
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_Exit",
	True)[0]


# for circuit in boards:
circuits = [i for i in toolsrvt.elsys_by_brd(board_inst)[1]
	if i.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]


circuits.sort(key=lambda x: x.StartSlot)

# circuits_info_list = list()

elems_in_panel = getByCatAndStrParam(
	BuiltInCategory.OST_LightingFixtures,
	BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM,
	str(board_inst.Name),
	False)

# for circuit_inst in circuits:
	# get diagramm

	# circuit_num = circuit_inst.CircuitNumber
	# circuit_usv_link = circuit_number_to_usv_link(circuit_num)

# 	circuit_str = board_inst.Name + ":" + circuit_usv_link
# 	circuit_name = circuit_inst.LoadName
# 	circuit_wire_size = circuit_inst.WireSizeString
# 	circuit_wire_type = circuit_inst.WireType.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()

# 	if "#2.5" in circuit_wire_size and "NYM" in circuit_wire_type:
# 		circuit_wire_str = "NYM 3x2.5"
# 	elif "#2.5" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
# 		circuit_wire_str = "NHXH E30 3x2.5"
# 	elif "4" in circuit_wire_size and "NYM" in circuit_wire_type:
# 		circuit_wire_str = "NYM 3x4"
# 	elif "4" in circuit_wire_size and "NHXH E30" in circuit_wire_type:
# 		circuit_wire_str = "NHXH E30 3x4"
# 	else:
# 		circuit_wire_str = ""
	
# 	elems_in_circuit = [i for i in elems_in_panel if
# 		i.get_Parameter(
# 			BuiltInParameter.RBS_ELEC_CIRCUIT_NUMBER).AsString() == str(circuit_num)]
	

# 	if not elems_in_circuit:
# 		continue

# 	# read element parameters
# 	params_to_set = list()
# 	for elem in elems_in_circuit:
# 		elem_mark = get_parval(elem.Symbol, "WINDOW_TYPE_ID")  # Revit parameter "Type Mark"
# 		elem_light_num = get_parval(elem, "E_Light_number")
# 		param_list = list()
# 		param_list.append(elem_mark)
# 		param_list.append(circuit_usv_link)
# 		param_list.append(int(elem_light_num))
# 		param_list.append(circuit_name)
# 		param_list.append(circuit_wire_str)
# 		params_to_set.append(param_list)

# 	params_to_set.sort(key=itemgetter(2))
# 	circuits_info_list.append(params_to_set)


# # =========Start transaction
# TransactionManager.Instance.EnsureInTransaction(doc)

# instances_on_view = list()
# for pnt_y, params_to_set in enumerate(circuits_info_list):

# 	# insert 2D on drawing, add parameters
# 	# insert first element
# 	# Start point
# 	instance_on_view = None

# 	if params_to_set:
# 		insert_pnt = XYZ(0, -(pnt_y + 1) * mm_to_ft(2000), 0)
# 		instance_on_view = doc.Create.NewFamilyInstance(
# 			insert_pnt,
# 			type_first,
# 			view_diagramm)
# 		instance_on_view.LookupParameter("Beschriftung 1").Set(params_to_set[0][3])
# 		instance_on_view.LookupParameter("Beschriftung 2").Set(params_to_set[0][4])
# 		instances_on_view.append(instance_on_view)

# 	for pnt_x, info in enumerate(params_to_set):
# 		insert_pnt = XYZ((pnt_x + 2) * mm_to_ft(1000), -(pnt_y + 1) * mm_to_ft(2000), 0)

# 		if any(["03" in info[0], "04" in info[0], "06" in info[0]]):
# 			symbol_type = type_exit
# 		else:
# 			symbol_type = type_emergency

# 		instance_on_view = doc.Create.NewFamilyInstance(
# 			insert_pnt,
# 			symbol_type,
# 			view_diagramm)

# 		# set parameters to new instance
# 		setup_param_value(instance_on_view, "Type Mark", info[0])
# 		setup_param_value(instance_on_view, "Panel", info[1])
# 		setup_param_value(instance_on_view, "E_Light_number", str(info[2]))

# 		instances_on_view.append(instance_on_view)

# # =========End transaction
# TransactionManager.Instance.TransactionTaskDone()

# OUT = circuits_info_list
OUT = Diagramm.type

