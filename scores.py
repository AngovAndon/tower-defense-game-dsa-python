import os
from algorithms import insertion_sort_desc

SCORES_FILE = "scores.txt"


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        return [int(line.strip()) for line in f.readlines() if line.strip()]


def save_score(score):
    scores = load_scores()
    scores.append(int(score))

    # Custom sorting algorithm (no built-in .sort()).
    scores = insertion_sort_desc(scores)

    with open(SCORES_FILE, "w") as f:
        for s in scores[:10]:
            f.write(str(s) + "\n")
