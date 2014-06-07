from lxml import etree as ET

class Dict2XML(object):
	"""
	Based on a number of function available in the Internet.
	"""

	def __init__(self, data, node):
		self.__do(self, data, node)

	@staticmethod
	def __do(self, data, node):
		for key in data:
			subnode = ET.SubElement(node, key)

			if isinstance(data[key], basestring):
				subnode.text = data[key]
			elif isinstance(data[key], dict):
				self.__do(self, data[key], subnode)
			else:
				assert 1 == 2
