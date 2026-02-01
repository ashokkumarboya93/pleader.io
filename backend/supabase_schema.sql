-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Users Table
create table public.users (
  id uuid primary key default uuid_generate_v4(),
  email text unique not null,
  password text, -- Hashed password
  name text,
  avatar_url text,
  auth_provider text default 'email',
  preferences jsonb default '{"theme": "light", "language": "en", "notifications": true}',
  created_at timestamp with time zone default timezone('utc'::text, now()),
  last_active timestamp with time zone default timezone('utc'::text, now())
);

-- 2. Chats Table
create table public.chats (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.users(id) on delete cascade,
  title text,
  messages jsonb default '[]', -- Storing messages array as JSONB for flexibility
  created_at timestamp with time zone default timezone('utc'::text, now()),
  updated_at timestamp with time zone default timezone('utc'::text, now())
);

-- 3. Documents Table
create table public.documents (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid references public.users(id) on delete cascade,
  filename text,
  file_type text,
  analysis_result jsonb, -- Stores the AI analysis structure
  uploaded_at timestamp with time zone default timezone('utc'::text, now())
);

-- Enable Row Level Security (RLS)
alter table public.users enable row level security;
alter table public.chats enable row level security;
alter table public.documents enable row level security;

-- Create Policies
create policy "Users can view their own data" on public.users for select using (auth.uid() = id);
create policy "Users can view their own chats" on public.chats for all using (auth.uid() = user_id);
create policy "Users can view their own documents" on public.documents for all using (auth.uid() = user_id);
