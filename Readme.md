
# House Rent API

A Django REST Framework project for a house rental application where users can list houses for rent, send rent requests, add reviews and favorites, and perform various interactions. Admins can manage users, houses, categories, rent requests, and more.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Endpoints](#endpoints)
  - [Account Endpoints](#account-endpoints)
  - [Properties Endpoints](#properties-endpoints)
  - [Interactions Endpoints](#interactions-endpoints)
  - [Admin Endpoints](#admin-endpoints)
- [Authentication](#authentication)
- [Populate Database](#populate-database)
- [API Testing](#api-testing)
- [License](#license)

---

## Features

- **User Authentication:**
  Register, verify email, login (JWT based), token refresh, profile update.
- **Password Management:**
  Change password, request password reset, and reset password confirmation.
- **House Listings:**
  Users can list houses, add multiple categories to a house, and view a lightweight list or full house details (with nested reviews and owner details).
- **Interactions:**
  - **Rent Requests:** Users can send rent requests (with a message), and owners or admins can accept/reject requests or process payments using Stripe.
  - **Reviews:** Users can add, update, and delete multiple reviews for a house. The house detail view includes all reviews, average rating, and review count.
  - **Favorites:** Users can add/remove houses to/from their favorite list (via URL endpoints).
- **Admin Capabilities:**
  Admin users (role=`admin` or superuser) can view all houses (approved and unapproved), update house details, and manage categories and users through the same endpoints if using an admin token.
- **Optimized Queries:**
  Use of `select_related` and `prefetch_related` to reduce database queries.

---

## Tech Stack

- **Backend:** Python, Django, Django REST Framework
- **Authentication:** JWT (via djangorestframework-simplejwt)
- **Payment Integration:** Stripe (for rent request payments)
- **Database:** SQLite (for development; configurable to other backends)
- **Email:** SMTP or Console Email Backend for development

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd house_rent

## Reset The Project

2. **Reset and Load Dummy Data:**
   ```bash
   rm db.sqlite3
   find . -path "*/migrations/*.py" -not -name "__init__.py" -exec rm -f {} \;
   find . -type d -name "__pycache__" -exec rm -r {} \;

   python manage.py makemigrations
   python manage.py migrate
   python populate_db.py
   python manage.py runserver





