'''
Created on 27 May 2013

@author: Bartosz Alchimowicz
'''

import sys
from PyQt4 import QtGui, QtCore

class Clipboard(object):
	def __init__(self, application):
		self.app = application
		self.clipboard = self.app.clipboard()

	def send(self, text):
		self.clipboard.setText(text)
		event = QtCore.QEvent(QtCore.QEvent.Clipboard)
		self.app.sendEvent(self.clipboard, event)
