# API Endpoints & Views Reference



Complete documentation of all HTTP endpoints and their behaviors.



## Endpoint Overview



Total Endpoints: 40+



- **Main App**: 5 endpoints (homepage, product detail, AJAX operations)

- **Authentication**: 3 endpoints (signup, login, logout)

- **Catalog**: 5 endpoints (browsing, filtering, quick view)

- **Cart**: 8 endpoints (view, add, update, remove, checkout flow)

- **Order**: 8 endpoints (checkout, confirmation, history, delivery tracking, ratings)

- **Profiles**: 4 endpoints (view, edit, settings)

- **Stores**: 3 endpoints (list, detail, search)

- **Django Admin**: Unlimited (all registered models)



## Request/Response Format



### Standard Success Response

```json

{

  "success": true,

  "data": {},

  "message": "Operation completed"

}

```



### Standard Error Response

```json

{

  "success": false,

  "error": "Detailed error message",

  "data": {}

}

```



### CSRF Protection

All POST requests require CSRF token:



**Form method** (HTML):



{% raw %}

```django

<form method="post">

  {% csrf_token %}

  <!-- form fields here -->

</form>

```

{% endraw %}



**AJAX header** (JavaScript):

```javascript

fetch(url, {

  method: 'POST',

  headers: {

    'X-CSRFToken': getCookie('csrftoken')

  }

});

```



## Main App Endpoints



### GET / (Homepage)

**View**: `apps.main.views.home`  

**Template**: `main/home.html`  

**Authentication**: Not required



**Context Variables:**

```python

{

    'products': Product.objects.all()[:12],  # Featured

    'cart': cart_object,                     # From context processor

    'cart_item_count': int,                  # From context processor

}

```



**Features:**

- Hero section with call-to-action

- Featured products carousel

- Category showcase

- Search bar integration

- User greeting (if logged in)



**Response**: HTML page  

**Status**: 200 OK



---



### GET /product/<product_id>/

**View**: `apps.main.views.product_detail`  

**Template**: `main/product_detail.html`  

**Authentication**: Not required



**URL Parameters:**

- `product_id` (int): Product primary key



**Context Variables:**

```python

{

    'product': Product_instance,

    'images': ProductImage.objects.filter(product_id),

    'related_products': Product.objects.filter(

        product_type=product.product_type

    ).exclude(id=product_id)[:5],

    'average_rating': decimal,

    'ratings': ProductRating.objects.filter(product_id),

    'user_can_rate': boolean,  # Current user purchased

}

```



**Errors:**

- 404: Product not found



**Response**: HTML page with detailed product info  

**Status**: 200 OK or 404 Not Found



---



### POST /api/products/ (Get Products AJAX)

**View**: `apps.main.views.get_products_ajax`  

**Authentication**: Not required



**Request Format:**

```json

{

  "page": 1,

  "category": "running"

}

```



**Response:**

```json

{

  "success": true,

  "products": [

    {

      "id": 1,

      "name": "Running Shoes",

      "price": "99.99",

      "image": "https://...",

      "category": "Running"

    }

  ],

  "total": 42,

  "page": 1,

  "per_page": 20

}

```



**Query Parameters:**

- `page`: Page number (default: 1)

- `category`: ProductType filter (optional)



**Status**: 200 OK



---



### POST /api/products/add/ (Create Product - Admin Only)

**View**: `apps.main.views.add_product_ajax`  

**Authentication**: Required (admin only)



**Request Format:**

```json

{

  "name": "New Product",

  "description": "Description",

  "price": "99.99",

  "product_type": 1,

  "stock": 50,

  "brand": "Nike",

  "image_url": "https://..."

}

```



**Response:**

```json

{

  "success": true,

  "product_id": 42,

  "message": "Product created successfully"

}

```



**Validation:**

- All required fields must be present

- Price must be positive decimal

- Stock must be non-negative integer

- ProductType must exist



**Errors:**

- 403: User not admin

- 400: Invalid data



**Status**: 201 Created or 400 Bad Request



---



### POST /api/products/<product_id>/delete/ (Delete Product - Admin Only)

**View**: `apps.main.views.delete_product_ajax`  

**Authentication**: Required (admin only)



**Response:**

```json

{

  "success": true,

  "message": "Product deleted"

}

```



**Side Effects:**

- Cascade delete ProductImage entries

- Cascade delete CartItem entries

- Cascade delete OrderItem entries (soft-delete recommended)



**Errors:**

- 404: Product not found

- 403: User not admin



**Status**: 200 OK



## Authentication Endpoints



### GET /auth/signup/

**View**: `apps.authentication.views.signup`  

**Template**: `authentication/signup.html`



**Form Fields:**

- username (text, required)

- email (email, required)

- password (password, required)

- password_confirm (password, required)



**Response**: HTML form



---



### POST /auth/signup/

**View**: `apps.authentication.views.signup`



**Form Data:**

```

username=user

email=user@example.com

password=SecurePass123

password_confirm=SecurePass123

```



**On Success:**

1. Create User account

2. Auto-create Customer record

3. Redirect to login page



**Validation:**

- Username not already taken

- Valid email format

- Passwords match

- Password meets security requirements



**Response**: Redirect to /auth/login/  

**Status**: 302 Found



---



### GET /auth/login/

**View**: `apps.authentication.views.login`  

**Template**: `authentication/login.html`



**Response**: HTML form



---



### POST /auth/login/

**View**: `apps.authentication.views.login`



**Form Data:**

```

username=user

password=SecurePass123

```



**On Success:**

1. Authenticate user

2. Create session

3. Call `transfer_guest_cart_to_user(request)`

4. Redirect to next page or homepage



**Validation:**

- User exists

- Password correct



**Response**: Redirect to referrer or /  

**Status**: 302 Found



---



### GET /auth/logout/

**View**: `apps.authentication.views.logout`



**On Success:**

1. Delete session

2. Clear user context

3. Redirect to homepage



**Response**: Redirect to /  

**Status**: 302 Found



## Cart Endpoints



### GET /cart/

**View**: `apps.cart.views.cart_view`  

**Authentication**: Not required (works for guests too)



**Context Variables:**

```python

{

    'cart': Cart_instance,

    'items': CartItem.objects.filter(cart=cart),

    'subtotal': decimal,

    'tax': decimal,

    'total': decimal,

}

```



**Response**: HTML cart page  

**Status**: 200 OK



---



### POST /cart/add/<product_id>/

**View**: `apps.cart.views.add_to_cart`  

**Authentication**: Not required



**Form Data:**

```

quantity=1

csrfmiddlewaretoken=...

```



**Response:**

```json

{

  "success": true,

  "message": "Added to cart",

  "cart_count": 3,

  "item_total": 2

}

```



**Logic:**

1. Get or create cart (guest or user)

2. Get or create CartItem

3. Increment quantity

4. Return updated item count



**Validation:**

- Product exists

- Quantity > 0

- Product in stock



**Errors:**

- 404: Product not found

- 400: Quantity invalid or out of stock



**Status**: 200 OK



---



### POST /cart/update/<item_id>/

**View**: `apps.cart.views.update_cart_item`



**Form Data:**

```

quantity=5

csrfmiddlewaretoken=...

```



**Response:**

```json

{

  "success": true,

  "new_quantity": 5,

  "item_total": 299.95

}

```



**Validation:**

- Quantity > 0

- Quantity <= product.stock



**Status**: 200 OK



---



### POST /cart/remove/<item_id>/

**View**: `apps.cart.views.remove_from_cart`



**Response:**

```json

{

  "success": true,

  "message": "Item removed",

  "remaining_count": 2

}

```



**Status**: 200 OK



---



### POST /cart/clear/

**View**: `apps.cart.views.clear_cart`



**Response:**

```json

{

  "success": true,

  "message": "Cart cleared"

}

```



**Status**: 200 OK



---



### POST /cart/api/summary/

**View**: `apps.cart.views.api_cart_summary`



**Response:**

```json

{

  "success": true,

  "item_count": 3,

  "item_total": 2,

  "subtotal": 299.95,

  "tax": 30.00,

  "total": 329.95

}

```



**Used by**: Header cart summary widget (polls on page load)



**Status**: 200 OK



---



### POST /cart/api/count/

**View**: `apps.cart.views.api_cart_count`



**Response:**

```json

{

  "count": 3

}

```



**Used by**: Header cart badge updates (polls frequently)



**Status**: 200 OK



---



### GET /cart/checkout/

**View**: `apps.cart.views.checkout_view`



**Redirect**: To /order/checkout/ (order app handles checkout)



**Status**: 302 Found



## Order Endpoints



### GET /order/checkout/

**View**: `apps.order.views.checkout_view`  

**Authentication**: Required (login to checkout)  

**Template**: `order/checkout.html`



**Context Variables:**

```python

{

    'cart': Cart_instance,

    'items': CartItem.objects.filter(cart=cart),

    'subtotal': decimal,

    'tax': decimal,

    'total': decimal,

    'shipping_form': ShippingAddressForm(),

    'payment_form': PaymentMethodForm(),

}

```



**Validation:**

- User logged in (redirects to login if not)

- Cart not empty (error message if empty)



**Response**: HTML checkout form with shipping and payment sections



---



### POST /order/checkout/

**View**: `apps.order.views.process_checkout`  

**Authentication**: Required



**Form Data:**

```

full_name=John Doe

phone_number=08123456789

address=123 Main St

postal_code=12345

city=Jakarta

payment_method=CREDIT_CARD

csrfmiddlewaretoken=...

```



**Process:**

1. Validate forms

2. Create ShippingAddress

3. Create Order from Cart

4. Create Payment record

5. Start delivery tracking

6. Clear cart

7. Redirect to success



**Response:**

- Success: Redirect to /order/checkout/success/<order_id>/

- Error: Re-render form with error messages



**Status**: 302 Found (redirect)



---



### GET /order/checkout/success/<order_id>/

**View**: `apps.order.views.checkout_success`  

**Authentication**: Not required  

**Template**: `order/checkout_success.html`



**Context Variables:**

```python

{

    'order': Order_instance,

    'items': OrderItem.objects.filter(order=order),

    'payment': Payment_instance,

    'delivery_status': 'PROCESSING',

    'delivery_progress': 25,  # 0-100%

}

```



**Features:**

- Order confirmation details

- Items recap with prices

- Delivery tracking with timeline

- Order number for reference

- Continue shopping button



**Response**: HTML confirmation page



---



### GET /order/

**View**: `apps.order.views.order_list`  

**Authentication**: Required  

**Template**: `order/order_list.html`



**Context Variables:**

```python

{

    'orders': Order.objects.filter(user=request.user),

    'page_obj': Paginator(orders, 10),

}

```



**Features:**

- List of user's orders

- Status badges

- Quick links to order detail

- Pagination



**Response**: HTML order history page



---



### GET /order/<order_id>/

**View**: `apps.order.views.order_detail`  

**Authentication**: Required (if not owner, 403)  

**Template**: `order/order_detail.html`



**Context Variables:**

```python

{

    'order': Order_instance,

    'items': OrderItem.objects.filter(order=order),

    'payment': Payment_instance,

    'delivery_status': 'EN_ROUTE',

    'delivery_progress': 65,

}

```



**Authorization:**

- Order owner or admin only

- 403 Forbidden if unauthorized



**Response**: HTML order detail page



---



### POST /order/<order_id>/status/

**View**: `apps.order.views.check_delivery_status`



**Response:**

```json

{

  "success": true,

  "status": "EN_ROUTE",

  "progress": 65,

  "remaining_seconds": 45

}

```



**Purpose**: Polled by frontend for real-time delivery updates



**Poll Interval**: Every 2-3 seconds on confirmation page



**Status**: 200 OK



---



### POST /order/<order_id>/rate/

**View**: `apps.order.views.submit_rating`  

**Authentication**: Required



**Form Data:**

```

product_id=5

rating=4

review_text=Great product!

csrfmiddlewaretoken=...

```



**Response:**

```json

{

  "success": true,

  "message": "Thank you for your rating!"

}

```



**Validation:**

- User purchased this product (checked via OrderItem)

- Rating is 1-5

- Only one rating per user per product



**Side Effects:**

- Creates ProductRating record

- Triggers signal to update Product.rating aggregate



**Errors:**

- 403: User didn't purchase this product

- 400: Invalid rating value



**Status**: 201 Created or 400 Bad Request



## Error Codes Reference



| Status | Meaning | Example |

|--------|---------|---------|

| 200 | OK | Successful GET/POST |

| 201 | Created | Product/Rating created |

| 302 | Found (Redirect) | Login redirect |

| 400 | Bad Request | Invalid form data |

| 403 | Forbidden | Not admin, not owner |

| 404 | Not Found | Product not found |

| 405 | Method Not Allowed | GET on POST endpoint |

| 500 | Server Error | Database error |



## Common Error Messages



```json

{

  "error": "Please log in to continue"

}

```



```json

{

  "error": "Product not found"

}

```



```json

{

  "error": "Insufficient stock (Available: 5, Requested: 10)"

}

```



```json

{

  "error": "Invalid quantity"

}

```



```json

{

  "error": "Cart is empty"

}

```



---



**Next**: [Frontend Architecture](./05-frontend-architecture.md)

