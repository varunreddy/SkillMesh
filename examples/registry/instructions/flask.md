# Flask Web Framework Expert

Use this expert when tasks require building web applications or APIs with Flask, including application factory patterns, blueprints, extension integration, template rendering, error handling, and configuration management.

## When to use this expert
- The task involves building or extending a Python web application using Flask's ecosystem of extensions.
- A synchronous, WSGI-based web framework is appropriate for the use case (server-rendered pages, admin panels, simple APIs).
- The application requires blueprint-based modular structure, Flask-SQLAlchemy, Flask-Login, or similar extensions.
- Template rendering with Jinja2 and form handling with Flask-WTF is needed.

## Execution behavior

1. Create the application using the factory pattern: define a `create_app(config_name=None)` function that instantiates `Flask(__name__)`, loads configuration, initializes extensions, and registers blueprints. Never create the `app` instance at module level.
2. Organize features into `Blueprint` instances with clear URL prefixes (`/api/users`, `/auth`, `/admin`). Each blueprint lives in its own package with `routes.py`, `models.py`, and `forms.py` as needed.
3. Load configuration from a class hierarchy (`Config`, `DevelopmentConfig`, `ProductionConfig`) and override with environment variables. Use `app.config.from_object()` for defaults and `app.config.from_envvar()` for secrets.
4. Initialize extensions (SQLAlchemy, Migrate, Login, Mail) outside the factory as unbound instances, then call `ext.init_app(app)` inside the factory. This avoids circular imports and supports multiple app instances in testing.
5. Register error handlers (`@app.errorhandler(404)`, `@app.errorhandler(500)`) that return both HTML and JSON responses depending on the `Accept` header or a URL prefix convention (`/api/` returns JSON).
6. Use Flask-Login's `@login_required` decorator and `current_user` proxy for session-based authentication. For API endpoints, prefer token-based auth via a custom decorator or Flask-JWT-Extended.
7. Write templates using Jinja2 template inheritance: a `base.html` layout with `{% block content %}` that child templates extend. Keep logic in views, not templates.
8. Test using `app.test_client()` from a fixture that calls the factory with a test configuration and an in-memory SQLite database.

## Decision tree
- If the application has more than three routes or two distinct feature areas -> organize into blueprints with a dedicated package per blueprint.
- If authentication is needed for server-rendered pages -> use Flask-Login with session cookies; for API-only auth -> use Flask-JWT-Extended or a custom token decorator.
- If the project is purely an API with no templates -> consider whether FastAPI would be a better fit; use Flask only if the team has existing Flask infrastructure or needs specific Flask extensions.
- If database models are involved -> use Flask-SQLAlchemy with Flask-Migrate (Alembic) for schema migrations; never run `db.create_all()` in production.
- If forms are submitted via HTML -> use Flask-WTF for CSRF protection and validation; never process raw `request.form` without validation.
- If the app needs to serve both HTML pages and JSON API endpoints -> separate them into distinct blueprints with different error handling behavior.

## Anti-patterns
- NEVER create the `app` instance at module level (`app = Flask(__name__)` in a shared module). This causes circular imports and makes testing with different configurations impossible.
- NEVER mutate global state (module-level dicts or lists) to share data between requests. Use `g`, `session`, or a database.
- NEVER write raw SQL strings directly inside route handlers. Use SQLAlchemy models or, at minimum, parameterized queries to prevent SQL injection.
- NEVER skip CSRF protection on form endpoints. Flask-WTF's `CSRFProtect` should be initialized app-wide.
- NEVER hardcode secrets (`SECRET_KEY`, database URIs) in source code. Load them from environment variables or a secrets manager.
- NEVER use `app.run(debug=True)` in production. Use a WSGI server like Gunicorn or uWSGI behind a reverse proxy.

## Common mistakes
- Importing the `app` object in models or blueprints, creating circular imports. Instead, use `current_app` proxy or pass dependencies through `init_app`.
- Forgetting to set `SECRET_KEY`, causing session and CSRF token failures that only surface at runtime with cryptic errors.
- Calling `db.create_all()` without an application context, resulting in `RuntimeError: Working outside of application context`.
- Defining all routes in a single `app.py` file that grows to thousands of lines instead of refactoring into blueprints early.
- Using `redirect(url_for('function_name'))` with the wrong endpoint name because the blueprint prefix was not included (correct form: `url_for('blueprint.function_name')`).
- Returning bare strings from error handlers instead of proper `(response, status_code)` tuples, causing the client to receive `200 OK` for errors.

## Output contract
- The application must use the factory pattern with `create_app()` as the entry point.
- All routes must be registered via blueprints, not directly on the `app` object.
- Configuration must be externalized via config classes and environment variables, with no secrets in source code.
- Error handlers must return appropriate HTTP status codes and content types (HTML or JSON).
- Database schema changes must use Flask-Migrate (Alembic), not `db.create_all()`.
- Templates must use Jinja2 inheritance with a shared base layout.
- Tests must use the test client from a factory-created app with test-specific configuration.

## Composability hints
- Before this expert -> use the **REST API Design Expert** to plan resource URLs, methods, and error formats if building an API.
- Before this expert -> use the **SQLAlchemy Expert** to design models and relationships before integrating with Flask-SQLAlchemy.
- After this expert -> use the **Auth JWT Expert** for API token authentication or **Auth OAuth Expert** for social login integration.
- Related -> the **FastAPI Expert** when evaluating whether async-first with automatic validation is a better fit for the project.
- Related -> the **Visualization Expert** for generating charts that are embedded in server-rendered templates.
