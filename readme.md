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

# Setting Up Website For Production
1. Set `DEBUG` to `False` in `settings.py`. *(Only if external static server is configured otherwise leave on)*`
1. Set `SITE_URL` to the full site url that the server will be hosted on (eg: https://mlssociety.com).
1. Configure the variables in the `.env` file.
1. Delete existing `db.sqlite3` file (If exists) and run `python manage.py runserver` once to create a new db file.
1. Stop that server and run in sequence: `python manage.py makemigrations` and `python manage.py migrate`.
1. Run `python manage.py runserver` again to start the server and login with your RIT email to create your account.
1. Once created go into the `db.sqlite3` file and go to the `accounts_member` table and find your user and change the `is_superuser` and `is_staff` values to `1`.
1. Next reload the home page and their should be an option to click on "Admin Dashboard", click on it and click on the "Landing Page" tab and click "switch to django admin" which will redirect you to the Django admin portal.
1. First, go to the sites tab and create your site by setting the name to anything and the address to the same thing you put earlier in `SITE_URL` (Your root base url) and press SAVE.
1. Next, go to Social Applications and create a new social application, set these fields with your credentials, the rest leave blank:
   - `name`: Set this to `google`.
   - `Client ID`: Set this to your google client ID.
   - `Secret Key`: Set this to your google client secret.
   - `Sites`: Click on the site we made earlier and press the arrow to add it to the empty box.

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
