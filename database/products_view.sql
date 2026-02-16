-- Create view for anon users (Join products and categories)
create view public.products_view as
select
  p.id as product_id,
  p.name,
  p.description,
  p.price,
  p.stock,
  c.name as category_name
from
  public.products p
  left join public.categories c on p.category_id = c.id;


