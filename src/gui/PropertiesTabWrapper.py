'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.PropertiesTab import Ui_PropertiesTab

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class PropertiesTabWrapper():
	def __init__(self, parent, afefuc):
		self.parent = parent
		self.child = QtGui.QWidget(self.parent)
		self.tab = Ui_PropertiesTab()
		self.afefuc = afefuc

	def load(self):
		self.tab.projectNameEdit.setText(_fromUtf8(self.afefuc['project'].name))
		self.tab.versionEdit.setText(_fromUtf8(self.afefuc['project'].version))
		self.tab.abbreviationEdit.setText(_fromUtf8(self.afefuc['project'].abbreviation))
		self.tab.problemEdit.setPlainText(_fromUtf8(self.afefuc['project'].problem_description))
		self.tab.systemEdit.setPlainText(_fromUtf8(self.afefuc['project'].system_description))

		index = self.tab.languageComboBox.findText(_fromUtf8(self.afefuc['project'].language))
		if index != -1:
			self.tab.languageComboBox.setCurrentIndex(index);

	def show(self):
		self.tab.setupUi(self.child)
		self.parent.mainWindow.tabWidget.addTab(self.child, _fromUtf8("Properties"))

		self.tab.languageComboBox.addItems(["en", "pl"])
		QtCore.QObject.connect(self.tab.languageComboBox, QtCore.SIGNAL('currentIndexChanged(const QString&)'), self.onLanguageSelect)
		QtCore.QObject.connect(self.tab.projectNameEdit, QtCore.SIGNAL('editingFinished()'), self.onProjectNameEdit)
		QtCore.QObject.connect(self.tab.versionEdit, QtCore.SIGNAL('editingFinished()'), self.onVersionEdit)
		QtCore.QObject.connect(self.tab.abbreviationEdit, QtCore.SIGNAL('editingFinished()'), self.onAbbreviationEdit)

	def onLanguageSelect(self):
		self.afefuc['project'].language = unicode(self.tab.languageComboBox.currentText())

	def onProjectNameEdit(self):
		self.afefuc['project'].name = unicode(self.tab.projectNameEdit.text())

	def onVersionEdit(self):
		self.afefuc['project'].version = unicode(self.tab.versionEdit.text())

	def onAbbreviationEdit(self):
		self.afefuc['project'].abbreviation = unicode(self.tab.abbreviationEdit.text())
