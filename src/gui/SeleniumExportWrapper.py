#! /usr/bin/env python
#-*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
from generated.ui.SeleniumExport import Ui_SeleniumExport
from format.writer.selenium import selenium
from testcases.highlighter import highlighter
from format.model import TestCases

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class SeleniumExportWrapper(QtGui.QDialog):
	def __init__(self, parent, afefuc):
		super(SeleniumExportWrapper, self).__init__(parent)
		self.parent = parent
		self.form = Ui_SeleniumExport()
		self.afefuc = afefuc
		self.system = None
		self.browser = None
		self.path = None
		self.tc = None
		self.isClosed = False

	def load(self):
		self.form.testCaseComboBox.addItem('All test cases', self.afefuc['project'].testcases)

		for testcase in self.afefuc['project'].testcases.tests:
			self.form.testCaseComboBox.addItem(testcase.title, testcase)

	def show(self):
		self.form.setupUi(self)

		self.load()

		QtCore.QObject.connect(self.form.buttonOK, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.buttonCancel, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedCancelButton)
		QtCore.QObject.connect(self.form.selectPathButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedSelectButton)

		self.exec_()

	def clickedCancelButton(self):
		self.isClosed = True
		self.close()

	def clickedOKButton(self):
		tccb = self.form.testCaseComboBox
		self.tc = tccb.itemData(tccb.currentIndex()).toPyObject()

		bccb = self.form.browserComboBox
		self.browser = bccb.currentText()

		sccb = self.form.systemComboBox
		self.system = sccb.currentText()

		if self.path:
			if len(self.tc) > 0:
				sb = None

				if self.afefuc['project'].language == 'en':
					sb = highlighter('generated/testcases/en.xml')
				else:
					sb = highlighter('generated/testcases/pl.xml')

				s = selenium(sb, self)

				if isinstance(self.tc, TestCases):
					for test in self.tc.tests:
						s.generateCode(test, self.browser, self.system, self.path)
				else:
						s.generateCode(self.tc, self.browser, self.system, self.path)
						
				QtGui.QMessageBox.information(self, 'Message', 'Export finished.', QtGui.QMessageBox.Ok)
			else:
				QtGui.QMessageBox.information(self, 'Message', 'There is nothing to export.', QtGui.QMessageBox.Ok)
		else:
			QtGui.QMessageBox.warning(self, 'Message', 'Directory is not selected.', QtGui.QMessageBox.Ok)

		self.close()
		

	def clickedSelectButton(self):
		path = QtGui.QFileDialog.getExistingDirectory(self, 'Select directory')

		if path:
			self.path = path
			self.form.pathLineEdit.setText(path)

	def closeEvent(self, e):
		if self.isClosed:
			e.accept()
		else:
			e.ignore()