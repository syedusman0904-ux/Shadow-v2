# SHADOW Security Notes

## Current protections

1. Passwords are hashed with Argon2id via `pwdlib`.
2. Access tokens are short-lived JWTs.
3. Refresh tokens are random opaque values.
4. Refresh tokens are stored server-side only as SHA-256 hashes.
5. Refresh tokens rotate when refreshed.
6. Refresh token cookie is HttpOnly and SameSite=Lax.
7. Basic security response headers are enabled.
8. Database access uses SQLAlchemy parameterized queries.

## Not yet implemented

- E2EE
- Device identity keys
- Message encryption
- WebSocket authentication
- Rate limiting
- Account lockout/abuse controls
- CSRF defense for cross-site deployment configurations
- Password reset
- TOTP/recovery codes
- Media encryption
- Security audit
- Alembic production migrations

Do not describe this version as "unhackable", "military grade", or end-to-end encrypted.

For production, use a formal threat model and independent security review.
