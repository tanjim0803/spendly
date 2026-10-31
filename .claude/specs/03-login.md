---
# Spec: Login

## Overview
The Login feature allows registered users to authenticate themselves and access their personal expense tracking dashboard. This is a critical step in the Spendly roadmap to transition from a public landing/registration experience to a personalized user session.

## Depends on
- 01-database-setup
- 02-registration

## Routes
- `GET /login` — Render login form — public
- `POST /login` — Authenticate user and start session — public

## Database changes
No database changes.

## Templates
- **Modify:** `templates/login.html` — Update to include a functional `<form>` with `method="POST"`.

## Files to change
- `app.py` — Implement `POST /login` logic and session management.
- `templates/login.html` — Update form for submission.

## Files to create
No new files.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only
- Passwords hashed with werkzeug
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Use `flask.session` to store the `user_id` upon successful authentication.

## Definition of done
- [ ] Navigating to `/login` renders the login page.
- [ ] Submitting the login form with valid credentials redirects the user to the profile or dashboard (currently a stub).
- [ ] Submitting the login form with an unregistered email displays an error message.
- [ ] Submitting the login form with an incorrect password displays an error message.
- [ ] Leaving fields empty displays a validation error.
---
