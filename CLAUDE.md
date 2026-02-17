# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Flask-based personal blog system located in the `flask_blog/` subdirectory. Features article management, categories, tags, comments, and an admin dashboard with a Doraemon theme (blue #0093D6 and yellow #FFD700).

**Important:** All work should be done within the `flask_blog/` subdirectory.

## Common Commands

### Development

```bash
# Change to project directory first
cd flask_blog

# Initialize database (creates blog.db with default admin and categories)
python init_db.py

# Run development server (auto-reloads on code changes)
python app.py

# Access URLs:
# - Frontend: http://localhost:5000
# - Admin: http://localhost:5000/admin (admin/admin123)
```

### Environment Setup

**Option 1: pip + venv**

```bash
cd flask_blog
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Option 2: Conda**

```bash
cd flask_blog
conda env create -f environment.yml
conda activate flask_blog

# Update environment after dependency changes
conda env update -f environment.yml
```

### Production Deployment

```bash
cd flask_blog
conda install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Architecture

### Project Location

All application code is in `flask_blog/`:
- `app.py` - All routes, view functions, app factory
- `models.py` - SQLAlchemy models (Post, Category, Tag, Comment, Admin)
- `config.py` - Configuration classes (DevelopmentConfig, ProductionConfig, TestingConfig)
- `init_db.py` - Database initialization with interactive prompts
- `templates/` - Jinja2 templates
- `static/` - CSS, JS files

### Application Factory Pattern

The app uses a factory pattern in `app.py`:

```python
app = create_app('development')  # Config name: development/production/testing
```

Initialization steps in `create_app()`:
1. Load config from `config.py` via config dictionary
2. Initialize SQLAlchemy (`db.init_app(app)`)
3. Register context processors (injects sidebar data globally)
4. Register error handlers (404/500 templates)

### Routing Structure

All routes are defined in `app.py` (no Blueprints):

- **Public routes**: `/`, `/post/<id>`, `/category/<id>`, `/tag/<id>`, `/search`
- **Comment handling**: `POST /comment/<post_id>`
- **Admin routes**: `/admin/*` (protected by `@login_required` decorator)
- **Auth**: `/admin/login`, `/admin/logout`

### Authentication

Session-based auth with custom `login_required` decorator:
- Checks `session['admin_id']` for admin access
- Admin routes redirect to `/admin/login` if not authenticated
- Passwords hashed with Werkzeug `generate_password_hash`
- Default credentials: admin/admin123 (change in production)

### Data Model Relationships

```
Post (many-to-one) -> Category
Post (many-to-many) <-> Tag (via post_tags table)
Post (one-to-many) -> Comment (cascade delete)
```

Key model notes:
- `Post.is_published`: Boolean for draft/published state
- `Post.generate_summary()`: Auto-extracts summary from content (strips HTML, first 200 chars)
- `Admin.check_password()`: Uses Werkzeug password hashing
- Cascade delete: Deleting a Post deletes all associated Comments

### Template System

Jinja2 templates in `templates/`:
- `base.html`: Frontend base with Doraemon-themed sidebar
- `admin/base.html`: Admin dashboard base template
- `errors/`: 404.html and 500.html error pages

Context processors inject sidebar data automatically into all templates:
- `categories`, `tags`, `recent_posts`, `popular_posts`, `now`

### Database

SQLite (`flask_blog/blog.db`) managed via SQLAlchemy:

- Initialize: `cd flask_blog && python init_db.py` (idempotent, prompts to recreate if exists)
- Default data: 4 categories (技术, 生活, 随笔, 教程) + admin account
- Backup: Simply copy `flask_blog/blog.db` file
- Schema changes: Edit `models.py`, delete `blog.db`, run `init_db.py`

## Configuration

Edit `flask_blog/config.py` for settings:

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
| `flask_blog/app.py` | All routes, view functions, app factory |
| `flask_blog/models.py` | SQLAlchemy models: Post, Category, Tag, Comment, Admin |
| `flask_blog/config.py` | Configuration classes and environment settings |
| `flask_blog/init_db.py` | Database initialization with interactive prompts |
| `flask_blog/static/css/style.css` | Doraemon-themed styles (blue/yellow palette) |
| `flask_blog/templates/base.html` | Frontend base template with sidebar |

## Theme Customization

Current Doraemon theme uses CSS variables in `flask_blog/static/css/style.css`:

```css
:root {
    --dora-blue: #0093D6;
    --dora-yellow: #FFD700;
    --dora-red: #E60033;
}
```

To change theme: Modify these CSS variables and update emoji decorations in `flask_blog/templates/base.html`.

## Common Tasks

### Adding a New Route

Add to `flask_blog/app.py` following existing patterns. Use `@login_required` for admin-only routes.

### Modifying Database Schema

```bash
cd flask_blog
# 1. Edit models.py
# 2. Delete blog.db
# 3. Run python init_db.py to recreate
```

### Adding Sidebar Widget

Edit `flask_blog/templates/base.html` in the `{% block sidebar %}` section.

### Changing Admin Credentials

```python
# Python shell
cd flask_blog
python
from app import app
from models import db, Admin
with app.app_context():
    admin = Admin('newuser', 'newpassword')
    db.session.add(admin)
    db.session.commit()
```

### Running from Root Directory

When working from repository root, always prefix commands with the subdirectory:

```bash
python flask_blog/app.py
python flask_blog/init_db.py
```

Or `cd flask_blog` first for convenience.
