import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)
sys.path.append(IN[0].DirectoryName)  # type: ignore

import System
from System import Array
from System.Collections.Generic import *

# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager


doc = DocumentManager.Instance.CurrentDBDocument
reload = IN[1]  # type: ignore
board_from = UnwrapElement(IN[2])  # type: ignore
board_to = UnwrapElement(IN[3])  # type: ignore
row_start = IN[4]  # type: ignore
row_end = IN[5]  # type: ignore

# get PanelScheduleView if no view found Raise Value error
board_schedule = [x for x in FilteredElementCollector(doc).
	OfClass(Autodesk.Revit.DB.Electrical.PanelScheduleView).
	ToElements()
	if x.TargetId == board_from.Id]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView
if board_schedule:
	board_schedule = board_schedule[0]  # type: Autodesk.Revit.DB.Electrical.PanelScheduleView
else:
	raise ValueError("No Scheudle found")

range_of_rows = range(row_start, row_end + 1)
systems_from_schedule = [board_schedule.GetCircuitByCell(i, 1)
	for i in range_of_rows
	if board_schedule.GetCircuitByCell(i, 1)]  # type: list[Autodesk.Revit.DB.Electrical.ElectricalSystem]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for el_sys in systems_from_schedule:
	el_sys.SelectPanel(board_to)
	doc.Regenerate()

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = systems_from_schedule
