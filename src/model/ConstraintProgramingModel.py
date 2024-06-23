import argparse
import sys
import time
from typing import NamedTuple

import numpy as np
from ortools.sat.python import cp_model


class Input(NamedTuple):
    T: int
    N: int
    M: int
    K: int
    H: list
    G: list
    D: list


class Variable(NamedTuple):
    Start: np.array
    End: np.array
    Range: np.array
    X: np.array
    Mask: np.array
    MaskT: np.array


def get_input():
    T, N, M = list(map(int, input().strip().split()))
    K = 5 * 2 * 6  # So tiet hoc trong 1 tuan
    H = []
    for _ in range(N):
        H.append(
            list(map(int, input().strip().split()))[:-1]
        )  # So tiet hoc cua mon hoc m d[m]
    G = []
    for _ in range(T):
        G.append(list(map(int, input().strip().split()))[:-1])
    D = list(map(int, input().strip().split()))

    return Input(T=T, N=N, M=M, K=K, H=H, G=G, D=D)


def init_int_domain():
    domains = []
    for i in range(data.M):
        domains.append(cp_model.Domain.FromValues([0, data.D[i]]))
    return domains


def init_variables():
    N, M, T, K = data.N, data.M, data.T, data.K
    X = np.zeros((N, M, T), dtype=cp_model.IntervalVar)
    Mask = np.zeros((N, M), dtype=cp_model.IntVar)
    MaskT = np.zeros((N, M, T), dtype=cp_model.IntVar)
    Start = np.zeros((N, M, T), dtype=cp_model.IntVar)
    End = np.zeros((N, M, T), dtype=cp_model.IntVar)
    Range = np.zeros((N, M, T), dtype=cp_model.IntVar)

    for n in range(N):
        for m in range(M):
            if m in data.H[n]:
                Mask[n, m] = model.NewBoolVar(f"mask[{n},{m}]")
            else:
                Mask[n, m] = 0

    for n in range(N):
        for m in range(M):
            for t in range(T):
                if m in data.H[n] and m in data.G[t]:
                    Start[n, m, t] = model.NewIntVar(0, K, f"start[{n},{m},{t}]")
                    End[n, m, t] = model.NewIntVar(0, K, f"end[{n},{m},{t}]")
                    Range[n, m, t] = model.NewIntVarFromDomain(
                        domains[m], f"range[{n},{m},{t}]"
                    )
                    MaskT[n, m, t] = model.NewBoolVar(f"mask_t[{n},{m},{t}]")
                    X[n, m, t] = model.NewIntervalVar(
                        Start[n, m, t], Range[n, m, t], End[n, m, t], f"X[{n},{m},{t}]"
                    )
                else:
                    Start[n, m, t] = 0
                    End[n, m, t] = 0
                    Range[n, m, t] = 0
                    MaskT[n, m, t] = 0
                    X[n, m, t] = 0

    return Variable(Start, End, Range, X, Mask, MaskT)


def normalize(data):
    for i in range(len(data.H)):
        for j in range(len(data.H[i])):
            data.H[i][j] = data.H[i][j] - 1

    for i in range(len(data.G)):
        for j in range(len(data.G[i])):
            data.G[i][j] = data.G[i][j] - 1


# Ràng buộc
def add_valid_time_constraint():
    """
    Thời gian bắt đầu, kết thúc phải cùng buổi
    """
    N, M, T = data.N, data.M, data.T

    for n in range(data.N):
        for m in data.H[n]:
            for t in range(data.T):
                if m in data.G[t]:
                    div_start = model.NewIntVar(0, 9, "")
                    div_end = model.NewIntVar(0, 9, "")
                    model.AddDivisionEquality(div_start, variables.Start[n, m, t], 6)
                    model.AddDivisionEquality(div_end, variables.End[n, m, t] - 1, 6)
                    model.Add(div_start == div_end).OnlyEnforceIf(
                        variables.MaskT[n, m, t]
                    )


def add_mask_constraint():
    N, M, T = data.N, data.M, data.T
    for n in range(N):
        for m in data.H[n]:
            literals = []
            for t in range(T):
                if m in data.G[t]:
                    model.Add(variables.Range[n, m, t] == data.D[m]).OnlyEnforceIf(
                        variables.MaskT[n, m, t]
                    )
                    model.Add(variables.Range[n, m, t] == 0).OnlyEnforceIf(
                        variables.MaskT[n, m, t].Not()
                    )
                    literals.append(variables.MaskT[n, m, t])
            sum_literals = np.sum(literals, dtype=cp_model.IntVar)
            model.Add(sum_literals == 1).OnlyEnforceIf(variables.Mask[n, m])
            model.Add(sum_literals == 0).OnlyEnforceIf(variables.Mask[n, m].Not())


def add_at_most_teacher_constraint():
    """
    Mỗi lớp-môn chỉ có thể có tối đa 1 gv.
    Nếu lớp-môn không có giáo viên thì lớp đó không được xếp lịch
    """
    N, M, T = data.N, data.M, data.T
    for n in range(N):
        for m in data.H[n]:
            literals = []
            for t in range(T):
                if m in data.G[t]:
                    literals.append(variables.MaskT[n, m, t])
            model.AddAtMostOne(literals)


def add_no_overlap_courses_of_class_constraint():
    """Các môn của cùng lớp không trùng lịch"""
    for n in range(data.N):
        courses = []
        for m in data.H[n]:
            for t in range(data.T):
                if m in data.G[t]:
                    courses.append(variables.X[n, m, t])
        model.AddNoOverlap(courses)


def add_no_overlap_class_courses_of_teacher_constraint():
    """Các lớp-môn mà cùng giáo viên dạy không trùng lịch"""
    for t in range(data.T):
        class_courses = []
        for n in range(data.N):
            for m in range(data.M):
                if m in data.G[t] and m in data.H[n]:
                    class_courses.append(variables.X[n, m, t])

        model.AddNoOverlap(class_courses)


def objective_func():
    """
    Hàm mục tiêu: Số lượng lớp-môn được gán lịch là lớn nhất
    """
    value = 0
    for n in range(data.N):
        for m in data.H[n]:
            value += variables.Mask[n, m]
    return value


def find_first_lesson(mask):
    """# In kết quả tối ưu"""
    for i, k in enumerate(mask):
        if k:
            return i
    return -1


def print_result():
    print(int(solver.ObjectiveValue()))
    for n in range(data.N):
        for m in data.H[n]:
            if solver.Value(variables.Mask[n, m]):
                for t in range(data.T):
                    if solver.Value(variables.MaskT[n, m, t]):
                        start = solver.Value(variables.Start[n, m, t])
                        end = solver.Value(variables.End[n, m, t])
                        print(f"{n + 1} {m + 1} {start + 1} {t + 1}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=str, default=None, help="path to input file txt"
    )
    parser.add_argument(
        "--output", type=str, default=None, help="path to output file txt"
    )

    args = parser.parse_args()
    if args.input is not None:
        sys.stdin = open(args.input, "r")
    if args.output is not None:
        sys.stdout = open(args.output, "w")

    data = get_input()
    normalize(data)

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    domains = init_int_domain()
    variables = init_variables()
    add_mask_constraint()
    add_valid_time_constraint()
    add_at_most_teacher_constraint()
    add_no_overlap_courses_of_class_constraint()
    add_no_overlap_class_courses_of_teacher_constraint()

    model.Maximize(objective_func())
    st_time = time.perf_counter()
    status = solver.Solve(model)
    print_result()
    ed_time = time.perf_counter()
    print("Status: ", solver.StatusName())
    print(ed_time - st_time, "s")
