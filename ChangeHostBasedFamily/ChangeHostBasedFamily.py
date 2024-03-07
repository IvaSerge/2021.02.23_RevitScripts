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


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
elem_to_chnage = IN[2]  # type: ignore
elem_change_all = IN[3]  # type: ignore
elem_new_type = IN[4]  # type: ignore



# TODO: Get location point and rotation
# TODO: Get instance parameters to be set
# TODO: Get workset and phase to be set
# TODO: Find electrical circuit, that element to be connected

# TODO: Create new Family Instance
# TODO: Set geometry transforms
# TODO: Set parameters
# TODO: Assign electrical circuit
# TODO: Set workset and phase
# TODO: Remove existing family

OUT = None
