import clr

import sys
# sys.path.append(r"C:\Program Files\Dynamo 0.8")
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

dir_path = IN[0].DirectoryName  # type: ignore
sys.path.append(dir_path)


# ================ Revit imports
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
app = uiapp.Application
view = doc.ActiveView
family_manager = doc.FamilyManager

definition_file = uidoc.Application.Application.OpenSharedParameterFile()
definition_groups = definition_file.Groups

# parameter group, name,BuiltIn Group, is instance
parameters_to_load = [
	["Electrical", "MC Object Variable 1", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "MC Object Variable 2", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "MC CosPhi", BuiltInParameterGroup.PG_ELECTRICAL_LOADS, True],
	["Electrical", "MC Number of Poles", BuiltInParameterGroup.PG_ELECTRICAL_LOADS, False],
	["Electrical", "MC Active Power", BuiltInParameterGroup.PG_ELECTRICAL_LOADS, True],
	["Electrical", "MC Eload Classification", BuiltInParameterGroup.PG_ELECTRICAL_LOADS, True],
	["Electrical", "MC Voltage", BuiltInParameterGroup.PG_ELECTRICAL_LOADS, False],

	["Electrical", "st_devicetag", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_devicetag (NEW)", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_Load Classification", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_FLA", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_neutral", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_Voltage", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_connection_details", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_Number of Poles", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_Apparent Load", BuiltInParameterGroup.PG_TEXT, True],
	["Electrical", "st_Power Factor", BuiltInParameterGroup.PG_TEXT, True],

	["Electrical", "2D_Text", BuiltInParameterGroup.PG_TEXT, False],
	["Electrical", "2D_X", BuiltInParameterGroup.PG_LENGTH, True],
	["Electrical", "2D_Y", BuiltInParameterGroup.PG_LENGTH, True]
]

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)


for param_info in parameters_to_load:
	param_name = param_info[1]
	param_group = param_info[2]
	param_is_instance = param_info[3]
	definition_group = definition_groups.get_Item(param_info[0])
	param_definition = [i for i in definition_group.Definitions if i.Name == param_name][0]
	try:
		family_manager.AddParameter(param_definition, param_group, param_is_instance)
	except Autodesk.Revit.Exceptions.ArgumentException:
		pass

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = parameters_to_load
