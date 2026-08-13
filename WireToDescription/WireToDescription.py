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

# create empty list for electrical systems
circuits_list: List[Electrical.ElectricalSystem] = list()

# Check if selected element is FamilyInstance
if isinstance(rvt_elem, Autodesk.Revit.DB.FamilyInstance):
	# Check if the element is an electrical panel
	# OST_ElectricalEquipment.Id == -2001040
	if rvt_elem.Category.Id == ElementId(-2001040):
		# it is electrical panel - get main circuit using toolsrvt.elsys_by_brd(_brd)[0]
		main_circuit: Optional[Electrical.ElectricalSystem] = toolsrvt.elsys_by_brd(rvt_elem)[0]
		# add the main circuit to circuits_list
		if main_circuit:
			circuits_list.append(main_circuit)
	else:
		# it is another familyInstance
		# check if electrical instance has electrical systems
		mep_model: Optional[MEPModel] = rvt_elem.MEPModel
		if mep_model:
			elem_systems: List[Electrical.ElectricalSystem] = [
				sys for sys in mep_model.GetElectricalSystems()
			]
			# add all systems found to circuits_list
			circuits_list.extend(elem_systems)

OUT = circuits_list
