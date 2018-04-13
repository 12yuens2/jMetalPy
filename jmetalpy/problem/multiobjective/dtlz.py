from math import pi, cos

from jmetalpy.core.problem import Objective
from jmetalpy.core.problem import FloatProblem
from jmetalpy.core.solution import FloatSolution


class DTLZ1(FloatProblem):

    def __init__(self, number_of_variables: int = 30, number_of_objectives=3):
        super().__init__()
        self.objectives = [self.Dtlz1Objective() for i in range(number_of_objectives)]

        self.number_of_variables = number_of_variables
        self.number_of_objectives = number_of_objectives
        self.number_of_constraints = 0

        self.lower_bound = self.number_of_variables * [0.0]
        self.upper_bound = self.number_of_variables * [1.0]

        FloatSolution.lower_bound = self.lower_bound
        FloatSolution.upper_bound = self.upper_bound

    class Dtlz1Objective(Objective):
        def is_a_minimization_objective(self):
            return True

    def evaluate(self, solution: FloatSolution):
        g = 0.0
        k = self.number_of_variables - self.number_of_objectives + 1
        for i in range (self.number_of_variables - k, self.number_of_variables):
            g += (solution.variables[i] - 0.5) * (solution.variables[i] - 0.5) - \
                 cos(20.0 * pi * (solution.variables[i] - 0.5))

        g = 100 * (k + g)
        for i in range(self.number_of_objectives):
            solution.objectives[i] = (1.0 + g) * 0.5

        for i in range(self.number_of_objectives):
            for j in range(self.number_of_objectives - (i + 1)):
                solution.objectives[i] *= solution.variables[j]

            if i != 0:
                aux = self.number_of_objectives - (i + 1)
                solution.objectives[i] *= 1 - solution.variables[aux]

    def get_name(self):
        return "DTLZ1"
