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

def get_tag_info(rvt_tag):
	tag_ref = rvt_tag.GetTaggedReferences()[0]
	add_leader = rvt_tag.HasLeader
	tag_mode = Autodesk.Revit.DB.TagMode.TM_ADDBY_CATEGORY
	tag_orientation = rvt_tag.TagOrientation
	ins_pnt = rvt_tag.TagHeadPosition
	return tag_ref, add_leader, tag_mode, tag_orientation, ins_pnt

def get_update_info(rvt_tag):	
	tag_type_id = rvt_tag.GetTypeId()
	tag_ref = rvt_tag.GetTaggedReferences()[0]
	tag_visible = rvt_tag.IsLeaderVisible(tag_ref)
	tag_end_condition = rvt_tag.LeaderEndCondition

	if tag_visible and rvt_tag.HasLeaderElbow(tag_ref):
		tag_elbow = rvt_tag.GetLeaderElbow(tag_ref)
	else:
		tag_elbow = None

	if tag_end_condition == LeaderEndCondition.Free and tag_visible:
		tag_end = rvt_tag.GetLeaderEnd(tag_ref)
	else:
		tag_end = None
	return tag_type_id, tag_visible, tag_end_condition, tag_elbow, tag_end

def create_new_tag(doc, view_to_create, tag_info):
	return Autodesk.Revit.DB.IndependentTag.Create(
		doc,
		view_to_create,
		tag_info[0],
		tag_info[1],
		tag_info[2],
		tag_info[3],
		tag_info[4],
	)

def updtade_tag(rvt_tag, update_info, head_location):
	doc = rvt_tag.Document
	tag_ref = rvt_tag.GetTaggedReferences()[0]
	Autodesk.Revit.DB.Element.ChangeTypeId(doc, List[ElementId]([rvt_tag.Id]), update_info[0])
	rvt_tag.TagHeadPosition = head_location

	rvt_tag.HasLeader = update_info[1]
	rvt_tag.LeaderEndCondition = update_info[2]

	if update_info[3]:
		rvt_tag.SetLeaderElbow(tag_ref, update_info[3])


	if update_info[4]:
		rvt_tag.SetLeaderEnd(tag_ref, update_info[4])

def unwrap(_item):
	if isinstance(_item, list):
		return process_list(unwrap, _item)
	else:
		return [UnwrapElement(_item)]  # type: ignore

# ================ GLOBAL VARIABLES
doc = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument
view = doc.ActiveView
reload_var = IN[1]  # type: ignore
in_elem = IN[2]  # type: ignore

if in_elem:
	rvt_elems = unwrap(in_elem)
else:
	# Get the selection from the active view
	selection = uidoc.Selection
	selected_ids = selection.GetElementIds()
	selected_elements = [doc.GetElement(id) for id in selected_ids]
	rvt_elems = selected_elements

list_to_set = []
for elem in rvt_elems:
	new_tag_info = get_tag_info(elem)
	new_tag_update = get_update_info(elem)
	new_location = new_tag_info[-1]
	list_to_set.append([new_tag_info, new_tag_update, new_location])

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for info in list_to_set:
	new_tag = create_new_tag(doc, view.Id, info[0])
	updtade_tag(new_tag, info[1], info[2])

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = list_to_set
