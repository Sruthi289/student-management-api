# Student Management API

A REST API for managing students and their courses, built with FastAPI and PostgreSQL. It has user signup and login with JWT tokens, and the endpoints that change data are protected so only logged-in users can use them.

**Live demo:** _add your Render link here after deploying_ (open `/docs` on that link to try the API)

## Features

- Full CRUD for students (create, read, update, delete)
- Courses linked to students through a foreign key
- A report endpoint that counts courses per student (SQL JOIN + GROUP BY)
- Signup and login with hashed passwords (bcrypt) and JWT access tokens
- Protected endpoints: creating, updating and deleting need a valid token
- Proper error responses (400, 401, 404) instead of default failures
- Secrets kept in environment variables, not in the code

## Tech stack

| Part | Tool |
|---|---|
| Language | Python |
| Framework | FastAPI |
| Database | PostgreSQL (hosted on Supabase) |
| ORM | SQLAlchemy |
| Authentication | JWT (PyJWT) and bcrypt |
| Hosting | Render |

## API endpoints

| Method | Path | Needs login | What it does |
|---|---|---|---|
| POST | `/signup` | No | Create a user account |
| POST | `/login` | No | Log in and get an access token |
| POST | `/students` | Yes | Add a student |
| GET | `/students` | No | List all students |
| GET | `/students/{id}` | No | Get one student (404 if not found) |
| PUT | `/students/{id}` | Yes | Update a student |
| DELETE | `/students/{id}` | Yes | Delete a student |
| POST | `/courses` | Yes | Add a course for a student |
| GET | `/students/{id}/courses` | No | List one student's courses |
| GET | `/reports/courses-per-student` | No | Number of courses for each student |

FastAPI also generates an interactive page at `/docs`, where you can try every endpoint. Use the **Authorize** button there to log in before calling the protected ones.

## Run it locally

1. Clone the repository:
   ```
   git clone https://github.com/Sruthi289/student-management-api.git
   cd student-management-api
   ```
2. Install the packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a file named `.env` in the project folder:
   ```
   DATABASE_URL=your-postgresql-connection-string
   SECRET_KEY=a-long-random-string
   ```
   You can generate a secret key with:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
4. Start the server:
   ```
   python -m uvicorn main:app --reload
   ```
5. Open `http://127.0.0.1:8000/docs`.

The tables (`students`, `courses`, `users`) are created automatically the first time the app connects to the database.

## Environment variables

| Name | Purpose |
|---|---|
| `DATABASE_URL` | Connection string for the PostgreSQL database |
| `SECRET_KEY` | Secret used to sign JWT tokens |

The `.env` file is listed in `.gitignore` and is never uploaded.

## Known limitations and next steps

- Deleting a student who still has courses fails, because of the foreign key. It needs to delete or reassign the courses first.
- Student and course inputs are sent as query parameters. Moving them to request bodies with Pydantic models would be cleaner.
- Database changes are not managed with migrations (for example Alembic).
- There are no automated tests yet.
- All logged-in users have the same permissions. There are no roles.

## What I learned building this

- How a client and a server talk to each other, and how FastAPI routes requests
- Defining tables as Python classes with SQLAlchemy, and how that maps to SQL
- Foreign keys, JOINs and GROUP BY through a real endpoint
- Password hashing and token-based authentication
- Keeping secrets out of the code, and deploying from GitHub
