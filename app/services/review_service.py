import logging

from app.database import SessionLocal
from app.models import Review
from app.services.github_client import GitHubClient, GitHubError
from app.services.llm_reviewer import LLMError, LLMReviewer

logger = logging.getLogger(__name__)


def run_review(review_id: int) -> None:
    """Runs in the background after POST /reviews returns.
    Uses its own DB session because the request's session is already closed."""
    db = SessionLocal()
    try:
        review = db.get(Review, review_id)
        if review is None:
            return

        review.status = "processing"
        db.commit()

        try:
            with GitHubClient() as gh:
                pr = gh.get_pull_request(review.repo_owner, review.repo_name, review.pr_number)
            review.pr_title = pr.title

            reviewer = LLMReviewer()
            result = reviewer.review(pr)

            review.summary = result.summary
            review.comments = [c.model_dump(mode="json") for c in result.comments]
            review.model_used = reviewer.last_model_used
            review.status = "completed"

        except (GitHubError, LLMError) as e:
            review.status = "failed"
            review.error_message = str(e)
        except Exception as e:
            logger.exception("Unexpected error in review %s", review_id)
            review.status = "failed"
            review.error_message = f"Unexpected error: {e}"

        db.commit()
    finally:
        db.close()