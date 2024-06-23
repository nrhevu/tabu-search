from random import choice, randint, random

import numpy as np


class ClassCourseTeacherAssignmentProblem:
    def __init__(self, N, T, class_subjects, subject_periods, subject_teachers, subject_times):
        self.N = N
        self.T = T
        self.class_subjects = class_subjects
        self.subject_periods = subject_periods
        self.subject_teachers = subject_teachers
        self.subject_times = subject_times

    def initialize_state(self, prob=0.3):
        assignments = []
        for class_n in range(1, self.N + 1):
            subjects = self.class_subjects[class_n]
            for subject in subjects:
                assignments.append([class_n, subject, 0, 0])

                if random() < prob:
                    self.change_both(assignments[-1])

        return assignments
    
    def get_maximum_score(self):
        result = self.initialize_state(prob = 1.0)
        score = 0
        final_result = []
        for r in result:
            if r[2] and r[3]:
                final_result.append(r)
                score += 1
                
        return score
    
    ##################################################################################################
    # Constraint
    # assignments (Class, Subject, Start time, Teacher)
    # Thời gian bắt đầu, kết thúc phải cùng buổi
    def check_same_session_time(self, assignments):
        time_violation = 0

        for assignment in assignments:
            if (assignment[2]) == 0:
                continue

            # start_time // 6 - end_time // 6 = 0
            start_time_session = (assignment[2] - 1) // 6
            end_time_session = (
                (assignment[2] + self.subject_periods[assignment[1]]) - 2
            ) // 6

            if start_time_session != end_time_session:
                # return False
                time_violation += 1

        # return True
        return time_violation

    # Các lớp-môn mà cùng giáo viên dạy không trùng lịch
    def check_teacher_schedule_conflicts(self, assignments):
        time_violation = 0

        # Mang luu trang thai cua cac giao vien tu tiet 1-60
        teacher_periods = np.zeros((self.T + 1, 61), dtype=int)

        for assignment in assignments:
            if assignment[3] == 0:
                continue

            start_time = assignment[2]
            end_time = (assignment[2] + self.subject_periods[assignment[1]]) - 1
            teacher = assignment[3]
            if np.all(teacher_periods[teacher, start_time : end_time + 1] == 0):
                teacher_periods[teacher, start_time : end_time + 1] = 1
            else:
                # return False
                time_violation += 1

        # return True
        return time_violation

    # Các môn của cùng lớp không trùng lịch
    def check_class_schedule_conflicts(self, assignments):
        time_violation = 0

        # Mang luu trang thai cua cac lop tu tiet 1-60
        classtable = np.zeros((self.N + 1, 61), dtype=int)

        for assignment in assignments:
            if assignment[2] == 0:
                continue

            class_n = assignment[0]
            start_time = assignment[2]
            end_time = (assignment[2] + self.subject_periods[assignment[1]]) - 1
            if np.all(classtable[class_n, start_time : end_time + 1] == 0):
                classtable[class_n, start_time : end_time + 1] = 1
            else:
                # return False
                time_violation += 1

        # return True
        return time_violation

    # Thời gian kết thúc không vượt quá 60 tiết
    def check_end_time_limit(self, assignments):
        time_violation = 0

        for assignment in assignments:
            # start_time // 6 - end_time // 6 = 0
            # start_time_session = assignment[2]
            end_time_session = (assignment[2] + self.subject_periods[assignment[1]]) - 1

            if end_time_session > 60:
                # return False
                time_violation += 1

        # return True
        return time_violation

    # Change assignment
    def change_teacher(self, assignment):
        assignable_teacher = self.subject_teachers[assignment[1]]

        if len(assignable_teacher) == 0:
            return True

        if len(assignable_teacher) == 1 and assignment[3] != 0:
            return

        new_teacher = assignment[3]
        while new_teacher == assignment[3]:
            new_teacher = choice(assignable_teacher)

        assignment[3] = new_teacher

    def change_time(self, assignment):
        new_start_time = assignment[2]
        subject = assignment[1]

        while new_start_time == assignment[2]:
            new_start_time = choice(self.subject_times[subject])

        assignment[2] = new_start_time

    def change_both(self, assignment):
        if self.change_teacher(assignment) is not None:
            return
        self.change_time(assignment)
        
    def get_score(self, assignments, constraints):
        score = 0
        # Penalty
        if 0 in constraints:
            session_violations = self.check_same_session_time(assignments)
        else :
            session_violations = 0
            
        if 1 in constraints:
            class_violations = self.check_class_schedule_conflicts(assignments)
        else:
            class_violations = 0
            
        if 2 in constraints:
            teacher_violations = self.check_teacher_schedule_conflicts(assignments)
        else:
            teacher_violations = 0
        
        if 3 in constraints:
                endtimelimit_violations = self.check_end_time_limit(assignments)
        else: 
            endtimelimit_violations = 0
        
        score -= 100 * (session_violations + class_violations + teacher_violations + endtimelimit_violations)
            
        for assignment in assignments:
            if assignment[2] and assignment[3]:
                score += 1
                
        return score