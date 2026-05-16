ANALYZE_PROMPT = """You are an expert software engineer and coding interview coach.

Problem Statement:
{problem_text}

Detected Pattern: {pattern}

Give a concise response in this exact format:

TIME_COMPLEXITY: (e.g. O(n), O(n log n), O(1) — always provide this, infer from the algorithm)
SPACE_COMPLEXITY: (e.g. O(n), O(1) — always provide this, infer from the algorithm)

APPROACH:
(2-3 lines explaining the optimal approach)

PSEUDOCODE:
(clean step-by-step pseudocode)

KEY INSIGHT:
(one line — the "aha moment" for this problem)

OPTIMIZATION:
(2-3 bullet points on time/space optimizations and tradeoffs)

EDGE CASES:
(3-4 bullet points on edge cases to discuss in interviews)

SIMILAR PROBLEMS:
(3 LeetCode-style problem names)

IMPORTANT: Always fill TIME_COMPLEXITY and SPACE_COMPLEXITY. Never leave them blank.
"""

INTERVIEW_START_PROMPT = """You are a senior software engineer conducting a technical interview.

Problem:
{problem_text}

Pattern hint: {pattern}

Ask ONE challenging follow-up question about approach, optimization, or edge cases.
Keep it under 3 sentences. Be realistic and professional.
"""

INTERVIEW_EVALUATE_PROMPT = """You are evaluating a candidate's interview answer.

Problem: {problem_text}
Question asked: {question}
Candidate answer: {answer}

Respond in this exact format:

SCORE: (1-10)

FEEDBACK:
(2-3 sentences on strengths and gaps)

FOLLOW_UP:
(one follow-up question about optimization, edge cases, or complexity — or "DONE" if interview should end)
"""

# User-supplied path lists and README are concatenated — never passed through str.format.
GITHUB_ANALYSIS_PROMPT_META = """You are a senior staff engineer reviewing a public GitHub repository.

Use plain-text section headings exactly as shown (e.g. OVERVIEW:). Do not prefix lines with # markdown characters.

Repository: {repo_full_name}
Description: {description}
GitHub primary language: {language}
GitHub topics: {topics}

Detected languages (bytes of code, GitHub API):
{languages_block}

A newline-separated path listing from the GitHub Contents API is appended after PATH_LIST (may be truncated).
"""

GITHUB_ANALYSIS_PROMPT_TAIL = """
Respond in this EXACT section format (headings verbatim):

OVERVIEW:
(2-4 sentences: purpose, audience, maturity)

ARCHITECTURE:
(bullet points: layout, major modules, how pieces fit)

TECH_STACK:
(bullet points: frameworks, tooling inferred from paths/topics/languages)

STRENGTHS:
(bullet points)

WEAKNESSES:
(bullet points)

SCALABILITY:
(bullet points: scaling limits, bottlenecks, ops concerns)

CODE_QUALITY:
(bullet points: consistency, testing — infer only from structure)

README_SUGGESTIONS:
(bullet points)

RECOMMENDATIONS:
(bullet points: 3-7 prioritized actions)

Use cautious wording when inferring ("likely", "appears"). Do not claim files exist unless listed in PATH_LIST or README_EXCERPT.

PATH_LIST
"""

GITHUB_ANALYSIS_README_MARKER = """
--- README_EXCERPT (may be empty) ---
"""
