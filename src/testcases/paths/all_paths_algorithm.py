# -*- coding: utf-8 -*-

'''
@author: Jakub Brek
'''

from format.model import *

class Algorithm:
		def __init__(self):
				self.init()

		def execute(self, usecase):
				self.init(usecase)
				self.initNextSteps(usecase)
				self.DFS(usecase.scenario.items[0], [], [])

				tcs = TestCases()

				for path in self.paths:
						tcs.tests.append(TestCase(path))

				return tcs

		def initNextSteps(self, usecase):
				steps = usecase.scenario.items
				for i in xrange(len(steps)):
						del steps[i].nextSteps[:]
                    
				for i in xrange(len(steps)):
						for stepItem in steps[i].items:
								if isinstance(stepItem, GoToCommand):
									if isinstance(stepItem.item, Step):
										steps[i].nextSteps.append(stepItem.item)
									#elif isinstance(stepItem.item, UseCase):
									#	steps[i].nextSteps.append(stepItem.item.scenario.items[0])
									#elif isinstance(stepItem.item, Event):
									#	steps[i].nextSteps.append(stepItem.item.scenario.items[0])

						if i + 1 < len(steps):
								steps[i].nextSteps.append(steps[i + 1])

						if steps[i].events:
								for event in steps[i].events:
										steps[i].nextSteps.append(event.scenario.items[0])
										self.initNextSteps(event)

		def init(self, usecase=None):
				self.paths = []
				self.usecase = usecase

		def isMainPath(self, step):
				for item in self.usecase.scenario.items:
						if step == item:
								return True

		def DFS(self, startingStep, path, visited):
				path.append(startingStep)

				if not self.isMainPath(startingStep):
						visited.append(startingStep)

				if not startingStep.nextSteps:
						self.paths.append(list(path))
						return

				for step in startingStep.nextSteps:
						if step not in visited:
								self.DFS(step, path, visited)
								nextStep = path.pop()
								if nextStep in visited:
										visited.remove(nextStep)
