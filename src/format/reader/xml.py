'''
Created on May 9, 2013

@author: Bartosz Alchimowicz
'''

from lxml import etree
from StringIO import StringIO
from format import model

def read(filename = None):
	ref = {}
	fix = []

	def add_ref(id, item):
		if not ref.has_key(id):
			ref[id] = item

		return item

	def get_ref(id, obj):
		retval = obj()

		if ref.has_key(id):
			retval.item = ref[id]

			return retval

		retval.item = id
		fix.append(retval)

		return retval

	def fix_ref():
		for i in fix:
			i.item = ref[i.item]

	def text(project, node):
		retval = model.TextItem(node.text)

		return retval

	def items(project, node):
		retval = []

		for n in node.getchildren():
			if n.tag == 'text':
				retval.append(text(project, n))
			elif n.tag == 'text':
				retval.append(text(project, n))
			elif n.tag == 'business-object':
				retval.append(business_object(project, n))
			elif n.tag == 'actor':
				retval.append(actor(project, n))
			elif n.tag == 'eouc':
				retval.append(model.EoUCCommand())
			elif n.tag == 'goto':
				retval.append(get_ref(n.attrib['ref'], model.GoToCommand))
			else:
				print n.tag
				assert 1 == 2

		return retval

	def generic_list_iterator(project, node, func):
		retval = []

		for n in node.getchildren():
			retval.append(func(project, n))

		return retval

	def priority(project, node):
		if node.attrib.has_key('ref'):
			return get_ref(node.attrib['ref'], model.Reference)

		retval = model.Priority(node.text)

		add_ref(node.attrib['id'], retval)

		return retval

	def goal_level(project, node):
		if node.attrib.has_key('ref'):
			return get_ref(node.attrib['ref'], model.Reference)

		retval = model.GoalLevel(node.text)

		add_ref(node.attrib['id'], retval)

		return retval

	def actor(project, node):
		if node.attrib.has_key('ref'):
			return get_ref(node.attrib['ref'], model.Reference)

		retval = model.Actor()

		add_ref(node.attrib['id'], retval)

		for n in node.getchildren():
			if n.tag == 'name':
				retval.name = n.text
			elif n.tag == 'id':
				retval.identifier = n.text
			elif n.tag == 'type':
				retval.type = {
						"Business": model.ActorType.HUMAN_BUSINESS,
						"Support": model.ActorType.HUMAN_SUPPORT,
						"System": model.ActorType.SYSTEM,
				}.get(n.text, model.ActorCommunication.NA)
			elif n.tag == 'communication':
				retval.communication = {
						"Puts data": model.ActorCommunication.PUTS_DATA,
						"Gets data": model.ActorCommunication.GETS_DATA,
						"Bidirectional": model.ActorCommunication.BIDIRECTIONAL
				}.get(n.text, model.ActorCommunication.NA)
			elif n.tag == 'description':
				retval.description = items(project, n)
			elif n.tag == 'properties':
				pass
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	def business_object(project, node):
		def attribute(project, node):
			retval = model.Attribute()

			for n in node.getchildren():
				if n.tag == 'name':
					retval.name = n.text
				elif n.tag == 'type':
					retval.type = {
						"Main": model.AttributeType.MAIN,
						"Supplementary": model.AttributeType.SUPPLEMENTARY,
					}.get(n.text, model.AttributeType.MAIN)
				elif n.tag == 'description':
					retval.description = items(project, n)
				else:
					print n.tag
					raise ValueError("Unsupported format file")

			return retval

		if node.attrib.has_key('ref'):
			return get_ref(node.attrib['ref'], model.Reference)

		retval = model.BusinessObject()

		add_ref(node.attrib['id'], retval)

		for n in node.getchildren():
			if n.tag == 'name':
				retval.name = items(project, n)
			elif n.tag == 'id':
				retval.identifier = n.text
			elif n.tag == 'description':
				retval.description = items(project, n)
			elif n.tag == 'attributes':
				retval.attributes = generic_list_iterator(retval, n, attribute)
			elif n.tag == 'state-diagram':
				retval.state_diagram = n.text
			elif n.tag == 'properties':
				pass
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	def business_rule(project, node):
		if node.attrib.has_key('ref'):
			return get_ref(node.attrib['ref'], model.Reference)

		retval = model.BusinessRule()

		add_ref(node.attrib['id'], retval)

		for n in node.getchildren():
			if n.tag == 'id':
				retval.identifier = n.text
			elif n.tag == 'description':
				retval.description = items(project, n)
			elif n.tag == 'type':
				retval.type = n.text
			elif n.tag == 'dynamism':
				retval.dynamism = n.text
			elif n.tag == 'source':
				retval.source = retval.source = items(project, n)
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	def conditions(project, node):
		retval = []

		for n in node.getchildren():
			condition = {
				'trigger': model.Trigger,
				'pre-condition': model.PreCondition,
				'post-condition': model.PostCondition
			}.get(n.tag)()

			condition.items = items(project, n)

			retval.append(condition)

		return retval

	def usecase(project, node):
		def scenario(project, node):
			retval = model.Scenario()

			# can not use generic_list_iterator since going through items list
			for n in node.getchildren():
				retval.items.append(step(project, n))

			return retval

		def step(project, node):
			if node.attrib.has_key('ref'):
				return get_ref(node.attrib['ref'], model.Reference)

			retval = model.Step()

			add_ref(node.attrib['id'], retval)

			retval.items = items(project, node)

			return retval

		def event(project, node):
			if node.attrib.has_key('ref'):
				return get_ref(node.attrib['ref'], model.Reference)

			retval = model.Event()

			for n in node.getchildren():
				if n.tag == 'title':
					retval.title = items(project, n)
				elif n.tag == 'type':
					retval.type = {
							"extension": model.EventType.EXTENSION,
							"exception": model.EventType.EXCEPTION
					}.get(n.text, model.EventType.ALTERNATION)
				elif n.tag == 'anchor':
					retval.anchor = {
							"post-step":    model.EventAnchor.POST_STEP,
							"pre-scenario": model.EventAnchor.PRE_SCENARIO,
							"in-step":      model.EventAnchor.IN_STEP
					}.get(n.text, model.EventAnchor.PRE_STEP)
				elif n.tag == 'scenario':
					retval.scenario = scenario(project, n)
				else:
					print n.tag
					raise ValueError("Unsupported format file")

			add_ref(node.attrib['id'], retval)

			step = get_ref(node.attrib['step'], model.Reference).item

			step.events.append(retval)

			# NO RETURN

		retval = model.UseCase()

		add_ref(node.attrib['id'], retval)

		for n in node.getchildren():
			if n.tag == 'title':
				retval.title = items(project, n)
			elif n.tag == 'id':
				retval.identifier = n.text
			elif n.tag == 'main-actors':
				retval.main_actors = generic_list_iterator(retval, n, actor)
			elif n.tag == 'other-actors':
				retval.other_actors = generic_list_iterator(retval, n, actor)
			elif n.tag == 'summary':
				retval.summary = items(project, n)
			elif n.tag == 'remarks':
				retval.remarks = items(project, n)
			elif n.tag == 'goal-level':
				retval.goal_level = goal_level(project, n)
			elif n.tag == 'priority':
				retval.priority = priority(project, n)
			elif n.tag == 'triggers':
				retval.triggers = conditions(project, n)
			elif n.tag == 'pre-conditions':
				retval.preconditions = conditions(project, n)
			elif n.tag == 'post-conditions':
				retval.postconditions = conditions(project, n)
			elif n.tag == 'scenario':
				retval.scenario = scenario(project, n)
			elif n.tag == 'testcases':
				pass
			elif n.tag == 'events':
				generic_list_iterator(retval, n, event)
				# ignore returned value
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	def term(project, node):
		retval = model.Term()

		for n in node.getchildren():
			if n.tag == 'name':
				retval.name = n.text
			elif n.tag == 'definition':
				retval.definition = items(project, n)
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	def ucspec(project, node):
		retval = model.UCSpec()

		for n in node.getchildren():
			if n.tag == 'priorities':
				retval.priorities = generic_list_iterator(retval, n, priority)
			elif n.tag == 'goal-levels':
				retval.goal_levels = generic_list_iterator(retval, n, goal_level)
			elif n.tag == 'usecases':
				retval.usecases = generic_list_iterator(retval, n, usecase)
			else:
				print n.tag
				assert 1 == 2

		return retval

	def testcases(project, node):
		retval = model.TestCases()

		for n in node.getchildren():
			if n.tag == 'testcase':
				retval.tests.append(testcase(project, n))
			else:
				print n.tag
				assert 1 == 2

		return retval

	def testcase(project, node):
		retval = model.TestCase()

		for n in node.getchildren():
			if n.tag == 'id':
				if n.text:
					retval.identifier = n.text
				else:
					retval.identifier = ''
			elif n.tag == 'title':
				if n.text:
					retval.title = n.text
				else:
					retval.title = ''
			elif n.tag == 'uc_ref':
				retval.uc_ref = uc_ref(project, n.text)
			elif n.tag == 'path':
				retval.path = path(project, n)

		return retval

	def uc_ref(project, uc_id):

		for uc in project.ucspec.usecases:
			if uc.identifier == uc_id:
				return uc

	def path(project, node):
		retval = []

		# can not use generic_list_iterator since going through items list
		for n in node.getchildren():
			if n.tag == 'tc_step':
				retval.append(teststep(project, n))

		return retval

	def uc_step(project, node):
		if node.attrib.has_key('ref'):
			ref = get_ref(node.attrib['ref'], model.Reference)
			return ref.item

	def teststep(project, node):
		retval = model.TestStep()

		for n in node.getchildren():
			if n.tag == 'step':
				retval.ucstep = uc_step(project, n)
			elif n.tag == 'tc_desc':
				if n.text:
					retval.tcstep = n.text
				else:
					retval.tcstep = ''

		return retval

	def descriptions(project, node):
		retval = {'problem': '', 'system': ''}

		for n in node.getchildren():
			if n.tag == 'problem':
				retval['problem'] = n.text
			elif n.tag == 'system':
				retval['system'] = n.text

		return retval['problem'], retval['system']

	def project(node):
		if node.tag != 'project':
			raise ValueError('Tag screen-spec not found')

		retval = model.Project()

		if node.attrib['format'] != "1":
			raise ValueError("Unsupported format file")

		for n in node.getchildren():
			if n.tag == 'name':
				retval.name = n.text
			elif n.tag == 'abbreviation':
				retval.abbreviation = n.text
			elif n.tag == 'version':
				retval.version = n.text
			elif n.tag == 'language':
				retval.language = n.text
			elif n.tag == 'actors':
				retval.actors = generic_list_iterator(retval, n, actor)
			elif n.tag == 'business-objects':
				retval.business_objects = generic_list_iterator(retval, n, business_object)
			elif n.tag == 'business-rules':
				retval.business_rules = generic_list_iterator(retval, n, business_rule)
			elif n.tag == 'ucspec':
				retval.ucspec = ucspec(retval, n)
			elif n.tag == 'glossary':
				retval.glossary = generic_list_iterator(retval, n, term)
			elif n.tag == 'testcases':
				retval.testcases = testcases(retval, n)
			elif n.tag == 'description':
				retval.problem_description, retval.system_description = descriptions(retval, n)
			else:
				print n.tag
				raise ValueError("Unsupported format file")

		return retval

	assert filename is not None

	fd = open(filename)
	data = fd.read()
	fd.close()

	root = etree.fromstring(data)

	retval = project(root)
	retval.setParents()

	fix_ref()

	return retval
