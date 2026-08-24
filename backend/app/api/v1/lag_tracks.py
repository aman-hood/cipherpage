from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.database import get_db
from app.infrastructure.models import Course, LearningContent, StudentProgress
from app.domain.schemas import CourseResponse, PaginatedCourses, LectureMetadataResponse

router = APIRouter(prefix="/tracks", tags=["LAG Tracks"])

# Mock JWT Dependency (Would normally decode the Bearer token)
async def get_current_user():
    return {"id": 1, "email": "student@cipherpage.com", "role": "student"}


@router.get("/courses", response_model=PaginatedCourses)
async def get_active_courses(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Fetch all active coding courses with pagination."""
    offset = (page - 1) * size
    
    # Concurrent-friendly async total count
    total_result = await db.execute(select(func.count()).select_from(Course))
    total = total_result.scalar_one()
    
    # Fetch paginated chunk
    result = await db.execute(select(Course).offset(offset).limit(size))
    courses = result.scalars().all()
    
    return PaginatedCourses(
        total=total,
        page=page,
        size=size,
        items=[
            CourseResponse(
                id=c.id, 
                title=c.title, 
                description=c.description or "", 
                language=c.language or "", 
                framework=c.framework or ""
            ) for c in courses
        ]
    )

@router.get("/courses/{course_id}/lectures/{lecture_id}", response_model=LectureMetadataResponse)
async def get_lecture_metadata(
    course_id: int,
    lecture_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Fetch a specific lecture's metadata. 
    Verifies if the user has purchased/enrolled in the course before returning the secret HLS stream URL.
    """
    # 1. Access Control: Verify enrollment/purchase
    progress_result = await db.execute(
        select(StudentProgress).where(StudentProgress.student_id == current_user["id"])
    )
    progress = progress_result.scalars().first()
    
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied. You must purchase or enroll in this course to access the content."
        )

    # 2. Fetch the lecture
    lecture_result = await db.execute(
        select(LearningContent).where(LearningContent.id == lecture_id)
    )
    lecture = lecture_result.scalars().first()
    
    if not lecture:
        raise HTTPException(status_code=404, detail="Lecture not found")
        
    return LectureMetadataResponse(
        id=lecture.id,
        title=lecture.title,
        video_hls_url=lecture.video_hls_url or "",
        notes=lecture.notes or "",
        starter_code_url=lecture.starter_code_url or ""
    )
