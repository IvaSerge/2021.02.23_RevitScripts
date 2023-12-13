"""
Script copies parameter values from family to other family or list of families.
Families may be selected inside Dynamo or using API.
"""
import clr
import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from System import Array
from System.Collections.Generic import *
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *


def get_par_val_by_list(elem, param_list):
	values = list()
	for param in param_list:
		try:
			param_value = toolsrvt.get_parval(elem, param)
			if param_value is not None:
				values.append([param, param_value])
		except:
			pass
	return values


def get_electrical_circuits(elems_list):
	out_circuits = list()
	for elem in elems_list:
		if elem.Category.Id.IntegerValue == -2001040:
			main_circuit = toolsrvt.elsys_by_brd(elem)[0]
			out_circuits.append(main_circuit)
		else:
			try:
				mep_model = elem.MEPModel
			except:
				continue
			elem_circuits = [
				i for i in mep_model.GetElectricalSystems()
				if elem.MEPModel]
			out_circuits.extend(elem_circuits)
	return out_circuits


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView

# =============== IN Block
reload_var = IN[1]  # type: ignore
copy_from = UnwrapElement(IN[2])  # type: ignore
copy_to = IN[3]  # type: ignore
settings_worksets = IN[4]  # type: ignore
settings_parameters = IN[5]  # type: ignore
params_to_set = list()

# Check selection in Dynamo
if copy_to:
	if not isinstance(copy_to, list):
		copy_to = [copy_to]
	elems_list = [UnwrapElement(i) for i in copy_to]  # type: ignore

# Propose selection via Revit API
else:
	rvt_ref = uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element, "")
	elems_list = [doc.GetElement(rvt_ref.ElementId)]

# apply wokrset
if settings_worksets[0]:
	params_to_set.append("ELEM_PARTITION_PARAM")
# apply phase
if settings_worksets[1]:
	params_to_set.append("PHASE_CREATED")

# Copy parameters to circuit
if settings_worksets[2]:
	el_circuits = get_electrical_circuits(elems_list)
	elems_list.extend(el_circuits)

params_to_set.extend(settings_parameters)
param_values = get_par_val_by_list(copy_from, params_to_set)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

# set parameter values
for elem in elems_list:
	for param in param_values:
		p_name = param[0]
		p_value = param[1]
		try:
			toolsrvt.setup_param_value(elem, p_name, p_value)
		except:
			pass

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# OUT = param_values
OUT = elems_list
