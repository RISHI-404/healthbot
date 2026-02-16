Migration notes

- Updated model timestamp fields to use timezone-aware datetimes:
  - `DateTime(timezone=True)` for SQLAlchemy columns.
  - Defaults use `datetime.now(timezone.utc)`.
    This ensures UTC-aware timestamps and avoids deprecation warnings about `datetime.utcnow()`.

- Updated `app/utils/jwt_handler.py` to use timezone-aware expirations (`datetime.now(timezone.utc)`).

- Added `email-validator==2.3.0` to `requirements.txt` to satisfy `pydantic` email validation dependency.

Recommended actions:

- If you use a database with older timestamp columns, consider migrating existing DATETIME columns to include timezone awareness if your DB supports it.
- Recreate virtualenv and run `pip install -r backend/requirements.txt` in deployment pipelines to ensure `email-validator` is present.
