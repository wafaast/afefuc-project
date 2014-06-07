'''
@author: Jakub Brek
'''

import unittest
from utils.use_case_utils import createUseCase
from format.model import *

class UseCaseCreatorTest(unittest.TestCase):
    def testUseCase(self):
        useCase = createUseCase("Title", 5)

        self.assertEquals(len(useCase.scenario.items), 5, "Main scenario length")
        for step in useCase.scenario.items:
            self.assertEqual(step.events, [], "No events in step")
        self.assertIsInstance(useCase.scenario.items[4].items[0], EoUCCommand)

    def testUseCaseWithAlternationGoToEvent(self):
        useCase = createUseCase("Title", 5, [[0, 3, 3], [0, 3, 4]])

        self.assertEquals(len(useCase.scenario.items), 5)
        self.assertEquals(len(useCase.scenario.items[0].events), 2)
        self.assertEquals(len(useCase.scenario.items[1].events), 0)
        self.assertEquals(len(useCase.scenario.items[2].events), 0)
        self.assertEquals(len(useCase.scenario.items[3].events), 0)
        self.assertEquals(len(useCase.scenario.items[4].events), 0)
        self.assertIsInstance(useCase.scenario.items[0].events[0], Event)
        self.assertIsInstance(useCase.scenario.items[0].events[1], Event)

        event0Steps = useCase.scenario.items[0].events[0].scenario.items
        event1Steps = useCase.scenario.items[0].events[1].scenario.items

        self.assertIsInstance(event0Steps[2].items[0], GoToCommand)
        self.assertIsInstance(event1Steps[3].items[0], GoToCommand)

    def testUseCaseWithAlternationEndEvent(self):
        useCase = createUseCase(usecaseTitle="Title", mainScenario=5, alternationEventEnd=[[3, 4], [1, 2]])

        self.assertEquals(len(useCase.scenario.items), 5)

        self.assertEquals(len(useCase.scenario.items[0].events), 0)
        self.assertEquals(len(useCase.scenario.items[1].events), 1)
        self.assertEquals(len(useCase.scenario.items[2].events), 0)
        self.assertEquals(len(useCase.scenario.items[3].events), 1)
        self.assertEquals(len(useCase.scenario.items[4].events), 0)

        self.assertIsInstance(useCase.scenario.items[1].events[0], Event)
        self.assertIsInstance(useCase.scenario.items[3].events[0], Event)

        event1Steps = useCase.scenario.items[1].events[0].scenario.items
        event3Steps = useCase.scenario.items[3].events[0].scenario.items

        self.assertEquals(len(event1Steps), 2)
        self.assertEquals(len(event3Steps), 4)

        self.assertIsInstance(event1Steps[1].items[0], EoUCCommand)
        self.assertIsInstance(event3Steps[3].items[0], EoUCCommand)

if __name__ == "__main__":
    unittest.main()
