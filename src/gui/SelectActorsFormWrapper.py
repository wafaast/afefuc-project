'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.SelectForm import Ui_SelectForm
#from format import model
#from utils import converter

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class SelectActorsTableModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, project, item, target, unselectable):
		QtCore.QAbstractItemModel.__init__(self, parent)
		self.project = project
		self.parent = parent
		#self.item = item
		self.target = target
		self.unselectable = []

		unselectable = [a.item for a in unselectable]

		for i, a in enumerate(project.actors):
			if a in unselectable:
				self.unselectable.append(i)

	def rowCount(self, index):
		return len(self.project.actors)

	def columnCount(self, parent):
		return 2

	def index(self, row, column, parent):
		if not parent.isValid():
			return self.createIndex(row, column, None)

	def data(self, index, role):
		column = index.column()

		if column == 0 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.project.actors[index.row()].identifier)
		elif column == 1 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.project.actors[index.row()].name)

	def flags(self, index):
		flags = super(QtCore.QAbstractTableModel, self).flags(index)

		if index.row() in self.unselectable:
			flags = QtCore.Qt.NoItemFlags

		return flags

	def parent(self, index):
		return QtCore.QModelIndex()

class SelectActorsFormWrapper():
	def __init__(self, parent, project, item, target, unselectable, single):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_SelectForm()
		self.project = project
		self.item = None #item
		self.target = target
		self.unselectable = unselectable
		self.single = single

	def load(self):
		toSelect = [i.item for i in self.target]
		tmp = self.form.itemsView.selectionModel()

		for i, a in enumerate(self.project.actors):
			if a in toSelect:
				tmp.select(
						self.model.createIndex(i, 0, None),
						QtGui.QItemSelectionModel.Select | QtGui.QItemSelectionModel.Rows
				)

	def show(self):
		self.form.setupUi(self.dialog)

		self.model = SelectActorsTableModel(self.form.itemsView, self.project, self.item, self.target, self.unselectable)
		self.form.itemsView.setModel(self.model)
		self.form.itemsView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.form.itemsView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.form.itemsView.horizontalHeader().hide()
		self.form.itemsView.verticalHeader().hide()
		self.form.itemsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

		if self.single:
			self.form.itemsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.load()

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		indexes = set([i.row() for i in self.form.itemsView.selectedIndexes()])

		while len(self.target): del self.target[0] # ???

		for i in indexes:
			self.target.append(self.project.actors[i].get_ref())

		self.dialog.close()
