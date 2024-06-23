from copy import deepcopy
from random import randint

from src.model.modeling import ClassCourseTeacherAssignmentProblem
from src.model.TabuSearch import TabuSearch


# TabuSearch Algorithms
class TabuSearchAlgorithm(TabuSearch):
    """
    Tries to get a randomly-generated classtable
    """

    def __init__(
        self,
        problem: ClassCourseTeacherAssignmentProblem,
        initial_state,
        tabu_tenure,
        max_steps,
        neighborhood_size,
        constraints=[0, 1, 2],
        print_interval=100,
        max_score=None,
    ):
        super().__init__(
            initial_state,
            tabu_tenure,
            max_steps,
            neighborhood_size,
            constraints,
            print_interval,
            max_score,
        )
        self.problem = problem
        self.CHANGE_STRATEGY = [
            problem.change_teacher,
            problem.change_time,
            problem.change_both,
        ]

    def _neighborhood(self):
        neighborhood = []
        attribute_change = []
        for _ in range(self.neighborhood_size):
            neighbor = deepcopy(self.current)
            # Find neighbor by randomly change start_time or teacher or both in one random class-subject
            choice = randint(0, len(neighbor) - 1)
            candidate = neighbor[choice]
            if candidate[2] * candidate[3] == 0:
                change_strategy_choice = 2
            else:
                change_strategy_choice = randint(0, 2)
            self.CHANGE_STRATEGY[change_strategy_choice](candidate)

            neighborhood.append(neighbor)
            # attribute_change.append((choice, candidate[2], candidate[3]))
            attribute_change.append((choice))
        return neighborhood, attribute_change

    def _score(self, assignments):
        score = 0
        # Penalty
        if 0 in self.constraints:
            session_violations = self.problem.check_same_session_time(assignments)
        else:
            session_violations = 0

        if 1 in self.constraints:
            class_violations = self.problem.check_class_schedule_conflicts(assignments)
        else:
            class_violations = 0

        if 2 in self.constraints:
            teacher_violations = self.problem.check_teacher_schedule_conflicts(
                assignments
            )
        else:
            teacher_violations = 0

        if 3 in self.constraints:
            endtimelimit_violations = self.problem.check_end_time_limit(assignments)
        else:
            endtimelimit_violations = 0

        score -= 100 * (
            session_violations
            + class_violations
            + teacher_violations
            + endtimelimit_violations
        )

        # Score
        for assignment in assignments:
            if assignment[2] and assignment[3]:
                score += 1

        return score
