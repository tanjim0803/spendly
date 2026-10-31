---
# Spec: Registration

## Overview
Implement the user registration functionality, allowing new users to create an account with a name, email, and password. This is a core identity feature that enables personalized expense tracking for users in the Spendly roadmap.

## Depends on
Step 1 (Database Setup)

## Routes
- `GET /register` — Renders the registration form — public
- `POST /register` — Processes registration data and creates a user — public

## Database changes
No database changes (Users table already exists with name, email, password_hash, and created_at).

## Templates
- **Create:** None (register.html already exists)
- **Modify:** `templates/register.html` — Update form to use POST method and include CSRF/validation fields if applicable.

## Files to change
- `app.py` — Implement POST /register route logic.
- `database/db.py` — Add a helper function to create a user and check for existing emails.

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

## Definition of done
- [ ] New user can successfully register with a unique email.
- [ ] Registration fails if the email is already taken.
- [ ] Passwords are stored as hashes in the database, not plain text.
- [ ] User is redirected to the login page upon successful registration.
- [ ] Form validation errors (e.g., empty fields) are displayed to the user.
---
