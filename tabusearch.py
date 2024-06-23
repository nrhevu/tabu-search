import argparse
import glob
import os
import time

from src.model.algorithm import TabuSearchAlgorithm
from src.model.modeling import ClassCourseTeacherAssignmentProblem


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


def run(opt, N, T, class_subjects, subject_periods, subject_teachers, subject_times):
    # Initialize problem modeling
    problem = ClassCourseTeacherAssignmentProblem(
        N, T, class_subjects, subject_periods, subject_teachers, subject_times
    )
    # Initialize algorithm
    if opt.early_stopping:
        max_score = problem.get_maximum_score()
        print("MAX_SCORE: ", max_score)
    else:
        max_score = None
    algorithm = TabuSearchAlgorithm(
        problem,
        problem.initialize_state(),
        opt.tabu_tenure,
        opt.max_steps,
        opt.neighborhood_size,
        constraints=opt.constraints,
        print_interval=opt.interval,
        max_score=max_score,
    )
    result, score = algorithm.run(verbose=opt.verbose)
    if opt.dynamic_tenure:
        tabu_tenure = opt.tabu_tenure
        max_steps = opt.max_steps
        for _ in range(opt.dynamic_loop):
            tabu_tenure *= 10
            max_steps *= 0.7
            max_steps = int(max_steps)
            algorithm = TabuSearchAlgorithm(
                problem,
                result,
                tabu_tenure,
                max_steps,
                opt.neighborhood_size,
                constraints=opt.constraints,
                print_interval=opt.interval,
                max_score=None,
            )
            result, score = algorithm.run(verbose=opt.verbose)

    return result, score


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tabu_tenure", type=int, default=10, help="tabu tenure size")
    parser.add_argument(
        "--max_steps", type=int, default=1000, help="max number of steps"
    )
    parser.add_argument(
        "--neighborhood_size", type=int, default=10, help="neighborhood size"
    )
    parser.add_argument(
        "--constraints",
        nargs="+",
        type=int,
        default=[0, 1, 2, 3],
        help="constraints for evaluating score:\n 0 - a class must be within the same session. \
                                                               \n 1 - a class cannot have two subjects taught at the same time. \
                                                               \n 2 - a teacher cannot teach two classes at the same time. \
                                                               \n 3 - last class end time must not exceed 60",
    )
    parser.add_argument(
        "--keyboard", action="store_true", help="input is obtained from the keyboard"
    )
    parser.add_argument(
        "--file_path",
        type=str,
        default="input.txt",
        help="input is obtained from the file",
    )
    parser.add_argument("--verbose", action="store_true", help="print progress")
    parser.add_argument(
        "--early_stopping",
        action="store_true",
        help="early stop when reached maximum score",
    )
    parser.add_argument(
        "--interval", type=int, default=100, help="set interval of printing results"
    )
    parser.add_argument(
        "--dynamic_tenure",
        action="store_true",
        help="tabu tenure will increase by 10 each max_steps",
    )
    parser.add_argument(
        "--dynamic_loop",
        type=int,
        default=10,
        help="set loop when using dynamic strategy",
    )
    parser.add_argument("--score", action="store_true", help="print score")
    parser.add_argument("--time", action="store_true", help="print total running time")

    opt = parser.parse_args()

    if opt.file_path == "all":
        for file_path in glob.glob("test/test*/input.txt"):
            # Read_from_file
            # file_path = opt.file_path
            print(file_path)

            # Đọc dữ liệu từ file txt
            with open(file_path, "r") as file:
                lines = file.readlines()

            # Chuyển đổi dữ liệu đọc được thành các giá trị số
            T, N, M = map(int, lines[0].split())
            class_subjects = []
            class_subjects.append([])
            for i in range(1, N + 1):
                subjects = list(map(int, lines[i].split()))
                class_subjects.append(subjects[:-1])

            teacher_subjects = []
            teacher_subjects.append([])
            for i in range(N + 1, N + T + 1):
                subjects = list(map(int, lines[i].split()))
                teacher_subjects.append(subjects[:-1])

            subject_periods = list(map(int, lines[N + T + 1].split()))
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

            start_time = time.time()
            result, score = run(
                opt,
                N,
                T,
                class_subjects,
                subject_periods,
                subject_teachers,
                subject_times,
            )

            # print_final_result(result)
            filename = os.path.join(os.path.dirname(file_path), "pred.txt")
            write_final_result(result, filename)

            if opt.score:
                print(f"SCORE: {score}")

            if opt.time:
                print(f"Total run time: {time.time() - start_time}s")

        exit()

    # Input
    if opt.keyboard:
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
    else:
        # Read_from_file
        file_path = opt.file_path

        # Đọc dữ liệu từ file txt
        with open(file_path, "r") as file:
            lines = file.readlines()

        # Chuyển đổi dữ liệu đọc được thành các giá trị số
        T, N, M = map(int, lines[0].split())
        class_subjects = []
        class_subjects.append([])
        for i in range(1, N + 1):
            subjects = list(map(int, lines[i].split()))
            class_subjects.append(subjects[:-1])

        teacher_subjects = []
        teacher_subjects.append([])
        for i in range(N + 1, N + T + 1):
            subjects = list(map(int, lines[i].split()))
            teacher_subjects.append(subjects[:-1])

        subject_periods = list(map(int, lines[N + T + 1].split()))
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

    start_time = time.time()
    result, score = run(
        opt,
        N,
        T,
        class_subjects,
        subject_periods,
        subject_teachers,
        subject_times,
    )
    print_final_result(result)

    if opt.score:
        print(f"SCORE: {score}")

    if opt.time:
        print(f"Total run time: {time.time() - start_time}s")
