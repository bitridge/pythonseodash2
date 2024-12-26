# SEO Work Log Dashboard

A Django-based dashboard for managing and tracking SEO work, generating reports, and maintaining client relationships.

## Features

- User role management (Admin, Provider, Client)
- Project and client management
- SEO work logging system
- Report generation
- Media file management
- Dashboard analytics

## Prerequisites

- Python 3.9 or later
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd seo-work-log
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On macOS/Linux
# or
env\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at http://127.0.0.1:8000/

## Project Structure

- `core/` - Main application directory
  - `models.py` - Database models
  - `views.py` - View logic
  - `admin.py` - Admin interface configuration
  - `urls.py` - URL routing

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 