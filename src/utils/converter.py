'''
Created on May 4, 2013

@author: Bartosz Alchimowicz
'''

import re

import format.model

def textToItems(project, text, replace = None):
    RE_ACTOR = re.compile(r"@(actor):(\w+)")
    RE_BUSINESS_OBJECT = re.compile(r"@(bo):(\w+)")
    RE_EOUC = re.compile(r"@(eouc)")
    RE_GOTO = re.compile(r"@(goto):((\w+.)*\w+)")

    def helper(project, text, replace = None):
        t = RE_ACTOR.match(text)
        if t:
            actor = project.getActorByIdentifier(t.groups()[1])

            return actor.get_ref()

        t = RE_BUSINESS_OBJECT.match(text)
        if t:
            bo = project.getBusinessObjectByIdentifier(t.groups()[1])

            return bo.get_ref()

        t = RE_EOUC.match(text)
        if t:
            return format.model.EoUCCommand()

        t = RE_GOTO.match(text)
        if t:
            tmp = t.groups()[1].split(".")

            uc = project.getUseCaseByIdentifier(tmp[0], replace)

            if len(tmp) == 1:
                item = uc
            elif len(tmp) == 2:
                i = int(tmp[1]) - 1
                item = uc.scenario.items[i]
            elif len(tmp) == 3:
                i = int(tmp[1]) - 1
                j = ord(tmp[2]) - 65

                item = uc.scenario.items[i].events[j]
            elif len(tmp) == 4:
                i = int(tmp[1]) - 1
                j = ord(tmp[2]) - 65
                k = int(tmp[3]) - 1

                item = uc.scenario.items[i].events[j].scenario.items[k]
            else:
                raise ValueError()

            return format.model.GoToCommand(item)

        return format.model.TextItem(text)

    assert isinstance(project, format.model.Project)
    assert isinstance(text, basestring)

    tmp = text.split(" ")
    symbols = ".,"

    items = []
    retval = []

    for i in tmp:
        if len(i) > 0:
            if i[0] in symbols:
                items.append(i[0])

                if len(i) > 1:
                    items.append(i[1:])

                continue

            if i[-1] in symbols:
                items.append(i[:-1])

                if len(i) > 1:
                    items.append(i[-1])

                continue

            items.append(i)

    for i in items:
        n = helper(project, i, replace)

        if len(retval) > 0:
            if isinstance(n, format.model.TextItem) and isinstance(retval[-1], format.model.TextItem):
                if len(n.text) == 1 and n.text in symbols:
                    retval[-1].text += n.text
                else:
                    retval[-1].text += " " + n.text
            else:
                retval.append(n)
        else:
            retval.append(n)

    return retval

def itemsToText(items, edit = False):
    try:
        assert isinstance(items, list)
    except :
        pass
    retval = []
    lastIdx = len(items) - 1

    for i, item in enumerate(items):
        
        if isinstance(item, format.model.Item):
            retval.append(item.toText(edit))
        elif isinstance(item, format.model.Referencable):
            retval.append(item.toIdentifierText(edit))
        else:
            print i, item
            assert 1 == 2 and "unknown type"

        if i < lastIdx:
            if isinstance(items[i + 1], format.model.TextItem) and items[i + 1].text in ".,":
                pass
            else:
                retval.append(" ")

    return "".join(retval)

def nameToText(type):
    if isinstance(type, format.model.Reference):
        type = type.item

    return type.name

def actorsToText(items):
    retval = []

    for a in items:
        retval.append(nameToText(a))

    return ", ".join(retval)

def actorTypeToText(type):
    return {
            format.model.ActorType.HUMAN_BUSINESS: "Human - Business role",
            format.model.ActorType.HUMAN_SUPPORT:  "Human - Support role",
            format.model.ActorType.SYSTEM:         "System",
    }.get(type, "N/A")


def actorCommunicationToText(type):
    return {
        format.model.ActorCommunication.PUTS_DATA:     "Only provides data",
        format.model.ActorCommunication.GETS_DATA:     "Only gets data",
        format.model.ActorCommunication.BIDIRECTIONAL: "Provides and gets data",
    }.get(type, "N/A")

def businessObjectTypeToText(type):
    return {
        format.model.AttributeType.MAIN:          'Main',
        format.model.AttributeType.SUPPLEMENTARY: 'Supplementary',
    }.get(type, "N/A")

def businessRuleTypeToText(type):
    return {
            format.model.BusinessRuleType.FACTS: "Facts",
            format.model.BusinessRuleType.CONSTRAINTS: "Constraints",
            format.model.BusinessRuleType.ACTION_ENABLERS: "Action Enablers",
            format.model.BusinessRuleType.COMPUTATIONS: "Computations",
            format.model.BusinessRuleType.INTERFACES: "Interfaces",
    }.get(type, "N/A")

def businessRuleDynamismToText(type):
    return {
            format.model.BusinessRuleDynamism.STATIC: "Static",
            format.model.BusinessRuleDynamism.DYNAMIC: "Dynamic",
    }.get(type, "N/A")
