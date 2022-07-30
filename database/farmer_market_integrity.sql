-- checking that there is no duplicate farmer market reported.
SELECT * FROM farmers_market
WHERE FMID in (SELECT FMID from farmers_market
              Group by FMID having count(*)>1);

-- checking no farmer market records has empty FMID.
SELECT * FROM farmers_market
WHERE FMID  = NULL;
