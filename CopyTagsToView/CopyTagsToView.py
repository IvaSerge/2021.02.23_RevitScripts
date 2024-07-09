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

def get_tag_info(rvt_tag, elem_to_tag):
	# tag_ref = rvt_tag.GetTaggedReferences()[0]
	tag_ref = Reference(elem_to_tag)
	add_leader = rvt_tag.HasLeader
	tag_mode = Autodesk.Revit.DB.TagMode.TM_ADDBY_CATEGORY
	tag_orientation = rvt_tag.TagOrientation
	ins_pnt = rvt_tag.TagHeadPosition
	return tag_ref, add_leader, tag_mode, tag_orientation, ins_pnt

def get_tag_by_doc_and_tagged_id(_doc, view_name, rvt_elem):
	outlist = []
	elem_in_doc = find_inst_in_other_doc(_doc, rvt_elem)
	view_from = inst_by_cat_strparamvalue(_doc, BuiltInCategory.OST_Views, BuiltInParameter.VIEW_NAME, view_name, False)[0]

	# get tags on view
	tags_on_view = FilteredElementCollector(_doc, view_from.Id).\
		OfCategory(BuiltInCategory.OST_ElectricalFixtureTags).\
		OfClass(IndependentTag).\
		WhereElementIsNotElementType().\
		ToElements()
	for tag in tags_on_view:
		tagged_elems = tag.GetTaggedElementIds()
		check_elements = [i.HostElementId == elem_in_doc.Id for i in tagged_elems]
		if any(check_elements):
			outlist.append(tag)
	return outlist

def find_inst_in_other_doc(_doc, rvt_elem):
	"""
		Fine the instance of the same family and type with the same location in other document
	"""
	elem_symbol_id = rvt_elem.Symbol.Id
	elem_insert_point = rvt_elem.Location.Point
	# filter_instance = FamilyInstanceFilter(_doc, elem_symbol_id)
	filter_box = BoundingBoxContainsPointFilter(elem_insert_point, 0.1)
	# filter_logical_and = LogicalAndFilter(filter_instance, filter_box)
	other_element = FilteredElementCollector(_doc).\
		OfCategory(BuiltInCategory.OST_ElectricalFixtures).\
		WhereElementIsNotElementType().\
		WherePasses(filter_box).\
		FirstElement()
	return other_element


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
	Autodesk.Revit.DB.Element.ChangeTypeId(
		doc, 
		List[ElementId]([rvt_tag.Id]),
		update_info[0])
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

# Get tags from nearest opened doc
documents = uiapp.Application.Documents
view_name = "BER-GF-SE-DU-1F-DR-EF-TSLA-1000-001 - ELECTRICAL FACILITY 1F"
other_doc = [i for i in documents if i.Title != doc.Title][0]
tags_in_other_doc = list()
for rvt_elem in rvt_elems:
	tags_found = get_tag_by_doc_and_tagged_id(other_doc, view_name, rvt_elem)
	if tags_found:
		tags_in_other_doc.extend([[i_tag, rvt_elem] for i_tag in tags_found])
rvt_elems = tags_in_other_doc


list_to_set = []
for elems in rvt_elems:
	rvt_tag = elems[0]
	rvt_elem_to_tag = elems[1]
	new_tag_info = get_tag_info(rvt_tag, rvt_elem_to_tag)
	new_tag_update = get_update_info(rvt_tag)
	new_location = new_tag_info[-1]
	list_to_set.append([new_tag_info, new_tag_update, new_location])

# =========Start transaction
TransactionManager.Instance.EnsureInTransaction(doc)

for info in list_to_set:
	new_tag = create_new_tag(doc, view.Id, info[0])
	updtade_tag(new_tag, info[1], info[2])

# =========End transaction
TransactionManager.Instance.TransactionTaskDone()

OUT = rvt_elems
