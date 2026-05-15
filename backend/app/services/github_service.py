from __future__ import annotations

import base64
import re
from urllib.parse import urlparse

import httpx

from app.config import get_settings
from app.llm.client import LLMClient
from app.schemas.github import (
    GitHubAnalyzeRequest,
    GitHubAnalyzeResponse,
    GitHubRepoMeta,
)

GITHUB_API = "https://api.github.com"
ALLOWED_HOSTS = {"github.com", "www.github.com"}


def _parse_repo_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url.strip())
    if parsed.netloc.lower() not in ALLOWED_HOSTS:
        raise ValueError("Only github.com repository URLs are allowed.")

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL. Use: https://github.com/owner/repo")

    owner, repo = parts[0], parts[1].removesuffix(".git")
    if not re.match(r"^[A-Za-z0-9_.-]+$", owner + repo):
        raise ValueError("Invalid owner or repository name.")

    return owner, repo


class GitHubService:
    def __init__(self) -> None:
        self._llm = LLMClient()
        self._settings = get_settings()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "AlgoLens/2.0",
        }
        if self._settings.github_token:
            headers["Authorization"] = f"Bearer {self._settings.github_token}"
        return headers

    async def analyze(
        self, request: GitHubAnalyzeRequest
    ) -> GitHubAnalyzeResponse:
        owner, repo = _parse_repo_url(request.repo_url)
        full_name = f"{owner}/{repo}"

        async with httpx.AsyncClient(timeout=20.0) as client:
            repo_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}",
                headers=self._headers(),
            )
            if repo_resp.status_code == 404:
                raise ValueError("Repository not found or is private.")
            repo_resp.raise_for_status()
            repo_data = repo_resp.json()

            tree_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}/git/trees/{repo_data['default_branch']}?recursive=1",
                headers=self._headers(),
            )
            tree_paths: list[str] = []
            if tree_resp.status_code == 200:
                items = tree_resp.json().get("tree", [])
                tree_paths = [
                    item["path"]
                    for item in items[:80]
                    if item.get("type") == "blob"
                ]

            readme_excerpt = ""
            readme_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}/readme",
                headers=self._headers(),
            )
            if readme_resp.status_code == 200:
                content = readme_resp.json().get("content", "")
                if content:
                    readme_excerpt = base64.b64decode(content).decode(
                        "utf-8", errors="replace"
                    )

        meta = GitHubRepoMeta(
            full_name=full_name,
            description=repo_data.get("description"),
            language=repo_data.get("language"),
            stars=repo_data.get("stargazers_count", 0),
            forks=repo_data.get("forks_count", 0),
            topics=repo_data.get("topics", []),
            default_branch=repo_data.get("default_branch", "main"),
        )

        tree_display = "\n".join(tree_paths[:40]) or "(empty or unavailable)"
        ai_analysis = self._llm.analyze_github_repo(
            full_name=full_name,
            description=meta.description or "",
            language=meta.language or "Unknown",
            topics=meta.topics,
            tree=tree_display,
            readme_excerpt=readme_excerpt,
        )

        return GitHubAnalyzeResponse(
            meta=meta,
            file_tree=tree_paths[:40],
            ai_analysis=ai_analysis,
        )
