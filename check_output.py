import argparse

import numpy as np


# Constraint
# assignments (Class, Subject, Start time, Teacher)
# Thời gian bắt đầu, kết thúc phải cùng buổi
def check_same_session_time(assignments):
    time_violation = 0
    
    for assignment in assignments:
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
        start_time_session = assignment[2]
        end_time_session = ((assignment[2] + subject_periods[assignment[1]]) - 1)
        
        if end_time_session > 60:
            # return False
            time_violation += 1
        
    # return True
    return time_violation

def get_score(assignments, constraints):
    score = 0
    # Penalty
    if 0 in constraints:
        session_violations = check_same_session_time(assignments)
    else :
        session_violations = 0
        
    if 1 in constraints:
        class_violations = check_class_schedule_conflicts(assignments)
    else:
        class_violations = 0
        
    if 2 in constraints:
        teacher_violations = check_teacher_schedule_conflicts(assignments)
    else:
        teacher_violations = 0
    
    if 3 in constraints:
        endtimelimit_violations = check_end_time_limit(assignments)
    else: 
        endtimelimit_violations = 0
    
    score -= 100 * (session_violations + class_violations + teacher_violations + endtimelimit_violations)
        
    for assignment in assignments:
        if assignment[2] and assignment[3]:
            score += 1
            
    return score

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, default='./input.txt', help='path to input file txt')
    parser.add_argument('--output_path', type=str, default='./output.txt', help='path to output file txt')
    parser.add_argument('--constraints', nargs='+', type=int, default=[0, 1, 2, 3], 
                        help='constraints for evaluating score:\n 0 - a class must be within the same session. \
                                                               \n 1 - a class cannot have two subjects taught at the same time. \
                                                               \n 2 - a teacher cannot teach two classes at the same time. \
                                                               \n 3 - last class end time must not exceed 60')

    opt = parser.parse_args()
    
    # INPUT
    input_path = opt.input_path

    # Đọc dữ liệu từ file txt
    with open(input_path, 'r') as file:
        input = file.readlines()

    # Chuyển đổi dữ liệu đọc được thành các giá trị số
    T, N, M = map(int, input[0].split())
    class_subjects = []
    class_subjects.append([])
    for i in range(1, N+1):
        subjects = list(map(int, input[i].split()))
        class_subjects.append(subjects[:-1])

    teacher_subjects = []
    teacher_subjects.append([])
    for i in range(N+1, N+T+1):
        subjects = list(map(int, input[i].split()))
        teacher_subjects.append(subjects[:-1])
        
    subject_periods = list(map(int, input[N+T+1].split()))
    subject_periods.insert(0, [])
    
    # OUTPUT
    output_path = opt.output_path

    # Đọc dữ liệu từ file txt
    with open(output_path, 'r') as file:
        output = file.readlines()
        
    O = int(output[0])
    
    assignments = []
    for i in range(1, O+1):
        assignment = list(map(int, output[i].split()))
        assignments.append(assignment)
        
    # Score
    print("SCORE: ", get_score(assignments, opt.constraints))
    
    