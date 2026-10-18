# Authentication and profile provisioning are handled by verified Firebase tokens
# in app.dependencies.auth. This service remains available for future account
# administration operations and intentionally does not issue credentials.

class AuthService:
    pass

auth_service = AuthService()
