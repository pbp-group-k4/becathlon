# Becathlon Implementation Guide



## What Was Implemented



### 1. Authentication System

- **Location**: `apps/authentication/`

- **Features**:

  - User registration (Sign Up)

  - User login

  - User logout

  - Custom sign-up form with email validation

  - Beautiful, modern UI with gradient design



### 2. Product Management System

- **Models** (in `apps/main/models.py`):

  - **Customer**: Extends Django User model for logged-in users

  - **ProductType**: Categories for sports equipment (Running, Cycling, Swimming, etc.)

  - **Product**: Main product model with fields:

    - name, description, price

    - product_type (ForeignKey)

    - stock, image_url

    - created_by (ForeignKey to User)

    - timestamps (created_at, updated_at)



### 3. Home Page with AJAX

- **Location**: `apps/main/templates/main/home.html`

- **Features**:

  - Minimalist, modern design with purple gradient theme

  - Responsive product grid layout

  - AJAX functionality for:

    - Loading products dynamically

    - Adding new products (logged-in users only)

    - Deleting products (only your own products)

  - Real-time updates without page refresh

  - Beautiful product cards with hover effects

  - Form validation



### 4. Access Control

- **Guest Users**: Can view all products but cannot add/delete

- **Logged-in Users (Customers)**: Can add products and delete their own products

- Clear visual prompts encouraging guests to sign up



## How to Use



### 1. Start the Development Server

```bash

python manage.py runserver

```



### 2. Access the Application

- Homepage: http://127.0.0.1:8000/

- Login: http://127.0.0.1:8000/auth/login/

- Sign Up: http://127.0.0.1:8000/auth/signup/



### 3. Create an Account

1. Click "Sign Up" in the navigation

2. Fill in the registration form

3. Log in with your credentials



### 4. Add Products

1. Once logged in, you'll see the "Add New Product" form on the homepage

2. Fill in:

   - Product Name

   - Product Type (dropdown with 12 sports categories)

   - Price

   - Stock

   - Description

   - Image URL (optional)

3. Click "Add Product"

4. Product appears instantly without page reload



### 5. Delete Products

- You can only delete products you created

- Click the "Delete" button on your product cards

- Confirm deletion in the popup



## Pre-seeded Data



The database includes 12 product types:

- Running

- Cycling

- Swimming

- Fitness

- Team Sports

- Racket Sports

- Hiking

- Camping

- Water Sports

- Winter Sports

- Yoga

- Boxing



## Technical Details



### Technologies Used

- **Backend**: Django 5.2.5

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)

- **AJAX**: Fetch API

- **Database**: SQLite (default Django)

- **Authentication**: Django's built-in auth system



### API Endpoints

- `GET /api/products/` - Get all products

- `POST /api/products/add/` - Add a new product (authenticated)

- `DELETE /api/products/<id>/delete/` - Delete a product (authenticated, owner only)



### Security Features

- CSRF protection on all forms

- Login required decorators on sensitive views

- Owner-only deletion (users can only delete their own products)

- Password validation

- SQL injection protection (Django ORM)



## Project Structure

```

becathlon/

├── apps/

│   ├── authentication/

│   │   ├── forms.py

│   │   ├── views.py

│   │   ├── urls.py

│   │   └── templates/

│   │       └── authentication/

│   │           ├── login.html

│   │           └── signup.html

│   └── main/

│       ├── models.py (Customer, Product, ProductType)

│       ├── views.py (home, AJAX endpoints)

│       ├── urls.py

│       ├── admin.py

│       └── templates/

│           └── main/

│               └── home.html

├── becathlon/

│   ├── settings.py

│   └── urls.py

└── seed_product_types.py

```



## Features Highlight



### Minimalist Design

- Clean, modern interface

- Purple gradient color scheme

- Smooth animations and transitions

- Responsive layout



### AJAX Benefits

- No page reloads

- Instant feedback

- Better user experience

- Real-time updates



### User Experience

- Clear visual feedback with messages

- Form validation

- Loading states

- Confirmation dialogs for destructive actions

- Empty states with helpful prompts



## Next Steps (Future Enhancements)

- Add product search and filtering

- Implement product editing

- Add user profile pages

- Product images upload (not just URLs)

- Shopping cart functionality

- Product reviews and ratings

- Admin dashboard for product management

