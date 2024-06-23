# tabu-search

# HOW TO RUN
run command ```./run.sh``` or ```python tabusearch.py --score --time --file_path all --tabu_tenure 15 --neighborhood_size 70 --max_steps 500 --constraints 1 2 --early_stopping```

# HOW TO EVALUATE RESULT
The results will appear on the terminal screen in the following format:
Line 1: Path to the input.txt file of each test case
Line 2: MAX_SCORE is the number of subjects to sort
Line 3: SCORE is the number of classes-subjects for which the algorithm has been successfully organized (Can have a negative value if the solution violates the constraint)
Line 4: Total test case running time

Example:
"Test cases/test1/input.txt
MAX_SCORE:  170
SCORE: 164
Total run time: 87.46003293991089s"