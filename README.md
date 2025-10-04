# Becathlon

> A Django-powered storefront that mirrors the visual polish and browsing experience of Decathlon—minus the heavy operational tooling.

## Team Members

- Muhammad Adra Prakoso – Backend developer / 2406453530
- !!Insert your name!!

## Application Story & Benefits

_Becathlon_ is an online multisport equipment catalogue that recreates the look, feel, and partial functionality of the Decathlon website. 

## Modules

| App Name | Modules | Purpose |
|----------|---------|---------|
| main | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/main/, static/main/ | Homepage, navigation, footer, about pages |
| authentication | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/authentication/ | User login, registration, logout |
| catalog | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/catalog/, static/catalog/, fixtures/products.json | Product listings, categories, product details |
| search | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/search/, static/search/ | Search functionality with filters |
| cart | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/cart/, static/cart/ | Shopping cart management |
| checkout | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/checkout/, static/checkout/ | Mock checkout process |
| orders | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/orders/, static/orders/ | Order history and mock refunds |
| stores | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/stores/, static/stores/, fixtures/stores.json | Store locator with mock locations |
| recommendations | apps.py, models.py, views.py, urls.py, admin.py, tests.py, migrations/, templates/recommendations/ | recommendation system |
| profiles | apps.py, models.py, views.py, urls.py, forms.py, admin.py, tests.py, migrations/, templates/profiles/, static/profiles/ | User profiles and preferences |


NOTES:
```Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process``` to fix any execution policy issues on PS.
go to /becathlon_app and run ```\venv\Scripts\activate.ps1``` to activate the virtual environment.