# Planventure API - AI Coding Agent Instructions

## Project Overview
Planventure is a Flask-based REST API for travel planning. It manages user accounts and trip itineraries with authentication, database persistence, and geolocation support.

**Key Stack:** Flask, SQLAlchemy ORM, SQLite (default), JWT authentication, bcrypt password hashing

## Architecture & Data Model

### Core Domain: Users & Trips
- **User** model ([models/user.py](models/user.py#L1)): Email-based authentication with bcrypted passwords. Owns multiple trips via relationship.
- **Trip** model ([models/trip.py](models/trip.py#L1)): Travel records with destination, dates, coordinates, and itineraries. Always belongs to a user (enforced by `user_id` foreign key).
- **Cascade Delete:** Trips auto-delete when user is deleted (see Trip model cascade rules).

### Database Configuration
- SQLAlchemy configured in [app.py](app.py#L17-L20) with `DATABASE_URL` env var (defaults to SQLite).
- UTC timestamps on all models using `datetime.now(timezone.utc)` for consistency.
- Initialize DB with: `python init_db.py` (creates tables; won't drop existing unless explicitly enabled).

## Critical Developer Patterns

### Password Handling
```python
# Always use bcrypt via User.set_password() and User.check_password()
# Never store plaintext passwords; never hash in routes directly
user.set_password(raw_password)  # Hashing happens here
if user.check_password(provided_password):  # Validation here
```

### Serialization Convention
Models implement `.to_dict()` for API responses:
- User: excludes password hash (security)
- Trip: wraps lat/long in `coordinates` object, returns None if missing
- Always use `.isoformat()` for datetime fields in responses

### Environment Setup
- Copy `.sample.env` → `.env` before running; never commit `.env`
- Required vars: `DATABASE_URL` (optional, defaults to local SQLite)
- Local dev: `flask run` (debug mode auto-enabled in app.py when `__name__ == '__main__'`)

## Integration Points

### CORS & API Structure
- CORS enabled globally in [app.py](app.py#L22) via `CORS(app)` (allows cross-origin requests)
- Two starter endpoints: GET `/` (welcome), GET `/health` (status check)
- New routes should follow REST convention: resource-based paths, proper HTTP methods

### Model Imports & Circular Dependency Prevention
- Import models **after** db initialization in [app.py](app.py#L24): avoids circular imports
- When adding new models, import them in app.py the same way

### JWT Authentication (Declared but Not Yet Implemented)
- `flask-jwt-extended==4.5.2` is installed; `@jwt_required()` decorator ready for use
- Implement token generation on login; protect routes with decorator

## Common Workflows

### Adding a New API Endpoint
1. Define route in `app.py` (POST/GET/PATCH/DELETE)
2. Use model `.to_dict()` for responses
3. Return `jsonify(dict_or_list)` and appropriate HTTP status codes
4. Test with API client (Bruno recommended); curl works too

### Adding a New Model Field
1. Modify model in `models/` directory
2. Add db.Column() with appropriate type and nullable rules
3. Run `python init_db.py` to recreate schema (in dev; production requires migration tool)
4. Update `.to_dict()` if field should appear in API responses

### Handling Dates in Requests/Responses
- Incoming Trip dates: expect ISO 8601 strings; parse with `datetime.fromisoformat()`
- Outgoing: always `.isoformat()` (UTC timestamps are already UTC)

## Conventions & Gotchas

- **No migrations tool configured yet:** schema changes require database reset in dev (fine for now)
- **Debug mode always on locally:** [app.py](app.py#L29) sets `debug=True` in dev; disable for production
- **SQLite default:** good for dev/testing; switch DATABASE_URL for PostgreSQL in production
- **Marshmallow installed but unused:** consider for input validation if API grows
- **Table naming:** explicit `__tablename__` in models (users, trips) for clarity

## Testing & Debugging

- API client: Use [Bruno](https://github.com/usebruno/bruno) or Postman to test endpoints
- Health check: `GET http://localhost:5000/health` verifies server is running
- Database state: SQLite file is `planventure.db` in project root (dev only)
- Flask debug: check terminal output for request logs and errors
