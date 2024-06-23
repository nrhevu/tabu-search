import time

import numpy as np

start = time.time()


# Kiem tra giao vien co lich khong
def check_teacher(teacher, start_time, periods):
    end_time = start_time + periods
    return np.all(teacher_periods[teacher - 1, start_time : end_time + 1] == 0)


# Kiem tra thoi gian chung 1 buoi khong
def check_time(start_time, periods):
    end_time = start_time + periods
    end_time = int(end_time / 6)
    start_time = int(start_time / 6)
    if start_time == end_time:
        return True

    return False


# Kiem tra giao vien phu hop voi so tiet day dang la it nhat
def search_candidate(list_candidate):
    if len(list_candidate) == 1:
        return list_candidate[0]
    min = 100
    teacher = list_candidate[0]
    for can in list_candidate:
        unique_values = np.unique(teacher_periods[can])
        periods = np.count_nonzero(unique_values)
        if periods < min:
            min = periods
            teacher = can

    return teacher


# Kiem tra lop co dang duoc su dung khong
def check_lop(num_class, start_time, periods):
    end_time = start_time + periods
    return np.all(classtable[num_class - 1, start_time : end_time + 1] == 0)


def assign_classtable(T, N, M, class_subjects, teacher_subjects, subject_periods):
    # Xay dung cac bo theo dang (lop, mon, so tiet cua mon)
    class_subjects_list = []
    for i in range(N):
        subjects = class_subjects[i]
        for subject in subjects:
            class_subjects_list.append((i + 1, subject, subject_periods[subject - 1]))

    # Sap xep theo so tiet tang dan
    class_subjects_list.sort(key=lambda x: x[2], reverse=False)

    # Duyet qua cac bo
    for k, class_subject in enumerate(class_subjects_list):
        class_num, subject, periods = class_subject
        assigned_teacher = None
        list_candidate = []

        for t in range(T):
            # Lay danh sach giao vien phu hop
            if subject in teacher_subjects[t]:
                list_candidate.append(t)

        if len(list_candidate) == 0:
            continue

        teacher = search_candidate(list_candidate=list_candidate) + 1

        for i in range(60):
            # Kiem tra tung tiet
            if (
                check_lop(class_num, i, periods)
                and check_teacher(teacher, i, periods)
                and check_time(i, periods)
            ):
                assigned_teacher = teacher
                class_subjects_list[k] = class_subject + (
                    i + 1,
                    teacher,
                )

                for index in range(i, i + periods + 1):
                    # Them tiet vao phan cong
                    classtable[class_num - 1, index] = 1
                    teacher_periods[teacher - 1, index] = i

                break
            if assigned_teacher is not None:
                break

    # Ouput
    class_subjects_list.sort(key=lambda x: x[0])
    count = 0
    for c in class_subjects_list:
        if len(c) == 5:
            count += 1

    print(count)
    for c in class_subjects_list:
        if len(c) == 5:
            print(c[0], c[1], c[3], c[4])

    # print(teacher_periods)


"""
Input:
3 5 4
2 4 0
2 3 4 0
2 3 0
1 2 4 0
1 3 0
1 3 0
2 3 0
1 2 4 0
2 4 4 4
"""


# Read_from_file
# file_path = "/home/hieunguyen/DHBK/tulkh/phan_cong/Test-cases/Test cases/test10/input.txt"

# with open(file_path, 'r') as file:
#     lines = file.readlines()

# # Chuyển đổi dữ liệu đọc được thành các giá trị số
# T, N, M = map(int, lines[0].split())
# class_subjects = []
# for i in range(1, N+1):
#     subjects = list(map(int, lines[i].split()))
#     class_subjects.append(subjects[:-1])

# teacher_subjects = []
# for i in range(N+1, N+T+1):
#     subjects = list(map(int, lines[i].split()))
#     teacher_subjects.append(subjects[:-1])

# subject_periods = list(map(int, lines[N+T+1].split()))

# Read from keyboard
T, N, M = map(int, input().split())
class_subjects = []
for _ in range(N):
    subjects = list(map(int, input().split()))
    class_subjects.append(subjects[:-1])
teacher_subjects = []
for _ in range(T):
    subjects = list(map(int, input().split()))
    teacher_subjects.append(subjects[:-1])
subject_periods = list(map(int, input().split()))

classtable = np.zeros(
    (N, 60), dtype=int
)  # Mang luu trang thai cua cac lop tu tiet 1-60
teacher_periods = np.zeros(
    (T, 60), dtype=int
)  # Mang luu trang thai cua cac giao vien tu tiet 1-60

# Sovle
assign_classtable(T, N, M, class_subjects, teacher_subjects, subject_periods)
end = time.time()

print(end - start)
