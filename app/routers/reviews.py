from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Review
from app.schemas import ReviewCreate, ReviewOut
from app.services.github_client import parse_pr_url
from app.services.review_service import run_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=ReviewOut, status_code=202)
def create_review(
    payload: ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Submit a PR for review. Returns immediately with status 'pending'."""
    owner, repo, number = parse_pr_url(payload.pr_url)

    review = Review(repo_owner=owner, repo_name=repo, pr_number=number, status="pending")
    db.add(review)
    db.commit()
    db.refresh(review)

    background_tasks.add_task(run_review, review.id)
    return review


@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: int, db: Session = Depends(get_db)):
    """Retrieve a review (poll this until status is 'completed' or 'failed')."""
    review = db.get(Review, review_id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("", response_model=list[ReviewOut])
def list_reviews(
    repo_owner: str | None = None,
    repo_name: str | None = None,
    pr_number: int | None = None,
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List reviews, newest first, with optional filters and pagination."""
    stmt = select(Review)
    if repo_owner:
        stmt = stmt.where(Review.repo_owner == repo_owner)
    if repo_name:
        stmt = stmt.where(Review.repo_name == repo_name)
    if pr_number is not None:
        stmt = stmt.where(Review.pr_number == pr_number)
    if status:
        stmt = stmt.where(Review.status == status)

    stmt = stmt.order_by(Review.created_at.desc()).limit(limit).offset(offset)
    return db.scalars(stmt).all()