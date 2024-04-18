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
import light_symbol
reload(light_symbol)
from light_symbol import *


# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
view_name = IN[2]  # type: ignore
rvt_panel = UnwrapElement(IN[3])  # type: ignore
LightSymbol.start_point = XYZ(0, 0, 0)
LightSymbol.get_symbols_types(doc)
symbols_to_install: list[LightSymbol] = []

# get view
view_diagramm = inst_by_cat_strparamvalue(
	doc, 
	BuiltInCategory.OST_Views,
	BuiltInParameter.VIEW_NAME,
	view_name,
	False)[0]

# get circuits of the panel
circuits = [i for i in elsys_by_brd(rvt_panel)[1]
	if i.CircuitType == Autodesk.Revit.DB.Electrical.CircuitType.Circuit]

# test circuit is 48
# start point to be changed by -y*i
LightSymbol.current_column = 0
LightSymbol.current_row = 0
rvt_circuit = [i for i in circuits if i.StartSlot == 48][0]
first_elem = LightSymbol.get_first_symbol(rvt_circuit)
symbols_to_install.append(first_elem)


# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for elem_2D in symbols_to_install:
	elem_2D.create_2D(view_diagramm)
	# elem_2D.set_parameters()

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()


# for circuit get all elements
# sort elements by distance along circuit path
# find quasi panels
# calculate insert points for elements
# calculate length
# read parameters
# create 2D symbols
# insert parameters to 2D

OUT = [i.inst_2D for i in symbols_to_install]
