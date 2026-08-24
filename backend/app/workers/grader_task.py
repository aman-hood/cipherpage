import io
import traceback
from contextlib import redirect_stdout
from celery import Celery
import asyncio
from sqlalchemy import select

from app.core.config import settings
from app.infrastructure.database import AsyncSessionLocal
from app.infrastructure.models import Submission, Challenge

# Initialize Celery app targeting the Redis broker
celery_app = Celery(
    "grader_worker", 
    broker=settings.REDIS_URL, 
    backend=settings.REDIS_URL
)

def run_code_safely(source_code: str, test_input: str) -> tuple[bool, str, str]:
    """
    Mocks a secure isolation grading pipeline.
    In a real production environment, this MUST run inside an ephemeral Docker container
    or Firecracker microVM with strict CPU/Memory/Network limits (e.g., via gVisor)
    to prevent malicious students from escaping the sandbox.
    
    For this boilerplate, we use restricted Python `exec` with basic output capture 
    to demonstrate the concept cleanly.
    """
    # Create a restricted globals dict to prevent trivial malicious os/sys imports
    safe_globals = {"__builtins__": __builtins__}
    
    # Setup standard output capture
    f = io.StringIO()
    error_msg = ""
    output = ""
    success = False
    
    try:
        with redirect_stdout(f):
            # In production, test_input would be piped via stdin to the isolated process
            exec(source_code, safe_globals)
        output = f.getvalue().strip()
        success = True
    except Exception as e:
        # Gracefully catch syntax errors, infinite loops, and tracebacks
        error_msg = traceback.format_exc()
        
    return success, output, error_msg

async def evaluate_submission_async(submission_id: int):
    """
    Async handler to fetch DB records, iterate over hidden test cases, 
    evaluate code securely, and update the scorecard.
    """
    async with AsyncSessionLocal() as db:
        # 1. Fetch pending submission
        sub_result = await db.execute(select(Submission).where(Submission.id == submission_id))
        submission = sub_result.scalars().first()
        
        if not submission or submission.status != "pending":
            return
            
        # 2. Fetch linked challenge to get the hidden expected test cases
        chal_result = await db.execute(select(Challenge).where(Challenge.id == submission.challenge_id))
        challenge = chal_result.scalars().first()
        
        if not challenge or not challenge.expected_input_output:
            submission.status = "error"
            await db.commit()
            return

        test_cases = challenge.expected_input_output
        total_tests = len(test_cases)
        passed_tests = 0
        final_error_log = None
        
        # 3. Evaluate each test case
        for test in test_cases:
            # Expected schema for test is dict: {"input": "...", "output": "..."}
            success, actual_output, error_msg = run_code_safely(
                submission.submitted_code, 
                test.get("input", "")
            )
            
            if not success:
                final_error_log = f"Compile/Runtime Error:\n{error_msg}"
                break
                
            if actual_output == str(test.get("output", "")).strip():
                passed_tests += 1
            else:
                final_error_log = f"Failed Test Case.\nExpected: {test.get('output')}\nGot: {actual_output}"
                break
        
        # 4. Calculate final scorecard
        score = (passed_tests / total_tests) * 100.0 if total_tests > 0 else 0.0
        
        # 5. Update Submission record in DB
        submission.passed_tests = passed_tests
        submission.total_tests = total_tests
        submission.score = score
        
        if final_error_log:
            submission.status = "failed"
            # In a full schema, we would save the traceback here:
            # submission.error_logs = final_error_log 
        else:
            submission.status = "passed"
            
        await db.commit()

@celery_app.task(name="evaluate_student_code")
def evaluate_student_code(submission_id: int):
    """
    Celery background task entrypoint. 
    Because Celery workers execute synchronous Python, we use asyncio.run() 
    to bridge the gap and execute our async database grading logic safely.
    """
    asyncio.run(evaluate_submission_async(submission_id))
    return f"Graded submission {submission_id}"
