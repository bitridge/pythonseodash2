# SEO Work Log Dashboard

A Django-based dashboard for managing and tracking SEO work, generating reports, and maintaining customer relationships.

## Features

- User Role Management
  - Administrators: Full system access and management
  - Providers: SEO service delivery and project management
  - Customers: Project tracking and report access

- Customer Management
  - Customer profiles and account management
  - Project association and history tracking
  - Custom branding and preferences

- Project Management
  - Project creation and assignment
  - Progress tracking and milestones
  - Customer-specific project views

- SEO Work Logging
  - On-page and off-page SEO tracking
  - File attachments and media management
  - Service history documentation

- Reporting System
  - Automated report generation
  - Custom report sections
  - PDF export functionality
  - Customer-branded reports

- Communication System
  - Integrated messaging
  - Automated notifications
  - Customer support channels

## User Guides

### For Administrators
- User management and role assignment
- System configuration and settings
- Customer account management
- Provider assignment and oversight

### For Providers
- Project management and tracking
- SEO work logging
- Report generation
- Customer communication

### For Customers
- Project overview and tracking
- Report access and downloads
- Service history review
- Account management

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

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Apply database migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

```
seo-work-log/
├── core/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── admin.py          # Admin interface
│   ├── urls.py           # URL routing
│   └── templates/        # HTML templates
├── static/                # Static files
├── media/                 # User uploads
├── docs/                  # Documentation
└── requirements/          # Requirements files
```

## API Documentation

The system provides RESTful APIs for:
- Customer management
- Project operations
- SEO log entries
- Report generation
- User management

For detailed API documentation, see `docs/api.md`.

## Security

- Role-based access control
- Secure customer data handling
- Encrypted communications
- Regular security updates

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Support

For support inquiries:
- Email: support@example.com
- Documentation: docs/
- Issue Tracker: GitHub Issues

## License

This project is licensed under the MIT License - see the LICENSE file for details. 