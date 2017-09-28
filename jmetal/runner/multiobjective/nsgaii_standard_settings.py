import logging
from typing import List

from jmetal.algorithm.multiobjective.nsgaii import NSGAII
from jmetal.core.solution import FloatSolution
from jmetal.operator.crossover import SBX
from jmetal.operator.mutation import Polynomial
from jmetal.operator.selection import BinaryTournamentSelection, BinaryTournament2Selection
from jmetal.problem.multiobjective.constrained import Srinivas
from jmetal.problem.multiobjective.dtlz import DTLZ1
from jmetal.problem.multiobjective.unconstrained import Kursawe, Schaffer, Fonseca, Viennet2
from jmetal.problem.multiobjective.zdt import ZDT1
from jmetal.util.comparator import RankingAndCrowdingDistanceComparator, SolutionAttributeComparator
from jmetal.util.solution_list_output import SolutionListOutput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    problem = ZDT1()
    algorithm = NSGAII[FloatSolution, List[FloatSolution]](
        problem=problem,
        population_size=100,
        max_evaluations=25000,
        mutation=Polynomial(1.0/problem.number_of_variables, distribution_index=20),
        crossover=SBX(1.0, distribution_index=20),
        selection=BinaryTournamentSelection(RankingAndCrowdingDistanceComparator()))
        #selection = BinaryTournament2([SolutionAttributeComparator("dominance_ranking"), SolutionAttributeComparator("crowding_distance", lowest_is_best=False)]))

    algorithm.run()
    result = algorithm.get_result()

    setattr(result, "value", 4) ;
    print("solution aatr: " + str(getattr(result,  "value")))

    SolutionListOutput[FloatSolution].print_function_values_to_file("FUN."+problem.get_name(), result)

    logger.info("Algorithm (continuous problem): " + algorithm.get_name())
    logger.info("Problem: " + problem.get_name())
    logger.info("Computing time: " + str(algorithm.total_computing_time))

if __name__ == '__main__':
    main()
