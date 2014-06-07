'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from PyQt4 import QtCore, QtGui
from generated.ui.WikiExport import Ui_WikiExport
from format import model
from format.writer import wiki
from utils import converter
from jinja2 import Environment, PackageLoader, FileSystemLoader

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class WikiExportWrapper():
	def __init__(self, parent, afefuc):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_WikiExport()
		self.afefuc = afefuc

		self.generator = Environment(loader=PackageLoader('format.writer.wiki', 'templates'), trim_blocks=True)
		self.generator.filters['itemsToText'] = converter.itemsToText
		self.generator.filters['actorTypeToText'] = converter.actorTypeToText
		self.generator.filters['actorCommunicationToText'] = converter.actorCommunicationToText
		self.generator.filters['businessObjectTypeToText'] = converter.businessObjectTypeToText
		self.generator.filters['businessRuleTypeToText'] = converter.businessRuleTypeToText
		self.generator.filters['businessRuleDynamismToText'] = converter.businessRuleDynamismToText
		self.generator.filters['nameToText'] = converter.nameToText
		self.generator.filters['actorsToText'] = converter.actorsToText
		self.generator.filters['chr'] = lambda x : chr(x)

		self.outputs = wiki.support

	def show(self):
		self.form.setupUi(self.dialog)

		QtCore.QObject.connect(self.form.copyButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedCopyButton)
		QtCore.QObject.connect(self.form.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedCloseButton)
		QtCore.QObject.connect(self.form.generateButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clickedGenerateButton)

		for k, v in self.outputs.items():
			self.form.typeComboBox.addItem(v, QtCore.QVariant(k))

		self.dialog.exec_()

	def clickedCopyButton(self):
		self.afefuc['clipboard'].send(unicode(self.form.outputEdit.toPlainText().toUtf8(), "utf-8"))

	def clickedGenerateButton(self):
		index = self.form.typeComboBox.currentIndex()
		template_name = unicode(self.form.typeComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")

		template = self.generator.get_template(template_name)

		self.form.outputEdit.setPlainText(template.render(project=self.afefuc['project']))

	def clickedCloseButton(self):
		self.dialog.close()
