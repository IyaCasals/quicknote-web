# QuickNote

QuickNote is a personal notes organization and management system. The project now contains a Vercel-ready Next.js web app backed by Supabase, plus the earlier Python desktop implementation retained as reference code for the academic OOP version.

## Web App Features

- Supabase username-or-email/password authentication.
- Per-user notes and categories protected by Supabase Row Level Security.
- Dashboard with total notes, pinned notes, total categories, recent notes, and category summaries.
- Create, view, edit, delete, pin, prioritize, search, and filter notes.
- Create, rename, and delete categories. Deleting a category leaves existing notes uncategorized.
- Reports for total notes, pinned notes, and notes per category.

## Local Web Setup

```bash
npm install
copy .env.example .env.local
npm run dev
```

Set these values in `.env.local`:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your-publishable-key
SUPABASE_SERVICE_ROLE_KEY=your-server-only-service-role-key
```

Open `http://localhost:3000`.

## Supabase Setup

1. Create a new Supabase project.
2. Open the SQL editor.
3. Run the contents of `supabase/schema.sql`.
4. Copy the project URL and anon public key into `.env.local` and Vercel environment variables.

The schema creates:

- `profiles`
- `categories`
- `notes`

It also enables RLS, creates user-owned CRUD policies, maintains `notes.updated_at`, and seeds starter categories for new users.

## Vercel Deployment

1. Push this repository to the new GitHub account.
2. Import the GitHub repository into the new Vercel account.
3. Add these production environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
4. Deploy the production build.

## Tests and Checks

```bash
npm run test
npm run typecheck
npm run build
```

The earlier Python service tests can still be run separately:

```bash
python -m pytest
```

## Academic OOP Mapping

The original Python implementation remains in `desktop_app/`, `main.py`, `requirements.txt`, and `tests/`. It demonstrates:

- Encapsulation through model methods such as note validation and pinning.
- Inheritance through base model, manager, and view classes.
- Abstraction through services that keep database access out of views.
- Polymorphism through view-specific `render()` methods.

The web implementation maps those ideas into React modules:

- Validation rules live in `src/lib/validators.ts`.
- Search/filtering behavior lives in `src/lib/filters.ts`.
- Reporting behavior lives in `src/lib/reports.ts`.
- UI screens are componentized in `src/app/page.tsx`.

## Important Git Hygiene

Do not commit local runtime data or secrets. `.gitignore` excludes:

- `.env*` except `.env.example`
- `node_modules/`
- `.next/`
- `.venv/`
- `data/`
- `__pycache__/`
