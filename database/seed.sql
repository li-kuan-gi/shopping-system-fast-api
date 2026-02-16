-- Seed Categories
INSERT INTO public.categories (name) VALUES
('Electronics'),
('Books'),
('Clothing'),
('Home & Kitchen'),
('Sports & Outdoors');

-- Seed Products
-- Electronics
INSERT INTO public.products (name, description, price, stock, category_id) VALUES
('Smartphone X', 'Latest model smartphone with high-res camera', 699.99, 50, (SELECT id FROM public.categories WHERE name = 'Electronics')),
('Laptop Pro', 'High performance laptop for professionals', 1299.00, 30, (SELECT id FROM public.categories WHERE name = 'Electronics')),
('Wireless Earbuds', 'Noise cancelling wireless earbuds', 149.50, 100, (SELECT id FROM public.categories WHERE name = 'Electronics'));

-- Books
INSERT INTO public.products (name, description, price, stock, category_id) VALUES
('The Great Algorithm', 'A comprehensive guide to modern algorithms', 45.00, 200, (SELECT id FROM public.categories WHERE name = 'Books')),
('Sci-Fi Adventure', 'A journey to the stars', 12.99, 150, (SELECT id FROM public.categories WHERE name = 'Books'));

-- Clothing
INSERT INTO public.products (name, description, price, stock, category_id) VALUES
('Cotton T-Shirt', 'Premium cotton t-shirt, unisex', 19.99, 500, (SELECT id FROM public.categories WHERE name = 'Clothing')),
('Denim Jeans', 'Classic blue denim jeans', 49.99, 200, (SELECT id FROM public.categories WHERE name = 'Clothing')),
('Running Shoes', 'Lightweight running shoes for daily use', 89.99, 75, (SELECT id FROM public.categories WHERE name = 'Clothing'));

-- Home & Kitchen
INSERT INTO public.products (name, description, price, stock, category_id) VALUES
('Coffee Maker', 'Programmable coffee maker with timer', 79.99, 60, (SELECT id FROM public.categories WHERE name = 'Home & Kitchen')),
('Blender', 'High speed blender for smoothies', 55.00, 40, (SELECT id FROM public.categories WHERE name = 'Home & Kitchen'));

-- Sports
INSERT INTO public.products (name, description, price, stock, category_id) VALUES
('Yoga Mat', 'Non-slip yoga mat', 25.00, 120, (SELECT id FROM public.categories WHERE name = 'Sports & Outdoors')),
('Dumbbell Set', 'Adjustable dumbbell set', 150.00, 20, (SELECT id FROM public.categories WHERE name = 'Sports & Outdoors'));
