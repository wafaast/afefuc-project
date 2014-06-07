'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from collections import OrderedDict
from PyQt4 import QtCore, QtGui
from generated.ui.BusinessRuleForm import Ui_BusinessRuleForm
from format import model
from utils import validation
from utils import converter

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class BusinessRuleFormWrapper():
	def __init__(self, parent, afefuc, item = None):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_BusinessRuleForm()
		self.afefuc = afefuc
		self.item = item[1]
		self.item_orginal = item[0]

		self.typeOptions = OrderedDict()
		self.typeOptions[model.BusinessRuleType.NA]              = "N/A"
		self.typeOptions[model.BusinessRuleType.FACTS]           = "Facts"
		self.typeOptions[model.BusinessRuleType.CONSTRAINTS]     = "Constraints"
		self.typeOptions[model.BusinessRuleType.ACTION_ENABLERS] = "Action Enablers"
		self.typeOptions[model.BusinessRuleType.COMPUTATIONS]    = "Computations"
		self.typeOptions[model.BusinessRuleType.INTERFACES]      = "Interfaces"

		self.dynamisOptions = OrderedDict()
		self.dynamisOptions[model.BusinessRuleDynamism.NA]      = "N/A"
		self.dynamisOptions[model.BusinessRuleDynamism.STATIC]  = "Static"
		self.dynamisOptions[model.BusinessRuleDynamism.DYNAMIC] = "Dynamic"

	def load(self):
		self.form.idEdit.setText(_fromUtf8(self.item.identifier))

		self.form.descriptionEdit.setPlainText(
				_fromUtf8(
						converter.itemsToText(self.item.description, edit = True)
				)
		)

		index = self.form.typeComboBox.findData(QtCore.QVariant(self.item.type))

		if index != -1:
			self.form.typeComboBox.setCurrentIndex(index)

		index = self.form.dynamismComboBox.findData(QtCore.QVariant(self.item.dynamism))

		if index != -1:
			self.form.dynamismComboBox.setCurrentIndex(index)

		self.form.sourceEdit.setPlainText(
				_fromUtf8(
						converter.itemsToText(self.item.source, edit = True)
				)
		)


	def show(self):
		self.form.setupUi(self.dialog)

		for k, v in self.typeOptions.items():
			self.form.typeComboBox.addItem(v, QtCore.QVariant(k))

		for k, v in self.dynamisOptions.items():
			self.form.dynamismComboBox.addItem(v, QtCore.QVariant(k))

		self.load()

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		self.item.identifier = unicode(self.form.idEdit.text().toUtf8(), "utf-8")

		index = self.form.typeComboBox.currentIndex()
		self.item.type = unicode(self.form.typeComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")

		index = self.form.dynamismComboBox.currentIndex()
		self.item.dynamism = unicode(self.form.dynamismComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")
		
		try:
			self.item.description = converter.textToItems(
				self.afefuc['project'],
				unicode(self.form.descriptionEdit.toPlainText().toUtf8(), "utf-8")
			)
		except ValueError:
			validation.errorMessage(self.dialog, "Invalid reference in description")
			return
		
		try:
			self.item.source = converter.textToItems(
				self.afefuc['project'],
				unicode(self.form.sourceEdit.toPlainText().toUtf8(), "utf-8")
			)
		except ValueError:
			validation.errorMessage(self.dialog, "Invalid reference in source")
			return

		# validate

		errors = validation.business_rule(self.afefuc['project'], self.item, self.item_orginal is None)

		if errors:
			validation._show(self.dialog, errors)
			return

		if self.item_orginal:
			self.parent.model.updateItem((self.item_orginal, self.item))
		else:
			self.parent.model.insertItem((self.item_orginal, self.item))

		self.dialog.close()
