# -*- coding: utf-8 -*-

'''
@author: Jakub Brek
'''

from format.model import *

def createUseCase(usecaseTitle, mainScenario, alternationEventGoTo=[], alternationEventEnd=[]):
    '''
    @param usecaseTitle - title of the usecase
    @param mainScenario -  number of main scenario steps
    @param alternationEventGoTo - list of list containing 3 numbers:
                1st - number of step containing the event
                2nd - number of step where to go after the event finished
                3rd - number of steps in the event
            example [[1,2,5],[5,6,5],[4,4,5]] -> 3 alternation events;
            (counting from 0)
            alternation event 1 -> starts in step 1 ends in step 2, has 5 steps
            alternation event 2 -> starts in step 5 ends in step 6, has 5 steps
            alternation event 3 -> starts in step 4 ends in step 4, has 5 steps - cycle
    @param alternationEventEnd - list of list containing 2 numbers
                1st - number of step containing the event
                2nd - number of steps in the event
    @return UseCase()
    '''

    usecase = UseCase([TextItem(usecaseTitle)])
    usecase.scenario = Scenario()

    #    MAIN SCENARIO
    mainSteps = []
    for i in xrange(mainScenario - 1):
        newStep = Step([TextItem("Step" + str(i))])
        mainSteps.append(newStep)
    mainSteps.append(Step([EoUCCommand()]))
    usecase.scenario.items = mainSteps

    #        Alternation evenets With GoToCommand in the end
    for i in xrange(len(alternationEventGoTo)):
        eventGoTo_steps = []
        eventGoTo = Event(EventType.ALTERNATION, [TextItem(u"Alternation EventGoTo " + str(i))])
        eventGoTo.scenario = Scenario()
        for j in xrange(alternationEventGoTo[i][2] - 1):                 # (-1) - because add GoTo step in the end
            newStep = Step([TextItem("Alternation1 Step" + str(j))])
            eventGoTo_steps.append(newStep)
        eventGoTo_steps.append(Step([GoToCommand(mainSteps[alternationEventGoTo[i][1]])]))
        mainSteps[alternationEventGoTo[i][0]].events.append(eventGoTo)
        eventGoTo.scenario.items = eventGoTo_steps

    #        Alternation evenets With EoUCCommand in the end
    for i in xrange(len(alternationEventEnd)):
        eventEnd_steps = []
        eventEnd = Event(EventType.ALTERNATION, [TextItem(u"Alternation EventEnd " + str(i))])
        eventEnd.scenario = Scenario()
        for j in xrange(alternationEventEnd[i][1] - 1):                # (-1) - because add EoUC step in the end
            newStep = Step([TextItem("Alternation1 Step" + str(j))])
            eventEnd_steps.append(newStep)
        eventEnd_steps.append(Step([EoUCCommand()]))
        mainSteps[alternationEventEnd[i][0]].events.append(eventEnd)
        eventEnd.scenario.items = eventEnd_steps

    return usecase


