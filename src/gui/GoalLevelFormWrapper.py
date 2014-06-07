'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.LineEditForm import Ui_LineEditForm
from format import model
from utils import validation

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s

try:
	_encoding = QtGui.QApplication.UnicodeUTF8
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
	def _translate(context, text, disambig):
		return QtGui.QApplication.translate(context, text, disambig)

class GoalLevelFormWrapper():
	def __init__(self, parent, afefuc, item = None):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_LineEditForm()
		self.afefuc = afefuc
		self.item = item[1]
		self.item_orginal = item[0]

	def load(self):
		self.form.nameEdit.setText(_fromUtf8(self.item.name))

	def show(self):
		self.form.setupUi(self.dialog)
		self.dialog.setWindowTitle(_translate("GaolLevelForm", "Goal level", None))

		self.load()

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		self.item.name = unicode(self.form.nameEdit.text().toUtf8(), "utf-8")

		# validate

		errors = validation.goal_level(self.afefuc['project'], self.item, self.item_orginal is None)

		if errors:
			validation._show(self.dialog, errors)
			return

		if self.item_orginal:
			self.parent.model.updateItem((self.item_orginal, self.item))
		else:
			self.parent.model.insertItem((self.item_orginal, self.item))

		self.dialog.close()
