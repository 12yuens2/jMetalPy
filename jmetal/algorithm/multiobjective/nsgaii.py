from typing import TypeVar, List, Generic

import time

from dask.distributed import Client, as_completed

from jmetal import logger
from jmetal.config import store
from jmetal.algorithm.singleobjective.genetic_algorithm import GeneticAlgorithm
from jmetal.component import DominanceComparator
from jmetal.component.evaluator import Evaluator
from jmetal.component.generator import Generator
from jmetal.core.algorithm import EvolutionaryAlgorithm
from jmetal.core.operator import Mutation, Crossover, Selection
from jmetal.core.problem import Problem
from jmetal.operator import RankingAndCrowdingDistanceSelection
from jmetal.util.termination_criteria import TerminationCriteria

S = TypeVar('S')
R = TypeVar('R')

"""
.. module:: NSGA-II
   :platform: Unix, Windows
   :synopsis: NSGA-II (Non-dominance Sorting Genetic Algorithm II) implementation.

.. moduleauthor:: Antonio J. Nebro <antonio@lcc.uma.es>, Antonio Benítez-Hidalgo <antonio.b@uma.es>
"""


class NSGAII(GeneticAlgorithm):

    def __init__(self,
                 problem: Problem,
                 population_size: int,
                 offspring_size: int,
                 mating_pool_size: int,
                 mutation: Mutation,
                 crossover: Crossover,
                 selection: Selection,
                 termination_criteria: TerminationCriteria,
                 pop_generator: Generator = None,
                 pop_evaluator: Evaluator = None,
                 dominance_comparator: DominanceComparator = DominanceComparator()):
        """  NSGA-II implementation as described in

        * K. Deb, A. Pratap, S. Agarwal and T. Meyarivan, "A fast and elitist
          multiobjective genetic algorithm: NSGA-II," in IEEE Transactions on Evolutionary Computation,
          vol. 6, no. 2, pp. 182-197, Apr 2002. doi: 10.1109/4235.996017

        NSGA-II is a genetic algorithm (GA), i.e. it belongs to the evolutionary algorithms (EAs)
        family. The implementation of NSGA-II provided in jMetalPy follows the evolutionary
        algorithm template described in the algorithm module (:py:mod:`jmetal.core.algorithm`).

        .. note:: A steady-state version of this algorithm can be run by setting the offspring size to 1 and the mating pool size to 2.

        :param problem: The problem to solve.
        :param population_size: Size of the population.
        :param mutation: Mutation operator (see :py:mod:`jmetal.operator.mutation`).
        :param crossover: Crossover operator (see :py:mod:`jmetal.operator.crossover`).
        :param selection: Selection operator (see :py:mod:`jmetal.operator.selection`).
        """
        super(NSGAII, self).__init__(
            problem=problem,
            population_size=population_size,
            offspring_size=offspring_size,
            mating_pool_size=mating_pool_size,
            mutation=mutation,
            crossover=crossover,
            selection=selection,
            pop_evaluator=pop_evaluator,
            pop_generator=pop_generator,
            termination_criteria=termination_criteria
        )
        self.dominance_comparator = dominance_comparator

    def replacement(self, population: List[S], offspring_population: List[S]) -> List[List[S]]:
        """ This method joins the current and offspring populations to produce the population of the next generation
        by applying the ranking and crowding distance selection.

        :param population: Parent population.
        :param offspring_population: Offspring population.
        :return: New population after ranking and crowding distance selection is applied.
        """
        join_population = population + offspring_population
        return RankingAndCrowdingDistanceSelection(self.population_size, dominance_comparator=self.dominance_comparator).execute(join_population)

    def get_result(self) -> R:
        return self.population

    def get_name(self) -> str:
        return 'NSGAII'


class DistributedNSGAII(Generic[S, R]):

    def __init__(self,
                 population_size: int,
                 problem: Problem[S],
                 max_evaluations: int,
                 mutation: Mutation[S],
                 crossover: Crossover[S, S],
                 selection: Selection[List[S], S],
                 number_of_cores: int,
                 client: Client):
        super().__init__()
        self.problem = problem
        self.max_evaluations = max_evaluations
        self.mutation_operator = mutation
        self.crossover_operator = crossover
        self.selection_operator = selection

        self.population = None
        self.population_size = population_size
        self.number_of_cores = number_of_cores
        self.client = client
        self.observable = store.default_observable
        self.evaluations = 0
        self.start_computing_time = 0
        self.total_computing_time = 0

    def update_progress(self, population):
        observable_data = {'EVALUATIONS': self.evaluations,
                           'COMPUTING_TIME': self.total_computing_time,
                           'SOLUTIONS': population,
                           'reference_front': self.problem.reference_front}

        self.observable.notify_all(**observable_data)

    def create_initial_population(self) -> List[S]:
        population = []

        for _ in range(self.number_of_cores):
            population.append(self.problem.create_solution())

        return population

    def run(self):
        population_to_evaluate = self.create_initial_population()

        self.start_computing_time = time.time()

        futures = []
        for solution in population_to_evaluate:
            futures.append(self.client.submit(self.problem.evaluate, solution))

        task_pool = as_completed(futures)

        population = []
        # MAIN LOOP
        while self.evaluations < self.max_evaluations:
            for future in task_pool:
                print("TASK_POOL_SIZE: " + str(len(task_pool.futures)))
                self.evaluations += 1
                # The initial population is not full
                if len(population) < self.population_size:
                    received_solution = future.result()
                    population.append(received_solution)

                    new_task = self.client.submit(self.problem.evaluate, self.problem.create_solution())
                    task_pool.add(new_task)
                # Perform an algorithm step to create a new solution to be evaluated
                else:
                    offspring_population = []
                    if self.evaluations < self.max_evaluations:
                        offspring_population.append(future.result())

                        # Replacement
                        join_population = population + offspring_population
                        #self.check_population(join_population)
                        population = RankingAndCrowdingDistanceSelection(self.population_size).execute(join_population)

                        # Selection
                        mating_population = []
                        for _ in range(2):
                            solution = self.selection_operator.execute(population_to_evaluate)
                            mating_population.append(solution)

                        # Reproduction
                        offspring = self.crossover_operator.execute(mating_population)
                        self.mutation_operator.execute(offspring[0])

                        solution_to_evaluate = offspring[0]

                        # Evaluation
                        new_task = self.client.submit(self.problem.evaluate, solution_to_evaluate)
                        task_pool.add(new_task)
                    else:
                        print("TIME: " + str(time.time() - self.start_computing_time))
                        for future in task_pool.futures:
                            future.cancel()

                        break

                self.evaluations += 1

                if self.evaluations % 10 == 0:
                    self.update_progress(population_to_evaluate)

        self.total_computing_time = time.time() - self.start_computing_time
        self.population = population

    #def check_population(self, join_population: []):
    #    for solution in join_population:
    #        if solution is None:
    #            raise Exception('Solution is none')

    def get_result(self) -> R:
        return self.population

    def get_name(self) -> str:
        return 'Distributed Non-dominated Sorting Genetic Algorithm II'


# def reproduction(mating_population: List[S], problem, crossover_operator, mutation_operator) -> S:
#     offspring = crossover_operator.execute(mating_population)
#
#     # todo Este operador podría ser el causante del problema "Minimum and maximum are the same!"
#     offspring = mutation_operator.execute(offspring[0])
#
#     return problem.evaluate(offspring)
