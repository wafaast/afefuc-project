#! /usr/bin/env python
#-*- coding: utf-8 -*-

'''
To install the Python client library:
	pip install -U selenium

We use unittest which is a part of Python STD library

To run generated tests simply type:
	fileName.py

To run tests you need Selenium RC - download from:
	http://docs.seleniumhq.org/download/
'''

from os import path
from os import remove
import re
import codecs
from PyQt4 import QtGui

class selenium():

	def __init__(self, sb, parent):
		self.parent = parent
		self.sb = sb
		self.browser = None
		self.system = None

	def translateBrowserName(self, browserName):
		if browserName in ['iPad', 'iPhone']:
			return browserName
		else:
			return browserName.toLower()

	def generateCode(self, tc, browser, system, directory):
		fileName = self.makeFileName(tc.title)
		actions = tc.path
		self.browser = self.translateBrowserName(browser)
		self.system = system.toUpper()
		outputDir = directory + '/'
		outputPath = outputDir + fileName + '.py'

		if path.isdir(outputDir):
			try:
				if path.exists(outputPath):
					msg = 'File ' + fileName + '.py already exists. Do you want to overwrite this file?'
					ret = QtGui.QMessageBox.warning(self.parent, "Warning", msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
					if ret == 65536:
						return
					else:
						outputFile = codecs.open(outputPath, 'w', 'utf-8')

						self.generateHeader(outputFile, fileName)
						self.generateActions(actions, outputFile)
						self.generateFooter(outputFile)

						outputFile.close()
				else:
					outputFile = codecs.open(outputPath, 'w', 'utf-8')

					self.generateHeader(outputFile, fileName)
					self.generateActions(actions, outputFile)
					self.generateFooter(outputFile)

					outputFile.close()
			except IOError as e:
				QtGui.QMessageBox.warning(self.parent, 'Message', 'I/O error({0}): {1}'.format(e.errno, e.strerror), QtGui.QMessageBox.Ok)
			except Exception as e:
				remove(outputPath)
				msg = 'Unexpected error occured in TC: ' + tc.title + '\n' + 'Error message: ' + e.message

				QtGui.QMessageBox.warning(self.parent, 'Message', msg, QtGui.QMessageBox.Ok)
		else:
			QtGui.QMessageBox.warning(self.parent, 'Message', 'Wrong path, or file name', QtGui.QMessageBox.Ok)

	def makeFileName(self, input):
		dic = {'ś':'s', 'ć':'c', 'ą':'a', 'ę':'e', 'ż':'z', 'ź':'z', 'ó':'o', 'ł':'l', 'ń':'n'}
		
		for i in dic:
			i = i.decode('utf-8')
			input = input.replace(i, dic[i.encode('utf-8')])

		input = re.sub(ur'[^a-zA-Z0-9 ]+', '', input)
		words = input.title().split(' ')
		output = ''.join(words)
		return output

	def parseActions(self, sentence):
		action = ['', '', '']

		o = self.sb.getElements(sentence)
		for e in o:
			if e.getElementClass() == 'action':
				action[0] = e.getAction()
			elif e.getElementClass() in ['name', 'url']:
				if e.getElementClass() == 'url':
					action[1] = e.getParsedValue()
				else:
					action[1] = e.getParsedValue()
			elif e.getElementClass() in ['value', 'number']:
				action[2] = e.getParsedValue()

		return action

	def generateHeader(self, file, fileName):
		file.write('#! /usr/bin/env python\n')
		file.write('#-*- coding: utf-8 -*-\n\n')

		file.write('from selenium import webdriver\nimport unittest\nimport sys\n\n')
		file.write('class ' + fileName + '(unittest.TestCase):\n\n')
		file.write('\tdef setUp(self):\n\t\tself.driver = webdriver.Remote(desired_capabilities={"browserName": "' + self.browser + '","platform": "' + self.system + '"})\n')
		file.write('\t\tself.driver.implicitly_wait(3)\n\n')

	def generateFooter(self, file):
		file.write('\tdef tearDown(self):\n\t\tself.driver.quit()\n\nif __name__ == "__main__":\n\tunittest.main()')

	def generateActions(self, actions, file):
		file.write('\tdef test(self):\n')

		actionsBuffer = []
		i = 0;

		for action in actions:

			output = None

			if action.tcstep and len(action.tcstep) > 0:
				output = self.parseActions(action.tcstep)
				actionsBuffer.insert(len(actionsBuffer), output)
				i = i + 1
			else:
				actionsBuffer.insert(len(actionsBuffer), output)
				continue

			if output[0] == 'redo':
				if output[2] == '':
					raise Exception('Invalid number of parameters for action: redo')
				else:
					if int(output[2]) < len(actionsBuffer)-1 and int(output[2]) > 0:
						output = actionsBuffer[int(output[2])-1]
					else:
						raise Exception('Invalid value of parameter for action: redo')	
			if output[0] == 'open':
				if output[1] == '':
					raise Exception('Invalid number of parameters for action: open')
				else:
					file.write('\t\tself.driver.get(' + output[1] + ')\n\n')
			elif output[0] == 'click':
				if output[1] == '':
					raise Exception('Invalid number of parameters for action: click')
				else:
					file.write('\t\telement = self.driver.find_element_by_id(' + output[1] + ')\n')
					file.write('\t\telement.click()\n\n')
			elif output[0] == 'type':
				if output[1] == '' or output[2] == '':
					raise Exception('Invalid number of parameters for action: type')
				else:
					file.write('\t\telement = self.driver.find_element_by_id(' + output[1] + ')\n')
					file.write('\t\telement.send_keys(' + output[2] + ')\n\n')
			elif output[0] == 'checkTextPresent':
				if output[2] == '':
					raise Exception('Invalid number of parameters for action: checkTextPresent')
				else:
					if output[1] == '':
						# all page
						file.write('\t\tallPageCode = self.driver.page_source\n\n')
						file.write('\t\tself.assertTrue(allPageCode.find(' + output[2] + '))\n\n')
					else:
						# specified element
						file.write('\t\telement = self.driver.find_element_by_id(' + output[2] + ').text\n\n')
						file.write('\t\tself.assertTrue(element.find(' + output[2] + '))\n\n')
			elif output[0] == 'openWindow':
				if output[1] == '':
					raise Exception('Invalid number of parameters for action: openWindow')
				else:
					file.write('\t\tself.driver.get(' + output[1] + ')\n\n')
			elif output[0] == 'checkPagePresent':
				if output[1] == '':
					raise Exception('Invalid number of parameters for action: checkPagePresent')
				else:
					file.write('\t\tself.assertEqual(self.driver.current_url, ' + output[1] + ')\n\n')
			else:
				raise Exception('Invalid action.')

		if i == 0:
			file.write('\t\tpass\n\n')