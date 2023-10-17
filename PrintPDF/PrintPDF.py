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
import print_view
reload(print_view)
from print_view import PrintView


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
printer_name = IN[2]  # type: ignore
print_file_path = IN[3] + "\\test.pdf"  # type: ignore
rvt_sheet = IN[4]  # type: ignore


# TODO: provide some tools to create filtered list of views
test_sheet = UnwrapElement(rvt_sheet)  # type: ignore

sheets_list = list()
sheets_list.append(test_sheet)

# TransactionManager.Instance.EnsureInTransaction(doc)

# view_sets = FilteredElementCollector(doc).OfClass(ViewSheetSet)
# for i in view_sets:
# 	if i.Name == "tempSetName":
# 		doc.Delete(i.Id)

# for rvt_sheet in sheets_list:
# 	PrintView.print_view(rvt_sheet, printer_name)

# TransactionManager.Instance.TransactionTaskDone()

OUT = PrintView.get_sheet_name(test_sheet)
