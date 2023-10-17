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
printer_name = IN[2]  # type: ignore
print_file_path = IN[3] + "\\test.pdf"  # type: ignore
rvt_sheet = IN[4]  # type: ignore
rvt_sheet = UnwrapElement(rvt_sheet)  # type: ignore


# # Element selection
# if rvt_elem:
# 	rvt_elem = UnwrapElement(rvt_elem)  # type: ignore
# else:
# 	sel_elem = uidoc.Selection.PickObject(
# 		Autodesk.Revit.UI.Selection.ObjectType.Element,
# 		"Selection of two elements")

# print_manager = doc.PrintManager

# print_manager.SelectNewPrintDriver(printer_name)
# print_manager.Apply()


# doc, sheet, pRange, printerName, combined, filePath, printSetting


# view_sets = FilteredElementCollector(doc).OfClass(ViewSheetSet)
# for i in view_sets:
# 	if i.Name == "tempSetName":
# 		TransactionManager.Instance.EnsureInTransaction(doc)
# 		doc.Delete(i.Id)
# 		TransactionManager.Instance.ForceCloseTransaction()
# 	else:
# 		continue


print_range = Autodesk.Revit.DB.PrintRange.Select
print_settings = FilteredElementCollector(doc).\
	OfClass(Autodesk.Revit.DB.PrintSetting).ToElements()[1]
print_combine = False


print_manager = doc.PrintManager
print_manager.PrintRange = print_range
print_manager.Apply()

view_set = ViewSet()
view_set.Insert(rvt_sheet)

# make new view set current
view_setting = print_manager.ViewSheetSetting
view_setting.CurrentViewSheetSet.Views = view_set

# set printer
print_manager.SelectNewPrintDriver(printer_name)
print_manager.Apply()

# set combined and print to file
print_manager.CombinedFile = True
print_manager.Apply()
print_manager.PrintToFile = True
print_manager.Apply()
print_manager.PrintToFileName = "C:\\!!!test.pdf"
print_manager.Apply()

print_setup = print_manager.PrintSetup
print_settings = print_setup.CurrentPrintSetting
print_settings = print_settings
print_settings.PageOrientation = PageOrientationType.Landscape
print_manager.Apply()

TransactionManager.Instance.EnsureInTransaction(doc)
view_sets = FilteredElementCollector(doc).OfClass(ViewSheetSet)

for i in view_sets:
	if i.Name == "tempSetName":
		doc.Delete(i.Id)

view_setting.SaveAs("tempSetName")
print_manager.Apply()
print_manager.SubmitPrint()
view_setting.Delete()
TransactionManager.Instance.TransactionTaskDone()

OUT = view_setting.CurrentViewSheetSet.Views
