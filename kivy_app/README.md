# QuickNote Kivy Mobile App

This is a separate Python/Kivy mobile client for QuickNote. It connects to the same Supabase project used by the hosted web app.

## Features

- Login with email or username.
- Register with username, email, and password.
- View notes in a mobile list.
- Create, edit, delete, pin, and prioritize notes.
- Assign categories.
- Search notes by title, content, or category.

## Local Desktop Run

```bash
cd kivy_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## APK Build

Buildozer works best on Linux or WSL Ubuntu, not native Windows.

```bash
cd kivy_app
pip install buildozer
buildozer android debug
```

The APK will be created under:

```text
kivy_app/bin/
```

## Configuration

Public Supabase frontend values are in `config.py`. Username sign-in uses the deployed Vercel API route:

```text
https://quicknote-web-two.vercel.app/api/auth/login
```

The service role key is never stored in this app.
