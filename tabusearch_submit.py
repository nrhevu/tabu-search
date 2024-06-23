import argparse
import logging
import math
import os
import time
from copy import deepcopy
from random import choice, randint, random
import itertools
import glob

import numpy as np 
################################# Tabu Search ######################################################
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from collections import deque
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

    def __init__(self, initial_state, tabu_tenure, max_steps, neighborhood_size,
                 constraints = [0, 1, 2, 3], print_interval=100, max_score=None):
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
            raise TypeError('Tabu size must be a positive integer')

        if isinstance(max_steps, int) and max_steps > 0:
            self.max_steps = max_steps
        else:
            raise TypeError('Maximum steps must be a positive integer')

        if isinstance(neighborhood_size, int) and tabu_tenure > 0:
            self.neighborhood_size = neighborhood_size
        else:
            raise TypeError('Neighborhood size must be a positive integer')
        
        if isinstance(print_interval, int):
            self.print_interval = print_interval
        else:
            raise TypeError('Interval must be a positive integer')
        
        self.constraints = constraints
        
        if max_score is not None:
            if isinstance(max_score, (int, float)):
                self.max_score = float(max_score)
            else:
                raise TypeError('Maximum score must be a numeric type')

    def __str__(self):
        return ('TABU SEARCH: \n' +
                'CURRENT STEPS: %d \n' +
                'CURRENT SCORE: %d \n' +
                'BEST SCORE: %f \n' +
                'BEST MEMBER: %s \n\n') % \
               (self.cur_steps, self._score(self.current), self._score(self.best), str(self.best))

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
            neighborhood_best, attribute_change_best = self._best(neighborhood, attribute_change)

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
                        neighborhood_best, attribute_change_best = self._best(neighborhood, attribute_change)
                else:
                    self.tabu_list.append(attribute_change_best)
                    self.current = neighborhood_best
                    if self._score(self.current) > self._score(self.best):
                        self.best = deepcopy(self.current)
                    break
                
            # print(self.tabu_list)

            if self.max_score is not None and self._score(self.best) >= self.max_score:
                if verbose:
                    print("TERMINATING - REACHED MAXIMUM SCORE")
                return self.best, self._score(self.best)
        if verbose:
            print("TERMINATING - REACHED MAXIMUM STEPS")
        return self.best, self._score(self.best)
##################################################################################################
# Constraint
# assignments (Class, Subject, Start time, Teacher)
# Thời gian bắt đầu, kết thúc phải cùng buổi
def check_same_session_time(assignments):
    time_violation = 0
    
    for assignment in assignments:
        if(assignment[2]) == 0:
            continue
        
        # start_time // 6 - end_time // 6 = 0 
        start_time_session = (assignment[2] - 1) // 6
        end_time_session = ((assignment[2] + subject_periods[assignment[1]]) - 2) // 6
        
        if start_time_session != end_time_session:
            # return False
            time_violation += 1
        
    # return True
    return time_violation
            
# Các lớp-môn mà cùng giáo viên dạy không trùng lịch
def check_teacher_schedule_conflicts(assignments):
    time_violation = 0
    
    # Mang luu trang thai cua cac giao vien tu tiet 1-60
    teacher_periods = np.zeros((T + 1, 61), dtype=int) 
    
    for assignment in assignments:
        if assignment[3] == 0:
            continue
        
        start_time = assignment[2]
        end_time = (assignment[2] + subject_periods[assignment[1]]) - 1
        teacher = assignment[3]
        if np.all(teacher_periods[teacher, start_time: end_time + 1] == 0):
            teacher_periods[teacher, start_time: end_time + 1] = 1
        else:
            # return False
            time_violation += 1
        
    # return True
    return time_violation

# Các môn của cùng lớp không trùng lịch
def check_class_schedule_conflicts(assignments):
    time_violation = 0
    
    # Mang luu trang thai cua cac lop tu tiet 1-60
    classtable = np.zeros((N + 1, 61), dtype=int) 
    
    for assignment in assignments:
        if assignment[2] == 0:
            continue
        
        class_n = assignment[0]
        start_time = assignment[2]
        end_time = (assignment[2] + subject_periods[assignment[1]]) - 1
        if np.all(classtable[class_n, start_time: end_time + 1] == 0):
            classtable[class_n, start_time: end_time + 1] = 1
        else: 
            # return False
            time_violation += 1
        
    # return True
    return time_violation

# Thời gian kết thúc không vượt quá 60 tiết
def check_end_time_limit(assignments):
    time_violation = 0
    
    for assignment in assignments:
        # start_time // 6 - end_time // 6 = 0 
        # start_time_session = assignment[2]
        end_time_session = ((assignment[2] + subject_periods[assignment[1]]) - 1)
        
        if end_time_session > 60:
            # return False
            time_violation += 1
        
    # return True
    return time_violation

# Change assignment
def change_teacher(assignment):
    assignable_teacher = subject_teachers[assignment[1]]
    
    if len(assignable_teacher) == 0:
        return True
    
    if len(assignable_teacher) == 1 and assignment[3] != 0:
        return
    
    new_teacher = assignment[3]
    while new_teacher == assignment[3]:
        new_teacher = choice(assignable_teacher)
        
    assignment[3] = new_teacher
def change_time(assignment):
    new_start_time = assignment[2]
    subject = assignment[1]
    
    while new_start_time == assignment[2]:
        new_start_time = choice(subject_times[subject])
        
    assignment[2] = new_start_time
def change_both(assignment):
    if change_teacher(assignment) is not None:
        return
    change_time(assignment)

CHANGE_STRATEGY = [change_teacher, change_time, change_both]
# Algorithms
class Algorithm(TabuSearch):
    """
    Tries to get a randomly-generated classtable 
    """
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
            CHANGE_STRATEGY[change_strategy_choice](candidate)
            
            neighborhood.append(neighbor)
            # attribute_change.append((choice, candidate[2], candidate[3]))
            attribute_change.append((choice))
        return neighborhood, attribute_change

    def _score(self, assignments):
        score = 0
        # Penalty
        if 0 in self.constraints:
            session_violations = check_same_session_time(assignments)
        else :
            session_violations = 0
            
        if 1 in self.constraints:
            class_violations = check_class_schedule_conflicts(assignments)
        else:
            class_violations = 0
            
        if 2 in self.constraints:
            teacher_violations = check_teacher_schedule_conflicts(assignments)
        else:
            teacher_violations = 0
        
        if 3 in self.constraints:
            endtimelimit_violations = check_end_time_limit(assignments)
        else: 
            endtimelimit_violations = 0
        
        score -= 100 * (session_violations + class_violations + teacher_violations + endtimelimit_violations)
        
        # Score
        for assignment in assignments:
            if assignment[2] and assignment[3]:
                score += 1
                
        return score
    
def initialize_state(N, class_subjects, prob = 0.3):
    assignments = []
    for class_n in range(1, N + 1):
        subjects = class_subjects[class_n]
        for subject in subjects:
            assignments.append([class_n, subject, 0, 0])
            
            if random() < prob:
                change_both(assignments[-1])
            
    return assignments

def get_maximum_score(N, class_subjects):
    result = initialize_state(N, class_subjects, prob = 1.0)
    score = 0
    final_result = []
    for r in result:
        if r[2] and r[3]:
            final_result.append(r)
            score += 1
            
    return score

def print_final_result(result):
    score = 0
    final_result = []
    for r in result:
        if r[2] and r[3]:
            final_result.append(r)
            score += 1
            
    print(score)
    for r in final_result:
        print(r[0], r[1], r[2], r[3])
        
def write_final_result(result, filename):
    score = 0
    final_result = []
    for r in result:
        if r[2] and r[3]:
            final_result.append(r)
            score += 1
    
    with open(filename, "w") as f:   
        f.writelines(str(score) + "\n")
        for r in final_result:
            f.writelines(f"{r[0]} {r[1]} {r[2]} {r[3]}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--tabu_tenure', type=int, default=105, help='tabu tenure size')
    parser.add_argument('--max_steps', type=int, default=500, help='max number of steps')
    parser.add_argument('--neighborhood_size', type=int, default=70, help='neighborhood size')
    parser.add_argument('--constraints', nargs='+', type=int, default=[1, 2], help='constraints for evaluating score:\n 0 - session constraint \n 1 - class schedule constraint \n 2 - teacher schedule constraint')
    parser.add_argument('--verbose', action='store_true', help='print progress')
    parser.add_argument('--interval', type=int, default=100, help='set interval of printing results')
    parser.add_argument('--score', action='store_true', help='print score')
    parser.add_argument('--time', action='store_true', help='print total running time')
    parser.add_argument('--keyboard', action='store_true', help='input is obtained from the keyboard')
    parser.add_argument('--file_path', type=str, default='input.txt', help='input is obtained from the file')
    
    opt = parser.parse_args()
    
    # Read from keyboard
    T, N, M = map(int, input().split())
    
    class_subjects = []
    class_subjects.append([])
    for _ in range(N):
        subjects = list(map(int, input().split()))
        class_subjects.append(subjects[:-1])
        
    teacher_subjects = []
    teacher_subjects.append([])
    for _ in range(T):
        subjects = list(map(int, input().split()))
        teacher_subjects.append(subjects[:-1])
    
    subject_periods = list(map(int, input().split()))
    subject_periods.insert(0, [])
    
    # Make subject teachers list
    subject_teachers = [[] for i in range(M + 1)]
    for teacher, subjects in enumerate(teacher_subjects):
        for subject in subjects:
            subject_teachers[subject].append(teacher)
            
    # Make choiceable time for each subject
    subject_times = [[i for i in range(1, 61)] for i in range(M + 1)]
    six_multiples = [s * 6 for s in range(1, 11)]
    for subject, subject_period in enumerate(subject_periods):
        if subject == 0:
            continue
        for s in six_multiples:
            for i in range(subject_periods[subject] - 1):
                subject_times[subject].remove(s - i)
    
    # Initialize algorithm
    if True:
        max_score = get_maximum_score(N, class_subjects)
        print("MAX_SCORE: ", max_score)
    else:
        max_score = None
    
    start_time = time.time()
    # Initialize algorithm
    algorithm = Algorithm(initialize_state(N, class_subjects), opt.tabu_tenure, 
                          opt.max_steps, opt.neighborhood_size, 
                          constraints=opt.constraints, print_interval=opt.interval, max_score=max_score)
    result, score = algorithm.run(verbose=opt.verbose)
            
    print_final_result(result)        

    if opt.score:
        print(f"SCORE: {score}")
    
    if opt.time:
        print(f"Total run time: {time.time() - start_time}s")