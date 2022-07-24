create table farmers_market
-- Table for USA's farmers markets (FM), it contains farmer demographics, firmographics about their goods,
-- social media, opening seasons, and time when farmer added to database.
(
    "index"       INTEGER,
    FMID          INTEGER -- numeric unique id for each FM,
    MarketName    TEXT -- Name of the FM,
    Website       TEXT -- Social media information,
    Facebook      TEXT,
    Twitter       TEXT,
    Youtube       TEXT,
    OtherMedia    TEXT,
    street        TEXT -- FM Address,
    city          TEXT,
    County        TEXT,
    State         TEXT,
    zip           TEXT,
    Season1Date   TEXT  -- Opening seasons and time of FM. They are in raw format from original datasource. For the cleansed version of seasons check Seasons date & time tables,
    Season1Time   TEXT,
    Season2Date   TEXT,
    Season2Time   TEXT,
    Season3Date   TEXT,
    Season3Time   TEXT,
    Season4Date   TEXT,
    Season4Time   TEXT,
    x             REAL -- FM location in the form of latitude (x) and (y),
    y             REAL,
    Location      TEXT,
    Credit        INTEGER -- accepts credit card or not- 1/0,
    WIC           INTEGER -- accepts card for special program (Women, Infants, and Children)  or not- 1/0,
    WICcash       INTEGER -- accepts cash for WIC program  or not- 1/0,
    SFMNP         INTEGER -- accepts Seniors Farmers' Market Nutrition Program or not- 1/0,
    SNAP          INTEGER -- participate The Supplemental Nutrition Assistance Program or not- 1/0 ,
    Organic       REAL -- From here to WildHarvested shows if FM sells particular goods or not- 1/0 ,
    Bakedgoods    REAL,
    Cheese        REAL,
    Crafts        REAL,
    Flowers       REAL,
    Eggs          REAL,
    Seafood       REAL,
    Herbs         REAL,
    Vegetables    REAL,
    Honey         REAL,
    Jams          REAL,
    Maple         REAL,
    Meat          REAL,
    Nursery       REAL,
    Nuts          REAL,
    Plants        REAL,
    Poultry       REAL,
    Prepared      REAL,
    Soap          REAL,
    Trees         REAL,
    Wine          REAL,
    Coffee        REAL,
    Beans         REAL,
    Fruits        REAL,
    Grains        REAL,
    Juices        REAL,
    Mushrooms     REAL,
    PetFood       REAL,
    Tofu          REAL,
    WildHarvested REAL,
    updateTime    TIMESTAMP-- time when FM reported in database
);

create index ix_farmers_market_index
    on farmers_market ("index");


create table City
-- USA cities for farmers market
(
    city     TEXT -- name of the city,
    County   TEXT -- country of city,
    zip      INT -- numeric postal code,
    state_id integer,
    city_id  integer -- primary key numeric column of city
        constraint City_pk
            primary key
        constraint City_farmer_market_city_id_fk
            references farmers_market (city_id)
            on update restrict on delete restrict
);


create table State
-- USA states for farmers market
(
    State    TEXT --State name,
    country  TEXT -- country of state,
    state_id integer -- an unique numeric id for each state introduced in this database.
        constraint State_pk
            primary key
        constraint State_city__fk
            references City (state_id)
            on update restrict on delete restrict
);
create table fm_seasons_dates
(
    "index" INTEGER,
    FMID    INTEGER
        constraint fm_seasons_dates_farmers_market_FMID_fk
            references farmers_market (FMID)
            on update restrict on delete restrict,
    start   TEXT,
    end     TEXT,
    zip     INTEGER
);

create table fm_seasons_times
(
    "index"   INTEGER,
    FMID      INTEGER
        constraint fm_seasons_times_farmers_market_FMID_fk
            references farmers_market (FMID)
            on update restrict on delete restrict,
    zip       INTEGER,
    mon_start TEXT,
    mon_end   TEXT,
    tue_start TEXT,
    tue_end   TEXT,
    wed_start TEXT,
    wed_end   TEXT,
    thu_start TEXT,
    thu_end   TEXT,
    fri_start TEXT,
    fri_end   TEXT,
    sat_start TEXT,
    sat_end   TEXT,
    sun_start TEXT,
    sun_end   TEXT
);

-- Enable not null constraint
alter table CITY add  int not null;

-- Populate primary key column using running sequence number
ALTER TABLE farmers_market ADD COLUMN city_id INTEGER NOT NULL DEFAULT '';