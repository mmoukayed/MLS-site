# MLS-site
A Django-based web application for the Machine Learning Society at Rochester Institute of Technology (RIT). This platform allows students to manage profiles, join teams, participate in events, and access an admin dashboard for content management.

# Features
- **User Authentication**: Signup, login via OTP or magic links, profile management.
- **Teams**: Create, join, and manage teams with roles (members, leaders, creators).
- **Events**: View and register for upcoming workshops, hackathons, and networking events.
- **Admin Dashboard**: Manage users, teams, events, and landing page content.
- **Responsive Design**: Modern UI with dark theme and neural network animations.

# Tech Stack
- **Backend**: Django (Python web framework)
- **Database**: SQLite (default; can be configured for PostgreSQL/MySQL)
- **Frontend**: HTML, CSS, JavaScript (with static assets)
- **Email**: SMTP for OTP and magic link authentication

# Prerequisites
- Python 3.8+
- Django 5.0+ (install via pip)
- Git

# Installation
1. **Clone the repository**:
```
git clone https://github.com/mmoukayed/MLS-site.git
cd MLS-site
```

2. **Set up a virtual environment** (recommended):
```
python -m venv venv
source venv/bin/activate 
# On Windows: venv\Scripts\activate
```
Install dependencies:
```
pip install django django-countries python-dotenv
```

3. Configure environment variables:

   Set `SECRET_KEY`, `EMAIL_HOST_PASSWORD`, and other secrets.

4. Run migrations:
5. Create a superuser (for admin access):

# Running the Application
1. **Start the development server**:
```
python manage.py runserver
```
2. Access at http://127.0.0.1:8000/.

   Admin panel: Visit http://127.0.0.1:8000/admin/ with superuser credentials.

# Project Structure
- `MLS_site`: Project settings, URLs, WSGI/ASGI configs.
- `accounts`: User authentication, models (Member, Major), views, emails.
- `website`: Core app with models (Team, Event), views, URLs, templates.
- `templates`: HTML templates (base, dashboards, etc.).
static: CSS, JS, assets.
- `uploaded_media`: User-uploaded files (events, etc.).

# Key URLs
- `/`: Home page
- `/dashboard/`: Student dashboard (authenticated)
- `/teams/`: Teams page
- `/events/`: Events page
- `/profile/`: User profile
- `/admin/`: Django admin
- `/auth/`: Authentication endpoints

# Contributing
1. Fork the repository.
1. Create a feature branch: git checkout -b feature-name.
1. Make changes and run tests (if any).
1. Commit: `git commit -m "Description"`.
1. Push and create a pull request.

# License
This project is proprietary to the RIT Machine Learning Society. Contact the maintainers for usage permissions.

# Support
For issues, contact the development team or open an issue in the repository. Ensure to follow RIT's code of conduct.
