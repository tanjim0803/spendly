---
# Spec: Profile Page Backend

## Overview
The profile page currently uses hardcoded mock data for UI validation. This feature replaces that mock data with real data fetched from the SQLite database based on the currently logged-in user's session. It will calculate total spending, transaction counts, top categories, and retrieve recent transactions and category breakdowns.

## Depends on
- Step 1: Database Initialization (users and expenses tables)
- Step 2: User Registration
- Step 3: User Login (authentication and session management)
- Step 4: Profile Page UI (templates and styles)

## Routes
- `GET /profile` — Fetches authenticated user data and calculates spending statistics — logged-in

## Database changes
No database changes. Using existing `users` and `expenses` tables.

## Templates
- **Create:** None
- **Modify:** `templates/profile.html` (Update any remaining mock-specific logic if necessary, though the route handles the data mapping)

## Files to change
- `app.py`: Update `/profile` route to fetch real data.
- `database/db.py`: Add helper functions to fetch user profile and expense statistics.

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
- Ensure `get_db()` is used for all database interactions
- Handle cases where a user has no expenses gracefully (display zero/empty states)

## Definition of done
- [ ] Logged-in user is redirected to `/login` if no session exists.
- [ ] `/profile` displays the correct name and email of the logged-in user.
- [ ] Total spent is correctly summed from the `expenses` table for the current user.
- [ ] Transaction count reflects the actual number of entries in the `expenses` table.
- [ ] Top category is correctly identified as the one with the highest total spend.
- [ ] Recent transactions list shows the most recent expenses from the database.
- [ ] Category breakdown shows correct totals and percentages per category.
- [ ] App does not crash if a user has zero expenses.
---
