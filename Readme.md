  # House Rent API

  A Django REST Framework project for a house rental application where users can list houses for rent, send rent requests, add reviews and favorites, and perform various interactions. Admins can manage users, houses, categories, rent requests, and more.

  ## Table of Contents

  - [Features](#features)
  - [Tech Stack](#tech-stack)
  - [Installation](#installation)
  - [Project Reset & Database Setup](#project-reset--database-setup)
  - [Project Structure](#project-structure)
  - [Configuration](#configuration)
  - [API Endpoints](#api-endpoints)
    - [Account Endpoints](#account-endpoints)
    - [Password Management Endpoints](#password-management-endpoints)
    - [Properties Endpoints](#properties-endpoints)
    - [Interactions Endpoints](#interactions-endpoints)
    - [Admin Endpoints](#admin-endpoints)
  - [Authentication](#authentication)
  - [User Roles](#user-roles)
  - [Testing the API](#testing-the-api)
  - [Payment Processing](#payment-processing)
  - [License](#license)

  ## Features

  - **User Authentication:**

    - Register (regular users and admins)
    - Email verification
    - JWT-based login/authentication
    - Profile management (view/update)
    - Token refresh

  - **Password Management:**

    - Change password (authenticated users)
    - Request password reset
    - Reset password confirmation

  - **House Listings:**

    - Create, read, update house listings
    - Add multiple categories to houses
    - View lightweight list or detailed house information
    - Approval workflow for new listings

  - **Interactions:**

    - **Rent Requests:**

      - Send rent requests with custom messages
      - Accept/reject requests (owners or admins)
      - Process payments via Stripe
      - View all rent requests

    - **Reviews:**

      - Add, update, and delete reviews for houses
      - View average ratings and review counts

    - **Favorites:**
      - Add/remove houses to personal favorite list
      - View all favorited houses

  - **Admin Capabilities:**

    - Manage all users (create, view, update)
    - Manage house listings (approve, update, view all including unapproved)
    - Manage categories
    - Override rent request processes

  - **Optimized Performance:**
    - Efficient database queries using `select_related` and `prefetch_related`
    - Pagination for list endpoints

  ## Tech Stack

  - **Backend:**

    - Python 3.x
    - Django
    - Django REST Framework

  - **Authentication:**

    - JWT (djangorestframework-simplejwt)

  - **Payment Integration:**

    - Stripe

  - **Database:**

    - SQLite (development)
    - Configurable for production databases

  - **Email:**
    - SMTP or Console Email Backend (configurable)

  ## Installation

  1. **Clone the repository:**

    ```bash
    git clone https://github.com/RafiurRahmanSaikat/RentEase_Backend
    cd house_rent
    ```

  2. **Set up a virtual environment (recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

  3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

  ## Project Reset & Database Setup

  Use these commands to reset the project and load dummy data for testing:

  ```bash
  # Reset database and migrations
  rm db.sqlite3
  find . -path "*/migrations/*.py" -not -name "__init__.py" -exec rm -f {} \;
  find . -type d -name "__pycache__" -exec rm -r {} \;

  # Set up static files and database
  python manage.py collectstatic
  python manage.py makemigrations
  python manage.py migrate

  # Load sample data
  python populate_db.py

  # Run the development server
  python manage.py runserver
  ```

  ## Project Structure

  The project is organized into several Django apps:

  - **accounts**: User authentication, registration, profile management
  - **properties**: House listings and categories management
  - **interactions**: Rent requests, reviews, and favorites
  - **admin_api**: Admin-specific functionality

  ## Configuration

  Key configurations can be found in `settings.py`:

  - JWT settings for authentication
  - Email backend configuration
  - Stripe API keys (for payment processing)
  - Database settings

  ## API Endpoints

  ### Account Endpoints

  | Method    | Endpoint                              | Description               | Auth Required |
  | --------- | ------------------------------------- | ------------------------- | ------------- |
  | POST      | `/api/auth/register/`                 | Register a new user       | No            |
  | GET       | `/api/auth/email-verify/?token=TOKEN` | Verify email              | No            |
  | POST      | `/api/auth/login/`                    | Log in and get JWT tokens | No            |
  | GET       | `/api/auth/profile/`                  | Get user profile          | Yes           |
  | PUT/PATCH | `/api/auth/profile/`                  | Update user profile       | Yes           |

  ### Password Management Endpoints

  | Method | Endpoint                                             | Description            | Auth Required |
  | ------ | ---------------------------------------------------- | ---------------------- | ------------- |
  | POST   | `/api/auth/change-password/`                         | Change password        | Yes           |
  | POST   | `/api/auth/reset-password/`                          | Request password reset | No            |
  | POST   | `/api/auth/reset-password-confirm/<uidb64>/<token>/` | Confirm password reset | No            |

  ### Properties Endpoints

  | Method    | Endpoint                                           | Description             | Auth Required     |
  | --------- | -------------------------------------------------- | ----------------------- | ----------------- |
  | GET       | `/api/properties/houses/`                          | List houses (paginated) | No                |
  | POST      | `/api/properties/houses/`                          | Create a house listing  | Yes               |
  | GET       | `/api/properties/houses/<id>/`                     | Get house details       | No                |
  | PUT/PATCH | `/api/properties/houses/<id>/`                     | Update house            | Yes (Owner/Admin) |
  | POST      | `/api/properties/houses/<id>/submit_for_approval/` | Submit for approval     | Yes (Owner)       |
  | POST      | `/api/properties/houses/<id>/approve/`             | Approve house           | Yes (Admin)       |
  | GET       | `/api/properties/categories/`                      | List categories         | No                |
  | POST      | `/api/properties/categories/`                      | Create category         | Yes (Admin)       |

  ### Interactions Endpoints

  | Method | Endpoint                                       | Description            | Auth Required      |
  | ------ | ---------------------------------------------- | ---------------------- | ------------------ |
  | POST   | `/api/interactions/rent-requests/`             | Create rent request    | Yes                |
  | GET    | `/api/interactions/rent-requests/`             | List rent requests     | Yes                |
  | POST   | `/api/interactions/rent-requests/<id>/accept/` | Accept rent request    | Yes (Owner/Admin)  |
  | POST   | `/api/interactions/rent-requests/<id>/reject/` | Reject rent request    | Yes (Owner/Admin)  |
  | POST   | `/api/interactions/rent-requests/<id>/pay/`    | Process payment        | Yes                |
  | GET    | `/api/interactions/reviews/`                   | List all reviews       | No                 |
  | POST   | `/api/properties/houses/<id>/add_review/`      | Add review to house    | Yes                |
  | PUT    | `/api/interactions/reviews/<id>/`              | Update review          | Yes (Author)       |
  | DELETE | `/api/interactions/reviews/<id>/`              | Delete review          | Yes (Author/Admin) |
  | GET    | `/api/interactions/favorites/`                 | List favorite houses   | Yes                |
  | POST   | `/api/interactions/favorites/<id>/add/`        | Add house to favorites | Yes                |
  | DELETE | `/api/interactions/favorites/<id>/remove/`     | Remove from favorites  | Yes                |

  ### Admin Endpoints

  | Method | Endpoint                 | Description    | Auth Required |
  | ------ | ------------------------ | -------------- | ------------- |
  | GET    | `/api/admin/users/`      | List all users | Yes (Admin)   |
  | POST   | `/api/admin/users/`      | Create a user  | Yes (Admin)   |
  | PUT    | `/api/admin/users/<id>/` | Update a user  | Yes (Admin)   |

  ## Authentication

  The API uses JWT (JSON Web Token) authentication:

  1. **Obtain tokens**: Send credentials to `/api/auth/login/` to receive access and refresh tokens
  2. **Use token**: Include the access token in the Authorization header for authenticated requests:
    ```
    Authorization: Bearer <access_token>
    ```
  3. **Refresh token**: Use the refresh token to get a new access token when it expires

  ## User Roles

  The system supports two main user roles:

  - **Regular User**: Can list properties, send rent requests, add reviews, manage favorites
  - **Admin User**: Has all regular user privileges plus administrative capabilities

  ## Testing the API

  You can test the API using REST clients like Postman, Insomnia, or the VS Code REST Client extension (using the provided api.http file).

  Sample user credentials from the populated database:

  - Regular User: username: `john_doe`, password: `password123`
  - Admin User: username: `adminuser`, password: `password123`
  - House Owner: username: `frank_garcia`, password: `password123`

  ## Payment Processing

  The API integrates with Stripe for payment processing:

  1. Send a rent request for a house
  2. When approved, use the `/api/interactions/rent-requests/<id>/pay/` endpoint with a Stripe token
  3. For testing, use Stripe's test tokens (e.g., `tok_visa`)

  ## License

  This project is licensed under the MIT License - see the LICENSE file for details.

  ## Contributors

  - Rafiur Rahman Saikat (GitHub: [RafiurRahmanSaikat](https://github.com/RafiurRahmanSaikat))
