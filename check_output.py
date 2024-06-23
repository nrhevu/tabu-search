import argparse

import numpy as np

from src.model.modeling import ClassCourseTeacherAssignmentProblem

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
        
    ########## RUN #############    
    problem = ClassCourseTeacherAssignmentProblem(
        N, T, class_subjects, subject_periods, None, None
    )    
    # Score
    print("SCORE: ", problem.get_score(assignments, opt.constraints))
    
    