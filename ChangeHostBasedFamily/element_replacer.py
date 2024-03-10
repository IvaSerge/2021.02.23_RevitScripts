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

	def __init__(self, _old_instance):
		self.old_instance: FamilyInstance = _old_instance
		self.new_type: FamilyType = None
		self.new_inst: FamilyInstance = None
		self.tags_list: list[IndependentTag]
		self.param_list = []
		self.el_sys: Electrical.ElectricalSystem = None

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
		doc.Regenerate()

		# set rotation
		old_rotation = self.old_instance.Location.Rotation
		# inst_transform = family_inst.GetTotalTransform()
		inst_axes_Z = Line.CreateUnbound(XYZ.Zero, XYZ.BasisZ)
		ElementTransformUtils.RotateElement(doc, family_inst.Id, inst_axes_Z, float(old_rotation))
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
			try:
				tag_elbow = tag.GetLeaderElbow(old_ref)
			except:
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

	def get_parameters(self):
		# chec if readonly and value exists
		param_list = []
		old_inst = self.old_instance
		for param in old_inst.GetOrderedParameters():
			p_has_value = param.HasValue
			p_read_only = param.IsReadOnly
			p_modifiable = param.UserModifiable
			is_valid = all([p_has_value, not(p_read_only), p_modifiable])
			if is_valid:
				p_name = param.Definition.Name
				p_value = toolsrvt.get_parval(old_inst, p_name)
				if p_value:
					param_list.append([p_name, p_value])
		self.param_list = param_list

	def set_parameters(self):
		new_inst = self.new_inst
		param_list = self.param_list
		for param in param_list:
			p_name = param[0]
			p_value = param[1]
			try:
				toolsrvt.setup_param_value(new_inst, p_name, p_value)
			except:
				continue
		# set phase
		new_inst.CreatedPhaseId = self.old_instance.CreatedPhaseId

		# there is no Workset in standalone model.
		workset_id = toolsrvt.get_parval(self.old_instance, "ELEM_PARTITION_PARAM")
		# if workset_id:
		toolsrvt.setup_param_value(new_inst, "ELEM_PARTITION_PARAM", int(workset_id))

	def get_el_sys(self):
		old_inst = self.old_instance
		old_elsystems = old_inst.MEPModel.GetElectricalSystems()
		if old_elsystems:
			first_sys = [i for i in old_elsystems][0]
		else:
			return None
		self.el_sys = first_sys


	def assign_el_sys(self):
		new_inst = self.new_inst
		el_sys = self.el_sys
		if not el_sys:
			return None

		connectors = new_inst.MEPModel.ConnectorManager.UnusedConnectors
		con = next(iter(connectors))
		con_set = List[Connector]([con])
		el_sys.Add(connectors)

		return con_set
