import sys

from app.services.github_client import GitHubClient, parse_pr_url

owner, repo, number = parse_pr_url(sys.argv[1])

with GitHubClient() as gh:
    pr = gh.get_pull_request(owner, repo, number)

print(f"PR #{pr.number}: {pr.title}  (by {pr.author})")
print(f"{pr.head_branch} -> {pr.base_branch} | {len(pr.files)} file(s) changed")

for f in pr.reviewable_files():
    print(f"\n--- {f.filename} ({f.status}, +{f.additions}/-{f.deletions})")
    print(f.patch[:600])