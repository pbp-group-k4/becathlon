# Becathlon

> A Django-powered storefront that mirrors the visual polish and browsing experience of Decathlon—minus the heavy operational tooling.


## Team Members

- Muhammad Adra Prakoso – Backend developer / 2406453530
- Berguegou Briana Yadjam – Frontend and Backend / 2506561555
- Zahran Musyaffa Ramadhan Mulya – 2406365401
- Gunata Prajna Putra Sakri – 2406453461
- Muhammad Vegard Fathul Islam – 2406365332
- Kent Wilbert Wijaya

## Application Story & Benefits

### 1. 🏠 Landing Page
Users start on the homepage, where they can explore the **Catalog** or **Sign In / Sign Up** to create an account.

---

### 2. 👥 Account Selection
When registering, users choose between:
- **Buyer** — can browse and order products.  
- **Seller** — can list and manage products.

---

### 3. 🧑‍💼 Seller Features
Sellers can:
- Add new product listings with name, price, and details.  
- Edit or delete their listings.  
- View and track buyer orders.

---

### 4. 🧍 Buyer Features
Buyers can:
- Browse products by category.  
- Add items to the cart.  
- Checkout to place orders.  
- Track their order status in the **Orders** tab.

---

### 5. 🛒 Cart & Orders
- The **Cart** stores selected items before checkout.  
- The **Orders** tab lets buyers monitor order progress (Pending → Shipped → Delivered).


## Modules

| App Name | Modules | Purpose |
|----------|---------|---------|
| main  | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/main/, static/main/ | Homepage, navigation, footer, about pages |
| authentication | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/authentication/ | User login, registration, logout |
| catalog | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/catalog/, static/catalog/, fixtures/products.json | Product listings, categories, product details |
| search | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/search/, static/search/ | Search functionality with filters |
| cart | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/cart/, static/cart/ | Shopping cart management |
| checkout | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/checkout/, static/checkout/ | Mock checkout process |
| orders | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/orders/, static/orders/ | Order history and mock refunds |
| stores | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/stores/, static/stores/, fixtures/stores.json | Store locator with mock locations |
| recommendations | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/recommendations/ | recommendation system |
| profiles | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/profiles/, static/profiles/ | User profiles and preferences |

## Initial Dataset Source 

- https://www.kaggle.com/datasets/whenamancodes/adidas-us-retail-products-dataset
- https://www.kaggle.com/datasets/joyshil0599/h-and-m-sports-apparel-data-set9k
- https://github.com/MaxwellHouston/E-Commerce-Full-Stack
  
## User Roles

| Role              | Description | Permissions | Relevant Modules |
|-------------------|-------------|-------------|------------------|
| **Guest / Visitor** | Unregistered users browsing the site. | - View products, categories, promotions<br>- Search and filter items<br>- Add to temporary cart (session-based)<br>- Read reviews (limited) | `main` (homepage, about)<br>`catalog` (product listings, categories)<br>`search` (search & filters)<br>`cart` (temporary cart)<br>`recommendations` (basic suggestions) |
| **Client / Customer** | Registered shoppers with an account. | - Everything a guest can do<br>- Manage profile (addresses, preferences)<br>- Place orders<br>- Checkout with payment<br>- Write reviews & ratings<br>- Save wishlists<br>- Access personalized recommendations | `authentication` (login, registration)<br>`profiles` (user info, preferences)<br>`cart` (persistent cart)<br>`checkout` (payment, shipping)<br>`orders` (order history, refunds)<br>`recommendations` (personalized) |
| **Administrator** | Full control over the platform. | - Manage all users, roles, and permissions<br>- Add/edit/remove products<br>- Configure payments, shipping, taxes<br>- Access analytics<br>- Approve/remove content<br>- Handle disputes and refunds | `authentication` (user management)<br>`profiles` (role assignments)<br>`catalog` (product management)<br>`checkout` (payment config)<br>`orders` (refunds, disputes)<br>`stores` (store management)<br>`admin.py` across all apps |

## PWS deployment link and design link

https://muhammad-vegard-becathlon.pbp.cs.ui.ac.id/

