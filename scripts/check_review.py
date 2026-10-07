import sys

from app.services.github_client import GitHubClient, parse_pr_url
from app.services.llm_reviewer import LLMReviewer

owner, repo, number = parse_pr_url(sys.argv[1])

with GitHubClient() as gh:
    pr = gh.get_pull_request(owner, repo, number)

reviewer = LLMReviewer()
result = reviewer.review(pr)

print("SUMMARY:", result.summary, "\n")
for c in result.comments:
    print(f"[{c.severity.value.upper()}] [{c.category.value}] {c.file}:{c.line}")
    print(f"  {c.message}")
    print(f"  Fix: {c.suggestion}\n")

print("Model used:", reviewer.last_model_used)