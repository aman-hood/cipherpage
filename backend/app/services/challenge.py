from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repositories.challenge import challenge_repo
from app.models.challenge import Challenge, TestCase
from app.schemas.challenge import ChallengeCreate, ChallengeDetail, TestCaseDetail

class ChallengeService:
    @staticmethod
    def get_challenges(db: Session, skip: int = 0, limit: int = 100) -> List[Challenge]:
        return challenge_repo.get_active_challenges(db, skip=skip, limit=limit)

    @staticmethod
    def get_challenge_by_id(db: Session, challenge_id: int, sanitize_hidden: bool = True) -> ChallengeDetail:
        challenge = challenge_repo.get_with_test_cases(db, challenge_id=challenge_id)
        if not challenge:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Challenge not found")

        # Sanitize test cases if requested (CODE-06: Never return hidden test cases or secret inputs)
        safe_test_cases = []
        for tc in challenge.test_cases:
            if sanitize_hidden and tc.is_hidden:
                # Completely exclude hidden evaluation tests to protect test inputs (CODE-06)
                continue
            safe_test_cases.append(TestCaseDetail(
                id=tc.id,
                input_data=tc.input_data,
                expected_output=tc.expected_output,
                explanation=tc.explanation,
                is_hidden=tc.is_hidden,
                order=tc.order
            ))

        detail = ChallengeDetail(
            id=challenge.id,
            title=challenge.title,
            slug=challenge.slug,
            description=challenge.description,
            difficulty=challenge.difficulty,
            category=challenge.category,
            time_limit=challenge.time_limit,
            memory_limit=challenge.memory_limit,
            starter_code=challenge.starter_code or {},
            hints=challenge.hints or [],
            constraints=challenge.constraints or [],
            examples=challenge.examples or [],
            is_active=challenge.is_active,
            created_at=challenge.created_at,
            test_cases=safe_test_cases
        )
        return detail

    @staticmethod
    def create_challenge(db: Session, challenge_in: ChallengeCreate) -> Challenge:
        existing = challenge_repo.get_by_slug(db, slug=challenge_in.slug)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Challenge with this slug already exists")
        
        challenge_data = challenge_in.model_dump(exclude={"test_cases"})
        challenge = Challenge(**challenge_data)
        db.add(challenge)
        db.flush()

        if challenge_in.test_cases:
            for tc_data in challenge_in.test_cases:
                tc = TestCase(
                    challenge_id=challenge.id,
                    **tc_data.model_dump()
                )
                db.add(tc)

        db.commit()
        db.refresh(challenge)
        return challenge

challenge_service = ChallengeService()
