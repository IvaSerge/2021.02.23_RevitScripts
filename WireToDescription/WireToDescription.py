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
	rvt_inst: Autodesk.Revit.DB.FamilyInstance
) -> Optional[List[Electrical.ElectricalSystem]]:
	"""Get electrical systems from a family instance.

	args:
		rvt_inst: Revit FamilyInstance
	return:
		list of ElectricalSystem or None if no systems found
	"""
	# Check if the element is an electrical panel
	# OST_ElectricalEquipment.Id == -2001040
	if rvt_inst.Category.Id == ElementId(-2001040):
		# it is electrical panel - get main circuit
		main_circuit: Optional[Electrical.ElectricalSystem] = toolsrvt.elsys_by_brd(rvt_inst)[0]
		if main_circuit:
			return [main_circuit]
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

circuits_list: Optional[List[Electrical.ElectricalSystem]] = get_system_by_instance(rvt_elem)

# Check if instance has electrical systems
if not circuits_list:
	except_string: str = "Instance do not have electrical systems"
	print(except_string)
	raise ValueError(except_string)

# for every circuit in circuits_list
elec_sys_objects = list()
for circuit in circuits_list:
	elec_sys_object: ElecSys = ElecSys(circuit)
	elec_sys_objects.append(elec_sys_object)
	print(elec_sys_object.wire_string)

OUT = circuits_list
