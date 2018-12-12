import logging
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar, List
import random

from jmetal.core.observable import Observable, DefaultObservable
from jmetal.core.solution import BinarySolution, FloatSolution, IntegerSolution

LOGGER = logging.getLogger('jmetal')

S = TypeVar('S')


class Problem(Generic[S]):
    """ Class representing problems. """

    __metaclass__ = ABCMeta

    MINIMIZE = -1
    MAXIMIZE = 1

    def __init__(self):
        self.number_of_variables: int = None
        self.number_of_objectives: int = None
        self.number_of_constraints: int = None

        self.reference_front: List[S] = None

        self.directions: List[int] = []
        self.labels: List[str] = []

    @abstractmethod
    def create_solution(self) -> S:
        """ Creates a random solution to the problem.

        :return: Solution. """
        pass

    @abstractmethod
    def evaluate(self, solution: S) -> S:
        """ Evaluate a solution. For any new problem inheriting from :class:`Problem`, this method should be
        replaced. Note that this framework ASSUMES minimization, thus solutions must be evaluated in consequence.

        :return: Evaluated solution. """
        pass

    def evaluate_constraints(self, solution: S):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class BinaryProblem(Problem[BinarySolution]):
    """ Class representing binary problems. """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(BinaryProblem, self).__init__()

    def create_solution(self) -> BinarySolution:
        pass

    @abstractmethod
    def evaluate(self, solution: BinarySolution) -> BinarySolution:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class FloatProblem(Problem[FloatSolution]):
    """ Class representing float problems. """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(FloatProblem, self).__init__()
        self.lower_bound = None
        self.upper_bound = None

    def create_solution(self) -> FloatSolution:
        new_solution = FloatSolution(self.number_of_variables, self.number_of_objectives, self.number_of_constraints,
                                     self.lower_bound, self.upper_bound)
        new_solution.variables = \
            [random.uniform(self.lower_bound[i]*1.0, self.upper_bound[i]*1.0) for i in range(self.number_of_variables)]

        return new_solution

    @abstractmethod
    def evaluate(self, solution: FloatSolution) -> FloatSolution:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class IntegerProblem(Problem[IntegerSolution]):
    """ Class representing integer problems. """

    __metaclass__ = ABCMeta

    def __init__(self):
        super(IntegerProblem, self).__init__()
        self.lower_bound = None
        self.upper_bound = None

    def create_solution(self) -> IntegerSolution:
        new_solution = IntegerSolution(
            self.number_of_variables,
            self.number_of_objectives,
            self.number_of_constraints,
            self.lower_bound, self.upper_bound)

        new_solution.variables = \
            [int(random.uniform(self.lower_bound[i]*1.0, self.upper_bound[i]*1.0))
             for i in range(self.number_of_variables)]

        return new_solution

    @abstractmethod
    def evaluate(self, solution: IntegerSolution) -> IntegerSolution:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass


class DynamicProblem(Problem[S]):

    __metaclass__ = ABCMeta

    def __init(self):
        self.observable = DefaultObservable()

    @abstractmethod
    def the_problem_has_changed(self) -> bool:
        pass

    @abstractmethod
    def reset(self) -> None:
        pass
