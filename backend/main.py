from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from classifier import classify_problem, get_complexity_hint
from gemini_helper import get_ai_explanation

app = FastAPI(title="AlgoLens API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProblemRequest(BaseModel):
    problem_text: str

class AnalysisResponse(BaseModel):
    pattern: str
    confidence: str
    time_complexity: str
    space_complexity: str
    ai_explanation: str
    all_matches: dict

@app.get("/")
def root():
    return {"message": "AlgoLens API is live", "version": "1.0.0"}

@app.post("/analyze", response_model=AnalysisResponse)
def analyze_problem(request: ProblemRequest):
    # Step 1: Classify
    classification = classify_problem(request.problem_text)
    pattern = classification["pattern"]
    confidence = classification["confidence"]
    all_matches = classification["all_matches"]

    # Step 2: Get complexity
    complexity = get_complexity_hint(pattern)

    # Step 3: Get Gemini explanation
    ai_explanation = get_ai_explanation(
        request.problem_text,
        pattern,
        complexity
    )

    return AnalysisResponse(
        pattern=pattern,
        confidence=confidence,
        time_complexity=complexity["time"],
        space_complexity=complexity["space"],
        ai_explanation=ai_explanation,
        all_matches=all_matches
    )

@app.get("/patterns")
def list_patterns():
    patterns = [
        "Dynamic Programming", "Sliding Window", "Two Pointers",
        "Binary Search", "Graph / BFS / DFS", "Stack / Queue",
        "Recursion / Backtracking", "Greedy", "Hashing", "Linked List"
    ]
    return {"patterns": patterns, "total": len(patterns)}
