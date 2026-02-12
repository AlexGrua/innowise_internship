-- BoM explosion (final view)
-- Source: public.bom_raw (loaded from task_2_data_ex.xlsx)
-- Output columns follow the task requirements


create or replace view public.bom_explosion_final_all as
with recursive

-- 1) Clean + приведение типов (qty -- numeric, production_type -- int)
bom_clean as (
  select
    plant_id,
    year,
    month,

    produced_material,
    nullif(regexp_replace(coalesce(produced_material_production_type, ''), '\.0$', ''), '')::int
      as produced_material_production_type_int,
    produced_material_release_type,
    nullif(replace(coalesce(produced_material_quantity, ''), ',', ''), '')::numeric
      as produced_material_quantity_num,

    component_material,
    nullif(regexp_replace(coalesce(component_material_production_type, ''), '\.0$', ''), '')::int
      as component_material_production_type_int,
    component_material_release_type,
    nullif(replace(coalesce(component_material_quantity, ''), ',', ''), '')::numeric
      as component_material_quantity_num

  from public.bom_raw
),

-- 2) edges_year: годовые связи + годовой расход компонента
edges_year as (
  select
    plant_id,
    year,

    produced_material,
    produced_material_release_type,
    produced_material_production_type_int as produced_material_production_type,

    component_material,
    component_material_release_type,
    component_material_production_type_int as component_material_production_type,

    sum(component_material_quantity_num) as component_consumption_quantity
  from bom_clean
  group by
    plant_id, year,
    produced_material, produced_material_release_type, produced_material_production_type_int,
    component_material, component_material_release_type, component_material_production_type_int
),

-- 3) mat_year: годовой выпуск produced_material (max по месяцу, sum по месяцам)
mat_year as (
  with per_month as (
    select
      plant_id,
      year,
      month,
      produced_material,
      produced_material_release_type,
      produced_material_production_type_int as produced_material_production_type,
      max(produced_material_quantity_num) as prod_qty_month
    from bom_clean
    group by
      plant_id, year, month,
      produced_material, produced_material_release_type, produced_material_production_type_int
  )
  select
    plant_id,
    year,
    produced_material,
    produced_material_release_type,
    produced_material_production_type,
    sum(prod_qty_month) as prod_material_production_quantity
  from per_month
  group by
    plant_id, year,
    produced_material, produced_material_release_type, produced_material_production_type
),

-- 4) expandable: что можно раскрывать дальше
expandable as (
  select plant_id, year, produced_material
  from mat_year
  where produced_material_release_type in ('FIN','PROD')
),

-- 5) список FIN по каждому plant+year
fin as (
  select plant_id, year, produced_material as fin_material_id
  from mat_year
  where produced_material_release_type = 'FIN'
),

-- 6) Делаем обход по FIn и вних (FIN -- компоненты -- компоненты компонентов)
walk as (
  select
    f.plant_id,
    f.year,
    f.fin_material_id,
    e.produced_material as prod_material_id,
    e.component_material as component_id
  from fin f
  join edges_year e
    on e.plant_id = f.plant_id
   and e.year = f.year
   and e.produced_material = f.fin_material_id

  union all

  -- раскрываем только если component входит в expandable
  select
    w.plant_id,
    w.year,
    w.fin_material_id,
    e.produced_material as prod_material_id,
    e.component_material as component_id
  from walk w
  join edges_year e
    on e.plant_id = w.plant_id
   and e.year = w.year
   and e.produced_material = w.component_id
  join expandable x
    on x.plant_id = w.plant_id
   and x.year = w.year
   and x.produced_material = w.component_id
),

-- 7) ids: убираем дубли если есть

ids as (
  select distinct
    plant_id,
    year,
    fin_material_id,
    prod_material_id,
    component_id
  from walk
)

-- 8) финальный формат ТЗ
select
  ids.plant_id as plant,

  ids.fin_material_id,
  fin_info.produced_material_release_type as fin_material_release_type,
  fin_info.produced_material_production_type as fin_material_production_type,
  fin_info.prod_material_production_quantity as fin_production_quantity,

  ids.prod_material_id,
  pm_info.produced_material_release_type as prod_material_release_type,
  pm_info.produced_material_production_type as prod_material_production_type,
  pm_info.prod_material_production_quantity as prod_material_production_quantity,

  ids.component_id,
  e.component_material_release_type as component_material_release_type,
  e.component_material_production_type as component_material_production_type,
  e.component_consumption_quantity as component_consumption_quantity,

  ids.year
from ids
join mat_year fin_info
  on fin_info.plant_id = ids.plant_id
 and fin_info.year = ids.year
 and fin_info.produced_material = ids.fin_material_id
join mat_year pm_info
  on pm_info.plant_id = ids.plant_id
 and pm_info.year = ids.year
 and pm_info.produced_material = ids.prod_material_id
join edges_year e
  on e.plant_id = ids.plant_id
 and e.year = ids.year
 and e.produced_material = ids.prod_material_id
 and e.component_material = ids.component_id
;
