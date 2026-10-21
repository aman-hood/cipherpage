import unittest
from datetime import datetime, timedelta
from app.database.session import SessionLocal
from app.models.user import User
from app.models.gamification import UserStats, UserActivity, UserPOTDCompletion
from app.schemas.gamification import UserActivityCreate, POTDCompletionRequest
from app.routers.gamification import (
    get_user_stats,
    get_user_activities,
    record_user_activity,
    get_user_potds,
    toggle_potd_completion,
    get_user_dashboard
)


class TestUserPersonalizationAndIsolation(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()
        # Clean up any leftover test users
        self.db.query(User).filter(User.email.in_(["test_alice@cipherpage.com", "test_bob@cipherpage.com"])).delete(synchronize_session=False)
        self.db.commit()

        # Create two distinct test users
        self.user_a = User(
            firebase_uid="uid_alice_123",
            name="Alice Coder",
            email="test_alice@cipherpage.com",
            role="STUDENT",
            is_active=True
        )
        self.user_b = User(
            firebase_uid="uid_bob_456",
            name="Bob Builder",
            email="test_bob@cipherpage.com",
            role="STUDENT",
            is_active=True
        )
        self.db.add_all([self.user_a, self.user_b])
        self.db.commit()
        self.db.refresh(self.user_a)
        self.db.refresh(self.user_b)

    def tearDown(self):
        self.db.query(User).filter(User.email.in_(["test_alice@cipherpage.com", "test_bob@cipherpage.com"])).delete(synchronize_session=False)
        self.db.commit()
        self.db.close()

    def test_new_user_starts_with_clean_empty_state(self):
        """Verify Requirement 3: New accounts start with 0 streak, 0 solved, 0 XP, Level 1, and no activities."""
        dashboard_a = get_user_dashboard(db=self.db, current_user=self.user_a)
        self.assertEqual(dashboard_a.stats.total_xp, 0)
        self.assertEqual(dashboard_a.stats.level, 1)
        self.assertEqual(dashboard_a.stats.current_streak, 0)
        self.assertEqual(dashboard_a.stats.total_solved, 0)
        self.assertEqual(dashboard_a.hours_learned, 0.0)
        self.assertEqual(len(dashboard_a.recent_activity), 0)
        self.assertEqual(len(dashboard_a.solved_potds), 0)

    def test_user_a_and_user_b_complete_isolation(self):
        """Verify Requirement 2 & 4: User A's activities and POTDs do not bleed into User B's dashboard."""
        today_key = datetime.utcnow().date().isoformat()

        # Alice completes a POTD
        req = POTDCompletionRequest(
            video_id="video_aug1_486",
            problem_number="486",
            title="Predict the Winner",
            date_key=today_key,
            completed=True
        )
        alice_dash = toggle_potd_completion(req=req, db=self.db, current_user=self.user_a)

        # Alice's stats reflect the solve
        self.assertEqual(alice_dash.stats.total_solved, 1)
        self.assertEqual(alice_dash.stats.total_xp, 50)
        self.assertEqual(alice_dash.stats.current_streak, 1)
        self.assertEqual(alice_dash.solved_potds, ["video_aug1_486"])
        self.assertEqual(len(alice_dash.recent_activity), 1)
        self.assertEqual(alice_dash.recent_activity[0].action_label, "Solved")

        # Alice records watching a video lecture
        act = UserActivityCreate(
            activity_type="VIDEO_WATCHED",
            title="Dynamic Programming Masterclass",
            description="Watched full video walkthrough",
            action_label="Watched"
        )
        record_user_activity(activity_in=act, db=self.db, current_user=self.user_a)

        # Verify Bob's dashboard is completely untouched and clean
        bob_dash = get_user_dashboard(db=self.db, current_user=self.user_b)
        self.assertEqual(bob_dash.stats.total_solved, 0, "Bob must not inherit Alice's solved count")
        self.assertEqual(bob_dash.stats.total_xp, 0, "Bob must not inherit Alice's XP")
        self.assertEqual(bob_dash.stats.current_streak, 0, "Bob must not inherit Alice's streak")
        self.assertEqual(bob_dash.hours_learned, 0.0, "Bob must not inherit Alice's hours learned")
        self.assertEqual(len(bob_dash.recent_activity), 0, "Bob must have no recent activity")
        self.assertEqual(len(bob_dash.solved_potds), 0, "Bob must have no solved POTDs")

    def test_toggle_potd_unmark_updates_streak_and_solved_count(self):
        """Verify un-marking a problem updates only the authenticated user."""
        today_key = datetime.utcnow().date().isoformat()

        # Alice marks as solved
        req_solve = POTDCompletionRequest(
            video_id="video_877",
            problem_number="877",
            title="Stone Game",
            date_key=today_key,
            completed=True
        )
        dash = toggle_potd_completion(req=req_solve, db=self.db, current_user=self.user_a)
        self.assertEqual(dash.stats.total_solved, 1)
        self.assertIn("video_877", dash.solved_potds)

        # Alice un-marks the problem
        req_unsolve = POTDCompletionRequest(
            video_id="video_877",
            problem_number="877",
            title="Stone Game",
            date_key=today_key,
            completed=False
        )
        dash2 = toggle_potd_completion(req=req_unsolve, db=self.db, current_user=self.user_a)
        self.assertEqual(dash2.stats.total_solved, 0)
        self.assertNotIn("video_877", dash2.solved_potds)
        self.assertEqual(dash2.stats.current_streak, 0)


if __name__ == "__main__":
    unittest.main()
