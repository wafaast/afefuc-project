#! /usr/bin/env python
#-*- coding: utf-8 -*-

'''
This script converts .mm files (current format for FreeMind) to XML format

How to use:

./mm2xml.py [input file] [output file] 

Output XML file structure:

main element -> [start]
 children elements:
  actor
  text
  action -> has attributes:
   action 
  value 
  name 
  url 
  object -> has attributes:
   type 
  number
'''

from os import path
from sys import argv, exit
from xml.dom import minidom
import codecs

class element(object):

	def __init__(self, el):
		
		self.children = []
		self.value = None;
		self.elementClass = None;
		self.action = None;
		self.objectType = None;

		if el.attributes and el.tagName == 'node':
			
			for i in range(el.attributes.length):
				if el.attributes.item(i).name == 'TEXT':
					self.value = el.attributes.item(i).value

			if self.value == None:
				raise Exception('There is an error in your input file - no TEXT attribute for element named NODE specified.')

			for subEl in el.childNodes:
				if subEl.nodeType == 1 and subEl.tagName == 'attribute' and subEl.attributes:
					name = None;
					value = None;

					for i in range(subEl.attributes.length):
						if subEl.attributes.item(i).name == 'NAME':
							name = subEl.attributes.item(i).value
						elif subEl.attributes.item(i).name == 'VALUE':
							value = subEl.attributes.item(i).value
							if name == 'class':
								self.elementClass = value
							elif name == 'action':
								self.action = value
							elif name == 'type':
								self.objectType = value
							else:
								raise Exception('There is an error in your input file - no NAME attribute for element named ATTRIBUTE specified.')
					if value == None:
						raise Exception('There is an error in your input file - no VALUE attribute for element named ATTRIBUTE specified.')
					name = None;
					value = None;

				if subEl.nodeType == 1 and subEl.tagName == 'node' and subEl.attributes:
					self.children.append(element(subEl))

	def getChildrenNum(self):
		return len(self.children)

	def getChildren(self):
		return self.children

	def getValue(self):
		return self.value

	def getElementClass(self):
		return self.elementClass

	def getAction(self):
		return self.action

	def getObjectType(self):
		return self.objectType

	def toXML(self, intendation = 0):
		output = ''
		if self.elementClass != None:
			output = ' '*intendation + '<' + self.elementClass 
			if self.action != None:
				output += ' action="' + self.action + '"'
			if self.objectType != None:
				output += ' type="' + self.objectType + '"'
			if self.value != None:
				output += '>' + self.value
			if len(self.children) > 0:
				for nestedElement in self.children:
					output += '\n' + nestedElement.toXML(intendation+1)
				output += '\n' + ' '*intendation + '</' + self.elementClass + '>'
			else:
				output += '</' + self.elementClass + '>'
		return output

if __name__ == "__main__":
	if len(argv) == 3:
		inputFileName = argv[1]
		outputFileName = argv[2]
	else:
		raise Exception('Wrong arguments. Try: ./converter.py [input file] [output file]')

	if path.isfile(inputFileName):
		DOMTree = minidom.parse(inputFileName)
		cNodes = DOMTree.childNodes[0].childNodes

		xml = None;

		for el in cNodes:
			if el.nodeType == 1 and el.tagName == 'node' and el.getAttribute('TEXT') == '[start]':
				xml = element(el)
		if xml == None:
			raise Exception('No START element found in input file.')

		output = xml.toXML()

		try:
			outputFile = codecs.open(outputFileName, 'w', 'utf-8')
			outputFile.write(output)
			outputFile.close()
		except IOError as e:
			raise Exception('I/O error({0}): {1}'.format(e.errno, e.strerror))
	else:
		raise Exception('Input file doesn\'t exist')