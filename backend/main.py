"""
Leave Management API
--------------------
FastAPI backend with:
- JWT authentication (python-jose + bcrypt)
- Role-based access control (employee / employer)
- Rate limiting on auth endpoints (slowapi)
- Request logging middleware
- Pydantic v2 input validation with stricƒt field constraints
- MongoDB indexes for query performance
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Literal

import bcrypt
from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_settings import BaseSettings
from pymongo import ASCENDING, MongoClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


# ---------------------------------------------------------------------------
# Logging — structured logs so you can trace issues in production
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config — all secrets come from environment variables, never hardcoded
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    jwt_secret: str = "changeme-use-a-long-random-string-in-production"
    jwt_expire_minutes: int = 1440  # 24 hours

    class Config:
        env_file = ".env"


settings = Settings()


# ---------------------------------------------------------------------------
# Database — create indexes on startup for efficient queries
# ---------------------------------------------------------------------------
client = MongoClient(settings.mongo_uri, tls=True, tlsAllowInvalidCertificates=True)

db = client["leave_app"]

# Indexes: unique email prevents duplicate accounts; status index speeds up
# employer queries that filter by status
db.users.create_index([("email", ASCENDING)], unique=True)
db.leaves.create_index([("employee_id", ASCENDING)])
db.leaves.create_index([("status", ASCENDING)])


# ---------------------------------------------------------------------------
# Rate limiter — prevents brute force attacks on auth endpoints
# ---------------------------------------------------------------------------
limiter = Limiter(key_func=get_remote_address)


# ---------------------------------------------------------------------------
# Auth utilities
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(payload: dict) -> str:
    data = {
        **payload,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.utcnow(),  # issued-at — useful for token audit
    }
    return jwt.encode(data, settings.jwt_secret, algorithm="HS256")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Decode JWT and return payload. Raises 401 if token is invalid or expired."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_employer(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="Access restricted to employers")
    return user


def require_employee(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Access restricted to employees")
    return user


# ---------------------------------------------------------------------------
# Request schemas — Pydantic validates and sanitizes all incoming data
# ---------------------------------------------------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr                          # validates email format
    password: str = Field(min_length=6, max_length=128)
    role: Literal["employee", "employer"]


class LeaveRequest(BaseModel):
    leave_type: str = Field(min_length=1, max_length=100)
    start_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")  # enforce YYYY-MM-DD
    end_date: str   = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    reason: str     = Field(min_length=10, max_length=500)    # forces meaningful reason

    @field_validator("end_date")
    @classmethod
    def end_must_be_after_start(cls, end_date, info):
        start = info.data.get("start_date")
        if start and end_date < start:
            raise ValueError("end_date must be on or after start_date")
        return end_date


# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="LeaveDesk API",
    version="1.0.0",
    description="Leave management REST API with JWT auth and RBAC",
)

# Rate limiter error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — in production, replace "*" with your Vercel frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request logging middleware — logs every request with method, path, duration
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000)
    logger.info(
        f"{request.method} {request.url.path} "
        f"→ {response.status_code} ({duration}ms)"
    )
    return response


# ---------------------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------------------
@app.post("/auth/register", status_code=201, tags=["Auth"])
@limiter.limit("10/minute")
def register(request: Request, body: RegisterRequest):
    """Create a new user. Email must be unique. Password is bcrypt-hashed."""
    if db.users.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    db.users.insert_one({
        "email": body.email,
        "password": hash_password(body.password),
        "role": body.role,
        "created_at": datetime.utcnow().isoformat(),
    })
    logger.info(f"New {body.role} registered: {body.email}")
    return {"message": "Account created successfully"}


@app.post("/auth/login", tags=["Auth"])
@limiter.limit("5/minute")   # 5 attempts/minute per IP — brute force protection
def login(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and return JWT. Username field = email."""
    user = db.users.find_one({"email": form.username})
    if not user or not verify_password(form.password, user["password"]):
        # Same error message for both cases — don't leak which one failed
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user["role"],
    })
    logger.info(f"Login: {user['email']}")
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}


# ---------------------------------------------------------------------------
# Employee routes
# ---------------------------------------------------------------------------
@app.post("/leaves", status_code=201, tags=["Leaves"])
def apply_for_leave(body: LeaveRequest, user: dict = Depends(require_employee)):
    """Submit a leave application. Validation is handled by the Pydantic model."""
    db.leaves.insert_one({
        "employee_id": user["sub"],
        "employee_email": user["email"],
        "leave_type": body.leave_type,
        "start_date": body.start_date,
        "end_date": body.end_date,
        "reason": body.reason,
        "status": "Pending",
        "applied_at": datetime.utcnow().isoformat(),
    })
    return {"message": "Leave application submitted"}


@app.get("/leaves/mine", tags=["Leaves"])
def get_my_leaves(user: dict = Depends(get_current_user)):
    """Return the current user's leave history, newest first."""
    leaves = list(
        db.leaves
        .find({"employee_id": user["sub"]})
        .sort("applied_at", -1)  # newest first
    )
    for leave in leaves:
        leave["id"] = str(leave.pop("_id"))
    return leaves


# ---------------------------------------------------------------------------
# Employer routes
# ---------------------------------------------------------------------------
@app.get("/leaves", tags=["Leaves"])
def get_all_leaves(
    user: dict = Depends(require_employer),
    status: str | None = None,   # optional ?status=Pending filter
):
    """Return all leave applications. Optionally filter by status."""
    query = {}
    if status in ("Pending", "Approved", "Rejected"):
        query["status"] = status

    leaves = list(db.leaves.find(query).sort("applied_at", -1))
    for leave in leaves:
        leave["id"] = str(leave.pop("_id"))
    return leaves


@app.patch("/leaves/{leave_id}/approve", tags=["Leaves"])
def approve_leave(leave_id: str, user: dict = Depends(require_employer)):
    result = db.leaves.update_one(
        {"_id": ObjectId(leave_id), "status": "Pending"},  # only update if still pending
        {"$set": {"status": "Approved", "actioned_by": user["email"],
                  "actioned_at": datetime.utcnow().isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave not found or already actioned")
    logger.info(f"Leave {leave_id} approved by {user['email']}")
    return {"message": "Leave approved"}


@app.patch("/leaves/{leave_id}/reject", tags=["Leaves"])
def reject_leave(leave_id: str, user: dict = Depends(require_employer)):
    result = db.leaves.update_one(
        {"_id": ObjectId(leave_id), "status": "Pending"},
        {"$set": {"status": "Rejected", "actioned_by": user["email"],
                  "actioned_at": datetime.utcnow().isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Leave not found or already actioned")
    logger.info(f"Leave {leave_id} rejected by {user['email']}")
    return {"message": "Leave rejected"}


# ---------------------------------------------------------------------------
# Health check — used by Railway/deployment platform to verify app is alive
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"])
def health():
    """Returns 200 if the API is running. Deployment platforms ping this."""
    try:
        # Verify DB connection is alive
        client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
    }
