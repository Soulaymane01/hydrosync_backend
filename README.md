<div align="center">
  <img src="public/images/hydrosync-logo.png" alt="HydroSync Logo" width="120" height="120">
  
  # HydroSync Backend – API & Core Services
  
  **Enterprise-grade backend powering the HydroSync water management platform**

  [![Django](https://img.shields.io/badge/Django-5.0-092E20?style=flat-square&logo=django)](https://www.djangoproject.com/)
  [![Django REST Framework](https://img.shields.io/badge/DRF-3.15-red?style=flat-square)](https://www.django-rest-framework.org/)
  [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
  [![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

  [API Docs](#api-documentation) · [Setup](#quick-start) · [Report Bug](https://github.com/yourusername/hydrosync/issues) · [Request Feature](https://github.com/yourusername/hydrosync/issues)

</div>

---

## Overview

The HydroSync backend is a **scalable, secure, and modular REST API** built with Django and Django REST Framework.  
It serves as the core engine for managing users, operations, billing, analytics, and system integrity for municipal water utilities.

The backend is designed with:
- **Enterprise security**
- **Role-based access control**
- **Clean domain separation**
- **Production-ready architecture**

---

## Core Responsibilities

| Domain | Description |
|------|-------------|
| **Authentication & RBAC** | User authentication, roles, permissions |
| **Operations** | Assets, meters, work orders, incidents |
| **Business Logic** | Billing, inventory, compliance |
| **Analytics** | Consumption, performance, reporting |
| **Integrations** | Frontend, future IoT & third-party services |
| **Admin Tools** | Django Admin for internal operations |

---

## Quick Start

### Prerequisites

- Python **3.12+**
- PostgreSQL **14+**
- pip / virtualenv / pyenv (recommended)

---

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/hydrosync-backend.git
cd hydrosync-backend
```

## Create virtual environment
```bash
python -m venv venv
source .venv/bin/activate
```
## Install dependencies

```bash
pip install -r requirements.txt
```

# Environment variables
```bash
cp .env.example .env
```

## Run server 
- using django : 
```bash
python manage.py runserver
```