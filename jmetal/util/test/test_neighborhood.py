import unittest

import numpy

from jmetal.core.solution import Solution
from jmetal.util.ckecking import NoneParameterException, InvalidConditionException
from jmetal.util.neighborhood import WeightVectorNeighborhood, TwoDimensionalMesh


class WeightVectorNeighborhoodTestCases(unittest.TestCase):

    def test_should_constructor_work_properly(self) -> None:
        number_of_weight_vectors = 100
        neighborhood_size = 20
        neighborhood: WeightVectorNeighborhood = WeightVectorNeighborhood(number_of_weight_vectors, neighborhood_size)

        self.assertEqual(number_of_weight_vectors, neighborhood.number_of_weight_vectors)
        self.assertEqual(neighborhood_size, neighborhood.neighborhood_size)
        self.assertEqual(2, neighborhood.weight_vector_size)

        self.assertEqual(0.0, neighborhood.weight_vectors[0][0])
        self.assertEqual(1.0, neighborhood.weight_vectors[0][1])
        self.assertEqual(0.0101010101010101010101, neighborhood.weight_vectors[1][0])
        self.assertEqual(0.989898989898989898, neighborhood.weight_vectors[1][1])
        self.assertEqual(1.0, neighborhood.weight_vectors[99][0])
        self.assertEqual(0.0, neighborhood.weight_vectors[99][1])

        self.assertTrue(numpy.array_equal(numpy.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),
                         neighborhood.neighborhood[0]))
        self.assertTrue(numpy.array_equal(numpy.array([69, 70, 68, 71, 67, 72, 66, 73, 65, 64, 74, 75, 63, 76, 62, 77, 61, 78, 60, 79]),
                         neighborhood.neighborhood[69]))

    def test_should_get_neighbors_work_properly_with_two_objectives(self):
        number_of_weight_vectors = 100
        neighborhood_size = 20
        neighborhood: WeightVectorNeighborhood = WeightVectorNeighborhood(number_of_weight_vectors, neighborhood_size)

        solution_list = [Solution(2, 2) for _ in range(number_of_weight_vectors)]

        neighbors = neighborhood.get_neighbors(0, solution_list)
        self.assertEqual(neighborhood_size, len(neighbors))
        self.assertTrue(solution_list[0] == neighbors[0])
        self.assertTrue(solution_list[19] == neighbors[19])

        neighbors = neighborhood.get_neighbors(69, solution_list)
        self.assertEqual(neighborhood_size, len(neighbors))
        self.assertTrue(solution_list[69] == neighbors[0])
        self.assertTrue(solution_list[79] == neighbors[19])


class TwoDimensionalMeshTestCases(unittest.TestCase):
    def test_should_get_neighbors_throw_an_exception_if_the_solution_list_is_none(self):
        """
        Topology:
        north = -1,  0
        south =  1,  0
        east  =  0,  1
        west  =  0, -1
        :return:
        """
        neighborhood = TwoDimensionalMesh(3, 3, [[-1, 0], [1, 0], [0, 1], [0, -1]])
        with self.assertRaises(NoneParameterException):
            neighborhood.get_neighbors(0, None)

    def test_should_get_neighbors_throw_an_exception_if_the_solution_list_is_empty(self):
        """
        Topology:
        north = -1,  0
        south =  1,  0
        east  =  0,  1
        west  =  0, -1
        :return:
        """
        neighborhood = TwoDimensionalMesh(3, 3, [[-1, 0], [1, 0], [0, 1], [0, -1]])
        with self.assertRaises(InvalidConditionException()):
            neighborhood.get_neighbors(0, [])

    def test_should_get_neighbors_return_four_neighbors_case1(self):
        """
        Case 1
           Solution list:
            0 1 2
            3 4 5
            6 7 8

            The solution location is 4, so the neighborhood is 1, 3, 5, 7
        """
        rows = 3
        columns = 3
        solution_list = [Solution(2, 2) for _ in range(rows * columns)]
        neighborhood = TwoDimensionalMesh(rows, columns, [[-1, 0], [1, 0], [0, 1], [0, -1]])

        result = neighborhood.get_neighbors(4, solution_list)
        self.assertEqual(4, len(result))


if __name__ == '__main__':
    unittest.main()
