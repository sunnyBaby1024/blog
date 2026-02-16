# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based personal blog system with a Doraemon theme (blue #0093D6 and yellow #FFD700). Features article management, categories, tags, comments, and an admin dashboard.

## Common Commands

### Development

```bash
# Initialize database (creates blog.db with default admin and categories)
python init_db.py

# Run development server (auto-reloads on code changes)
python app.py

# Access URLs:
# - Frontend: http://localhost:5000
# - Admin: http://localhost:5000/admin (admin/admin123)
```

### Production Deployment

```bash
# Using Gunicorn
conda install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Environment Setup

**Option 1: pip + venv**

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option 2: Conda**

```bash
conda env create -f environment.yml
conda activate flask_blog

# Update environment after dependency changes
conda env update -f environment.yml
```

## Architecture

### Application Factory Pattern

The app uses a factory pattern in `app.py`:

```python
app = create_app('development')  # Config name: development/production/testing
```

Key initialization steps in `create_app()`:
1. Load config from `config.py` via config dictionary
2. Initialize SQLAlchemy (`db.init_app(app)`)
3. Register context processors (sidebar data injection)
4. Register error handlers (404/500 templates)

### Routing Structure

All routes are defined directly in `app.py` (no Blueprints used):

- **Public routes**: `/`, `/post/<id>`, `/category/<id>`, `/tag/<id>`, `/search`
- **Comment handling**: `POST /comment/<post_id>`
- **Admin routes**: `/admin/*` (protected by `@login_required` decorator)
- **Auth**: `/admin/login`, `/admin/logout`

### Authentication

Session-based auth with custom `login_required` decorator:
- Checks `session['admin_id']` for admin access
- Admin routes redirect to `/admin/login` if not authenticated
- Default credentials: admin/admin123 (change in production)

### Data Model Relationships

```
Post (many-to-one) -> Category
Post (many-to-many) <-> Tag (via post_tags table)
Post (one-to-many) -> Comment (cascade delete)
```

Key model notes:
- `Post.is_published`: Boolean for draft/published state
- `Post.generate_summary()`: Auto-extracts summary from content
- `Admin.check_password()`: Uses Werkzeug password hashing

### Template System

Jinja2 templates organized by function:

- `base.html`: Frontend base with Doraemon-themed sidebar
- `admin/base.html`: Admin dashboard base template
- `errors/`: 404.html and 500.html error pages

Context processors inject sidebar data automatically:
- `categories`, `tags`, `recent_posts`, `popular_posts`

### Database

SQLite (`blog.db`) managed via SQLAlchemy:

- Initialize: `python init_db.py` (idempotent, prompts to recreate if exists)
- Default data: 4 categories (技术, 生活, 随笔, 教程) + admin account
- Backup: Simply copy `blog.db` file

## Configuration

Edit `config.py` for settings:

```python
# Security (CRITICAL for production)
SECRET_KEY = 'change-this-in-production'
DEFAULT_ADMIN_PASSWORD = 'admin123'

# Pagination
POSTS_PER_PAGE = 5    # Frontend article listing
ADMIN_PER_PAGE = 10   # Admin dashboard tables

# Database
SQLALCHEMY_DATABASE_URI = 'sqlite:///blog.db'
```

Environment-based configs: `DevelopmentConfig`, `ProductionConfig`, `TestingConfig`

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | All routes, view functions, app factory |
| `models.py` | SQLAlchemy models: Post, Category, Tag, Comment, Admin |
| `config.py` | Configuration classes and environment settings |
| `init_db.py` | Database initialization with prompts |
| `static/css/style.css` | Doraemon-themed styles (blue/yellow palette) |
| `templates/base.html` | Frontend base template with sidebar |

## Theme Customization

Current Doraemon theme uses CSS variables in `style.css`:

```css
:root {
    --dora-blue: #0093D6;
    --dora-yellow: #FFD700;
    --dora-red: #E60033;
}
```

To change theme: Modify these CSS variables and update emoji decorations in `templates/base.html`.

## Common Tasks

### Adding a New Route

Add to `app.py` following existing patterns. Use `@login_required` for admin-only routes.

### Modifying Database Schema

1. Edit `models.py`
2. Delete `blog.db`
3. Run `python init_db.py` to recreate

### Adding Sidebar Widget

Edit `templates/base.html` in the `{% block sidebar %}` section.

### Changing Admin Credentials

```python
# Python shell
from app import app
from models import db, Admin
with app.app_context():
    admin = Admin('newuser', 'newpassword')
    db.session.add(admin)
    db.session.commit()
```
