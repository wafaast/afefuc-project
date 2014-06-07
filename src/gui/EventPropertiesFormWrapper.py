'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

from collections import OrderedDict
from PyQt4 import QtCore, QtGui
from generated.ui.EventPropertiesForm import Ui_EventPropertiesForm
from format import model
from utils import converter
from utils import validation

try:
		_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
		_fromUtf8 = lambda s: s

class EventPropertiesFormWrapper():
	def __init__(self, parent, afefuc, position):
		self.parent = parent

		self.dialog = QtGui.QDialog()
		self.form = Ui_EventPropertiesForm()
		self.afefuc = afefuc

		path = self.parent.form.eventsView.model().positionToCoordinates(position)

		self.item = self.parent.item.scenario.items[path[1]].events[path[2]]

		self.types = OrderedDict()
		self.types[model.EventType.ALTERNATION] = "Alternation"
		self.types[model.EventType.EXTENSION]   = "Extension"
		self.types[model.EventType.EXCEPTION]   = "Exception"

		self.anchors = OrderedDict()
		self.anchors[model.EventAnchor.PRE_STEP]     = "Pre-step"
		self.anchors[model.EventAnchor.POST_STEP]    = "Post-step"
		self.anchors[model.EventAnchor.PRE_SCENARIO] = "Pre-scenario"
		self.anchors[model.EventAnchor.IN_STEP]      = "In-step"

	def load(self):
		index = self.form.typeComboBox.findData(QtCore.QVariant(self.item.type))
		if index != -1:
			self.form.typeComboBox.setCurrentIndex(index)

		index = self.form.anchorComboBox.findData(QtCore.QVariant(self.item.anchor))
		if index != -1:
			self.form.anchorComboBox.setCurrentIndex(index)

	def show(self):
		self.form.setupUi(self.dialog)

		for k, v in self.types.items():
			self.form.typeComboBox.addItem(v, QtCore.QVariant(k))

		for k, v in self.anchors.items():
			self.form.anchorComboBox.addItem(v, QtCore.QVariant(k))

		self.load()

		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("accepted()")), self.clickedOKButton)
		QtCore.QObject.connect(self.form.boxButton, QtCore.SIGNAL(_fromUtf8("rejected()")), self.clickedCancelButton)

		self.dialog.exec_()

	def clickedCancelButton(self):
		self.dialog.close()

	def clickedOKButton(self):
		index = self.form.typeComboBox.currentIndex()
		self.item.type = unicode(self.form.typeComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")

		index = self.form.anchorComboBox.currentIndex()
		self.item.anchor = unicode(self.form.anchorComboBox.itemData(index).toPyObject().toUtf8(), "utf-8")
		
		self.dialog.close()
