-- Chips League (ליגת הצ'יפים) database setup.
-- Run once in Supabase: SQL Editor -> New query -> paste everything -> Run.
-- Safe to run again.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  nick text not null unique,
  is_admin boolean not null default false,
  created_at timestamptz not null default now()
);
create table if not exists public.matches (
  id text primary key,
  doc jsonb not null,
  updated_at timestamptz not null default now()
);
create table if not exists public.bets (
  id text primary key,
  user_id uuid not null references public.profiles(id) on delete cascade,
  stake integer not null check (stake > 0),
  mode text not null default 'single',
  legs jsonb not null,
  created_at timestamptz not null default now()
);
create table if not exists public.ledger (
  user_id uuid primary key references public.profiles(id) on delete cascade,
  adjust integer not null default 0,
  voided jsonb not null default '[]'::jsonb,
  log jsonb not null default '[]'::jsonb
);
create table if not exists public.config (
  id text primary key,
  doc jsonb not null
);
insert into public.config (id, doc) values ('settings', '{"startChips":1000,"maxStake":0}')
on conflict (id) do nothing;

create or replace function public.is_admin() returns boolean
language sql stable security definer set search_path = public as $$
  select coalesce((select is_admin from public.profiles where id = auth.uid()), false)
$$;

-- The first player to register becomes the admin. Nobody can promote themselves.
create or replace function public.profiles_guard() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  if tg_op = 'INSERT' then
    new.is_admin := not exists (select 1 from public.profiles);
  elsif new.is_admin is distinct from old.is_admin and not public.is_admin() then
    raise exception 'not allowed';
  end if;
  return new;
end $$;
drop trigger if exists profiles_guard on public.profiles;
create trigger profiles_guard before insert or update on public.profiles
for each row execute function public.profiles_guard();

alter table public.profiles enable row level security;
alter table public.matches  enable row level security;
alter table public.bets     enable row level security;
alter table public.ledger   enable row level security;
alter table public.config   enable row level security;

drop policy if exists "read profiles" on public.profiles;
drop policy if exists "create own profile" on public.profiles;
drop policy if exists "admin updates profiles" on public.profiles;
drop policy if exists "admin deletes profiles" on public.profiles;
create policy "read profiles" on public.profiles for select to authenticated using (true);
create policy "create own profile" on public.profiles for insert to authenticated with check (id = auth.uid());
create policy "admin updates profiles" on public.profiles for update to authenticated using (public.is_admin()) with check (public.is_admin());
create policy "admin deletes profiles" on public.profiles for delete to authenticated using (public.is_admin());

drop policy if exists "read matches" on public.matches;
drop policy if exists "admin writes matches" on public.matches;
create policy "read matches" on public.matches for select to authenticated using (true);
create policy "admin writes matches" on public.matches for all to authenticated using (public.is_admin()) with check (public.is_admin());

drop policy if exists "read ledger" on public.ledger;
drop policy if exists "admin writes ledger" on public.ledger;
create policy "read ledger" on public.ledger for select to authenticated using (true);
create policy "admin writes ledger" on public.ledger for all to authenticated using (public.is_admin()) with check (public.is_admin());

drop policy if exists "read config" on public.config;
drop policy if exists "admin writes config" on public.config;
create policy "read config" on public.config for select to authenticated using (true);
create policy "admin writes config" on public.config for all to authenticated using (public.is_admin()) with check (public.is_admin());

-- Bets are readable by every player; they are created only through place_bet().
drop policy if exists "read bets" on public.bets;
drop policy if exists "admin deletes bets" on public.bets;
create policy "read bets" on public.bets for select to authenticated using (true);
create policy "admin deletes bets" on public.bets for delete to authenticated using (public.is_admin());

-- Places a bet for the signed-in player. The server clock decides whether a match has started.
create or replace function public.place_bet(p_id text, p_stake integer, p_mode text, p_legs jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare
  leg jsonb;
  m jsonb;
  max_stake integer;
begin
  if auth.uid() is null or not exists (select 1 from public.profiles where id = auth.uid()) then
    raise exception 'not a player';
  end if;
  if p_stake is null or p_stake < 1 then raise exception 'bad stake'; end if;
  if jsonb_typeof(p_legs) <> 'array' or jsonb_array_length(p_legs) < 1 or jsonb_array_length(p_legs) > 20 then
    raise exception 'bad legs';
  end if;
  select coalesce((doc->>'maxStake')::integer, 0) into max_stake from public.config where id = 'settings';
  if coalesce(max_stake, 0) > 0 and p_stake > max_stake then raise exception 'stake over max'; end if;
  for leg in select * from jsonb_array_elements(p_legs) loop
    select doc into m from public.matches where id = leg->>'m';
    if m is null then raise exception 'match not found'; end if;
    if m->>'status' <> 'open' or coalesce((m->>'locked')::boolean, false) or m->>'source' = 'estimate'
       or now() >= (m->>'kickoff')::timestamptz then
      raise exception 'match closed';
    end if;
    if (leg->>'o')::numeric < 1.01 or (leg->>'o')::numeric > 1000 then raise exception 'bad odds'; end if;
  end loop;
  insert into public.bets (id, user_id, stake, mode, legs)
  values (p_id, auth.uid(), p_stake, coalesce(p_mode, 'single'), p_legs);
end $$;
revoke all on function public.place_bet(text, integer, text, jsonb) from public, anon;
grant execute on function public.place_bet(text, integer, text, jsonb) to authenticated;

-- Live updates for every open page.
do $$
declare t text;
begin
  foreach t in array array['matches','bets','profiles','ledger','config'] loop
    begin
      execute format('alter publication supabase_realtime add table public.%I', t);
    exception when others then null;
    end;
  end loop;
end $$;

-- Lets the sign-up form tell whether a nickname is already taken.
create or replace function public.nick_taken(p_nick text) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where lower(nick) = lower(trim(p_nick)))
$$;
grant execute on function public.nick_taken(text) to anon, authenticated;
