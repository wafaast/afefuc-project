#!/usr/bin/env python

'''
Created on Apr 25, 2013

@author: Bartosz Alchimowicz
'''

import sys
import signal

sys.path.append('../src-ui')

from PyQt4 import QtCore, QtGui
from gui.MainWindowWrapper import MainWindowWrapper

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal.SIG_DFL)

	app = QtGui.QApplication(sys.argv)
	app.setStyleSheet("QLineEdit  { background-color: white }\nQLineEdit[readOnly=\"true\"]  { color: gray }");
	myapp = MainWindowWrapper(application = app)
	myapp.show()
	sys.exit(app.exec_())
