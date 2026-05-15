from typing import List, Optional

from pydantic import BaseModel, Field


class GitHubAnalyzeRequest(BaseModel):
    repo_url: str = Field(..., min_length=10, max_length=500)


class GitHubRepoMeta(BaseModel):
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int
    forks: int
    topics: List[str]
    default_branch: str


class GitHubAnalyzeResponse(BaseModel):
    meta: GitHubRepoMeta
    file_tree: List[str]
    ai_analysis: str
