'''
@author: Jakub Brek
'''

from testcases.paths.all_paths_algorithm import Algorithm
from utils.use_case_utils import createUseCase
import unittest
from format.model import *

import format.writer.xml as renderer_xml

class AllPathsAlgorithmTest(unittest.TestCase):
		def setUp(self):
				self.algorithm = Algorithm()

		def testUseCaseWithoutCycles(self):
				useCase0 = createUseCase("useCase0", 5, [[0, 3, 3], [0, 3, 4]], [[1, 4]])
				result0 = self.algorithm.execute(useCase0)
				self.assertEquals(len(result0), 4)
				pathLengthList = [len(path) for path in result0.tests]
				self.assertIn(5, pathLengthList)
				self.assertIn(7, pathLengthList)
				self.assertIn(6, pathLengthList)
				self.assertEquals(pathLengthList.count(5), 1)
				self.assertEquals(pathLengthList.count(7), 1)
				self.assertEquals(pathLengthList.count(6), 2)

				useCase1 = createUseCase("useCase1", 8, [[2, 4, 3]], [[0, 4], [1, 4], [2, 3]])
				result1 = self.algorithm.execute(useCase1)

				self.assertEquals(len(result1), 5)
				pathLengthList = [len(path) for path in result1.tests]
				self.assertIn(5, pathLengthList)
				self.assertIn(6, pathLengthList)
				self.assertIn(8, pathLengthList)
				self.assertIn(10, pathLengthList)
				self.assertEquals(pathLengthList.count(5), 1)
				self.assertEquals(pathLengthList.count(6), 2)
				self.assertEquals(pathLengthList.count(8), 1)
				self.assertEquals(pathLengthList.count(10), 1)

				useCase2 = createUseCase("useCase2", 2, [[0, 1, 2]], [[0, 4]])
				result2 = self.algorithm.execute(useCase2)

				for t in result2.tests:
					print t.path

#				self.assertEquals(len(result2), 3)
#				pathLengthList = [len(path) for path in result2.tests]
#
#
#				renderer_xml.attach();
#				project = Project()
#				spec = UCSpec()
#				project.ucspec = spec
#				project.setParents()
#
#				spec.usecases.append(useCase0)
#				useCase0.testcases = result0
#				spec.usecases.append(useCase1)
#				useCase1.testcases = result1
#				spec.usecases.append(useCase2)
#				useCase2.testcases = result2
#
#				retval = project.to_xml();
#
#				print retval
#				renderer_xml.detach()


		def testUseCaseWithCycles(self):
				useCase0 = createUseCase(usecaseTitle="useCase0", mainScenario=3, alternationEventGoTo=[[0, 0, 3]])
				result0 = self.algorithm.execute(useCase0)
				self.assertEquals(len(result0), 2)
				pathLengthList = [len(path) for path in result0.tests]
				self.assertIn(3, pathLengthList)
				self.assertIn(7, pathLengthList)

				useCase1 = createUseCase(usecaseTitle="useCase1", mainScenario=3, alternationEventGoTo=[[0, 0, 3], [0, 0, 2]])
				result1 = self.algorithm.execute(useCase1)
				self.assertEquals(len(result1), 5)
				pathLengthList = [len(path) for path in result1.tests]
				self.assertIn(3, pathLengthList)
				self.assertIn(7, pathLengthList)
				self.assertIn(6, pathLengthList)
				self.assertIn(10, pathLengthList)
				self.assertEquals(pathLengthList.count(3), 1)
				self.assertEquals(pathLengthList.count(7), 1)
				self.assertEquals(pathLengthList.count(6), 1)
				self.assertEquals(pathLengthList.count(10), 2)

				useCase2 = createUseCase(usecaseTitle="useCase2", mainScenario=4, alternationEventGoTo=[[2, 0, 2], [1, 1, 3]])
				result2 = self.algorithm.execute(useCase2)
				self.assertEquals(len(result2), 5)
				pathLengthList = [len(path) for path in result2.tests]
				self.assertIn(4, pathLengthList)
				self.assertIn(9, pathLengthList)
				self.assertIn(13, pathLengthList)
				self.assertIn(8, pathLengthList)
				self.assertEquals(pathLengthList.count(4), 1)
				self.assertEquals(pathLengthList.count(9), 1)
				self.assertEquals(pathLengthList.count(13), 2)
				self.assertEquals(pathLengthList.count(8), 1)

				useCase3 = createUseCase(usecaseTitle="useCase3", mainScenario=3, alternationEventGoTo=[[1, 0, 2]])
				result3 = self.algorithm.execute(useCase3)
				self.assertEquals(len(result3), 2)
				pathLengthList = [len(path) for path in result3.tests]
				self.assertIn(3, pathLengthList)
				self.assertIn(7, pathLengthList)

				useCase4 = createUseCase(usecaseTitle="useCase4", mainScenario=3, alternationEventGoTo=[[1, 0, 2],[1,1,2]],alternationEventEnd=[[0,2]])
				result4 = self.algorithm.execute(useCase4)
				self.assertEquals(len(result4), 8)
				pathLengthList = [len(path) for path in result4.tests]
				self.assertIn(3, pathLengthList)
				self.assertIn(7, pathLengthList)
				self.assertIn(6, pathLengthList)
				self.assertIn(10, pathLengthList)
				self.assertEquals(pathLengthList.count(3), 2)
				self.assertEquals(pathLengthList.count(7), 2)
				self.assertEquals(pathLengthList.count(6), 1)
				self.assertEquals(pathLengthList.count(10), 3)

		def testRealWorldExamples(self):
				useCase0 = createUseCase(usecaseTitle="useCase0", mainScenario=4)
				result0 = self.algorithm.execute(useCase0)
				self.assertEquals(len(result0), 1)
				pathLengthList = [len(path) for path in result0.tests]
				self.assertIn(4, pathLengthList)

				useCase1 = createUseCase(usecaseTitle="useCase1", mainScenario=6,alternationEventGoTo=[[4,2,2]])
				result1 = self.algorithm.execute(useCase1)
				self.assertEquals(len(result1), 2)
				pathLengthList = [len(path) for path in result1.tests]
				self.assertIn(6, pathLengthList)
				self.assertIn(11, pathLengthList)

				useCase2 = createUseCase(usecaseTitle="useCase2", mainScenario=6,alternationEventGoTo=[[3,1,2]])
				result2 = self.algorithm.execute(useCase2)
				self.assertEquals(len(result2), 2)
				pathLengthList = [len(path) for path in result2.tests]
				self.assertIn(6, pathLengthList)
				self.assertIn(11, pathLengthList)


if __name__ == "__main__":
		unittest.main()