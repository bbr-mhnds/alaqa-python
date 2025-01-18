# Django PostgreSQL Project

A modern Django project with PostgreSQL database integration.

## Prerequisites

- Python 3.8+
- PostgreSQL 14+
- virtualenv

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your environment variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=django_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

5. Create the database:
```bash
createdb django_db
```

6. Run migrations:
```bash
python manage.py migrate
```

7. Create a superuser:
```bash
python manage.py createsuperuser
```

8. Run the development server:
```bash
python manage.py runserver
```

Visit http://localhost:8000/admin to access the Django admin interface.

## Project Structure

```
├── config/             # Project configuration
├── static/            # Static files
├── media/             # User-uploaded files
├── staticfiles/       # Collected static files
├── requirements.txt   # Project dependencies
└── manage.py         # Django management script
```

## Development

- Run tests: `python manage.py test`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 