
CREATE TABLE farmers_market (
	"index" INTEGER
	,FMID INTEGER CONSTRAINT farmers_market_pk UNIQUE
	,MarketName TEXT
	,Website TEXT
	,Facebook TEXT
	,Twitter TEXT
	,Youtube TEXT
	,OtherMedia TEXT
	,street TEXT
	,Season1Date TEXT
	,Season1Time TEXT
	,Season2Date TEXT
	,Season2Time TEXT
	,Season3Date TEXT
	,Season3Time TEXT
	,Season4Date TEXT
	,Season4Time TEXT
	,LAT REAL
	,LON REAL
	,Location TEXT
	,Credit INTEGER
	,WIC INTEGER
	,WICcash INTEGER
	,SFMNP INTEGER
	,SNAP INTEGER
	,Organic INTEGER
	,Bakedgoods INTEGER
	,Cheese INTEGER
	,Crafts INTEGER
	,Flowers INTEGER
	,Eggs INTEGER
	,Seafood INTEGER
	,Herbs INTEGER
	,Vegetables INTEGER
	,Honey INTEGER
	,Jams INTEGER
	,Maple INTEGER
	,Meat INTEGER
	,Nursery INTEGER
	,Nuts INTEGER
	,Plants INTEGER
	,Poultry INTEGER
	,Prepared INTEGER
	,Soap INTEGER
	,Wine INTEGER
	,Coffee INTEGER
	,Beans INTEGER
	,Fruits INTEGER
	,Grains INTEGER
	,Juices INTEGER
	,Mushrooms INTEGER
	,PetFood INTEGER
	,Tofu INTEGER
	,WildHarvested INTEGER
	,updateTime TIMESTAMP
	,city_id INTEGER DEFAULT '' NOT NULL
	);

CREATE TABLE City (
	city TEXT
	,STATE TEXT
	,County TEXT
	,zip INT
	,city_id INTEGER CONSTRAINT City_pk PRIMARY KEY CONSTRAINT City_farmer_market_city_id_fk REFERENCES farmers_market(city_id) ON UPDATE RESTRICT ON DELETE RESTRICT
	);

CREATE INDEX ix_farmers_market_index ON farmers_market ("index");

CREATE TABLE City AS
SELECT DISTINCT city, State, County, zip
FROM farmers_market;

DELETE from City WHERE city IS NULL OR city = '-';
DELETE from farmers_market WHERE city IS NULL OR city = '-';
--32 rows affected in 8 ms

alter table CITY add  int not null;

UPDATE city
SET city_id = (
		SELECT row_number() over (partition by 1) FROM City cn
		WHERE cn.city = city.city
		);

ALTER TABLE farmers_market ADD COLUMN city_id INTEGER NOT NULL DEFAULT '';

UPDATE farmers_market
SET city_id = (
		SELECT city_id
		FROM city
		WHERE city.city = farmers_market.city
		);


CREATE TABLE State as select distinct State,'USA' as country, row_number() over (partition by 1) as state_id from City

UPDATE City
SET state_id = (
		SELECT state_id
		FROM State
		WHERE city.State = State.State
		);

ALTER TABLE City drop column state;

