'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.ItemsTabGen import Ui_ItemsTabGen
from gui.TestCaseFormWrapper import TestCaseFormWrapper
from gui.SelectUseCaseFormWrapper import SelectUseCaseFormWrapper

from format import model
from utils import converter
from utils import clone
import re

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class TestCasesTableModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, afefuc):
		QtCore.QAbstractItemModel.__init__(self, parent)
		self.afefuc = afefuc
		self.parent = parent

	def rowCount(self, index):
		return len(self.afefuc['project'].testcases.tests)

		#return 0

	def columnCount(self, parent):
		return 2

	def index(self, row, column, parent):
		if not parent.isValid():
			return self.createIndex(row, column, None)

	def data(self, index, role):
		column = index.column()

		if column == 0 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.afefuc['project'].testcases.tests[index.row()].identifier)
		elif column == 1 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.afefuc['project'].testcases.tests[index.row()].title)

		#if column == 0 and role == QtCore.Qt.DisplayRole:
        #	return QtCore.QVariant(self.afefuc['project'].testcases[index.row()].identifier)
    	#elif column == 1 and role == QtCore.Qt.DisplayRole:
        #	return QtCore.QVariant(converter.itemsToText(self.afefuc['project'].testcases[index.row()].title))


		#return QtCore.QVariant()

	def parent(self, index):
		return QtCore.QModelIndex()

	def removeItem(self, position):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position);
		del(self.afefuc['project'].testcases.tests[position])

		self.endRemoveRows();

		return True;

	def insertItem(self, testcase, position = None):
		self.beginInsertRows(
				QtCore.QModelIndex(),
				self.rowCount(QtCore.QModelIndex()),
				self.rowCount(QtCore.QModelIndex())
		)

		if position is None:
			self.afefuc['project'].testcases.tests.append(testcase[1])
		else:
			self.afefuc['project'].testcases.tests.insert(position, testcase[1])

		self.endInsertRows()

	def updateItem(self, testcase): #testcase = (original,new)
		counter = 0

		#print 'tests len', len(self.afefuc['project'].testcases.tests)

		for i, tc in enumerate(self.afefuc['project'].testcases.tests):
			if tc is testcase[0]:
				counter = i
				self.afefuc['project'].testcases.tests[i] = testcase[1]
				break

		self.emit(QtCore.SIGNAL("dataChanged(index, index)"),
				self.createIndex(counter, 0, None),
				self.createIndex(counter, 1, None)
		)

	def movePositionUp(self, position):
		if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
			return

		pos1 = position
		pos2 = position - 1

		(
			self.afefuc['project'].testcases.tests[pos1],
			self.afefuc['project'].testcases.tests[pos2]
		) = (
			self.afefuc['project'].testcases.tests[pos2],
			self.afefuc['project'].testcases.tests[pos1]
		)
#       (
#               self.afefuc['project'].ucspec.usecases[pos1],
#               self.afefuc['project'].ucspec.usecases[pos2]
#       ) = (
#               self.afefuc['project'].ucspec.usecases[pos2],
#               self.afefuc['project'].ucspec.usecases[pos1]
#       )

		self.emit(QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
				self.createIndex(min(pos1, pos2), 0, None),
				self.createIndex(max(pos1, pos2), 1, None)
		)

class TestCasesTabWrapper():
	def __init__(self, parent, afefuc):
		self.parent = parent

		self.can = QtGui.QWidget(self.parent)
		self.tab = Ui_ItemsTabGen()
		self.numRegEx = re.compile(r'(.*\()(\d+)(\))$')

		self.afefuc = afefuc

	def show(self):
		self.tab.setupUi(self.can)

		self.model = TestCasesTableModel(self.tab.itemsView, self.afefuc)
		self.tab.itemsView.setModel(self.model)
		self.tab.itemsView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.tab.itemsView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.tab.itemsView.horizontalHeader().hide()
		self.tab.itemsView.verticalHeader().hide()
		self.tab.itemsView.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
		self.tab.itemsView.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

		QtCore.QObject.connect(self.tab.generateButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedGenerateButton)
		QtCore.QObject.connect(self.tab.addButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedAddButton)
		QtCore.QObject.connect(self.tab.cloneButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedCloneButton)
		QtCore.QObject.connect(self.tab.deleteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteButton)
		QtCore.QObject.connect(self.tab.editButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedEditButton)
		QtCore.QObject.connect(self.tab.moveUpButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpButton)
		QtCore.QObject.connect(self.tab.moveDownButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownButton)

		self.parent.mainWindow.tabWidget.addTab(self.can, _fromUtf8("Test Cases"))

	def load(self):
		self.model.reset()

	def clickedGenerateButton(self):
		form = SelectUseCaseFormWrapper(self, self.afefuc)
		form.show()

	def clickedAddButton(self):
		tc = model.TestCase()
#       uc.setParent(self.afefuc['project'])
		TestCaseFormWrapper(self, self.afefuc, (None, tc)).show()
		pass

	def clickedCloneButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()
			original = self.afefuc['project'].testcases.tests[position]
			tc = clone.testcase(original, self.afefuc['project'])

			matchTitle = self.numRegEx.match(tc.title)
			if matchTitle:
				n = int(matchTitle.group(2))
				n += 1
			else:
				n = 2
				tc.title = tc.title + ' (2)'
				matchTitle = self.numRegEx.match(tc.title)

			matchIdentifier = self.numRegEx.match(tc.identifier)
			if matchIdentifier:
				m = int(matchIdentifier.group(2))
				m += 1
			else:
				m = 2
				tc.identifier = tc.identifier + ' (2)'
				matchIdentifier = self.numRegEx.match(tc.identifier)

			num = max(n, m)

			ok = False
			while ok is False:
				ok = True
				for test in self.afefuc['project'].testcases.tests:
					newValue = r'\g<1>' + str(num) + r'\g<3>'
					newTitle = self.numRegEx.sub(newValue,tc.title) 
					newIdentifier = self.numRegEx.sub(newValue, tc.identifier)
					if test.title == newTitle or test.identifier == newIdentifier:
						num += 1
						ok = False
						break

			tc.title = self.numRegEx.sub(r'\g<1>' + str(num) + r'\g<3>', tc.title)
			tc.identifier = self.numRegEx.sub(r'\g<1>' + str(num) + r'\g<3>', tc.identifier)

			self.model.insertItem((None,tc), position+1)

	def clickedDeleteButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()
			self.model.removeItem(position)

	def clickedEditButton(self):
		if len(self.tab.itemsView.selectedIndexes()) == 2:
			position = self.tab.itemsView.selectedIndexes()[0].row()
			original = self.afefuc['project'].testcases.tests[position]
			tc = clone.testcase(original, self.afefuc['project'])
			TestCaseFormWrapper(self, self.afefuc, item = (original, tc)).show()

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
