import re
from dataclasses import dataclass, field

import httpx

from app.config import settings

GITHUB_API = "https://api.github.com"

SKIP_FILENAMES = {"package-lock.json", "yarn.lock", "poetry.lock", "Pipfile.lock"}
SKIP_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".pdf", ".min.js", ".lock")


class GitHubError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


@dataclass
class FileChange:
    filename: str
    status: str
    additions: int
    deletions: int
    patch: str | None


@dataclass
class PullRequestData:
    owner: str
    repo: str
    number: int
    title: str
    body: str
    author: str
    base_branch: str
    head_branch: str
    head_sha: str
    files: list[FileChange] = field(default_factory=list)

    def reviewable_files(self) -> list[FileChange]:
        result = []
        for f in self.files:
            name = f.filename.split("/")[-1]
            if f.status == "removed" or not f.patch:
                continue
            if name in SKIP_FILENAMES or name.endswith(SKIP_EXTENSIONS):
                continue
            result.append(f)
        return result


def parse_pr_url(url: str) -> tuple[str, str, int]:
    match = re.match(r"^https?://github\.com/([\w.-]+)/([\w.-]+)/pull/(\d+)", url.strip())
    if not match:
        raise ValueError("Not a valid GitHub pull request URL")
    return match.group(1), match.group(2), int(match.group(3))


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 15.0):
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "pr-review-service",
        }
        token = token or settings.github_token
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.Client(base_url=GITHUB_API, headers=headers, timeout=timeout)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._client.close()

    def _get(self, path: str, params: dict | None = None) -> httpx.Response:
        try:
            resp = self._client.get(path, params=params)
        except httpx.RequestError as e:
            raise GitHubError(f"Could not reach GitHub: {e}") from e

        if resp.status_code == 404:
            raise GitHubError("Repository or pull request not found (or it is private)", 404)
        if resp.status_code == 401:
            raise GitHubError("GitHub token is invalid or expired", 401)
        if resp.status_code == 403 and resp.headers.get("x-ratelimit-remaining") == "0":
            raise GitHubError("GitHub API rate limit exceeded", 429)
        if resp.status_code >= 400:
            raise GitHubError(f"GitHub API error {resp.status_code}: {resp.text[:200]}", resp.status_code)
        return resp

    def get_pull_request(self, owner: str, repo: str, number: int) -> PullRequestData:
        pr = self._get(f"/repos/{owner}/{repo}/pulls/{number}").json()
        return PullRequestData(
            owner=owner,
            repo=repo,
            number=number,
            title=pr["title"],
            body=pr.get("body") or "",
            author=pr["user"]["login"],
            base_branch=pr["base"]["ref"],
            head_branch=pr["head"]["ref"],
            head_sha=pr["head"]["sha"],
            files=self._get_files(owner, repo, number),
        )

    def _get_files(self, owner: str, repo: str, number: int) -> list[FileChange]:
        files: list[FileChange] = []
        page = 1
        while True:
            batch = self._get(
                f"/repos/{owner}/{repo}/pulls/{number}/files",
                params={"per_page": 100, "page": page},
            ).json()
            for f in batch:
                files.append(FileChange(
                    filename=f["filename"],
                    status=f["status"],
                    additions=f["additions"],
                    deletions=f["deletions"],
                    patch=f.get("patch"),
                ))
            if len(batch) < 100 or page >= 30:
                break
            page += 1
        return files