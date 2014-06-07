#-*-coding: utf-8 -*-

'''
Created on Dec 14, 2012

@author: Bartosz Alchimowicz
'''

import copy
import utils.converter as converter

##############
# Reference
######

class Referencable(object):
    def __init__(self):
        self.referenced = True                  # boolean

    def get_ref(self, properties = None):
        #self.referenced = True
        return Reference(self, properties)

##############
# Dependable
######

class Configuration(object):
    def __init__(self):
        pass

class GoalLevel(Configuration, Referencable):
    def __init__(self, name = None):
        Referencable.__init__(self)

        self.name = name                        # str

class Priority(Configuration, Referencable):
    def __init__(self, name = None):
        Referencable.__init__(self)

        self.name = name                        # str

##############
# Independable
######

class Project(object):
    def __init__(self):
        self.name = ""                          # str
        self.abbreviation = ""                  # str
        self.language = "en"                    # str, according to ISO 639-1 (http://en.wikipedia.org/wiki/ISO_639-1)
        self.version = ""                       # str
        self.actors = []                        # Actor
        self.business_objects = []              # BusinessObject
        self.business_rules = []                # BusinessRule
        self.ucspec = UCSpec()                  # UCSpec
        self.testcases = TestCases()
            #TODO TCSpec()
        self.problem_description = ""           # str
        self.system_description = ""            # str
        self.glossary = []                      # Term{0..}

    def _getItemByName(self, item, storage, name, replace):
        if replace:
            storage = list(storage)
            storage[storage.index(replace[0])] = replace[1]

        for item in storage:
            if item.name == name:
                return item

        raise ValueError("%s %s not found" % (name, item))

    def _getItemByIdentifier(self, item, storage, identifier, replace):
        if replace:
            storage = list(storage)

            if replace[0] is not None:
                storage[storage.index(replace[0])] = replace[1]
            else:
                storage.append(replace[1])

        for item in storage:
            if item.identifier == identifier:
                return item

        raise ValueError("%s %s not found" % (item, identifier))

    def getActorByName(self, name, replace = None):
        return self._getItemByName("Actor", self.actors, name, replace)

    def getActorByIdentifier(self, identifier, replace = None):
        return self._getItemByIdentifier("Identifier", self.actors, identifier, replace)

    def getBusinessObjectByName(self, name, replace = None):
        return self._getItemByName("Actor", self.business_objects, name, replace)

    def getBusinessObjectByIdentifier(self, identifier, replace = None):
        return self._getItemByIdentifier("Identifier", self.business_objects, identifier, replace)

    def getUseCaseByIdentifier(self, identifier, replace = None):
        return self._getItemByIdentifier("Use case", self.ucspec.usecases, identifier, replace)

    def setParents(self):
        for usecase in self.ucspec.usecases:
            usecase.setParent(self)

class UCSpec(object):
    def __init__(self):
        self.priorities = []                    # Priority
        self.goal_levels = []                   # GoalLevel
        self.usecases = []                      # UseCase

class UseCase(Referencable):
    def __init__(self, title = []):
        Referencable.__init__(self)

        self.title = title                      # Item{0..}
        self.identifier = None                  # str
        self.main_actors = []                   # Actor
        self.other_actors = []                  # Actor
        self.goal_level = None                  # GoalLevel
        self.priority = None                    # Priority
        self.triggers = []                      # Trigger
        self.preconditions = []                 # PreCondition
        self.postconditions = []                # PostCondition
        self.scenario = Scenario()              # Scenario

        self.testcases = []                     # TestCase{0..}

        self.summary = []                       # Item{0..}
        self.remarks = []                       # Item{0..}

    def getPath(self):
        for i, u in enumerate(self.parent.ucspec.usecases):
            if u == self:
                    break

        return (i, )

    def setParent(self, parent = None):
        if parent is not None:
            self.parent = parent

        for step in self.scenario.items:
            step.setParent(self)

class Scenario(object):
    def __init__(self):
        self.items = []                         # Step{0..}

class Step(Referencable):
    def __init__(self, items = []):
        Referencable.__init__(self)
        self.nextSteps = []                     # Step{0..}
        self.items = items                      # Item{0..}
        #self.scenario = None                   # Scenario                 # unsuported
        self.events = []                        # Event{0..}

    def getPath(self):
        if isinstance(self.parent, UseCase):
            for i, s in enumerate(self.parent.scenario.items):
                if s == self:
                    break

            return self.parent.getPath() + (i, )
        elif isinstance(self.parent, Event):
            event = self.parent
            step = event.parent
            uc = step.parent

            for i, s in enumerate(event.scenario.items):
                if s == self:
                    break

            return event.getPath() + (i, )
        else:
            assert 1 == 2

    def setParent(self, parent):
        self.parent = parent

        for e in self.events:
            e.setParent(self)

class ActorType(object):
    HUMAN_BUSINESS = "Business"
    HUMAN_SUPPORT  = "Support"
    SYSTEM         = "System"

class ActorCommunication(object):
    NA            = "N/A"
    PUTS_DATA     = "Puts data"
    GETS_DATA     = "Gets data"
    BIDIRECTIONAL = "Bidirectional"

class Actor(Referencable):
    def __init__(self, name = None, identifier = None, description = []):
        Referencable.__init__(self)

        self.name = name                        # str
        self.identifier = identifier            # str
        self.type = None                        # ActorType
        self.communication = None               # ActorCommunication
        self.description = description          # Item{0..}
        self.properties = None                  # dict

    def toText(self, edit = False):
        if edit:
            return "@actor:" + self.identifier

        return self.name

class Item(object):
    def __init__(self):
        pass

    def toText(self, edit = False):
        raise NotImplemented()

class Reference(Item):
    def __init__(self, item = None, properties = None):
        #item.referenced = True                 # boolean
        self.item = item                        # Referencable
        self.properties = properties            # dict

    def toText(self, edit = False):
        return self.item.toText(edit)

class TextItem(Item):
    def __init__(self, text = None):
        self.text = text                        # str

    def toText(self, edit = False):
        return self.text

class Command(Item):
    pass

class GoToCommand(Command):
    def __init__(self, item = None, project = None):
        #step.referenced = True                 # boolean
        self.item = item                        # Step|Event|UseCase
        self.project = project

    def toText(self, edit = False):
        path = self.item.getPath()

        if isinstance(self.item, UseCase):
            retval = "%s" % (self.item.identifier)
        elif isinstance(self.item, Event):
            retval = "%s.%d.%c" % (self.item.parent.parent.identifier, path[1] + 1, path[2] + 65)
        elif isinstance(self.item, Step):
            if isinstance(self.item.parent, UseCase):
                retval = "%s.%d" % (self.item.parent.identifier, path[1] + 1)
            elif isinstance(self.item.parent, Event):
                retval = "%s.%d.%c.%d" % (
                        self.item.parent.parent.parent.identifier,
                        path[1] + 1,
                        path[2] + 65,
                        path[3] + 1
                )
            else:
                assert 1 == 2
        else:
            assert 1 == 2

#       if isinstance(self.item, UseCase):
#           print self.item, retval
#       else:
#           print self.item.parent, retval

        if edit:
            return "@goto:%s" % retval

        return "[%s]" % retval

class EoUCCommand(Command):
    def toText(self, edit = False):
        if edit:
            return u"@eouc"

        return "End of use case"

class ScreenCommand(Command):
    def __init__(self, identifier):
        self.referenced = True                  # boolean
        self.identifier = identifier            # str

##############
# Business
######

class BusinessObject(Referencable):
    def __init__(self, identifier = None, name = []):
        Referencable.__init__(self)

        self.name = name                        # Item{0..}
        self.identifier = identifier            # str
        self.description = []                   # Item{0..}
        self.attributes = []                    # Attribute{0..}
        self.state_diagram = None               # str
        self.properties = None                  # dict

    def toText(self, edit):
        if edit:
            return "@bo:" + self.identifier

        return converter.itemsToText(self.name)

class BusinessRuleType(object):
    NA = "N/A"
    FACTS = "Facts"
    CONSTRAINTS = "Constraints"
    ACTION_ENABLERS = "Action Enablers"
    COMPUTATIONS = "Computations"
    INTERFACES = "Interfaces"

class BusinessRuleDynamism(object):
    NA = "N/A"
    STATIC = "Static"
    DYNAMIC = "Dynamic"

class BusinessRule(Referencable):
    def __init__(self, identifier = None):
        self.identifier = identifier            # str
        self.description = []                   # Item{0..}
        self.type = None                        # BusinessRuleType
        self.dynamism = None                    # BusinessRuleDynamism
        self.source = []                        # Item{0..}

class AttributeType(object):
    MAIN = "Main"
    SUPPLEMENTARY = "Supplementary"

class Attribute(object):
    def __init__(self):
        self.name = None                        # str
        self.type = None                        # AttributeType
        self.description = []                   # Item{0..}

##############
# Trigger/Conditino
######

class Condition(object):
    def __init__(self, condition_type, items = []):
        self.condition_type = condition_type
        self.items = items                      # Item{0..}

class Trigger(Condition):
    def __init__(self, items = []):
        Condition.__init__(self, "trigger", items)

class PreCondition(Condition):
    def __init__(self, items = []):
        Condition.__init__(self, "pre-condition", items)

class PostCondition(Condition):
    def __init__(self, items = []):
        Condition.__init__(self, "post-condition", items)

##############
# Event
######

class EventType(object):
    ALTERNATION = "alternation"
    EXTENSION   = "extension"
    EXCEPTION   = "exception"

class EventAnchor(object):
    PRE_STEP     = "pre-step"
    POST_STEP    = "post-step"
    PRE_SCENARIO = "pre-scenario"
    IN_STEP      = "in-step"

class Event(Referencable):
    def __init__(self, type = None, title = []):
        Referencable.__init__(self)
        self.title = title                  # Item{0..}
        self.type = type                    # EventType
        self.anchor = EventAnchor.PRE_STEP  # EventAnchor
        self.scenario = Scenario()          # Scenario

    def getPath(self):
        step = self.parent

        for i, e in enumerate(step.events):
            if e == self:
                break

        return step.getPath() + (i, )

    def setParent(self, parent):
        self.parent = parent

        for step in self.scenario.items:
            step.setParent(self)

##############
# TestCases
######

class TestCases(object):
    def __init__(self):                         # TestCase{0..}
        self.tests = []

    def getUniqueId(self, identifier):
        while(self.doesIdExist(identifier)):
            identifier += ' (2)'
        return identifier

    def doesIdExist(self, identifier):
        for i in self.tests:
            if identifier == i.identifier:
                return True
        return False

    def __len__(self):
        return len(self.tests)

class TestCase(object):
    def __init__(self, path = None):    #path - lista krokow z UC
        #self.path = path                       # Step{0..}
        #if path is None : self.path = []

        self.title = None                       # Item{0..}
        self.identifier = None                  # str

        self.path = []
        if path is not None:
            for step in path:
                self.path.append(TestStep(step))

        self.uc_ref = None
        #self.scenario = Scenario()

    def __len__(self):
        return len(self.path)

class TestStep(object):
    def __init__(self, ucstep=None, tcstep=None):
        self.ucstep = ucstep    # Step
        self.tcstep = tcstep    # str


##############
# Glossary
######

class Term(Referencable):
    def __init__(self, name = None, definition = []):
        Referencable.__init__(self)
        self.name = name                        # str
        self.definition = definition            # Item{0..}
