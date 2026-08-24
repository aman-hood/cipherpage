from celery import Celery
from app.core.config import settings

# Initialize Celery app targeting Redis
celery_app = Celery(
    "cipherpage_worker", 
    broker=settings.REDIS_URL, 
    backend=settings.REDIS_URL
)

@celery_app.task(name="evaluate_student_code")
def evaluate_student_code(submission_id: int):
    """
    Background Task executed securely on the Celery Worker.
    This prevents locking the main FastAPI web server thread during intense compilation.
    
    Responsibilities:
    1. Pull the Submission from DB using submission_id.
    2. Pull expected I/O from the linked Challenge.
    3. Spin up an isolated process/docker container to execute the `submitted_code`.
    4. Compare stdout outputs with expected outputs.
    5. Update the Submission row in the DB with the final score and status.
    """
    print(f"[Worker] Starting secure code evaluation for submission ID: {submission_id}")
    # ... mock evaluation logic ...
    print(f"[Worker] Finished evaluation for submission ID: {submission_id}")
    return True
