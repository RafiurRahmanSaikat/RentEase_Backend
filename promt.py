    Create a modern, production-ready React.js frontend for a House Rent application that connects to a Django Rest Framework (DRF) API. The frontend should follow best practices, be highly scalable, and ensure a smooth user experience. I have include the bakend api.http file

    React.js
    Tailwind CSS Javsascript
    Axios
    Lucide React Icons
    Stripe toast etc whatever u need but never use (nextjs typeacript)

    make constans/index.js file to load statik data like base backend urls navlinks etc
    make componets/ui for reuable componts like buttons imnputs card modal etc
    make services folder and do backend jobs with axios like data fetch update etc
    try to avoid svgs use lucid react icons instead

    make the ui stunning

    Clean and minimal UI with smooth animations
    Fully responsive (mobile-first)
    Dark mode support (optional)
    Consistent  UI with Tailwind CSS

    add gradinents animatoin shadow background patterns light dark mood

    User Authentication:

    Register (regular users and admins)
    Email verification
    JWT-based login/authentication
    Profile management (view/update)
    Token refresh

    Password Management:
    Change password (authenticated users)
    Request password reset
    Reset password confirmation

    House Listings:

    Create, read, update house listings
    Add multiple categories to houses
    View lightweight list or detailed house information

    Interactions:

    Rent Requests:

    Send rent requests with custom messages
    Accept/reject requests (owners or admins)
    Process payments via Stripe
    View all rent requests

    Reviews:
    Add, update, and delete reviews for houses
    View average ratings and review counts

    Favorites:
    Add/remove houses to personal favorite list
    View all favorited houses

    Admin Capabilities:

    Manage all users (create, view, update)
    Manage house listings (approve, update, view all including unapproved)
    Manage categories
    Override rent request processes



    Backend API (Django DRF) Reference:

    Base URL: http://127.0.0.1:8000/api/

    Endpoints include:

    /api/auth/register/ (Register)
    /api/auth/login/ (Login)
    /api/auth/profile/ (User profile)
    /api/properties/houses/ (List houses)
    /api/properties/houses/<id>/ (House details)
    /api/interactions/rent-requests/ (Rent requests)
    /api/interactions/reviews/ (Reviews)
    /api/interactions/favorites/ (Favorites)
    /api/admin/users/ (Admin user management)



@baseurl = http://127.0.0.1:8000

###! ================== ACCOUNT ENDPOINTS ================== ##
###? 1. Register a Regular User
POST {{baseurl}}/api/auth/register/
Content-Type: application/json

{
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "johndoe@example.com",
  "password": "#password123",
  "password2": "#password123",
  "phone": "1234567890",
  "address": "123 Main St, City",
  "image": "http://example.com/profile.jpg"
}

###? 2. Register an Admin User
POST {{baseurl}}/api/auth/register/
Content-Type: application/json

{
  "username": "adminuser",
  "first_name": "Admin",
  "last_name": "User",
  "email": "adminuser@admin.com",
  "password": "AdminPass123",
  "password2": "AdminPass123",
  "phone": "1122334455",
  "address": "789 New St, City",
  "image": "http://example.com/another_profile.jpg",
  "role": "admin"
}

###? 3. Verify Email (Replace YOUR_VERIFICATION_TOKEN with actual token)
GET {{baseurl}}/api/auth/email-verify/?token=YOUR_VERIFICATION_TOKEN

###? 4. Login & Obtain JWT Token for Regular User
# @name userLogin
POST {{baseurl}}/api/auth/login/
Content-Type: application/json

{
  "username": "john_doe",
  "password": "password123"
}

###? 5. GET Profile (Authenticated User)
GET {{baseurl}}/api/auth/profile/
Authorization: Bearer {{user_access_token}}

###? 6. Update User Profile (Full Update)
PUT {{baseurl}}/api/auth/profile/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "first_name": "UpdatedFirstName",
  "last_name": "UpdatedLastName",
  "username": "johndoe_updated",
  "email": "johndoe_updated@example.com",
  "phone": "0987654321",
  "address": "Updated Address",
  "image": "http://example.com/new_profile.jpg"
}

###? 7. Update User Profile (Update only first_name)
PATCH {{baseurl}}/api/auth/profile/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "username": "jonh_doe"
}

###? 8. Update User Profile (Update only last_name and phone)
PATCH {{baseurl}}/api/auth/profile/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "last_name": "UpdatedLastName",
  "phone": "0987654321"
}

###? 9. Login & Obtain JWT Token for Admin User
# @name adminLogin
POST {{baseurl}}/api/auth/login/
Content-Type: application/json

{
  "username": "adminuser",
  "password": "password123"
}

###? 10. (Optional) Login as a House Owner (e.g. one regular user)
# @name ownerLogin
POST {{baseurl}}/api/auth/login/
Content-Type: application/json

{
  "username": "frank_garcia",
  "password": "password123"
}

###! Save Tokens:
@user_access_token = {{userLogin.response.body.access}}
@user_refresh_token = {{userLogin.response.body.refresh}}
@admin_access_token = {{adminLogin.response.body.access}}
@owner_access_token = {{ownerLogin.response.body.access}}

###! ================== PASSWORD ENDPOINTS ================== ##
###? 11. Change Password (Authenticated User)
POST {{baseurl}}/api/auth/change-password/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "current_password": "password123",
  "new_password": "Newpassword123",
  "new_password2": "Newpassword123"
}

###? 12. Request Password Reset
POST {{baseurl}}/api/auth/reset-password/
Content-Type: application/json

{
  "email": "johndoe@example.com"
}


###? 13. Confirm Password Reset (Replace <uidb64> and <token> accordingly)

#POST {{baseurl}}/api/auth/reset-password-confirm/<uidb64>/<token>/

POST http://127.0.0.1:8000/api/auth/reset-password-confirm/MjE/clw5p8-fe06e76424fba954d76fe8a75befbefd/
Content-Type: application/json

{
  "new_password": "Newpassword123",
  "new_password2": "Newpassword123"
}

###! ================== PROPERTIES ENDPOINTS ================== ##
###? 14. List Approved Houses (Paginated; regular users see only approved houses)
GET {{baseurl}}/api/properties/houses/?page=1
Authorization: Bearer {{user_access_token}}

###? 15. Create a House Listing (Requires Auth; created as unapproved)
POST {{baseurl}}/api/properties/houses/
Content-Type: application/json
Authorization: Bearer {{owner_access_token}}

{
  "title": "Test Apartment",
  "description": "A test apartment with modern amenities.",
  "location": "New York",
  "price": "1200.00",
  "images": "http://example.com/house1.jpg,http://example.com/house2.jpg",
  "category_ids": [1]
}

###? 16. Get House Details (Public - full details with owner and reviews)
GET {{baseurl}}/api/properties/houses/6/

###? 17. Submit House for Approval (Owner Only)
POST {{baseurl}}/api/properties/houses/26/submit_for_approval/
Authorization: Bearer {{owner_access_token}}

###? 18. Approve House Listing (Admin Only; assume house ID is 27)
POST {{baseurl}}/api/properties/houses/26/approve/
Authorization: Bearer {{admin_access_token}}

###! ================== INTERACTIONS ENDPOINTS ================== ##
###? 19. Create a Rent Request (Requires Auth; include duration in days)
POST {{baseurl}}/api/interactions/rent-requests/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "house_id": 26,
  "duration": 30,
  "message": "I am john want to rent this house for one month."
}

###? 20. List Rent Requests Sent by User (Paginated)
GET {{baseurl}}/api/interactions/rent-requests/?page=1
Authorization: Bearer {{user_access_token}}

###? 21. Accept Rent Request as Owner (Assume rent request ID is 26)
POST {{baseurl}}/api/interactions/rent-requests/26/accept/
Authorization: Bearer {{owner_access_token}}

###? 22. Accept Rent Request as Admin (Assume rent request ID is 26)
POST {{baseurl}}/api/interactions/rent-requests/26/accept/
Authorization: Bearer {{admin_access_token}}

###? 23. Reject Rent Request as Admin (Assume rent request ID is 26)
POST {{baseurl}}/api/interactions/rent-requests/26/reject/
Authorization: Bearer {{admin_access_token}}

###? 24. Process Payment for Rent Request (Assume rent request ID is 1)
POST {{baseurl}}/api/interactions/rent-requests/26/pay/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "stripeToken": "tok_visa"
}

###? 25. List All Reviews (Paginated)
GET {{baseurl}}/api/interactions/reviews/?page=1
Authorization: Bearer {{admin_access_token}}

###? 26. Add a Review for a House (Using house_id in URL)
POST {{baseurl}}/api/properties/houses/20/add_review/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "rating": 4,
  "comment": "I really like this house. Worth renting!"
}

###? 27. Update a Review (Assume review ID is 53)
PUT {{baseurl}}/api/interactions/reviews/53/
Content-Type: application/json
Authorization: Bearer {{user_access_token}}

{
  "rating": 2,
  "comment": "Updated: Good house, but with minor issues."
}

###? 28. Delete a Review (Assume review ID is 53)
DELETE {{baseurl}}/api/interactions/reviews/53/
Authorization: Bearer {{user_access_token}}

###? 29. List Favorite Houses (Paginated)
GET {{baseurl}}/api/interactions/favorites/?page=1
Authorization: Bearer {{user_access_token}}

###? 30. Add a Favorite via URL (Pass house id in URL)
POST {{baseurl}}/api/interactions/favorites/26/add/
Authorization: Bearer {{user_access_token}}

###? 31. Remove a Favorite via URL (Pass house id in URL)
DELETE {{baseurl}}/api/interactions/favorites/3/remove/
Authorization: Bearer {{user_access_token}}

###! ================== ADMIN ENDPOINTS ================== ##
###? 32. List All Categories (Paginated)
GET {{baseurl}}/api/properties/categories/?page=1
Authorization: Bearer {{admin_access_token}}

###? 33. Create a Category
POST {{baseurl}}/api/properties/categories/
Content-Type: application/json
Authorization: Bearer {{admin_access_token}}

{
  "name": "Residential",
  "description": "Residential apartments and houses"
}

###? 34. List All Houses (Admin sees all, Paginated)
GET {{baseurl}}/api/properties/houses/?page=1
Authorization: Bearer {{admin_access_token}}

###? 35. Update House (Admin Only; assume house ID is 2)
PUT {{baseurl}}/api/properties/houses/26/
Content-Type: application/json
Authorization: Bearer {{admin_access_token}}

{
  "title": "Updated Cozy Apartment",
  "description": "Updated description for the house.",
  "location": "Downtown",
  "price": "10.00",
  "images": "http://example.com/updated1.jpg,http://example.com/updated2.jpg",
  "category_ids": [1],
  "approved": true
}

###? 36. List All Users (Admin Only, Paginated)
GET {{baseurl}}/api/admin/users/?page=1
Authorization: Bearer {{admin_access_token}}

###? 37. Create a User (Admin Only)
POST {{baseurl}}/api/admin/users/
Content-Type: application/json
Authorization: Bearer {{admin_access_token}}

{
  "username": "newAdmin",
  "first_name": "New",
  "last_name": "Admin",
  "email": "newAdmin@example.com",
  "password": "password123",
  "phone": "1122334455",
  "address": "789 New St, City",
  "image": "http://example.com/another_profile.jpg",
  "role": "admin"
}
