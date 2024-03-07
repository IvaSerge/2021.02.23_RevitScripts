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

# ================ local imports
import toolsrvt
import boq_analyze

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