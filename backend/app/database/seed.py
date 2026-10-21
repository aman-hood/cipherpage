"""
Database seeder for CipherPage - Phase 1.
Populates standard challenges, test cases, badges, courses, and demo users.
"""
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
import app.models
from app.models.user import User
from app.models.course import Course, Module, Lecture
from app.models.challenge import Challenge, TestCase
from app.models.gamification import Badge, UserStats
from app.models.ai import Document

def seed_database():
    db: Session = SessionLocal()
    try:
        print("[*] Seeding database...")

        # 1. Seed Demo User
        demo_user = db.query(User).filter(User.email == "demo@cipherpage.com").first()
        if not demo_user:
            demo_user = User(
                name="Aman (Demo)",
                email="demo@cipherpage.com",
                role="ADMIN",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print("  Created demo user: demo@cipherpage.com")

        # 2. Seed User Stats
        stats = db.query(UserStats).filter(UserStats.user_id == demo_user.id).first()
        if not stats:
            stats = UserStats(
                user_id=demo_user.id,
                total_xp=450,
                level=4,
                current_streak=7,
                longest_streak=14,
                total_solved=12,
                easy_solved=8,
                medium_solved=4,
                hard_solved=0
            )
            db.add(stats)
            db.commit()
            print("  Created user stats for demo user")

        # 3. Seed Courses
        course_1 = db.query(Course).filter(Course.slug == "mastering-fastapi-postgresql").first()
        if not course_1:
            course_1 = Course(
                title="Mastering FastAPI & PostgreSQL",
                slug="mastering-fastapi-postgresql",
                description="Build enterprise-ready, async REST APIs with FastAPI, SQLAlchemy 2.0, and PostgreSQL.",
                category="Backend",
                difficulty="INTERMEDIATE",
                price=0.0,
                status="PUBLISHED"
            )
            db.add(course_1)
            db.commit()
            db.refresh(course_1)

            mod_1 = Module(title="Architecture & Foundation", order=1, course_id=course_1.id)
            db.add(mod_1)
            db.commit()
            db.refresh(mod_1)

            lec_1 = Lecture(title="Introduction to FastAPI & Pydantic", duration=600, video_url="https://youtube.com/watch?v=demo", module_id=mod_1.id)
            lec_2 = Lecture(title="Relational Modeling with SQLAlchemy 2", duration=900, video_url="https://youtube.com/watch?v=demo2", module_id=mod_1.id)
            db.add_all([lec_1, lec_2])
            db.commit()
            print("  Created sample course: Mastering FastAPI & PostgreSQL")

        # 4. Seed Challenges
        challenge_1 = db.query(Challenge).filter(Challenge.slug == "predict-the-winner").first()
        if not challenge_1:
            challenge_1 = Challenge(
                title="Predict the Winner",
                slug="predict-the-winner",
                difficulty="MEDIUM",
                category="Dynamic Programming / Game Theory",
                description=(
                    "You are given an integer array `nums`. Two players are playing a game with this array: player 1 and player 2.\n\n"
                    "Player 1 and player 2 take turns, with player 1 starting first. Both players start the game with a score of `0`. "
                    "At each turn, the player takes one of the numbers from either end of the array. The player adds the chosen number to their score.\n\n"
                    "Return `true` if Player 1 can win the game. If the scores are equal, player 1 still wins."
                ),
                time_limit=2.0,
                memory_limit=256,
                starter_code={
                    "python": "class Solution:\n    def predictTheWinner(self, nums: list[int]) -> bool:\n        # Write your code here\n        pass\n",
                    "javascript": "function predictTheWinner(nums) {\n  // Write your code here\n}\n",
                    "typescript": "function predictTheWinner(nums: number[]): boolean {\n  // Write your code here\n}\n"
                },
                constraints=["1 <= nums.length <= 20", "0 <= nums[i] <= 10^7"],
                examples=[
                    {"input": "nums = [1, 5, 2]", "output": "false", "explanation": "Player 1 can choose 1 or 2, then Player 2 chooses 5 to win."},
                    {"input": "nums = [1, 5, 233, 7]", "output": "true", "explanation": "Player 1 can always guarantee a winning score."}
                ],
                hints=[
                    "Consider dynamic programming or minimax recursion with memoization.",
                    "Track the maximum relative score difference player 1 can achieve."
                ],
                is_active=True
            )
            db.add(challenge_1)
            db.commit()
            db.refresh(challenge_1)

            # 10 Test Cases (5 public, 5 hidden)
            tc1 = TestCase(challenge_id=challenge_1.id, input_data="[1, 5, 2]", expected_output="false", is_hidden=False, order=1)
            tc2 = TestCase(challenge_id=challenge_1.id, input_data="[1, 5, 233, 7]", expected_output="true", is_hidden=False, order=2)
            tc3 = TestCase(challenge_id=challenge_1.id, input_data="[1, 1]", expected_output="true", is_hidden=False, order=3)
            tc4 = TestCase(challenge_id=challenge_1.id, input_data="[1, 2, 99, 4]", expected_output="true", is_hidden=False, order=4)
            tc5 = TestCase(challenge_id=challenge_1.id, input_data="[10, 9, 1]", expected_output="true", is_hidden=False, order=5)
            tc6 = TestCase(challenge_id=challenge_1.id, input_data="[1, 5, 2, 4, 6]", expected_output="true", is_hidden=True, order=6)
            tc7 = TestCase(challenge_id=challenge_1.id, input_data="[10, 15, 20, 99, 1]", expected_output="false", is_hidden=True, order=7)
            tc8 = TestCase(challenge_id=challenge_1.id, input_data="[3, 9, 1, 2]", expected_output="true", is_hidden=True, order=8)
            tc9 = TestCase(challenge_id=challenge_1.id, input_data="[1, 100, 1000, 50, 20, 80, 90, 12, 44, 99]", expected_output="true", is_hidden=True, order=9)
            tc10 = TestCase(challenge_id=challenge_1.id, input_data="[1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000]", expected_output="true", is_hidden=True, order=10)
            db.add_all([tc1, tc2, tc3, tc4, tc5, tc6, tc7, tc8, tc9, tc10])
            db.commit()
            print("  Created challenge: Predict the Winner (with 10 test cases)")

        challenge_2 = db.query(Challenge).filter(Challenge.slug == "two-sum").first()
        if not challenge_2:
            challenge_2 = Challenge(
                title="Two Sum",
                slug="two-sum",
                difficulty="EASY",
                category="Arrays & Hash Tables",
                description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
                time_limit=1.0,
                memory_limit=128,
                starter_code={
                    "python": "class Solution:\n    def twoSum(self, nums: list[int], target: int) -> list[int]:\n        # Write your code here\n        pass\n",
                    "javascript": "function twoSum(nums, target) {\n  // Write your code here\n}\n"
                },
                constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
                examples=[{"input": "nums = [2,7,11,15], target = 9", "output": "[0,1]"}],
                hints=["Use a hash map to look up the complement in O(1) time."],
                is_active=True
            )
            db.add(challenge_2)
            db.commit()
            db.refresh(challenge_2)

            tc2_1 = TestCase(challenge_id=challenge_2.id, input_data="nums = [2,7,11,15], target = 9", expected_output="[0,1]", is_hidden=False, order=1)
            tc2_2 = TestCase(challenge_id=challenge_2.id, input_data="nums = [3,2,4], target = 6", expected_output="[1,2]", is_hidden=False, order=2)
            tc2_3 = TestCase(challenge_id=challenge_2.id, input_data="nums = [3,3], target = 6", expected_output="[0,1]", is_hidden=False, order=3)
            tc2_4 = TestCase(challenge_id=challenge_2.id, input_data="nums = [-1,-2,-3,-4,-5], target = -8", expected_output="[2,4]", is_hidden=False, order=4)
            tc2_5 = TestCase(challenge_id=challenge_2.id, input_data="nums = [0,4,3,0], target = 0", expected_output="[0,3]", is_hidden=False, order=5)
            tc2_6 = TestCase(challenge_id=challenge_2.id, input_data="nums = [-3,4,3,90], target = 0", expected_output="[0,2]", is_hidden=True, order=6)
            tc2_7 = TestCase(challenge_id=challenge_2.id, input_data="nums = [1,5,8,12,14], target = 20", expected_output="[2,3]", is_hidden=True, order=7)
            tc2_8 = TestCase(challenge_id=challenge_2.id, input_data="nums = [2,5,5,11], target = 10", expected_output="[1,2]", is_hidden=True, order=8)
            tc2_9 = TestCase(challenge_id=challenge_2.id, input_data="nums = [1000000, 500, 2000000, 1000000], target = 2000000", expected_output="[0,3]", is_hidden=True, order=9)
            tc2_10 = TestCase(challenge_id=challenge_2.id, input_data="nums = [1,2,3,4,5,6,7,8,9,10], target = 19", expected_output="[8,9]", is_hidden=True, order=10)
            db.add_all([tc2_1, tc2_2, tc2_3, tc2_4, tc2_5, tc2_6, tc2_7, tc2_8, tc2_9, tc2_10])
            db.commit()
            print("  Created challenge: Two Sum (with 10 test cases)")

        # 5. Seed Badges
        badges_data = [
            {"slug": "first-blood", "name": "First Blood", "description": "Passed your first problem in the Monaco editor.", "category": "milestone", "tier": "bronze", "icon": "⚔️", "xp_reward": 50},
            {"slug": "streak-week", "name": "Consistent Coder", "description": "Maintained a 7-day coding streak.", "category": "streak", "tier": "silver", "icon": "🔥", "xp_reward": 100},
            {"slug": "algo-adept", "name": "Algorithm Adept", "description": "Solved 10 algorithm challenges.", "category": "skills", "tier": "gold", "icon": "⚡", "xp_reward": 250},
            {"slug": "cloud-architect", "name": "Cloud Architect", "description": "Completed first cloud deployment module.", "category": "milestone", "tier": "diamond", "icon": "☁️", "xp_reward": 500},
        ]
        for b_data in badges_data:
            existing_badge = db.query(Badge).filter(Badge.slug == b_data["slug"]).first()
            if not existing_badge:
                db.add(Badge(**b_data))
        db.commit()
        print("  Seeded badges successfully")

        # 6. Seed Course Document for RAG Learning Assistant (RAG-01..RAG-04)
        doc = db.query(Document).filter(Document.title == "FastAPI & PostgreSQL Architecture Guide").first()
        if not doc and course_1:
            from app.schemas.rag import DocumentIngestRequest
            from app.services.rag_assistant import rag_service
            rag_content = (
                "# Architecture & Monorepo Layout\n"
                "CipherPage follows a strict modular architecture separating backend (FastAPI), web (Next.js), and mobile (Flutter). "
                "The backend encapsulates routers, business services, repositories, database sessions, and Celery background workers.\n\n"
                "# Dependency Injection & Database Sessions\n"
                "In FastAPI, database connections are managed via SQLAlchemy 2.0 session generators using the `Depends(get_db)` pattern. "
                "Each incoming HTTP request receives an isolated database transaction that automatically closes upon request termination.\n\n"
                "# Asynchronous Code Execution & Background Tasks\n"
                "Untrusted student code is never executed inside the main FastAPI process. Instead, code submissions are queued into Redis "
                "and processed asynchronously by Celery workers in isolated disposable subprocesses with strict time and memory limits.\n\n"
                "# Vector Search & RAG\n"
                "The platform uses PostgreSQL with pgvector for semantic retrieval. Approved course notes are chunked into semantic segments "
                "and embedded into vector space to provide grounded Socratic answers with verified source citations."
            )
            rag_service.ingest_document(
                db=db,
                user=demo_user,
                req=DocumentIngestRequest(
                    title="FastAPI & PostgreSQL Architecture Guide",
                    course_id=course_1.id,
                    content=rag_content
                )
            )
            print("  Seeded course documentation for RAG Learning Assistant")

        print("[+] Database seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
