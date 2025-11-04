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



### What is Becathlon?



_Becathlon_ is a Django-powered e-commerce platform that brings the world of multisport equipment shopping online. Inspired by Decathlon's user-friendly design and comprehensive product offerings, Becathlon recreates the browsing experience of a modern sports retailer while serving as a learning platform for full-stack web development.



### The Story



In the digital age, sports enthusiasts need more than just a product catalog—they need an intuitive, engaging shopping experience that helps them find the right equipment for their passion. Whether you're a weekend cyclist, a yoga practitioner, or a serious mountaineer, Becathlon aims to make finding and purchasing sports equipment seamless and enjoyable.



Our platform bridges the gap between traditional brick-and-mortar sports stores and modern e-commerce, offering:

- **Comprehensive Product Catalog**: Browse thousands of sports products across multiple categories

- **Personalized Experience**: Get recommendations based on your interests and browsing history

- **Seamless Shopping Flow**: From discovery to checkout, every step is optimized for ease of use

- **Store Integration**: Find physical store locations when you need hands-on product experience



### Key Benefits



**For Customers:**

- **Easy Discovery**: Intuitive navigation and powerful search to find exactly what you need

- **Visual Excellence**: Clean, modern interface that makes browsing a pleasure

- **Smart Shopping**: Compare products, read details, and make informed decisions

- **Order Tracking**: Keep tabs on your purchases from checkout to delivery

- **Personalized Experience**: Tailored recommendations and saved preferences



**For Administrators:**

- **Complete Control**: Manage products, categories, and inventory through Django admin

- **User Management**: Handle customer accounts and permissions efficiently

- **Data Insights**: Track orders, popular products, and user behavior

- **Store Management**: Maintain store locations and information



**For Developers:**

- **Modern Stack**: Built with Django, demonstrating best practices in web development

- **Well Tested**: 90% code coverage ensuring reliability and maintainability

- **Learning Resource**: Clean architecture suitable for studying Django patterns

- **Scalable Design**: Modular app structure ready for expansion



### Website Flow



**For Guest Visitors:** You land on the homepage, browse sport categories, check out product listings with search/filter options, dive into product details, toss items in your cart, or find nearby stores. To actually buy stuff, you'll need to register or log in first.



**For Registered Customers:** After logging in, you hit the homepage with featured products, browse or search the catalog, check product details with personalized recommendations, add to cart, manage your cart quantities, proceed to checkout with shipping details, review and place your order, get confirmation, track the order status, and view your order history. You can also edit your profile info anytime.



**For Administrators:** Log into the Django admin dashboard to manage users (add/edit/delete), handle products (add/edit/delete/categorize), process orders and refunds, and manage store locations.



### User Journey Highlights



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

**Total Coverage: 90%**



Check coverage_output.txt for detailed report.







### Running Tests



```bash

# Run all tests

coverage run --source='apps' manage.py test; coverage report



# Run tests for a specific app

coverage run --source='apps/<app_name>' manage.py test apps.<app_name>; coverage



# Generate coverage report (will be written to coverage_output.txt)

coverage report -m | Out-File -FilePath coverage_output.txt -Encoding utf8; Get-Content coverage_output.txt

```

