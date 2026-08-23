import clr
import sys

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ Python imports
from typing import List, Optional
from System import Array
from System.Collections.Generic import *
from importlib import reload

# ================ local imports
import toolsrvt
reload(toolsrvt)
from toolsrvt import *
import elec_sys
reload(elec_sys)
from elec_sys import ElecSys


def get_system_by_instance(
	rvt_inst: Autodesk.Revit.DB.FamilyInstance,
	add_branch_circuits: bool
) -> Optional[List[Electrical.ElectricalSystem]]:
	"""Get electrical systems from a family instance.

	args:
		rvt_inst: Revit FamilyInstance
		add_branch_circuits: bool
	return:
		list of ElectricalSystem or None if no systems found
	"""
	# Check if the element is an electrical panel
	# OST_ElectricalEquipment.Id == -2001040
	if rvt_inst.Category.Id == ElementId(-2001040):
		panel_circuits = list()
		# it is electrical panel - get main circuit
		all_circuits: Optional[Electrical.ElectricalSystem] = toolsrvt.elsys_by_brd(rvt_inst)
		# include main circuit
		if all_circuits[0]:
			panel_circuits.append(all_circuits[0])
		# include branch circuits
		if all_circuits[1] and add_branch_circuits:
			panel_circuits.extend(all_circuits[1])
		if panel_circuits:
			return panel_circuits
		else:
			return None

	# it is another familyInstance
	# check if electrical instance has electrical systems
	mep_model: Optional[MEPModel] = rvt_inst.MEPModel
	if not mep_model:
		return None

	elem_systems: List[Electrical.ElectricalSystem] = [
		sys for sys in mep_model.GetElectricalSystems()
	]
	if elem_systems:
		return elem_systems
	return None


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
rvt_elem = IN[2]  # type: ignore
add_branch_circuits = IN[3]  # type: ignore
overwright_description = IN[4]  # type: ignore
ElecSys.overwright = overwright_description


# Element selection
if rvt_elem:
	rvt_elem = UnwrapElement(rvt_elem)  # type: ignore
else:
	sel_elem = uidoc.Selection.PickObject(
		Autodesk.Revit.UI.Selection.ObjectType.Element,
		"Element selection")
	rvt_elem = doc.GetElement(sel_elem.ElementId)

# Check if selected element is FamilyInstance
if not isinstance(rvt_elem, Autodesk.Revit.DB.FamilyInstance):
	except_string: str = "Element is not family instance: {}".format(rvt_elem.Id)
	print(except_string)
	raise ValueError(except_string)

circuits_list: Optional[List[Electrical.ElectricalSystem]] = get_system_by_instance(
	rvt_elem,
	add_branch_circuits
)

# Check if instance has electrical systems
if not circuits_list:
	except_string: str = "Instance do not have electrical systems"
	print(except_string)
	raise ValueError(except_string)

# filter out circuits that have discription
if not overwright_description:
	filtered_circuits = list()
	for circuit in circuits_list:
		isCircuit = circuit.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit
		isPower = circuit.SystemType == Autodesk.Revit.DB.Electrical.ElectricalSystemType.PowerCircuit
		if all([isCircuit, isPower]):
			cab_description = toolsrvt.get_parval(circuit, "Cable Description")
			isEmpty = any([cab_description is None, cab_description == ""])
		else:
			continue
		if isEmpty:
			filtered_circuits.append(circuit)
else:
	filtered_circuits = circuits_list

# for every circuit in circuits_list
elec_sys_objects = list()
for circuit in filtered_circuits:
	elec_sys_object: ElecSys = ElecSys(circuit)
	elec_sys_objects.append(elec_sys_object)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)
for obj in elec_sys_objects:
	rvt_sys = obj.rvt_sys
	cable_size_string = obj.wire_string
	isEmpty = any([cable_size_string is None, cable_size_string == ""])
	if isEmpty:
		continue
	toolsrvt.setup_param_value(
		rvt_sys,
		"Cable Description",
		cable_size_string
	)
	print(obj.wire_string)
	print(isEmpty)

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = [obj.wire_string for obj in elec_sys_objects], filtered_circuits
# OUT = elec_sys_objects
