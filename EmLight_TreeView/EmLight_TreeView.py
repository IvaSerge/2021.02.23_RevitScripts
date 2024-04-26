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
import elsys_extend
reload(elsys_extend)

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
view_name = IN[2]  # type: ignore
rvt_panel = UnwrapElement(IN[3])  # type: ignore
circuit_number = IN[4]  # type: ignore
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
rvt_circuit = [i for i in circuits if i.StartSlot == circuit_number][0]

# start point to be changed by -y*i
LightSymbol.current_column = 0
LightSymbol.current_row = 0
LightSymbol.circuit_symbols = []
circuit_number = rvt_circuit.StartSlot
number_usv = elsys_extend.circuit_number_to_usv_link(circuit_number)
LightSymbol.circuit_usv_number = number_usv
symbol_first = LightSymbol.get_first_symbol(rvt_circuit)

# it is mandatory that first circuit contains only one main junction box.
# Main junction box to contain only 1 main circuit
main_junction_box = [i for i in rvt_circuit.Elements][0]
main_circuit = elsys_by_brd(main_junction_box)[1][0]
circuit_elements = LightSymbol.get_all_symbols_by_circuit(main_circuit, [2,0])
symbols_to_install.append(symbol_first)
symbols_to_install.extend(LightSymbol.circuit_symbols)

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for elem_2D in symbols_to_install:
	elem_2D.create_2D(view_diagramm)
	elem_2D.set_parameters()

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

# read parameters

OUT = [[i.type_2D, i.insert_point] for i in symbols_to_install]
