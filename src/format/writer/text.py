'''
Created on Dec 24, 2012

@author: perf
'''

import model as orginal
from types import MethodType

def GoalLevel_att_to_text(self):
	return self.name

def Priority_att_to_text(self):
	return self.name

def UCSpec_att_to_text(self, indent = 0):
	indention = "\t" * indent

	retval  = "%sActors:\n\n" % (indention)

	retval += "\n".join([ a.to_uc(indent + 1) for a in self.actors])

	retval += "\n%sUse cases:\n\n" % (indention)

	retval += "\n".join([ uc.to_text(indent + 1) for uc in self.ucs])

	return retval

def UseCase_att_to_text(self, indent = 0):
	indention = "\t" * indent

	retval  = "%sID: %s\n" % (indention, self.identifier)
	retval += "%sTitle: %s\n" % (indention, self.title)
	retval += "%sGoal level: %s\n" % (indention, self.goal_level.to_text())
	retval += "%sPriority: %s\n" % (indention, self.priority.to_text())

	retval += "%sMain actors: %s\n" % (indention, ", ".join([a.to_text() for a in self.main_actors]))
	retval += "%sOther actors: %s\n" % (indention, ", ".join([a.to_text() for a in self.other_actors]))

	retval += "%sMain scenario:\n\n" % (indention)

	retval += self.scenario.to_text(indent)

	retval += "\n%sRest:\n\n" % (indention)

	events = []

	for number, item in enumerate(self.scenario.items):
		if isinstance(item, orginal.Step):
			if len(item.events) > 0:
				for letter, event in enumerate(item.events):
					events += [("%d.%s" % (number + 1, chr(letter + 65)), event)]

	retval += "\n".join([ev[1].to_text(indent, ev[0]) for ev in events])

	return retval

def Scenario_att_to_text(self, indent = 0, number = None):
	retval = ""
	prefix = "" if number == None else "%s." % number

	for i, item in enumerate(self.items):
		retval += prefix + item.to_text(indent + 1, i + 1)

	return retval

def Step_att_to_text(self, indent = 0, number = None):
	indention = "\t" * indent

	prefix = "" if number == None else "%s." % number

	retval =  "%s%s %s\n" % (indention, prefix, " ".join([i.to_text() for i in self.items]))

	return retval

def Reference_att_to_text(self):
	tmp = "" if self.properties == None else str(self.conf)

	return self.sth.to_text() + tmp


def TextItem_att_to_text(self):
	return self.text

def Event_att_to_text(self, indent = 0, number = None):
	indention = "\t" * indent

	prefix = "" if number == None else "%s." % number

	retval  = "%s%s\n" % (indention, self.event_type)
	retval += "%s%s. %s\n" % (indention, number, " ".join([i.to_text() for i in self.title]))

	for i, item in enumerate(self.scenario.items):
		retval += item.to_text(indent + 1, prefix + "%d" % (i + 1))

	return retval

def Actor_att_to_text(self):
	return self.name

def Actor_att_to_uc(self, indent = 0):
	indention = "\t" * indent

	return "%sID: %s\n%sName: %s\n%sDescription: %s\n" % \
			(indention, self.identifier, indention, self.name, indention, self.description)

def GoTo_att_to_text(self):
	return "Goto %s" % str(self.step)

attachments = {
	orginal.GoalLevel:   GoalLevel_att_to_text,
	orginal.Priority:    Priority_att_to_text,
	orginal.UCSpec:      UCSpec_att_to_text,
	orginal.UseCase:     UseCase_att_to_text,
	orginal.Scenario:    Scenario_att_to_text,
	orginal.Step:        Step_att_to_text,
	orginal.Reference:   Reference_att_to_text,
	orginal.TextItem:    TextItem_att_to_text,
	orginal.Event:       Event_att_to_text,
	orginal.Actor:       Actor_att_to_text,
	#orginal.Actor:       Actor_att_to_uc,
	orginal.GoToCommand: GoTo_att_to_text,
}

def attach():
	for clazz in attachments:
		method = attachments[clazz]
		clazz.to_text = MethodType(method, None, clazz)

	orginal.Actor.to_uc = MethodType(Actor_att_to_uc, None, orginal.Actor)

def detach():
	for clazz in attachments:
		del clazz.to_text

	del orginal.Actor.to_uc
