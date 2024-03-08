import clr
import os
import sys

# ================ Revit imports
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import *

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *

clr.AddReference("RevitServices")
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

import System
from System import Array
from System.Collections.Generic import *

# ================ local imports
import toolsrvt

import math

class ElementReplacer:
	"""
		Class represents Family instance that will replace existing family instance
	"""

	# class properties
	doc = None
	new_type = None

	def __init__(self, _old_instance):
		self.old_instance: FamilyInstance = _old_instance
		self.new_inst: FamilyInstance = None
		self.tags_list: list[IndependentTag]

	def get_element_tags(self):
		doc: Document = self.doc
		elem_bic = self.old_instance.Category.BuiltInCategory
		tag_collector = FilteredElementCollector(doc).OfClass(IndependentTag).WhereElementIsNotElementType().ToElements()
		target_element_id = self.old_instance.Id

		tags_associated_with_element = []
		for tag in tag_collector:
			tag_hosts_ids = [i.HostElementId for i in tag.GetTaggedElementIds()]
			if target_element_id in tag_hosts_ids:
				tags_associated_with_element.append(tag)
		self.tags_list = tags_associated_with_element


	def create_new_instance(self):
		doc: Document = self.doc
		new_type: FamilyType = self.new_type
		
		# create family instance based on lication point
		ins_pnt = self.old_instance.Location.Point
		# host
		host_lvl_Id = toolsrvt.get_parval(self.old_instance, "INSTANCE_SCHEDULE_ONLY_LEVEL_PARAM")
		rvt_host_lvl = doc.GetElement(host_lvl_Id)

		if not new_type.IsActive:
			new_type.Activate()
			doc.Regenerate()

		family_inst = doc.Create.NewFamilyInstance(
			ins_pnt,
			new_type,
			rvt_host_lvl,
			Structure.StructuralType.NonStructural)

		# set rotation
		old_rotation = self.old_instance.Location.Rotation
		inst_transform = family_inst.GetTotalTransform()
		inst_axes_Z = Line.CreateUnbound(XYZ.Zero, XYZ.BasisZ)
		ElementTransformUtils.RotateElement(doc, family_inst.Id, inst_axes_Z, math.pi / 2)
		family_inst.Location.Point = ins_pnt

		self.new_inst = family_inst
		return family_inst

	def switch_tags(self):
		for tag in self.tags_list:  # Assuming self.tags_list is List[IndependentTag]
			# Remove old reference
			old_ref_list = tag.GetTaggedReferences()
			old_ref = old_ref_list[0]
			tag_visible = tag.IsLeaderVisible(old_ref)
			tag_end_condition = tag.LeaderEndCondition
			if tag_visible:
				tag_elbow = tag.GetLeaderElbow(old_ref)
			else:
				tag_elbow = None

			if tag_end_condition == LeaderEndCondition.Free and tag_visible:
				tag_end = tag.GetLeaderEnd(old_ref)
			else:
				tag_end = None
			tag.RemoveReferences(old_ref_list)
	
			# Add reference
			new_ref = Reference(self.new_inst)
			new_ref_list = [new_ref]
			tag.AddReferences(new_ref_list)
			if tag_elbow:
				tag.SetLeaderElbow(new_ref, tag_elbow)
			if tag_end:
				tag.SetLeaderEnd(new_ref, tag_end)