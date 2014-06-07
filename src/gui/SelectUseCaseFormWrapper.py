'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.SelectUseCaseForm import Ui_SelectUseCaseForm
from format import model
from testcases.paths.all_paths_algorithm import Algorithm
from utils import clone
from utils import converter

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class SelectUseCaseFormWrapper():
	def __init__(self, parent, afefuc):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_SelectUseCaseForm()
		self.afefuc = afefuc
		self.uc_ref = None

	def load(self):
		for usecase in self.afefuc['project'].ucspec.usecases:
			self.form.useCaseComboBox.addItem(usecase.identifier, usecase)

	def show(self):
		self.form.setupUi(self.dialog)

		self.load()

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		uccb = self.form.useCaseComboBox
		self.uc_ref = uccb.itemData(uccb.currentIndex()).toPyObject()
		if self.uc_ref is not None:
			algorithm = Algorithm()
			result = algorithm.execute(self.uc_ref)
			for i, test in enumerate(result.tests):
				#tc = clone.testcase(test, self.afefuc['project'])
				#tc = model.TestCase(test.path)
				#print self.uc_ref.title.text
				test.uc_ref = self.uc_ref
				test.title = converter.itemsToText(self.uc_ref.title) + ' - test #' + str(i)
				test.identifier = self.afefuc['project'].testcases.getUniqueId(
						self.uc_ref.identifier + '_T' + str(i))
				self.parent.model.insertItem((None, test))
		self.dialog.close()
