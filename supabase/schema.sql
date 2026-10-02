create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.categories (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  created_at timestamptz not null default timezone('utc', now()),
  constraint categories_user_name_unique unique (user_id, name)
);

create table if not exists public.notes (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  category_id uuid references public.categories(id) on delete set null,
  title text not null,
  content text not null default '',
  priority text not null default 'Normal' check (priority in ('Low', 'Normal', 'High')),
  is_pinned boolean not null default false,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

alter table public.profiles enable row level security;
alter table public.categories enable row level security;
alter table public.notes enable row level security;

drop policy if exists "profiles_select_own" on public.profiles;
create policy "profiles_select_own" on public.profiles
  for select using (id = auth.uid());

drop policy if exists "profiles_update_own" on public.profiles;
create policy "profiles_update_own" on public.profiles
  for update using (id = auth.uid()) with check (id = auth.uid());

drop policy if exists "categories_select_own" on public.categories;
create policy "categories_select_own" on public.categories
  for select using (user_id = auth.uid());

drop policy if exists "categories_insert_own" on public.categories;
create policy "categories_insert_own" on public.categories
  for insert with check (user_id = auth.uid());

drop policy if exists "categories_update_own" on public.categories;
create policy "categories_update_own" on public.categories
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "categories_delete_own" on public.categories;
create policy "categories_delete_own" on public.categories
  for delete using (user_id = auth.uid());

drop policy if exists "notes_select_own" on public.notes;
create policy "notes_select_own" on public.notes
  for select using (user_id = auth.uid());

drop policy if exists "notes_insert_own" on public.notes;
create policy "notes_insert_own" on public.notes
  for insert with check (user_id = auth.uid());

drop policy if exists "notes_update_own" on public.notes;
create policy "notes_update_own" on public.notes
  for update using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "notes_delete_own" on public.notes;
create policy "notes_delete_own" on public.notes
  for delete using (user_id = auth.uid());

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists set_notes_updated_at on public.notes;
create trigger set_notes_updated_at
  before update on public.notes
  for each row execute function public.set_updated_at();

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  desired_username text;
begin
  desired_username := nullif(trim(new.raw_user_meta_data->>'username'), '');
  if desired_username is null then
    desired_username := split_part(new.email, '@', 1);
  end if;

  insert into public.profiles (id, username)
  values (new.id, desired_username);

  insert into public.categories (user_id, name)
  values
    (new.id, 'School'),
    (new.id, 'Personal'),
    (new.id, 'Ideas'),
    (new.id, 'Reminders');

  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();
