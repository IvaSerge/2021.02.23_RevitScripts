
"""
	All the tags need to be updated to draw dthe diagramm
	Quasi_Connecnors names need to be updated by "Update_subboard_name" script
	"E_Ligth_number" - need to be filled in manualy or by script ???
"""

import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


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

# ================ Python imports
import System
from System import Array
from System.Collections.Generic import *

import importlib
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import diag
reload(diag)
from diag import *


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
Diagramm.view_diagramm = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_Views,
	BuiltInParameter.VIEW_NAME,
	view_name,
	False)[0]

# type to install
Diagramm.type_first = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_NOT_1P",
	True)[0]

Diagramm.type_emergency = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_E01",
	True)[0]

Diagramm.type_exit = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_DetailComponents,
	BuiltInParameter.SYMBOL_NAME_PARAM,
	"2D_diagramm_Exit",
	True)[0]


# find circuits in boards:
circuits = [i for i in toolsrvt.elsys_by_brd(board_inst)[1]
	if i.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]

circuits.sort(key=lambda x: x.StartSlot)
circuits_info_list = list()

elems_in_panel = toolsrvt.inst_by_cat_strparamvalue(
	doc,
	BuiltInCategory.OST_LightingFixtures,
	BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM,
	str(board_inst.Name),
	False)
elems_in_panel_circuit_num = [
	i.get_Parameter(BuiltInParameter.RBS_ELEC_CIRCUIT_PANEL_PARAM).AsString()
	for i in elems_in_panel]
elems_with_circuits = list(zip(elems_in_panel, elems_in_panel_circuit_num))

diagramm_symbols: list[Diagramm] = list()
outlist = list()
row = 0

for circuit_inst in circuits:

	circuit_panel_name = circuit_inst.BaseEquipment.Name
	circuit_num = str(circuit_inst.CircuitNumber)
	circuit_name_str = circuit_panel_name + ": " + circuit_num
	elems_in_circuit = [i[0] for i in elems_with_circuits if i[1] == circuit_name_str]
	
	if not elems_in_circuit:
		continue
	
	# ============= First element
	first_elem = DiagFirst(circuit_inst, 0, row)
	first_elem.rvt_elem = circuit_inst
	diagramm_symbols.append(first_elem)

	# ============= Next elements
	for rvt_elem in elems_in_circuit:
		try:
			column = int(toolsrvt.get_parval(rvt_elem, "E_Light_number"))
		except:
			elem_id = rvt_elem.Id.IntegerValue
			error_string = "Light do not have tag number: " + str(elem_id)
			print(error_string)
			raise ValueError(error_string)
		
		next_elem = Diagramm(rvt_elem, column, row)
		next_elem.params.append(["Panel", circuit_num])
		diagramm_symbols.append(next_elem)
	row += 1


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for diag_symbol in diagramm_symbols:
	diag_symbol.create_elem_on_view()
	diag_symbol.get_params_to_set()
	diag_symbol.set_parameters()

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = [i.params for i in diagramm_symbols]
# OUT = symbols_on_view
