# Login Process & Authentication System

## Overview
We have implemented a secure JWT (JSON Web Token) authentication system that replaces the previous static mock authentication. This system is backed by a real database with role-based access control (RBAC).

## Architecture
- **Backend**: Django + Django REST Framework + SimpleJWT
- **Database**: PostgreSQL (Tables: `users`, `roles`, `permissions`)
- **Frontend**: React (HydroSync Partner)

## Authentication Flow

1.  **Login Request**
    *   Frontend sends `POST /api/auth/login` with `email` and `password`.
    *   Backend validates credentials against the `users` table.
    *   Backend checks if user status is `active`.

2.  **Token Generation**
    *   If valid, Backend generates:
        *   **Access Token** (Valid for 60 minutes): Used for API requests.
        *   **Refresh Token** (Valid for 7 days): Used to get new access tokens.

3.  **Response**
    *   Backend returns the tokens + full User object + Role + Permissions.
    *   **Crucial**: The `permissions` array returned matches the structure expected by the frontend `RoleGuard`.

4.  **Frontend Handling**
    *   Frontend stores tokens in `localStorage` (or cookies).
    *   Frontend updates the Authentication Context.
    *   `RoleGuard` uses the permissions data to allow/block access to routes.

## Database Roles & Permissions
We have seeded the database with 6 standard roles and their specific permissions:

| Role | Level | Key Permissions |
| :--- | :--- | :--- |
| **Admin** | 5 | All Access (`*:*`) |
| **Manager** | 4 | Dashboard, Reports, Billing, Users (Read) |
| **Technician** | 3 | Work Orders (Update), Field Ops, Meters |
| **Operator** | 3 | Meters, Quality, Emergency, Map |
| **Customer Service** | 2 | Clients, Billing, Revenue |
| **Viewer** | 1 | Dashboard, Reports (Read Only) |

## API Endpoints

### Authentication
*   `POST /api/auth/login`: Authenticate user
*   `POST /api/auth/logout`: Invalidate refresh token
*   `GET /api/auth/me`: Get current user details

### User Management (Admin Only)
*   `GET /api/users`: List all partner users
*   `POST /api/users`: Create a new user
*   `PUT /api/users/<id>`: Update a user
*   `DELETE /api/users/<id>`: Soft delete a user

## How to Test
1.  Ensure backend is running: `python manage.py runserver`
2.  Use Postman or the Frontend Login page.
3.  Default seeded users (if created) or use `createsuperuser` to create an initial admin.
