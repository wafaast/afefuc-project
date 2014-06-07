'''
Created on May 9, 2013

@author: Bartosz Alchimowicz
'''

import copy

import format.model

def _items(items, source, target, project):
    retval = []

    for item in items:
        if isinstance(item, format.model.TextItem):
            retval.append(copy.copy(item))
        elif isinstance(item, format.model.Reference):
            if item.item == source:
                retval.append(target.get_ref())
            else:
                retval.append(item.item.get_ref())
        else:
#           print type(item)
            assert 2 == 3

    return retval

def priority(source, project):
    target = format.model.Priority()

    target.name = source.name

    return target

def goal_level(source, project):
    target = format.model.GoalLevel()

    target.name = source.name

    return target

def business_object(source, project):
    def attribute(source, project):
        target = format.model.Attribute()

        target.name = source.name
        target.type = source.type
        target.description = _items(source.description, source, target, project)

        return target

    target = format.model.BusinessObject()

    target.name = _items(source.name, source, target, project)
    target.identifier = source.identifier
    target.state_diagram = source.state_diagram
    target.description = _items(source.description, source, target, project)
    target.attributes = [attribute(a, project) for a in source.attributes]
    target.properties = copy.deepcopy(source.properties)

    return target

def business_rule(source, project):
    target = format.model.BusinessRule()

    target.identifier = source.identifier
    target.description = _items(source.description, source, target, project)
    target.type = source.type
    target.dynamism = source.dynamism
    target.source = _items(source.source, source, target, project)

    return target

def actor(source, project):
    target = format.model.Actor()

    target.name = source.name
    target.identifier = source.identifier
    target.type = source.type
    target.communication = source.communication
    target.description = _items(source.description, source, target, project)
    target.properties = copy.deepcopy(source.properties)

    return target

def usecase_content(target, source, project):
    def items(items, source, target, project):
        """
        Copies items which are allowed to use in a step.

        This functions differs from the one above (i.e. _items).
        """
        assert isinstance(items, list)

        retval = []

        for item in items:
            if isinstance(item, format.model.TextItem):  #kopiowanie zawartosci textitem
                retval.append(copy.copy(item))
            elif isinstance(item, format.model.Reference): #reference
                if type(item.item) in [format.model.BusinessObject, format.model.Actor]:
                    retval.append(item.item.get_ref())
                else:
                    assert 1 == 2
            elif isinstance(item, format.model.EoUCCommand): #EoUC
                retval.append(format.model.EoUCCommand())
            elif isinstance(item, format.model.GoToCommand): #goto
                if isinstance(item.item, format.model.UseCase):
                    if item.item == source:
                        retval.append(format.model.GoToCommand(target))
                    else:
                        retval.append(format.model.GoToCommand(item.item))
                elif isinstance(item.item, format.model.Step):
                    if isinstance(item.item.parent, format.model.UseCase):
                        if item.item.parent == source:
                            i, j = item.item.getPath()

#                           print i, j

                            retval.append(format.model.GoToCommand(target.scenario.items[j]))
                        else:
                            retval.append(format.model.GoToCommand(item.item))
                    elif isinstance(item.item.parent, format.model.Event):
                        if item.item.parent.parent.parent == source:
                            i, j, k, l = item.item.getPath()

#                           print i, j, k, l

                            retval.append(
                                    format.model.GoToCommand(
                                            target.scenario.items[j].events[k].scenario.items[l]
                                    )
                            )
                        else:
                            assert 1 == 4
                    else:
#                       print type(item.item.parent)
                        assert 7 == 1
                else:
#                   print type(item.item)
                    assert 7 == 2
            else:
#               print type(item)
                assert 2 == 3

        return retval

    target.identifier = source.identifier
    target.goal_level = source.goal_level.item.get_ref() if source.goal_level else None
    target.priority = source.priority.item.get_ref() if source.priority else None
    target.main_actors =  source.main_actors
    target.other_actors = source.other_actors

    target.title = items(source.title, source, target, project)
    target.summary = items(source.summary, source, target, project)
    target.remarks = items(source.remarks, source, target, project)

    # scenario
    for step_id, step_co in enumerate(source.scenario.items):
        target.scenario.items[step_id].items = items(step_co.items, source, target, project)

        for event_id, event_co in enumerate(step_co.events):
#           print event_id

            target.scenario.items[step_id].events[event_id].title =\
                    items(event_co.title, source, target, project)

            target.scenario.items[step_id].events[event_id].type =\
                    source.scenario.items[step_id].events[event_id].type

            target.scenario.items[step_id].events[event_id].anchor =\
                    source.scenario.items[step_id].events[event_id].anchor

            for substep_id, substep_co in enumerate(event_co.scenario.items):
                target.scenario.items[step_id].events[event_id].scenario.items[substep_id].items = \
                        items(substep_co.items, source, target, project)

    # TODO: the structure should be copied in structure function!
    target.triggers = []
    for i, t in enumerate(source.triggers):
        target.triggers.append(format.model.Trigger(items(source.triggers[i].items, source, target, project)))

    target.preconditions = []
    for i, t in enumerate(source.preconditions):
        target.preconditions.append(format.model.PreCondition(items(source.preconditions[i].items, source, target, project)))

    target.postconditions = []
    for i, t in enumerate(source.postconditions):
        target.postconditions.append(format.model.PostCondition(items(source.postconditions[i].items, source, target, project)))


def usecase(source, project):
    def structure(target, source):
        refs = {}

        for step_org in source.scenario.items:
            step_cpy = format.model.Step()

            refs[step_cpy] = step_org

            for event_org in step_org.events:
                event_cpy = format.model.Event()

                refs[event_cpy] = event_org

                for ss_org in event_org.scenario.items:
                    ss_cpy = format.model.Step()

                    refs[ss_cpy] = ss_org

                    event_cpy.scenario.items.append(ss_cpy)

                step_cpy.events.append(event_cpy)

            target.scenario.items.append(step_cpy)

        target.refs = refs

        return refs

        #self.testcases = copy.deepcopy(instance.testcases)

    target = format.model.UseCase()

    structure(target, source)
    usecase_content(target, source, project)

    return target

def testcase(source, project):
    target = format.model.TestCase()

    target.identifier = source.identifier #str
    target.title = source.title #str
    target.uc_ref = source.uc_ref

    for step_org in source.path:
        step_cpy = format.model.TestStep()
        step_cpy.ucstep = step_org.ucstep #kopiowanie adresu! do zmiany jesli bedziemy modyfikowac UCstep
        step_cpy.tcstep = step_org.tcstep
        target.path.append(step_cpy)

    return target

def test_case(source, project):
    target = format.model.TestCase()

    return target

def term(source, project):
    target = format.model.Term()

    target.name = source.name
    target.definition = _items(source.definition, source, target, project)

    return target
