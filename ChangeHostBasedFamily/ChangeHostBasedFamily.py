"""
The script changes host based family to level (not host based).
It involves copying various parameters, including level and workset,
from the source family to the new family.
After the script is executed, the source family will be removed.
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
import element_replacer
reload(element_replacer)
from element_replacer import ElementReplacer

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
elem_to_chnage = UnwrapElement(IN[2])  # type: ignore
elem_change_all = IN[3]  # type: ignore


# TODO: To make script user friendly - add info by element selection
elem_new_family_name = IN[4]  # type: ignore
elem_new_type_name = IN[5]  # type: ignore

fnrvStr = FilterStringEquals()

pvpType = ParameterValueProvider(ElementId(int(BuiltInParameter.SYMBOL_NAME_PARAM)))
pvpFam = ParameterValueProvider(ElementId(int(BuiltInParameter.ALL_MODEL_FAMILY_NAME)))

fruleF = FilterStringRule(pvpFam, fnrvStr, elem_new_family_name)
filterF = ElementParameterFilter(fruleF)

fruleT = FilterStringRule(pvpType, fnrvStr, elem_new_type_name)
filterT = ElementParameterFilter(fruleT)

filter = LogicalAndFilter(filterT, filterF)

elem_new_rvt_type = FilteredElementCollector(doc).\
	WhereElementIsElementType().\
	WherePasses(filter).\
	FirstElement()

# elems_to_change = list()
ElementReplacer.doc = doc
ElementReplacer.new_type = elem_new_rvt_type
replacer = ElementReplacer(elem_to_chnage)

# TODO: Get instance parameters to be set
# TODO: Get workset and phase to be set
# TODO: Find electrical circuit, that element to be connected
# TODO: get existing tags

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

replacer.create_new_instance()
# TODO: Set parameters
# TODO: Assign electrical circuit
# TODO: Set workset and phase
# TODO: Change reference of existing tags
# TODO: Remove existing family

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = replacer.new_inst
