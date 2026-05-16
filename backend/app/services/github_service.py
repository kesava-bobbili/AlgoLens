from __future__ import annotations

import base64
import logging
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

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"
PRIORITY_DIRS = frozenset(
    {
        "src",
        "apps",
        "packages",
        "lib",
        "backend",
        "frontend",
        "tests",
        "docs",
        ".github",
        "examples",
        "tooling",
    }
)
MAX_PATHS = 140
MAX_CONTENT_FETCHES = 14


def _normalize_github_url(url: str) -> str:
    u = url.strip()
    if not u:
        raise ValueError("URL is empty.")
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u


def _parse_repo_url(url: str) -> tuple[str, str]:
    raw = _normalize_github_url(url)
    parsed = urlparse(raw)
    host = parsed.netloc.lower().split(":")[0].removeprefix("www.")
    if host != "github.com":
        raise ValueError(
            "Only github.com repository URLs are supported "
            "(e.g. https://github.com/owner/repo)."
        )

    parts = [p for p in parsed.path.strip("/").split("/") if p]
    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub URL. Expected https://github.com/owner/repository"
        )

    owner, repo = parts[0], parts[1].removesuffix(".git")
    segment_re = re.compile(r"^[a-zA-Z0-9._-]+$")
    if not segment_re.match(owner) or not segment_re.match(repo):
        raise ValueError("Invalid owner or repository name in URL.")

    return owner, repo


def _github_error_hint(resp: httpx.Response) -> str:
    try:
        data = resp.json()
        msg = str(data.get("message", "") or "")
        lower = msg.lower()
        if "rate limit" in lower:
            return (
                "GitHub API rate limit exceeded (anonymous quota is small). "
                "Set GITHUB_TOKEN in the backend .env for higher limits."
            )
        if msg:
            return msg
    except Exception:
        pass
    return resp.text[:240] or f"HTTP {resp.status_code}"


def _raise_github(resp: httpx.Response, context: str) -> None:
    if resp.status_code == 404:
        raise ValueError("Repository not found or is private.")
    if resp.status_code == 403:
        logger.warning(
            "GitHub 403 during %s: %s", context, _github_error_hint(resp)
        )
        raise ValueError(_github_error_hint(resp))
    if resp.status_code == 401:
        raise ValueError(
            "GitHub rejected credentials. Check GITHUB_TOKEN in backend .env."
        )
    try:
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.exception("GitHub HTTP error during %s", context)
        raise ValueError(
            f"GitHub request failed ({context}): {_github_error_hint(resp)}"
        ) from exc


def _format_languages(langs: dict[str, int]) -> str:
    if not langs:
        return "None returned by GitHub API."
    lines = [
        f"- {name}: {bytes_} bytes"
        for name, bytes_ in sorted(langs.items(), key=lambda x: -x[1])[:18]
    ]
    return "\n".join(lines)


async def _collect_paths(
    client: httpx.AsyncClient,
    full_name: str,
    headers: dict[str, str],
) -> list[str]:
    """Repository layout via Contents API (avoids huge recursive git trees)."""
    paths: set[str] = set()
    fetches = 0

    async def fetch_level(rel: str) -> None:
        nonlocal fetches
        if fetches >= MAX_CONTENT_FETCHES:
            return
        url = f"{GITHUB_API}/repos/{full_name}/contents"
        if rel:
            url += f"/{rel}"
        fetches += 1
        resp = await client.get(url, headers=headers)
        if resp.status_code == 404:
            logger.info("contents 404 for %s/%s", full_name, rel or "(root)")
            return
        _raise_github(resp, f"contents/{rel or 'root'}")
        data = resp.json()
        if isinstance(data, dict):
            if data.get("type") == "file":
                paths.add(str(data.get("path", rel)))
            return
        if not isinstance(data, list):
            return
        for item in data:
            if len(paths) >= MAX_PATHS:
                return
            p = str(item.get("path", ""))
            typ = item.get("type")
            if typ == "file":
                paths.add(p)
            elif typ == "dir":
                paths.add(p + "/")

    await fetch_level("")

    top_dirs = sorted(
        {p[:-1] for p in paths if p.endswith("/")},
        key=lambda x: (x.split("/")[0] not in PRIORITY_DIRS, x),
    )
    expanded = 0
    for d in top_dirs:
        if len(paths) >= MAX_PATHS:
            break
        head = d.split("/")[0]
        if head in PRIORITY_DIRS or expanded < 5:
            await fetch_level(d)
            expanded += 1

    ordered = sorted(paths)
    return ordered[:MAX_PATHS]


class GitHubService:
    def __init__(self) -> None:
        self._llm = LLMClient()
        self._settings = get_settings()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "AlgoLens-GitHub-Analyzer/2.1",
        }
        if self._settings.github_token:
            headers["Authorization"] = f"Bearer {self._settings.github_token}"
        return headers

    async def analyze(
        self, request: GitHubAnalyzeRequest
    ) -> GitHubAnalyzeResponse:
        owner, repo = _parse_repo_url(request.repo_url)
        full_name = f"{owner}/{repo}"
        logger.info("GitHub analyze start: %s", full_name)

        headers = self._headers()
        timeout = httpx.Timeout(45.0, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            repo_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}",
                headers=headers,
            )
            _raise_github(repo_resp, "repository metadata")
            repo_data = repo_resp.json()

            lang_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}/languages",
                headers=headers,
            )
            languages: dict[str, int] = {}
            if lang_resp.status_code == 200:
                raw_langs = lang_resp.json()
                if isinstance(raw_langs, dict):
                    languages = {str(k): int(v) for k, v in raw_langs.items()}
            elif lang_resp.status_code != 404:
                logger.warning(
                    "languages endpoint status=%s for %s",
                    lang_resp.status_code,
                    full_name,
                )

            readme_excerpt = ""
            readme_resp = await client.get(
                f"{GITHUB_API}/repos/{full_name}/readme",
                headers=headers,
            )
            if readme_resp.status_code == 200:
                body = readme_resp.json()
                content = body.get("content", "")
                if content:
                    readme_excerpt = base64.b64decode(content).decode(
                        "utf-8", errors="replace"
                    )
            elif readme_resp.status_code == 404:
                logger.info("No README for %s", full_name)
            else:
                logger.warning(
                    "README fetch status=%s for %s",
                    readme_resp.status_code,
                    full_name,
                )

            try:
                tree_paths = await _collect_paths(client, full_name, headers)
            except ValueError:
                raise
            except Exception:
                logger.exception("path collection failed for %s", full_name)
                tree_paths = []

            if not tree_paths:
                tree_paths = [
                    "(Could not list repository contents — "
                    "API limits or empty repo.)"
                ]

        meta = GitHubRepoMeta(
            full_name=full_name,
            description=repo_data.get("description"),
            language=repo_data.get("language"),
            stars=int(repo_data.get("stargazers_count") or 0),
            forks=int(repo_data.get("forks_count") or 0),
            topics=list(repo_data.get("topics") or []),
            default_branch=str(repo_data.get("default_branch") or "main"),
            languages=languages,
        )

        tree_display = "\n".join(tree_paths[:80])
        languages_block = _format_languages(languages)

        logger.info(
            "GitHub data fetched %s: langs=%s paths=%s readme_chars=%s",
            full_name,
            len(languages),
            len(tree_paths),
            len(readme_excerpt),
        )

        ai_analysis = self._llm.analyze_github_repo(
            repo_full_name=full_name,
            description=meta.description or "",
            language=meta.language or "Unknown",
            topics=meta.topics,
            languages_block=languages_block,
            tree=tree_display,
            readme_excerpt=readme_excerpt,
        )

        logger.info("GitHub analyze complete: %s", full_name)

        return GitHubAnalyzeResponse(
            meta=meta,
            file_tree=tree_paths[:80],
            ai_analysis=ai_analysis,
        )
