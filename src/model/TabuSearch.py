from abc import ABCMeta, abstractmethod
from collections import deque
from copy import deepcopy

from numpy import argmax


class TabuSearch:
    """
    Conducts tabu search
    """

    __metaclass__ = ABCMeta

    cur_steps = None

    neighborhood_size = None

    tabu_size = None
    tabu_list = None

    initial_state = None
    current = None
    best = None

    max_steps = None
    max_score = None

    def __init__(
        self,
        initial_state,
        tabu_tenure,
        max_steps,
        neighborhood_size,
        constraints=[0, 1, 2],
        print_interval=100,
        max_score=None,
    ):
        """
        :param initial_state: initial state, should implement __eq__ or __cmp__
        :param tabu_size: number of states to keep in tabu list
        :param max_steps: maximum number of steps to run algorithm for
        :param max_score: score to stop algorithm once reached
        """
        self.initial_state = initial_state

        if isinstance(tabu_tenure, int) and tabu_tenure > 0:
            self.tabu_size = tabu_tenure
        else:
            raise TypeError("Tabu size must be a positive integer")

        if isinstance(max_steps, int) and max_steps > 0:
            self.max_steps = max_steps
        else:
            raise TypeError("Maximum steps must be a positive integer")

        if isinstance(neighborhood_size, int) and tabu_tenure > 0:
            self.neighborhood_size = neighborhood_size
        else:
            raise TypeError("Neighborhood size must be a positive integer")

        if isinstance(print_interval, int):
            self.print_interval = print_interval
        else:
            raise TypeError("Interval must be a positive integer")

        self.constraints = constraints

        if max_score is not None:
            if isinstance(max_score, (int, float)):
                self.max_score = float(max_score)
            else:
                raise TypeError("Maximum score must be a numeric type")

    def __str__(self):
        return (
            "TABU SEARCH: \n"
            + "CURRENT STEPS: %d \n"
            + "BEST SCORE: %f \n"
            + "BEST MEMBER: %s \n\n"
        ) % (self.cur_steps, self._score(self.best), str(self.best))

    def __repr__(self):
        return self.__str__()

    def _clear(self):
        """
        Resets the variables that are altered on a per-run basis of the algorithm

        :return: None
        """
        self.cur_steps = 0
        self.tabu_list = deque(maxlen=self.tabu_size)
        self.current = self.initial_state
        self.best = self.initial_state

    @abstractmethod
    def _score(self, state):
        """
        Returns objective function value of a state

        :param state: a state
        :return: objective function value of state
        """
        pass

    @abstractmethod
    def _neighborhood(self):
        """
        Returns list of all members of neighborhood of current state, given self.current

        :return: list of members of neighborhood, changed attributes
        """
        pass

    def _best(self, neighborhood, attribute_change):
        """
        Finds the best member of a neighborhood

        :param neighborhood: a neighborhood
        :return: best member of neighborhood
        """

        indices = argmax([self._score(x) for x in neighborhood])

        return neighborhood[indices], attribute_change[indices]

    def run(self, verbose=True):
        """
        Conducts tabu search

        :param verbose: indicates whether or not to print progress regularly
        :return: best state and objective function value of best state
        """
        self._clear()
        for i in range(self.max_steps):
            self.cur_steps += 1

            if ((i + 1) % self.print_interval == 0) and verbose:
                print(self)

            neighborhood, attribute_change = self._neighborhood()
            neighborhood_best, attribute_change_best = self._best(
                neighborhood, attribute_change
            )

            while True:
                if all([x in self.tabu_list for x in attribute_change]):
                    print("TERMINATING - NO SUITABLE NEIGHBORS")
                    return self.best, self._score(self.best)
                if attribute_change_best in self.tabu_list:
                    # aspriration criteria
                    if self._score(neighborhood_best) > self._score(self.best):
                        self.tabu_list.append(attribute_change_best)
                        self.best = deepcopy(neighborhood_best)
                        break
                    else:
                        neighborhood.remove(neighborhood_best)
                        attribute_change.remove(attribute_change_best)
                        neighborhood_best, attribute_change_best = self._best(
                            neighborhood, attribute_change
                        )
                else:
                    self.tabu_list.append(attribute_change_best)
                    self.current = neighborhood_best
                    if self._score(self.current) > self._score(self.best):
                        self.best = deepcopy(self.current)
                    break

            if self.max_score is not None and self._score(self.best) > self.max_score:
                if verbose:
                    print("TERMINATING - REACHED MAXIMUM SCORE")
                return self.best, self._score(self.best)
        if verbose:
            print("TERMINATING - REACHED MAXIMUM STEPS")
        return self.best, self._score(self.best)
