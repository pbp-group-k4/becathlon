hihiahhaaha

> **Note:** If you're not comfortable with Git commands, use GitHub Desktop!

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source ./venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Useful Commands

- `python manage.py startapp <YOURAPPNAME>` - Create a new Django app (replace `<YOURAPPNAME>` with your app name)
- `python manage.py makemigrations` - Generate migration files for model changes
- `python manage.py migrate` - Apply migrations to the database
- `python manage.py runserver` - Start the development server


