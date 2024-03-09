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
import elem_getter
reload(elem_getter)

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
elem_to_chnage = UnwrapElement(IN[2])  # type: ignore
elem_change_all = IN[3]  # type: ignore


json_name = IN[4]  # type: ignore
json_file = dir_path + "\\" + json_name

# elems_to_change = list()
elem_new_rvt_type = elem_getter.get_new_type(elem_to_chnage, json_file)
ElementReplacer.doc = doc
ElementReplacer.new_type = elem_new_rvt_type
replacer = ElementReplacer(elem_to_chnage)
replacer.get_element_tags()
replacer.get_parameters()
replacer.get_el_sys()

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

replacer.create_new_instance()
replacer.switch_tags()
replacer.set_parameters()
replacer.assign_el_sys()

# TODO: Remove existing family??? Seems better to remove manualy after checks in model

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = replacer.new_inst
