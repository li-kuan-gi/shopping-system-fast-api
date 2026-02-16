-- RLS, Policies, and Grants

-- Categories
alter table public.categories enable row level security;
create policy "Enable read access for all users" on public.categories for select using (true);
revoke select on public.categories from anon;

-- Products
alter table public.products enable row level security;
create policy "Enable read access for all users" on public.products for select using (true);
revoke select on public.products from anon;

-- Products View
grant select on public.products_view to anon;

-- Carts
alter table public.carts enable row level security;
create policy "Users can view own cart" on public.carts for select to authenticated using (auth.uid()::text = user_id);

-- Cart Items
alter table public.cart_items enable row level security;
create policy "Users can view own cart items" on public.cart_items for select to authenticated using (
  exists (
    select 1 from public.carts
    where id = cart_items.cart_id and user_id = auth.uid()::text
  )
);
