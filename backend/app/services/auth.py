# Auth Service
# With Supabase Auth integration, authentication and JWT issuance are handled by Supabase.
# User synchronization is handled automatically in the get_current_user dependency.
# This service file is retained for future backend-specific auth logic (e.g. role escalation, banning).

class AuthService:
    pass

auth_service = AuthService()
