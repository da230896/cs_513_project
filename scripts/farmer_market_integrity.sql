-- checking that there is no duplicate farmer market reported.
SELECT COUNT(*) 
FROM farmers_market
GROUP BY farmers_market.FMID 
HAVING COUNT(farmers_market.FMID)>1;

-- checking that seasons_date is unique and contains no duplicate.
SELECT COUNT(*) 
FROM fm_seasons_dates
GROUP BY fm_seasons_dates.FMID 
HAVING COUNT(fm_seasons_dates.FMID)>1;

-- Every “seasons_date” is associated with a single farmers market
SELECT COUNT(*) 
FROM fm_seasons_dates
WHERE fm_seasons_dates.FMID IN (
    SELECT farmers_market.FMID 
    FROM  farmers_market);

-- Every “seasons_time” is  associated with a single farmers market.
SELECT COUNT(*) 
FROM fm_seasons_times
WHERE fm_seasons_times.FMID IN (
    SELECT farmers_market.FMID 
    FROM  farmers_market);

SELECT COUNT(*) 
FROM fm_seasons_times 
WHERE fm_seasons_times.FMID NOT IN (
    SELECT farmers_market.FMID 
    FROM farmers_market);

-- “fm_seasons_dates” cannot contain null values and should be of ISO8601 Format.
SELECT COUNT(*) 
FROM fm_seasons_dates
WHERE STR_TO_DATE(TRIM(fm_seasons_dates.start), '%Y-%m-%d') IS NOT null

SELECT COUNT(*)
FROM fm_seasons_dates
WHERE STR_TO_DATE(TRIM(fm_seasons_dates.end), '%Y-%m-%d') IS NOT null

-- farmers_market for which seasons(1,2,3,4)date is null should not be present in fm_seasons_date
SELECT COUNT(*) 
FROM farmers_market fm
WHERE fm.Season1Date is  NULL
AND fm.Season2Date is  NULL
AND fm.Season3Date is  NULL
AND fm.Season4Date is  NULL
AND fm.FMID in (SELECT FMID FROM fm_seasons_dates);

-- farmers_market for which seasons(1,2,3,4)time is null should not be present in fm_seasons_times.
SELECT COUNT(*) 
FROM farmers_market fm 
WHERE fm.Season1Time IS  NULL
AND fm.Season2Time is  NULL
AND fm.Season3Time is  NULL
AND fm.Season4Time is  NULL
AND fm.FMID NOT IN (SELECT FMID FROM fm_seasons_times);

-- “x”, “y” in “famers_market” corresponding to latitude & longitude should not be null.
SELECT COUNT(*) 
FROM farmers_market 
WHERE x is NULL and y is NULL


