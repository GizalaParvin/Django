# Healthcare Management Backend API

A secure, robust, and production-ready Healthcare Management Backend API built with **Django REST Framework (DRF)**, **Simple JWT**, and **PostgreSQL**.

---

## 1. Project Overview

The Healthcare Management Backend provides a scalable RESTful API designed to manage patients, medical doctors, and patient-doctor assignments with strict role-based access control and data security.

Key features include:
- **Custom User Model**: Authentication using email and password with strong password hashing (`PBKDF2SHA256`).
- **JWT Authentication**: Industry-standard stateless authentication via access and refresh tokens.
- **Patient Management**: Secure CRUD endpoints where users have exclusive access to their own patient records.
- **Doctor Directory**: Global directory of verified medical doctors with strict creator-only modification and deletion policies.
- **Patient-Doctor Mappings**: Relational mapping allowing users to assign doctors to their patients, prevent duplicate assignments, and inspect assignments with full nested doctor profiles.
- **Security & Validation**: Multi-layer input validation, database uniqueness constraints, and cross-user data isolation returning `HTTP 404` to prevent information disclosure.
- **PostgreSQL Database**: Configured via environment variables for cloud and production readiness.

---

## 2. Technology Stack

- **Language**: Python 3.11+
- **Framework**: Django & Django REST Framework (DRF)
- **Database**: PostgreSQL (via `psycopg` / `psycopg[binary]`)
- **Authentication**: `djangorestframework-simplejwt`
- **Environment Management**: `python-dotenv`
- **Testing**: Django Test Framework & DRF `APITestCase`
- **API Documentation & Testing**: Postman Collection (v2.1)

---

## 3. Project Structure

```text
healthcare_backend/
├── manage.py                                 # Django command-line utility
├── requirements.txt                          # Project dependencies
├── .env                                      # Environment variables (kept private / gitignored)
├── .env.example                              # Template environment variables
├── .gitignore                                # Git ignore file
├── README.md                                 # Complete documentation
├── Healthcare_Backend.postman_collection.json # 17 endpoints with test scripts
├── config/                                   # Project configuration
│   ├── __init__.py
│   ├── settings.py                           # DRF, JWT, and PostgreSQL configuration
│   ├── urls.py                               # Master routing table
│   ├── asgi.py                               # ASGI entrypoint
│   └── wsgi.py                               # WSGI entrypoint
├── accounts/                                 # Custom User model and JWT endpoints
│   ├── models.py                             # User & CustomUserManager
│   ├── serializers.py                        # Register, Safe User, Token serializers
│   ├── views.py                              # Register, Login, Token Refresh views
│   ├── urls.py                               # /api/auth/ routes
│   ├── admin.py                              # Admin registration
│   └── tests.py                              # Auth test suite
├── patients/                                 # Patient records management
│   ├── models.py                             # Patient model with user ownership
│   ├── serializers.py                        # Validation & data conversion
│   ├── views.py                              # PatientViewSet with user filtering
│   ├── urls.py                               # /api/patients/ routes
│   ├── admin.py                              # Admin registration
│   └── tests.py                              # Patient CRUD & isolation tests
├── doctors/                                  # Doctor directory
│   ├── models.py                             # Doctor model with created_by tracking
│   ├── serializers.py                        # Validation & serialization
│   ├── views.py                              # DoctorViewSet (read all, write creator)
│   ├── urls.py                               # /api/doctors/ routes
│   ├── admin.py                              # Admin registration
│   └── tests.py                              # Doctor CRUD & permission tests
└── mappings/                                 # Patient-Doctor associations
    ├── models.py                             # PatientDoctorMapping with UniqueConstraint
    ├── serializers.py                        # Nested summaries & validation
    ├── views.py                              # MappingListCreate & Detail views
    ├── urls.py                               # /api/mappings/ routes
    ├── admin.py                              # Admin registration
    └── tests.py                              # Mapping tests & constraints
```

---

## 4. Prerequisites

1. **Python**: Python 3.11 or higher installed on your system.
2. **PostgreSQL**: PostgreSQL 14+ installed and running locally or on a remote server.
3. **PowerShell / Terminal**: Windows PowerShell (or bash for Linux/macOS).
4. **Postman**: (Optional) For automated and manual API testing.

---

## 5. PostgreSQL Setup Instructions

Before running database migrations or starting the Django server, you must ensure PostgreSQL is running and the database is created.

### Step 1: Install PostgreSQL
If PostgreSQL is not yet installed on Windows:
- Download the installer from [EnterpriseDB PostgreSQL](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads).
- Follow the setup wizard and set a password for the default `postgres` user (e.g. `postgres` or your custom password).

### Step 2: Create the Database
Open **pgAdmin** or run the following command in PowerShell / Command Prompt using `psql`:

```powershell
# Connect to PostgreSQL CLI
psql -U postgres

# In the psql prompt, run:
CREATE DATABASE healthcare_db;
\q
```

### Step 3: Configure Environment Variables
Copy the `.env.example` file to `.env`:

```powershell
Copy-Item .env.example .env
```

Open `.env` in your editor and configure your PostgreSQL credentials:

```env
SECRET_KEY=django-insecure-healthcare-backend-super-secret-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password_here
DB_HOST=localhost
DB_PORT=5432
```

> **Note**: PostgreSQL must be running and the `.env` file must be properly configured with your PostgreSQL credentials before running migrations.

---

## 6. Installation & Quick Start (Windows PowerShell)

Run the following commands in order from the project root directory:

```powershell
# 1. Create a virtual environment
py -m venv venv

# 2. Activate the virtual environment
.\venv\Scripts\Activate.ps1

# (If PowerShell blocks script execution, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Generate migrations (already created, but good practice to verify)
python manage.py makemigrations

# 5. Apply migrations to PostgreSQL
python manage.py migrate

# 6. Create a superuser for Django Admin
python manage.py createsuperuser

# 7. Start the local development server
python manage.py runserver
```

The API will now be live at: `http://127.0.0.1:8000/`

---

## 7. API Endpoints Specification

### Authentication APIs (`/api/auth/`)

| Method | Endpoint | Description | Requires Auth |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Register new user | No |
| `POST` | `/api/auth/login/` | Obtain JWT access & refresh tokens | No |
| `POST` | `/api/auth/token/refresh/` | Refresh access token | No |

#### 1. Register User
- **POST** `/api/auth/register/`
- **Request Body**:
```json
{
  "name": "Aman Sharma",
  "email": "aman@example.com",
  "password": "StrongPass123!"
}
```
- **Response** (`201 Created`):
```json
{
  "message": "User registered successfully.",
  "data": {
    "id": 1,
    "name": "Aman Sharma",
    "email": "aman@example.com",
    "date_joined": "2026-10-27T15:00:00Z"
  }
}
```

#### 2. Login
- **POST** `/api/auth/login/`
- **Request Body**:
```json
{
  "email": "aman@example.com",
  "password": "StrongPass123!"
}
```
- **Response** (`200 OK`):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
  "access": "eyJhbGciOiJIUzI1NiIsIn...",
  "user": {
    "id": 1,
    "name": "Aman Sharma",
    "email": "aman@example.com"
  }
}
```

#### 3. Refresh Token
- **POST** `/api/auth/token/refresh/`
- **Request Body**:
```json
{
  "refresh": "<refresh_token_here>"
}
```
- **Response** (`200 OK`):
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsIn..."
}
```

---

### Patient Management APIs (`/api/patients/`)

All patient endpoints require a **Bearer Token** in the `Authorization` header:  
`Authorization: Bearer <access_token>`

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/patients/` | Create a patient (automatically assigns requesting user as owner) |
| `GET` | `/api/patients/` | List only patients owned by the authenticated user |
| `GET` | `/api/patients/<id>/` | Retrieve patient by ID (404 if not owned) |
| `PUT` | `/api/patients/<id>/` | Update patient record (404 if not owned) |
| `DELETE` | `/api/patients/<id>/` | Delete patient record (404 if not owned) |

#### Create Patient
- **POST** `/api/patients/`
- **Request Body**:
```json
{
  "name": "Riya Sharma",
  "age": 28,
  "gender": "female",
  "address": "42 Park Avenue, New Delhi",
  "phone": "+919876543210"
}
```
- **Response** (`201 Created`):
```json
{
  "message": "Patient created successfully.",
  "data": {
    "id": 1,
    "name": "Riya Sharma",
    "age": 28,
    "gender": "female",
    "address": "42 Park Avenue, New Delhi",
    "phone": "+919876543210",
    "created_at": "2026-10-27T15:10:00Z",
    "updated_at": "2026-10-27T15:10:00Z"
  }
}
```

---

### Doctor Management APIs (`/api/doctors/`)

All doctor endpoints require a **Bearer Token**.

| Method | Endpoint | Access Policy |
|---|---|---|
| `POST` | `/api/doctors/` | Any authenticated user can create a doctor (associated via `created_by`) |
| `GET` | `/api/doctors/` | Any authenticated user can list the doctor directory |
| `GET` | `/api/doctors/<id>/` | Any authenticated user can retrieve doctor details |
| `PUT` | `/api/doctors/<id>/` | **Only creator** can update; returns `404 Not Found` for other users |
| `DELETE` | `/api/doctors/<id>/` | **Only creator** can delete; returns `404 Not Found` for other users |

#### Create Doctor
- **POST** `/api/doctors/`
- **Request Body**:
```json
{
  "name": "Rajesh Verma",
  "specialization": "Cardiology",
  "email": "dr.rajesh@example.com",
  "phone": "+919811223344",
  "qualification": "MBBS, MD (Cardiology)",
  "experience_years": 14
}
```
- **Response** (`201 Created`):
```json
{
  "message": "Doctor created successfully.",
  "data": {
    "id": 1,
    "name": "Rajesh Verma",
    "specialization": "Cardiology",
    "email": "dr.rajesh@example.com",
    "phone": "+919811223344",
    "qualification": "MBBS, MD (Cardiology)",
    "experience_years": 14,
    "created_by": 1,
    "created_by_email": "aman@example.com",
    "created_at": "2026-10-27T15:20:00Z",
    "updated_at": "2026-10-27T15:20:00Z"
  }
}
```

---

### Patient-Doctor Mapping APIs (`/api/mappings/`)

All mapping endpoints require a **Bearer Token**.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/mappings/` | Assign doctor to a patient owned by requesting user |
| `GET` | `/api/mappings/` | List mappings for all patients owned by requesting user |
| `GET` | `/api/mappings/<patient_id>/` | List all doctors assigned to `<patient_id>` with full doctor details |
| `DELETE` | `/api/mappings/<id>/` | Remove doctor assignment by mapping ID (404 if not owned) |

#### 1. Assign Doctor to Patient
- **POST** `/api/mappings/`
- **Request Body**:
```json
{
  "patient": 1,
  "doctor": 1
}
```
- **Response** (`201 Created`):
```json
{
  "message": "Doctor assigned to patient successfully.",
  "data": {
    "id": 1,
    "patient": {
      "id": 1,
      "name": "Riya Sharma",
      "age": 28,
      "gender": "female",
      "phone": "+919876543210"
    },
    "doctor": {
      "id": 1,
      "name": "Rajesh Verma",
      "specialization": "Cardiology",
      "email": "dr.rajesh@example.com",
      "phone": "+919811223344",
      "qualification": "MBBS, MD (Cardiology)",
      "experience_years": 14
    },
    "assigned_at": "2026-10-27T15:30:00Z"
  }
}
```

#### 2. Get Doctors Assigned to Patient
- **GET** `/api/mappings/1/` (where `1` is the patient ID)
- Returns HTTP 404 if patient 1 does not belong to the requesting user.
- **Response** (`200 OK`):
```json
[
  {
    "id": 1,
    "patient": {
      "id": 1,
      "name": "Riya Sharma",
      "age": 28,
      "gender": "female",
      "phone": "+919876543210"
    },
    "doctor": {
      "id": 1,
      "name": "Rajesh Verma",
      "specialization": "Cardiology",
      "email": "dr.rajesh@example.com",
      "phone": "+919811223344",
      "qualification": "MBBS, MD (Cardiology)",
      "experience_years": 14
    },
    "assigned_at": "2026-10-27T15:30:00Z"
  }
]
```

---

## 8. Postman Testing Guide

A ready-to-run Postman collection is included in the project:
`Healthcare_Backend.postman_collection.json`

### Importing into Postman:
1. Open Postman.
2. Click **Import** in the upper left.
3. Select `Healthcare_Backend.postman_collection.json` from the project folder.

### Running Requests:
1. Ensure your Django server is running (`python manage.py runserver`).
2. Run **1. Register User** or **2. Login**.
3. **Automated Token Capture**: The collection includes Postman test scripts that automatically save `access_token` and `refresh_token` to Collection Variables upon successful login.
4. Subsequent requests in **Patients**, **Doctors**, and **Mappings** automatically inherit and send this Bearer token!
5. As you create resources, `patient_id`, `doctor_id`, and `mapping_id` are also automatically stored for seamless chaining.

---

## 9. Automated Testing

The project includes 30 automated tests verifying:
- User registration, duplicate prevention, and password complexity.
- Authentication, invalid credentials, and JWT token refresh.
- Complete CRUD operations for Patients with cross-user boundary isolation.
- Doctor directory viewing and creator-only modification enforcement.
- Mapping creation, duplicate assignment rejection, patient-specific doctor retrieval, and secure deletion.

### Running Automated Tests:

With PostgreSQL running:
```powershell
.\venv\Scripts\python.exe manage.py test
```

Running tests in isolated test mode (without active PostgreSQL service):
```powershell
$env:USE_SQLITE_FOR_TESTS="True"; .\venv\Scripts\python.exe manage.py test
```

**Results:**
```text
Creating test database for alias 'default'...
..............................
----------------------------------------------------------------------
Ran 30 tests in 29.157s

OK
Destroying test database for alias 'default'...
```

---

## 10. Common Errors and Troubleshooting

| Error | Root Cause | Solution |
|---|---|---|
| `psycopg.OperationalError: connection to server ... failed` | PostgreSQL service is stopped or port 5432 is blocked. | Start the PostgreSQL Windows Service via `services.msc` or `Start-Service postgresql*`. |
| `FATAL: password authentication failed for user "postgres"` | Incorrect `DB_PASSWORD` in `.env`. | Verify your PostgreSQL password in `.env`. |
| `FATAL: database "healthcare_db" does not exist` | Database has not been created yet in PostgreSQL. | Run `CREATE DATABASE healthcare_db;` in `psql`. |
| `Authentication credentials were not provided.` (401) | Missing or invalid JWT token. | Provide header `Authorization: Bearer <your_access_token>`. |
| `Not Found` (404) when editing another user's patient/doctor | Intentional access control policy. | Users can only modify records they created or own. |
| `Scripts execution is disabled on this system` in PowerShell | PowerShell execution policy restriction. | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window. |
