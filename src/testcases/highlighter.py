#! /usr/bin/env python
#-*- coding: utf-8 -*-

from xml.dom import minidom
from os import path
from PyQt4 import QtCore
import re

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s

class element(object):

	def __init__(self, el):
		
		self.children = []
		self.value = None
		self.elementClass = None
		self.action = None
		self.objectType = None
		self.parsedValue = None

		if el.nodeType == 1:
			
			self.elementClass = el.tagName
			
			if el.attributes:
			
				for i in range(el.attributes.length):
					if el.attributes.item(i).name == 'action':
						self.action = el.attributes.item(i).value
					elif el.attributes.item(i).name == 'type':
						self.objectType = el.attributes.item(i).value

			for subEl in el.childNodes:
				if subEl.nodeType == 3 and self.value is None:
					self.value = subEl.nodeValue.strip()
				elif subEl.nodeType == 1:
					self.children.append(element(subEl))

	def getChildrenNum(self):
		return len(self.children)

	def getChildren(self):
		return self.children

	def setValue(self, value):
		self.value = value

	def setParsedValue(self, value):
		self.parsedValue = value

	def getValue(self):
		return self.value

	def getParsedValue(self):
		return self.parsedValue

	def getElementClass(self):
		return self.elementClass

	def getAction(self):
		return self.action

	def getObjectType(self):
		return self.objectType


class highlighter(object):

	def __init__(self, fileName):
		
		if path.isfile(fileName):
			DOMTree = minidom.parse(fileName)
			cNodes = DOMTree.childNodes

			self.xml = None

			for el in cNodes:
				if el.nodeType == 1 and el.tagName == 'start':
					self.xml = element(el)
			if self.xml is None:
				raise Exception('No START element found in input file.')
		else:
			raise Exception('Input file doesn\'t exist')

	def getStructure(self):
		return self.xml

	def findWordAtBeginning(self, el, toCheck):
		actor = u'^[A-ZĄŚĆŻŹÓŁĘ][a-ząśżźćęłó]*$'
		value = '^\"[^\"]*'
		url = '^\"[^\"]*$'
		name = '^\"[^\"]*$'
		number = '^[0-9]+$'

		if len(toCheck.strip(' ')) == 0:
			return False
		elif el.getElementClass() == 'actor' and re.match(actor, toCheck):  
			return True
		elif el.getElementClass() == 'value' and re.match(value, toCheck):  
			return True
		elif el.getElementClass() == 'url' and re.match(url, toCheck):  
			return True
		elif el.getElementClass() == 'name' and re.match(name, toCheck): 
			return True
		elif el.getElementClass() not in ['actor', 'value', 'url', 'name']:  
			return re.compile(r'^({0}).+'.format(toCheck), flags=re.IGNORECASE).search(el.getValue())
		else:
			return False

	def compareWords(self, el, toCheck):
		actor = u'^[A-ZĄŚĆŻŹÓŁĘ][a-ząśżźćęłó]+$'
		value = '^\"[^\"]+\"$'
		url = '^\"[^\"]+\"$'
		name = '^\"[^\"]*\"$'
		number = '^[0-9]+$'

		if el.getValue() == toCheck and el.getElementClass() not in ['actor', 'value', 'url', 'name']:
			return True
		elif el.getElementClass() == 'actor' and re.match(actor, toCheck):  
			return True
		elif el.getElementClass() == 'value' and re.match(value, toCheck):  
			return True
		elif el.getElementClass() == 'url' and re.match(url, toCheck):  
			return True
		elif el.getElementClass() == 'name' and re.match(name, toCheck): 
			return True
		elif el.getElementClass() == 'number' and re.match(number, toCheck): 
			return True
		else:  
			return False

	def replace_spaces_and_dots(self, sentence):
		output = ""
		quote = False

		for c in sentence:
			if c == '"':
				if quote == False:
					quote = True
				else: 
					quote = False
				output += c
			elif c == ' ':
				if quote == True:
					output += "%20"
				else:
					output += c
			elif c == '.':
				if quote == True:
					output += "%2E"
				else:
					output += c
					return output
			else:
				output += c	

		return output

	def isDot(self, sentence):
		quote = False
		dot = False

		for c in sentence:
			if c == '"':
				if quote == False:
					quote = True
				else: 
					quote = False
			elif c == ".":
				if quote == True:
					dot = False
				else:
					dot = True

		return dot

	def getNext(self, sentence):
		sentence = sentence.replace('\n', '').replace('\r', '')
		sentence = self.replace_spaces_and_dots(unicode(sentence))

		dot = ''
		if self.isDot(sentence):
			dot = '.'

		wordsList = sentence.strip(' .').split(' ')
		output = [0, [], '']
		if wordsList[0] != '':
			for el in self.xml.getChildren():
				self.recCheck(el, wordsList, output, 0)
		else:
			for el in self.xml.getChildren():
				output[1].insert(len(output[1]), el)
		self.verifyResults(wordsList, output)
		wordsList[len(wordsList)-1] = wordsList[len(wordsList)-1] + dot

		num = output[0]
		if len(output[1]) > 0:
			num = num + 1

		for i in xrange(len(wordsList)):
			wordsList[i] = re.sub(r'%20', " ", wordsList[i])
			wordsList[i] = re.sub(r'%2E', ".", wordsList[i])

		output[2] = self.colorUp(wordsList, num)
		return output

	def getElements(self, sentence):
		sentence = sentence.replace('\n', '').replace('\r', '')
		output = []

		sentence = self.replace_spaces_and_dots(unicode(sentence))
		wordsList = sentence.strip(' .').split(' ')
		
		if wordsList[0] != '':
			for el in self.xml.getChildren():
				self.getWordsInformations(el, wordsList, output, 0)

		return output

	def recCheck(self, el, inputWords, output, depth):
		if depth >= len(inputWords):
			return
		if self.compareWords(el, inputWords[depth]):
			if output[0] < depth + 1:
				output[0] = depth + 1
				del output[1][:]
				for subElement in el.getChildren():
					output[1].insert(len(output[1]), subElement)
			for subElement in el.getChildren():
				self.recCheck(subElement, inputWords, output, depth + 1)
		return output

	def getWordsInformations(self, el, inputWords, output, depth):
		if depth >= len(inputWords):
			return
		if self.compareWords(el, inputWords[depth]):
			if self.checkIfNotExists(el, output):
				if el.getElementClass() in ['name', 'url', 'number', 'actor', 'value']:
					inputWords[depth] = re.sub(r'%2E', ".", inputWords[depth])
					el.parsedValue = re.sub(r'%20', " ", inputWords[depth])
				output.insert(len(output), el)
			for subElement in el.getChildren():
				self.getWordsInformations(subElement, inputWords, output, depth + 1)
		return output

	def verifyResults(self, wordsList, results):
		if results[0] < len(wordsList)-1:
			del results[1][:]
		elif results[0] == len(wordsList)-1 and wordsList[len(wordsList)-1].strip(' ') != '':
			tmpResult = []
			for el in results[1]:
				if self.findWordAtBeginning(el, wordsList[results[0]]):
					if self.checkIfNotExists(el, tmpResult):
						tmpResult.insert(len(tmpResult), el)
			if len(wordsList) > 0:
				del results[1][:]
				results.insert(1, tmpResult)
		else:
			tmpResult = []
			for el in results[1]:
				if self.checkIfNotExists(el, tmpResult):
					tmpResult.insert(len(tmpResult), el)
			del results[1][:]
			results.insert(1, tmpResult)

	def checkIfNotExists(self, el, touple):
		for e in touple:
			if el.getValue() == e.getValue():
				return False
		return True

	def getTypesStructure(self):
		pass

	def colorUp(self, wordsList, depth):
		output = ''
		if depth > 0:
			result = []
			for e in wordsList[:depth]:
				result.append(e)
				result.append(' ')
			output += '<font color="green">' + ' '.join(result) + '</font>'
		if depth < len(wordsList):
			output += '<font color="red">' + ' '.join(wordsList[depth:]) + '</font>'
		return output
