import clr
clr.AddReference('RevitAPI')
import Autodesk
from Autodesk.Revit.DB import *

import sys
pyt_path = r'C:\Program Files (x86)\IronPython 2.7\Lib'
sys.path.append(pyt_path)

import System
from System import Array
from System.Collections.Generic import *

import itertools
import math

clr.AddReference("RevitServices")
import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager
doc = DocumentManager.Instance.CurrentDBDocument
uidoc = DocumentManager.Instance.CurrentUIApplication.ActiveUIDocument

clr.AddReference('RevitAPIUI')
from Autodesk.Revit.UI import *


def SetpParVal(elem, name, pValue):
	global doc
	TransactionManager.Instance.EnsureInTransaction(doc)
	elem.LookupParameter(name).Set(pValue)
	TransactionManager.Instance.TransactionTaskDone()
	return elem


def getNextObj(_startObj):
	global objectList
	global wireIdList
	_outlist = list()
	objectListId = [i.Id for i in objectList]
	#получение провода из стартового объекта
	startObjId = _startObj.Id
	conList = [i for i in _startObj.MEPModel.ConnectorManager.Connectors]
	#Тут надо будет добавить проверку в какой именно сети находится 
	#семейство, а также то, что это электрический коннектор
	#В данный момент проверка упускается - в семействе только один
	#электрический коннектор
	
	
	conRefs = conList[0].AllRefs
	wire = None
	for con in conRefs:
		conOwner = con.Owner
		ownerCategory = conOwner.Category.Id.IntegerValue
		wireCat = -2008039
		#проверка, чтоб был найден новый провод
		if ownerCategory == wireCat and conOwner.Id not in wireIdList:
			wireIdList.append(conOwner.Id)
			wire = conOwner
	
	#получение из провода следующего объетка
	if not (wire):
		return None
	
	wireId = wire.Id
	wireCons = wire.ConnectorManager.Connectors
	allWireRefs = list()
	for con in wireCons:
		map(lambda x: allWireRefs.append(x.Owner), con.AllRefs)
	
	for ref in allWireRefs:
		refId = ref.Id
		isNextElem = (refId != wireId) and (refId != startObjId)
		if isNextElem and refId not in objectListId:
			return ref
	return None

reLoad = IN[0]
#получение начального номера
startNumber = IN[2]

#выбор стартового объекта
startObj = UnwrapElement(IN[1])
# startObj = uidoc.Selection.PickObjects(
		# Autodesk.Revit.UI.Selection.ObjectType.Element,
		# "Selection of start element")



objectList = list()
wireIdList = list()
objectList.append(startObj)

#Поиск следующего объекта. Продолжать до тех пор, пока есть следующий объект.
#Самый первый объект и есть следующий объект.
nextObj = startObj

while nextObj:
	nextObj = getNextObj(nextObj)
	if nextObj:
		objectList.append(nextObj)


#нумерация
numList = [i[0]+startNumber for i in enumerate (objectList)]

#Запись номера в семейство
TransactionManager.Instance.EnsureInTransaction(doc)
for obj, num in zip(objectList, numList):
	SetpParVal(obj, "MC Object Variable 1", str(num))

TransactionManager.Instance.TransactionTaskDone()


OUT = numList