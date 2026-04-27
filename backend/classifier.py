def classify_problem(problem_text: str) -> dict:
    problem = problem_text.lower()

    patterns = {
        "Dynamic Programming": [
            "maximum", "minimum", "longest", "shortest", "count ways",
            "fibonacci", "knapsack", "subsequence", "subset sum", "optimal"
        ],
        "Sliding Window": [
            "subarray", "substring", "window", "consecutive", "contiguous",
            "maximum sum subarray", "minimum window"
        ],
        "Two Pointers": [
            "two sum", "pair", "sorted array", "palindrome", "reverse",
            "three sum", "container with water"
        ],
        "Binary Search": [
            "sorted", "search", "find position", "rotated", "peak element",
            "log n", "divide"
        ],
        "Graph / BFS / DFS": [
            "graph", "tree", "connected", "path", "cycle", "island",
            "bfs", "dfs", "shortest path", "visited", "matrix"
        ],
        "Stack / Queue": [
            "stack", "queue", "bracket", "parenthesis", "next greater",
            "monotonic", "valid expression"
        ],
        "Recursion / Backtracking": [
            "permutation", "combination", "generate all", "backtrack",
            "n queens", "sudoku", "all possible"
        ],
        "Greedy": [
            "greedy", "interval", "activity selection", "minimum cost",
            "always pick", "locally optimal"
        ],
        "Hashing": [
            "frequency", "duplicate", "anagram", "hashmap", "count",
            "appeared", "unique"
        ],
        "Linked List": [
            "linked list", "node", "next pointer", "cycle detection",
            "merge", "reverse list"
        ],
    }

    scores = {}
    for pattern, keywords in patterns.items():
        score = sum(1 for kw in keywords if kw in problem)
        if score > 0:
            scores[pattern] = score

    if not scores:
        return {
            "pattern": "General / Unknown",
            "confidence": "Low",
            "all_matches": {}
        }

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_pattern = sorted_scores[0][0]
    top_score = sorted_scores[0][1]

    confidence = "High" if top_score >= 3 else "Medium" if top_score == 2 else "Low"

    return {
        "pattern": top_pattern,
        "confidence": confidence,
        "all_matches": dict(sorted_scores)
    }


def get_complexity_hint(pattern: str) -> dict:
    complexity_map = {
        "Dynamic Programming": {"time": "O(n²) or O(n)", "space": "O(n) or O(n²)"},
        "Sliding Window": {"time": "O(n)", "space": "O(1)"},
        "Two Pointers": {"time": "O(n)", "space": "O(1)"},
        "Binary Search": {"time": "O(log n)", "space": "O(1)"},
        "Graph / BFS / DFS": {"time": "O(V + E)", "space": "O(V)"},
        "Stack / Queue": {"time": "O(n)", "space": "O(n)"},
        "Recursion / Backtracking": {"time": "O(2^n) worst case", "space": "O(n)"},
        "Greedy": {"time": "O(n log n)", "space": "O(1)"},
        "Hashing": {"time": "O(n)", "space": "O(n)"},
        "Linked List": {"time": "O(n)", "space": "O(1)"},
    }
    return complexity_map.get(pattern, {"time": "Unknown", "space": "Unknown"})
