--*** Database normalization- Begin ***--
-- Populate cities values from raw records
INSERT INTO City
SELECT DISTINCT city, State, County
FROM farmers_market_raw;

-- Cleanup if any city missing records
-- we found total 32 invalid records in database
DELETE
from City
WHERE city IS NULL
   OR city = '-';
DELETE
from farmers_market_raw
WHERE city IS NULL
   OR city = '-';
--32 rows affected in 8 ms

commit;

-- Populate primary key column using running sequence number
UPDATE city
SET city_id = (
    SELECT row_number() over (partition by 1)
    FROM City cn
    WHERE cn.city = city.city
);

alter table farmers_market
    add city_id integer;


ALTER TABLE city drop column state;

UPDATE farmers_market
SET city_id = (
    SELECT city_id
    FROM city
    WHERE city.city = farmers_market.city
);
--8,636 rows affected in 1 s 418 ms

-- populate city id for lineage
UPDATE City
SET state_id = (
    SELECT state_id
    FROM State
    WHERE city.state_id = State.state_id
);

--List all tables
SELECT name
FROM sqlite_schema
WHERE type = 'table'
ORDER BY name;


-- check all stats
-- Show top states
select st.state, count(*) as cnt
from farmers_market fm
         join City ct on fm.city_id = ct.city_id
         join State st on ct.state_id = st.state_id
group by st.state
order by cnt desc
limit 10;


-- Show top cities
select city, count(*) as cnt
from farmers_market fm join City C on fm.city_id = C.city_id
group by city
order by cnt desc
limit 10;


