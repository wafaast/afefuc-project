#-*- coding: utf-8 -*-

import inspect
import re
import sip
from collections import OrderedDict
from PyQt4 import QtCore, QtGui
from utils import converter
from os import path
from sys import argv, exit
from xml.dom import minidom
from format import model
from testcases.highlighter import highlighter
from generated.ui.TestCaseForm import Ui_TestCaseForm
from testcases.paths.all_paths_algorithm import Algorithm
from SelectActorsFormWrapper import SelectActorsFormWrapper

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s

class CompleteTextEditDelegate(QtGui.QItemDelegate):
	def __init__(self, parent, afefuc, item): #item trzyma informacje o naszym modelu
		QtGui.QItemDelegate.__init__(self, parent)
		self.item = item
		self.afefuc = afefuc

	def createEditor(self, parent, option, index):
		editor = TextEdit(parent, self.afefuc)
		self.completer = QtGui.QCompleter(self)

		if self.afefuc['project'].language == 'en':
			sb = highlighter('generated/testcases/en.xml')
		else:
			sb = highlighter('generated/testcases/pl.xml')

		editor.setHighlighter(sb)
		output = sb.getNext('')
		words = []

		for element in output[1]:
			words.append(element.getValue())

		self.completer.setModel(QtGui.QStringListModel(words, self.completer))
		self.completer.setModelSorting(QtGui.QCompleter.CaseInsensitivelySortedModel)
		self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.completer.setWrapAround(False)
		editor.setCompleter(self.completer)
		
		return editor

	def setEditorData(self, editor, index):	
		step = self.item.path[index.row()].tcstep
		if step is not None:
			editor.setHtml(step)
		else:
			editor.setHtml('')

	def setModelData(self, editor, model, index):
		self.item.path[index.row()].tcstep = editor.toPlainText()

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class ComboBoxDelegate(QtGui.QItemDelegate):
	def __init__(self, parent, item):
		QtGui.QItemDelegate.__init__(self, parent)
		self.item = item

	def paint(self, painter, option, index):
		value = 'No reference to UC step'

		if(len(self.item.path) > index.row()): 
			step = self.item.path[index.row()].ucstep
			if step is not None:
				value = converter.itemsToText(step.items)
		
		style = QtGui.QApplication.style()
		opt = QtGui.QStyleOptionComboBox()
		opt.currentText = value
		opt.rect = option.rect
		opt.state = QtGui.QStyle.State_Active | QtGui.QStyle.State_Enabled;
		style.drawControl(QtGui.QStyle.CE_ComboBoxLabel, opt, painter)

	def createEditor(self, parent, option, index):
		editor = QtGui.QComboBox(parent)

		if self.item.uc_ref is None:
			editor.addItem('No reference to UC step')
		else :
			for step in self.item.uc_ref.scenario.items:

				for element in step.items:
					if isinstance(element, model.GoToCommand):
						for step_goto in element.item.scenario.items:
							editor.addItem('<' + converter.itemsToText(element.item.title) + '>' +  converter.itemsToText(step_goto.items), step_goto)

				editor.addItem(converter.itemsToText(step.items), step)

		return editor

	def setEditorData(self, editor, index):
		step = self.item.path[index.row()].ucstep
		idx = -1 

		if step is not None:
			if step.parent != self.item.uc_ref:
				toFind = '<' + converter.itemsToText(step.parent.title) + '>' +  converter.itemsToText(step.items)
			else:
				toFind = converter.itemsToText(step.items)
			idx = editor.findText(toFind)

		if index != -1:
			editor.setCurrentIndex(idx)

	def setModelData(self, editor, model, index):
		idx = editor.currentIndex()
		value = editor.itemData(idx).toPyObject()
		self.item.path[index.row()].ucstep = value 
		model.setData(index, QtCore.QVariant(value), QtCore.Qt.EditRole)

	def updateEditorGeometry(self, editor, option, index):
		editor.setGeometry(option.rect)

class ScenarioTableModel(QtCore.QAbstractTableModel):
	def __init__(self, parent, afefuc, items):
		QtCore.QAbstractItemModel.__init__(self,parent)
		self.afefuc = afefuc
		self.parent = parent
		self.item = items[1]
		self.item_original = items[0]
		self.headerdata = ["No", "Description", "Ref UC step"]

	def headerData(self, column, orientation, role):
		if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(self.headerdata[column])
		return QtCore.QVariant()

	def rowCount(self, index):
		return len(self.item.path) 

	def columnCount(self, parent):
		return 3

	def index(self, row, column, parent):
		if not parent.isValid():
			return self.createIndex(row, column, None)

	def data(self, index, role):
		column = index.column()
		row = index.row()
		step = self.item.path[row]
		
		if column == 0 and role == QtCore.Qt.DisplayRole:
			return QtCore.QVariant(row + 1)
		elif column == 1 and role in [QtCore.Qt.DisplayRole]:
			step = self.item.path[row].tcstep
			return QtCore.QVariant(step)

	def parent(self, index):
		return QtCore.QModelIndex()

	def flags(self, index):
		flags = super(QtCore.QAbstractTableModel, self).flags(index)

		if(index.column() == 1 or index.column() == 2):
			flags |= QtCore.Qt.ItemIsEditable|QtCore.Qt.ItemIsSelectable
			
		return flags	

	def setData(self, index, value, role):
		if index.isValid() and role == QtCore.Qt.EditRole:
			value = unicode(value.toString().toUtf8(), 'utf-8')
			return True
		return False

	def insertItem(self, item, position = None):
		if position is None:
			first = self.rowCount(QtCore.QModelIndex())
			last = self.rowCount(QtCore.QModelIndex())
		else:
			first = position
			last = first

		self.beginInsertRows(QtCore.QModelIndex(), first, last)
		
		if position is None:
			self.item.path.append(model.TestStep(None, item))
		else:
			self.item.path.insert(position, model.TestStep(None, item))

		self.endInsertRows()

	def removeItem(self, position):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position)
		del(self.item.path[position])
		self.endRemoveRows()
		return True

	def movePositionUp(self, position):
		if position <= 0 or position == self.rowCount(QtCore.QModelIndex()):
			return

		pos1 = position
		pos2 = position - 1

		(
				self.item.path[pos1],\
				self.item.path[pos2] \
		) = (\
				self.item.path[pos2],\
				self.item.path[pos1] \
		)

		self.emit(
				QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"),
				self.createIndex(min(pos1, pos2), 0, None),
				self.createIndex(max(pos1, pos2), 1, None)
		)

	def movePositionDown(self, position):
		self.movePositionUp(position + 1)

class TextEdit(QtGui.QTextEdit):
	def __init__(self, parent=None, afefuc=None):
		super(TextEdit, self).__init__(parent)
		self._completer = None
		self._highlighter = None
		self.afefuc = afefuc

	def setCompleter(self, c):
		if self._completer is not None:
				self._completer.activated.disconnect()

		self._completer = c
		c.setWidget(self)
		c.setCompletionMode(QtGui.QCompleter.PopupCompletion)
		c.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
		c.activated.connect(self.insertCompletion)

	def completer(self):
		return self._completer

	def setHighlighter(self, s):
		self._highlighter = s

	def highlighter(self):
		return self._highlighter

	def textUnderCursor(self):
		tc = self.textCursor()
		tc.select(QtGui.QTextCursor.WordUnderCursor)
		return tc.selectedText()

	def lineUnderCursor(self):
		return self.toPlainText()

	def insertCompletion(self, completion):
		if (self._completer.widget() is not self) or \
			(self.textUnderCursor() == completion):
			return

		sentence = self.lineUnderCursor()

		if re.search(r'\.$', unicode(sentence).strip(' ')) > 0: return

		tc = self.textCursor()
		extra = len(completion) - len(self._completer.completionPrefix())
		tc.movePosition(QtGui.QTextCursor.EndOfWord)

		if completion in ['[url]', '[value]', '[name]']:
			tc.insertText('""')
			tc.movePosition(QtGui.QTextCursor.EndOfWord)
			tc.setPosition(tc.position() - 1)
		elif completion in ['[number]', '[actor]']:
			return
		else:
			tc.insertText(completion[-extra:])

		self.setTextCursor(tc)

	def focusInEvent(self, e):
		if self._completer is not None:
			self._completer.setWidget(self)

		super(TextEdit, self).focusInEvent(e)

	def formatInput(self):
		textInTheBox = self.toPlainText()
		output = self._highlighter.getNext(self.lineUnderCursor())
		oldCursor = self.textCursor().position()
		myCursor = self.textCursor()
		self.setPlainText('')
		self.insertHtml(output[2])

		if len(self.toPlainText()) < oldCursor :
			myCursor.setPosition(len(self.toPlainText()))
		else:
			myCursor.setPosition(oldCursor)

		self.setTextCursor(myCursor)
		
	def keyPressEvent(self, e):
		if self._completer is not None and self._completer.popup().isVisible():
			if e.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab):
				e.ignore()
				return

		modifiers = e.modifiers()
		isShortcut = (modifiers == QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_Space)

		if self._completer is None or not isShortcut:
			super(TextEdit, self).keyPressEvent(e)

		if modifiers == QtCore.Qt.ControlModifier:
			return

		self.formatInput()
		sentence = self.lineUnderCursor()

		if re.search(r'\.$', unicode(sentence).strip(' ')) > 0:
			self._completer.setModel(QtGui.QStringListModel([], self._completer))
			return

		output = self._highlighter.getNext(self.lineUnderCursor())
		words = []

		for element in output[1]:
			words.append(element.getValue())

		if len(words) > 0 and words[0] == '[actor]' and len(self.afefuc['project'].actors) > 0:
			words = []
			for actor in self.afefuc['project'].actors:
				words.append(actor.name)
			
		self._completer.setModel(QtGui.QStringListModel(words, self._completer))
		completionPrefix = self.textUnderCursor()

		if completionPrefix != self._completer.completionPrefix():
			self._completer.setCompletionPrefix(completionPrefix)
			self._completer.popup().setCurrentIndex(self._completer.completionModel().index(0, 0))

		cr = self.cursorRect()
		cr.setWidth(self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width())
		self._completer.complete(cr)

class TestCaseFormWrapper():
	def __init__(self, parent, afefuc, item=None): #item[1] is a testCase object
		self.parent = parent
		self.dialog = QtGui.QDialog()
		self.form = Ui_TestCaseForm()
		self.afefuc = afefuc
		self.item = item[1]
		self.item_original = item[0]

	def load(self):
		self.form.titleEdit.setText(self.item.title)
		self.form.idEdit.setText(self.item.identifier)

		if self.item.uc_ref is not None:
			index = self.form.ucChoice.findText(self.item.uc_ref.identifier)
			if index != -1:
				self.form.ucChoice.setCurrentIndex(index)


	def show(self):
		self.form.setupUi(self.dialog)
		self.form.ucChoice.addItems(["no use case reference"])

		for usecase in self.afefuc['project'].ucspec.usecases:
			self.form.ucChoice.addItem(usecase.identifier, usecase)

		if self.item_original is not None: self.load()

		testIndex = self.form.ucChoice.findText('BC_001')
		self.scrollLayout = QtGui.QFormLayout()
		self.scrollWidget = QtGui.QWidget()
		self.scrollWidget.setLayout(self.scrollLayout)
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)
		QtCore.QObject.connect(self.form.insertStepButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedInsertStepButton)
		QtCore.QObject.connect(self.form.ucChoice, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.choseUseCase)
		QtCore.QObject.connect(self.form.idEdit, QtCore.SIGNAL(_fromUtf8("editingFinished()")), self.editingFinishedIdEdit)
		QtCore.QObject.connect(self.form.titleEdit, QtCore.SIGNAL(_fromUtf8("editingFinished()")), self.editingFinishedTitleEdit)
		QtCore.QObject.connect(self.form.deleteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedDeleteButton)
		QtCore.QObject.connect(self.form.moveUpButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveUpButton)
		QtCore.QObject.connect(self.form.moveDownButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedMoveDownButton)

		self.modelTC = ScenarioTableModel(self.form.stepView, self.afefuc, (self.item_original, self.item))
		self.form.stepView.setModel(self.modelTC)

		self.cted = CompleteTextEditDelegate(self.form.stepView, self.afefuc, self.item)
		self.cbd = ComboBoxDelegate(self.form.stepView, self.item)

		self.form.stepView.setItemDelegateForColumn(1, self.cted) #garbage collector won't cause segfault
		self.form.stepView.setItemDelegateForColumn(2, self.cbd)
		
		self.form.stepView.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
		self.form.stepView.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Stretch)
		self.form.stepView.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Stretch)
		self.form.stepView.setColumnWidth(1, 2)

		self.dialog.exec_()

	def editingFinishedIdEdit(self):
		self.item.identifier = unicode(self.form.idEdit.text().toUtf8(), 'utf-8')

	def editingFinishedTitleEdit(self):
		self.item.title = unicode(self.form.titleEdit.text().toUtf8(), 'utf-8')

	def choseUseCase(self, arg):
		uc = self.form.ucChoice.itemData(arg).toPyObject()
		self.item.uc_ref = uc

		# change of related UC => delete all references to steps in previous UC
		for step in self.item.path:
			step.ucstep = None

	def clickedInsertStepButton(self):
		step = ''

		if len(self.form.stepView.selectedIndexes()) != 0:
			position = self.form.stepView.selectedIndexes()[0].row()
			self.modelTC.insertItem(step, position)
		else:
			self.modelTC.insertItem(step)

	def clickedDeleteButton(self):
		position = self.form.stepView.selectedIndexes()[0].row()
		self.modelTC.removeItem(position)

	def clickedMoveUpButton(self):
		position = self.form.stepView.selectedIndexes()[0].row()
		self.modelTC.movePositionUp(position)

	def clickedMoveDownButton(self):
		position = self.form.stepView.selectedIndexes()[0].row()
		self.modelTC.movePositionDown(position)

	def getTextAttribute(self, node):
		if node.attributes:
			for i in range(node.attributes.length):
				if node.attributes.item(i).name == 'value':
					return node.attributes.item(i).value

	def getCurrentOptions(self, myList):
		toReturn = []
		for elem in myList:
			toReturn.append(elem[0])
		return toReturn

	def get_data(self, model):
		self.currentOptions = self.getCurrentOptions(self.completionInformation)
		model.setStringList(self.currentOptions)
		print self.getCurrentOptions(self.completionInformation)

	def createMenu(self):
		exitAction = QtGui.QAction("Exit", self)
		exitAction.triggered.connect(QtGui.qApp.quit)
		fileMenu = self.menuBar().addMenu("File")
		fileMenu.addAction(exitAction)

	def modelFromFile(self, fileName):
		f = QtCore.QFile(fileName)
		if not f.open(QtCore.QFile.ReadOnly):
			return QtGui.QStringListModel(self.completer)

		QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
		words = []

		while not f.atEnd():
			line = f.readLine().trimmed()
			if line.length() != 0:
				try:
					line = str(line, encoding='ascii')
				except TypeError:
					line = str(line)
				words.append(line)

		QtGui.QApplication.restoreOverrideCursor()
		return QtGui.QStringListModel(words, self.completer)

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		if isinstance(self.item_original, model.TestCase):
			self.parent.model.updateItem((self.item_original, self.item))
		else:
			self.parent.model.insertItem((self.item_original, self.item))

		self.dialog.close()
