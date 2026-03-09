# LeaveDesk — Leave Management Application

A full-stack web application where employees apply for leave and employers approve or reject requests.

---

## Architecture

```
┌─────────────────────┐        HTTPS / REST        ┌──────────────────────┐
│   Vue 3 + Tailwind  │  ─────────────────────────▶ │  FastAPI (Python)    │
│   Hosted on Vercel  │  ◀─────────────────────────  │  Hosted on Railway   │
└─────────────────────┘       JSON responses        └──────────┬───────────┘
                                                               │ PyMongo
                                                               ▼
                                                    ┌──────────────────────┐
                                                    │   MongoDB Atlas      │
                                                    │   (Free shared tier) │
                                                    └──────────────────────┘
```

**Auth flow:**
1. User registers → password hashed with bcrypt → stored in MongoDB
2. User logs in → credentials verified → server returns a signed JWT
3. Frontend stores JWT in localStorage
4. Every API request sends `Authorization: Bearer <token>` header
5. Backend decodes JWT, extracts role, enforces RBAC on protected routes

---

## Tech Stack

| Layer      | Technology          | Why                                          |
|------------|---------------------|----------------------------------------------|
| Frontend   | Vue 3 + Vite        | Composition API, fast HMR, simple SFC syntax |
| Styling    | Tailwind CSS        | Utility-first, no custom CSS needed          |
| State      | Pinia               | Lightweight Vue state management             |
| HTTP       | Axios               | Interceptors for automatic JWT attachment    |
| Backend    | FastAPI (Python)    | Auto docs, type hints, fast to scaffold      |
| Auth       | JWT + bcrypt        | Stateless auth, secure password hashing      |
| Database   | MongoDB Atlas       | Flexible schema, free tier, easy connection  |
| Deployment | Railway + Vercel    | Free tier, GitHub-connected auto-deploy      |

---

## Project Structure

```
leave-app/
├── backend/
│   ├── main.py          # All routes, auth, DB logic
│   ├── requirements.txt
│   └── .env.example
│
└── frontend/
    ├── src/
    │   ├── api.js                    # Axios instance + interceptors
    │   ├── main.js                   # App entry point
    │   ├── App.vue                   # Root layout + nav
    │   ├── router/
    │   │   └── index.js              # Routes + navigation guards
    │   ├── stores/
    │   │   └── auth.js               # Pinia auth store (JWT, role, email)
    │   ├── views/
    │   │   ├── Login.vue
    │   │   ├── Register.vue
    │   │   ├── Employee.vue          # Apply + view own leaves
    │   │   └── Employer.vue          # View all + approve/reject
    │   └── components/
    │       └── StatusBadge.vue       # Reusable status chip
    ├── index.html
    ├── vite.config.js
    ├── tailwind.config.js
    └── package.json
```

---

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- A MongoDB Atlas free cluster

### Backend

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env: add your MONGO_URI and a random JWT_SECRET

# Run
uvicorn main:app --reload
# API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Frontend

```bash
cd frontend

npm install

cp .env.example .env
# Edit .env: set VITE_API_URL=http://localhost:8000

npm run dev
# App: http://localhost:5173
```

---

## API Reference

### Auth

| Method | Endpoint         | Auth | Body                              | Description          |
|--------|------------------|------|-----------------------------------|----------------------|
| POST   | `/auth/register` | —    | `{email, password, role}`         | Create account       |
| POST   | `/auth/login`    | —    | form-data: `{username, password}` | Login → returns JWT  |

### Leaves

| Method | Endpoint                    | Auth     | Description                       |
|--------|-----------------------------|----------|-----------------------------------|
| POST   | `/leaves`                   | Employee | Submit a leave application        |
| GET    | `/leaves/mine`              | Any      | Get current user's leaves         |
| GET    | `/leaves`                   | Employer | Get all employee leave requests   |
| PATCH  | `/leaves/{id}/approve`      | Employer | Approve a leave request           |
| PATCH  | `/leaves/{id}/reject`       | Employer | Reject a leave request            |
| GET    | `/health`                   | —        | Health check                      |

**JWT payload structure:**
```json
{ "sub": "<mongo_object_id>", "email": "user@co.com", "role": "employee|employer", "exp": 1234567890 }
```

---

## Deployment

### Backend → Railway

1. Push repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo, set **Root Directory** to `backend`
4. Add environment variables:
   ```
   MONGO_URI=mongodb+srv://...
   JWT_SECRET=your-secret-here
   ```
5. Railway auto-detects Python. Set start command:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
6. Copy the generated URL (e.g. `https://leavedesk-api.up.railway.app`)

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → Add New Project → Import GitHub repo
2. Set **Root Directory** to `frontend`
3. Add environment variable:
   ```
   VITE_API_URL=https://leavedesk-api.up.railway.app
   ```
4. Deploy. Vercel auto-detects Vite.

---

## Key Design Decisions

**Why JWT over sessions?**
JWTs are stateless — the server doesn't need to store session data. The token carries the user's ID and role, so every request is self-contained. This scales horizontally without shared session storage.

**Why bcrypt directly instead of passlib?**
passlib has a known version conflict with bcrypt 4.1+. Using bcrypt directly removes the dependency and is simpler to understand — `hashpw` and `checkpw` are the only two functions needed.

**Why MongoDB for this use case?**
The leave schema is simple and unlikely to need complex joins. MongoDB Atlas offers a free shared tier with a connection URI that works identically in local dev and production, which simplifies deployment.

**Why Pinia over Vuex?**
Pinia is the officially recommended state manager for Vue 3. It's simpler — no mutations, just actions and state — and the code is easier to read and explain.
