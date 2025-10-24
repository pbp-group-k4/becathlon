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

### 🎯 What is Becathlon?

_Becathlon_ is a Django-powered e-commerce platform that brings the world of multisport equipment shopping online. Inspired by Decathlon's user-friendly design and comprehensive product offerings, Becathlon recreates the browsing experience of a modern sports retailer while serving as a learning platform for full-stack web development.

### 💡 The Story

In the digital age, sports enthusiasts need more than just a product catalog—they need an intuitive, engaging shopping experience that helps them find the right equipment for their passion. Whether you're a weekend cyclist, a yoga practitioner, or a serious mountaineer, Becathlon aims to make finding and purchasing sports equipment seamless and enjoyable.

Our platform bridges the gap between traditional brick-and-mortar sports stores and modern e-commerce, offering:
- **Comprehensive Product Catalog**: Browse thousands of sports products across multiple categories
- **Personalized Experience**: Get recommendations based on your interests and browsing history
- **Seamless Shopping Flow**: From discovery to checkout, every step is optimized for ease of use
- **Store Integration**: Find physical store locations when you need hands-on product experience

### ✨ Key Benefits

**For Customers:**
- 🛍️ **Easy Discovery**: Intuitive navigation and powerful search to find exactly what you need
- 🎨 **Visual Excellence**: Clean, modern interface that makes browsing a pleasure
- 💰 **Smart Shopping**: Compare products, read details, and make informed decisions
- 📦 **Order Tracking**: Keep tabs on your purchases from checkout to delivery
- 👤 **Personalized Experience**: Tailored recommendations and saved preferences

**For Administrators:**
- 🔧 **Complete Control**: Manage products, categories, and inventory through Django admin
- 👥 **User Management**: Handle customer accounts and permissions efficiently
- 📊 **Data Insights**: Track orders, popular products, and user behavior
- 🏪 **Store Management**: Maintain store locations and information

**For Developers:**
- 🚀 **Modern Stack**: Built with Django, demonstrating best practices in web development
- 🧪 **Well Tested**: 82% code coverage ensuring reliability and maintainability
- 📚 **Learning Resource**: Clean architecture suitable for studying Django patterns
- 🔄 **Scalable Design**: Modular app structure ready for expansion

### 🌊 Website Flow

#### **For Guest Visitors:**
```
Landing Page → Browse Categories → View Products → Search/Filter 
     ↓              ↓                    ↓              ↓
  About Us    Product Details      Add to Cart    Find Stores
                    ↓                    ↓
              [Register/Login]    [Register to Checkout]
```

#### **For Registered Customers:**
```
Login → Homepage → Browse/Search Products
  ↓         ↓            ↓
Profile  Featured    Product Details → Add to Cart → View Cart
  ↓      Products         ↓                              ↓
Edit                 Recommendations            Update Quantities
Info                                                     ↓
                                               Proceed to Checkout
                                                        ↓
                                            Enter Shipping Details
                                                        ↓
                                              Review & Place Order
                                                        ↓
                                                Order Confirmation
                                                        ↓
                                              Track Order Status
                                                        ↓
                                              View Order History
```

#### **For Administrators:**
```
Admin Login → Django Admin Dashboard
     ↓              ↓         ↓         ↓
  Users        Products    Orders    Stores
    ↓              ↓         ↓         ↓
Add/Edit/    Add/Edit/   Process    Manage
 Delete      Delete/     Refunds    Locations
           Categorize
```

### 🎨 User Journey Highlights

1. **Discovery Phase**: Users land on a visually appealing homepage with featured products and categories
2. **Exploration Phase**: Intuitive navigation allows browsing by sport, category, or using advanced search filters
3. **Decision Phase**: Detailed product pages with images, descriptions, and specifications help inform purchases
4. **Shopping Phase**: Seamless cart management with real-time updates and quantity adjustments
5. **Checkout Phase**: Streamlined checkout process with address management and order review
6. **Post-Purchase Phase**: Order tracking and history management for returning customers 

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

https://pbp.cs.ui.ac.id/muhammad.vegard/becathlon

## Test Coverage

### Overall Summary
**Total Coverage: 82%** (1,857 out of 2,251 statements covered)

Our test suite focuses on core functionality, with comprehensive coverage of business logic, models, and critical user flows. We've written 840+ lines of test code across all modules.

### Coverage by Module

| Module Category | Coverage | Status | What We Test |
|-----------------|----------|--------|--------------|
| **Core User Features** | 85% | ✅ Excellent | Authentication (98%), Cart (78%), User Profiles - comprehensive coverage of login, registration, shopping cart, and user data management |
| **Product & Catalog** | 74% | ✅ Good | Product browsing, filtering, search, category navigation, and product detail views |
| **Store & Discovery** | 69% | ✅ Good | Homepage, store locator, recommendations - covering navigation, content display, and personalization features |
| **Order Management** | 67% | ✅ Good | Order processing, checkout flows, and transaction handling - models and core business logic well-tested |

### Test Highlights
- ✅ **Models & Database Layer**: 95%+ coverage across all core models (Product, Cart, Order, Profile)
- ✅ **Authentication System**: Near-complete coverage of user registration, login, and permissions
- ✅ **Cart Functionality**: Comprehensive testing of add/remove/update operations
- ✅ **URL Routing**: 100% coverage ensuring all endpoints are properly configured
- ✅ **Forms & Validation**: Well-tested in authentication and catalog modules
- ✅ **Business Logic**: Critical user flows and transactions thoroughly tested
- ✅ **Integration Tests**: End-to-end coverage of key user journeys

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test apps.cart

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html  # Creates detailed HTML report in htmlcov/
```

---

### 📊 Overall Test Coverage: **82%**

With **1,857 out of 2,251 statements** thoroughly tested, our codebase demonstrates strong quality assurance practices. All critical user-facing features and business logic are well-covered, ensuring a reliable and maintainable application.
