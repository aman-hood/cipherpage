"""
AI Mentor Service for CipherPage.
Enforces daily user quotas (AI-07), fetches problem context,
invokes the LLM adapter, and logs token usage in PostgreSQL.
"""
from datetime import datetime, date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.ai import AIUsageRecord
from app.repositories.challenge import challenge_repo
from app.schemas.ai import AIMentorRequest, AIMentorResponse, AIQuotaStatus
from app.integrations.llm.adapter import llm_adapter

DAILY_AI_QUOTA_LIMIT = 50

class AIMentorService:
    @staticmethod
    def get_user_daily_usage(db: Session, user_id: int) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        count = db.query(func.count(AIUsageRecord.id)).filter(
            AIUsageRecord.user_id == user_id,
            AIUsageRecord.created_at >= today_start
        ).scalar()
        return count or 0

    @staticmethod
    def get_quota_status(db: Session, user: User) -> AIQuotaStatus:
        used = AIMentorService.get_user_daily_usage(db, user.id)
        remaining = max(0, DAILY_AI_QUOTA_LIMIT - used)
        return AIQuotaStatus(
            daily_requests_used=used,
            daily_limit=DAILY_AI_QUOTA_LIMIT,
            remaining_quota=remaining
        )

    @staticmethod
    def process_mentor_request(db: Session, user: User, req: AIMentorRequest) -> AIMentorResponse:
        # 1. Enforce quota limits (AI-07, NFR-08)
        used = AIMentorService.get_user_daily_usage(db, user.id)
        if used >= DAILY_AI_QUOTA_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Daily AI mentor quota exceeded ({used}/{DAILY_AI_QUOTA_LIMIT}). Quota resets at 00:00 UTC."
            )

        # 2. Get Challenge context if available
        problem_title = None
        problem_desc = None
        if req.challenge_id:
            challenge = challenge_repo.get(db, id=req.challenge_id)
            if challenge:
                problem_title = challenge.title
                problem_desc = challenge.description

        # 3. Call LLM adapter
        content, model_used, tokens_used = llm_adapter.get_mentor_response(
            mode=req.mode.upper(),
            code=req.code,
            language=req.language,
            problem_title=problem_title,
            problem_desc=problem_desc,
            error_output=req.error_output,
            request_full_solution=req.request_full_solution
        )

        # 4. Record usage in database (AI-07)
        usage_record = AIUsageRecord(
            user_id=user.id,
            mode=req.mode.upper(),
            model_name=model_used,
            prompt_tokens=tokens_used // 2,
            completion_tokens=tokens_used // 2
        )
        db.add(usage_record)
        db.commit()

        remaining_quota = max(0, DAILY_AI_QUOTA_LIMIT - (used + 1))

        return AIMentorResponse(
            mode=req.mode.upper(),
            content=content,
            tokens_used=tokens_used,
            disclaimer="AI guidance can occasionally make mistakes. Verify your solution logic by running test cases.",
            remaining_quota=remaining_quota
        )

ai_mentor_service = AIMentorService()
