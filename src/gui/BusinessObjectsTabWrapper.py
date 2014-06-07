'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from format import model
from generated.ui.ItemsTab import Ui_ItemsTab
from gui.BusinessObjectFormWrapper import BusinessObjectFormWrapper
from utils import converter
from utils import clone
from utils import update

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class BusinessObjectsTableModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, afefuc):
		QtCore.QAbstractItemModel.__init__(self, parent)
		self.afefuc = afefuc
		self.parent = parent

	def rowCount(self, index):
		return len(self.afefuc['project'].business_objects)

	def columnCount(self, parent):
		return 2

	def index(self, row, column, parent):
		if not parent.isValid():
			return self.createIndex(row, column, None)

	def data(self, index, role):
		column = index.column()

		if column == 0 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.afefuc['project'].business_objects[index.row()].identifier)
		elif column == 1 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(
					converter.itemsToText(
							self.afefuc['project'].business_objects[index.row()].name,
							edit = False
					)
			)

	def parent(self, index):
		return QtCore.QModelIndex()

	def removeItem(self, position):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position);

		del(self.afefuc['project'].business_objects[position])

		self.endRemoveRows();

		return True;

	def updateItem(self, item):
		counter = 0

		for i, uc in enumerate(self.afefuc['project'].business_objects):
			if uc is item[0]:
				counter = i
				#self.afefuc['project'].business_objects[i] = item[1]

				update.business_object(self.afefuc['project'].business_objects[i], item[1])
				break
		else:
			assert 1 == 2 and "actor not found"

		self.emit(QtCore.SIGNAL("dataChanged(index, index)"),
				self.createIndex(counter, 0, None),
				self.createIndex(counter, 1, None)
		)

	def insertItem(self, item):
		self.beginInsertRows(
				QtCore.QModelIndex(),
				self.rowCount(QtCore.QModelIndex()),
				self.rowCount(QtCore.QModelIndex())
		)

		self.afefuc['project'].business_objects.append(item[1])

		self.endInsertRows()

	def movePositionUp(self, position):
		if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
			return

		pos1 = position
		pos2 = position - 1

		(
				self.afefuc['project'].business_objects[pos1],
				self.afefuc['project'].business_objects[pos2]
		) = (
				self.afefuc['project'].business_objects[pos2],
				self.afefuc['project'].business_objects[pos1]
		)

		self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
				self.createIndex(min(pos1, pos2), 0, None),
				self.createIndex(max(pos1, pos2), 1, None)
		)

class BusinessObjectsTabWrapper():
	def __init__(self, parent, afefuc):
		self.parent = parent

		self.can = QtGui.QWidget(self.parent)
		self.tab = Ui_ItemsTab()

		self.afefuc = afefuc

	def show(self):
		self.tab.setupUi(self.can)

		self.model = BusinessObjectsTableModel(self.tab.itemsView, self.afefuc)
		self.tab.itemsView.setModel(self.model)
		self.tab.itemsView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.tab.itemsView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.tab.itemsView.horizontalHeader().hide()
		self.tab.itemsView.verticalHeader().hide()
		self.tab.itemsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.tab.itemsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		QtCore.QObject.connect(self.tab.addButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedAddButton)
		QtCore.QObject.connect(self.tab.deleteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteButton)
		QtCore.QObject.connect(self.tab.editButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedEditButton)
		QtCore.QObject.connect(self.tab.moveUpButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpButton)
		QtCore.QObject.connect(self.tab.moveDownButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownButton)

		self.parent.mainWindow.tabWidget.addTab(self.can, _fromUtf8("Business Objects"))

	def load(self):
		self.model.reset()

	def clickedAddButton(self):
		form = BusinessObjectFormWrapper(self, self.afefuc, (None, model.BusinessObject()))
		form.show()

	def clickedDeleteButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()

			self.model.removeItem(position)

	def clickedEditButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()

			original = self.afefuc['project'].business_objects[position]
			bo = clone.business_object(original, self.afefuc['project'])

			BusinessObjectFormWrapper(self, self.afefuc, (original, bo)).show()

	def clickedMoveUpButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()

			self.model.movePositionUp(position)
			self.tab.itemsView.selectRow(position - 1)

	def clickedMoveDownButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()

			self.model.movePositionUp(position + 1)
			self.tab.itemsView.selectRow(position + 1)
