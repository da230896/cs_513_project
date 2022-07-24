--*** Database normalization- Begin ***--
-- Populate cities values from raw records
INSERT INTO City
SELECT DISTINCT city, State, County, zip
FROM farmers_market;

-- Cleanup if any city missing records
-- we found total 32 invalid records in database
DELETE from City WHERE city IS NULL OR city = '-';
DELETE from farmers_market WHERE city IS NULL OR city = '-';
--32 rows affected in 8 ms

commit;

-- Populate primary key column using running sequence number
UPDATE city
SET city_id = (
		SELECT row_number() over (partition by 1) FROM City cn
		WHERE cn.city = city.city
		);

UPDATE farmers_market
SET city_id = (
		SELECT city_id
		FROM city
		WHERE city.city = farmers_market.city
		);


CREATE TABLE State as select distinct State,'USA' as country, row_number() over (partition by 1) as state_id from City

-- populate city id for lineage
UPDATE City
SET state_id = (
		SELECT state_id
		FROM State
		WHERE city.State = State.State
		);

--List all tables
SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name;


-- check all stats

select state,count(*) from farmers_market group by state;

select city,count(*) as cnt from farmers_market group by city order by cnt desc limit 10;
