'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from collections import OrderedDict
from PyQt4 import QtCore, QtGui
from generated.ui.ActorForm import Ui_ActorForm
from format import model
from utils import converter
from utils import validation

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class ActorFormWrapper():
	def __init__(self, parent, afefuc, item = None):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_ActorForm()
		self.afefuc = afefuc
		
		self.item = item[1]
		self.item_orginal = item[0]

		self.typesOfActor = OrderedDict()
		self.typesOfActor[model.ActorType.HUMAN_BUSINESS] = "Human - Business role"
		self.typesOfActor[model.ActorType.HUMAN_SUPPORT]  = "Human - Support role"
		self.typesOfActor[model.ActorType.SYSTEM]         = "System"

		self.typesOfCommunication = OrderedDict()
		self.typesOfCommunication[model.ActorCommunication.NA]            = "N/A"
		self.typesOfCommunication[model.ActorCommunication.PUTS_DATA]     = "Only provides data"
		self.typesOfCommunication[model.ActorCommunication.GETS_DATA]     = "Only gets data"
		self.typesOfCommunication[model.ActorCommunication.BIDIRECTIONAL] = "Provides and gets data"

	def load(self):
		self.form.nameEdit.setText(_fromUtf8(self.item.name))
		self.form.idEdit.setText(_fromUtf8(self.item.identifier))

		self.form.descriptionEdit.setPlainText(
				_fromUtf8(
						converter.itemsToText(self.item.description, edit = True)
				)
		)

		index = self.form.typeComboBox.findData(QtCore.QVariant(self.item.type))
		if index != -1:
			self.form.typeComboBox.setCurrentIndex(index)

		index = self.form.communicationComboBox.findData(QtCore.QVariant(self.item.communication))
		if index != -1:
			self.form.communicationComboBox.setCurrentIndex(index)

	def show(self):
		self.form.setupUi(self.dialog)

		for k, v in self.typesOfActor.items():
			self.form.typeComboBox.addItem(v, QtCore.QVariant(k))

		for k, v in self.typesOfCommunication.items():
			self.form.communicationComboBox.addItem(v, QtCore.QVariant(k))

		self.load()

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		try:
			self.item.name = unicode(self.form.nameEdit.text().toUtf8(), "utf-8")
			self.item.identifier = unicode(self.form.idEdit.text().toUtf8(), "utf-8")
			self.item.description = converter.textToItems(
					self.afefuc['project'],
					unicode(self.form.descriptionEdit.toPlainText().toUtf8(), "utf-8")
			)
		except ValueError:
			validation.errorMessage(self.dialog, "Invalid reference")

		index = self.form.typeComboBox.currentIndex()
		self.item.type = unicode(self.form.typeComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")

		index = self.form.communicationComboBox.currentIndex()
		self.item.communication = unicode(self.form.communicationComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")

		# validate
		errors = validation.actor(self.afefuc['project'], self.item, self.item_orginal is None)

		if errors:
			validation._show(self.dialog, errors)
			return

		# save

		if self.item_orginal:
			self.parent.model.updateItem((self.item_orginal, self.item))
		else:
			self.parent.model.insertItem((self.item_orginal, self.item))

		self.dialog.close()
