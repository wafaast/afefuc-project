'''
Created on May 9, 2013

@author: Bartosz Alchimowicz
'''

import copy
import clone

import format.model

def actor(target, source):
	target.name = source.name
	target.identifier = source.identifier
	target.type = source.type
	target.communication = source.communication
	target.description = source.description
	target.properties = source.properties

	return target

def business_object(target, source):
	target.name = source.name
	target.identifier = source.identifier
	target.description = source.description
	target.attributes = source.attributes
	target.properties = source.properties
	target.state_diagram = source.state_diagram

	return target

def usecase(target, source):
	def structure(target, source):
	# reuse structure in order not to fix all references
		refs = source.refs

		target.scenario.items = items = []

		for step_id, step_co in enumerate(source.scenario.items):
			if refs.has_key(step_co):
				items.append(refs[step_co])

				del refs[step_co]
			else:
				items.append(format.model.Step())

			items[step_id].events = events = []

			for event_id, event_co in enumerate(step_co.events):
				if refs.has_key(event_co):
					events.append(refs[event_co])

					del refs[event_co]
				else:
					events.append(format.model.Event())

				items[step_id].events[event_id].scenario.items = ssteps = []

				for sstep_id, sstep_co in enumerate(event_co.scenario.items):
					if refs.has_key(sstep_co):
						ssteps.append(refs[sstep_co])

						del refs[sstep_co]
					else:
						ssteps.append(format.model.Step())

	structure(target, source)                   # reuse structure
	clone.usecase_content(target, source, None) # copy content

	target.setParent()

	return target
