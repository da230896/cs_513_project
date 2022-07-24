#!/usr/bin/env python
# coding: utf-8

# # UO & U1.2
# ## Farmer Market Data Cleanup Steps

# In[65]:


import pandas as pd
import folium
import sqlite3
import pandas_usaddress,re, os


# In[66]:


os. getcwd()


# In[67]:


# @BEGIN main
# @PARAM DATASET_LOC
# @IN farmers_market @URI file:{DATASET_LOC}/input/farmers_markets.csv
# @IN address_suffx @AS address_suffx @URI file:{DATASET_LOC}/input/street_suffix_abbvr.csv
# @OUT result_farmers_market @URI file:{DATASET_LOC}/output/farmers_market.csv
# @OUT database_export @URI file:{DATASET_LOC}/../database/farmers_market.db
# @OUT address @URI file:{DATASET_LOC}/output/address.csv
# @OUT states @URI file:{DATASET_LOC}/output/states.csv
# @OUT seasons @URI file:{DATASET_LOC}/output/seasons.csv
DATASET_LOC="/Volumes/reeth/git/cca/cs513_project/dataset"
DATASET_INPUT_LOC=f"{DATASET_LOC}/input/farmers_market.csv"
DATASET_OUTPUT_LOC=f"{DATASET_LOC}/output/farmers_market.csv"
DATASET_OUTPUT_ADDR=f"{DATASET_LOC}/output/address.csv"
DATASET_OUTPUT_ADDR_CTRY=f"{DATASET_LOC}/output/states.csv"
DATASET_OUTPUT_SEASON=f"{DATASET_LOC}/output/seasons.csv"

# @BEGIN load_farmers
# @PARAM farmers_market
# @IN g @AS farmers_market @URI file:{DATASET_LOC}/input/farmers_markets.csv
# @OUT fm_ds
# @END load_farmers
fm_ds = pd.read_csv(DATASET_INPUT_LOC)
fm_ds.dtypes


# ## Data Analysis and cleaning using Pandas

# In[68]:


# @BEGIN data_validation
# @IN  fm_ds
# @OUT fm_ds @AS fm_ds_validated
# @END data_validation
fm_ds.isna().sum()


# ### Check for duplicate in market id

# In[69]:


fm_ds['FMID'].value_counts(ascending=False).head()


# ## Update Time cleanup
# 1990
# 1990/01/01
# 01/01/1990
# Jan 01 1990
# 1990/01/01 12:36PM
# 1990/01/01 12:36:01 PM
# 01/01/1990 12:36:01PM

# 

# In[70]:


# @BEGIN format_update_datetime
# @IN  fm_ds @AS fm_ds_validated
# @OUT fm_ds @AS fm_ds_date_formatted
# @END format_update_datetime
fm_ds.updateTime


# In[71]:


from datetime import datetime
def parse_date(text):
    for fmt in ('%Y','%y','%m/%d/%Y %H:%M:%S','%m/%d/%Y %I:%M:%S %p','%b %d %Y %I:%M%p','%b %d %Y %I:%M %p','%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError(f'Invalid date formats for:{text}')


# In[72]:


fm_ds['updateTime'] = fm_ds['updateTime'].apply(parse_date)
fm_ds.updateTime.head()


# In[73]:


#Change column datatypes to boolean
#fm_ds[fm_ds.columns[23:-1]]=fm_ds[fm_ds.columns[23:-1]].astype("boolean")


# In[74]:


# Check number of columns have missing values
fm_ds.isna().sum()


# ## Exclude missing lat & lon from Data
# ### Before filter

# In[75]:


# @BEGIN filter_invalid_location
# @IN  fm_ds @AS fm_ds_date_formatted
# @OUT fm_ds @AS fm_loc_filter
# @END filter_invalid_location


# In[76]:


len(fm_ds)


# In[77]:


fm_ds =fm_ds[fm_ds['x'].notna()]
fm_ds =fm_ds[fm_ds['y'].notna()]


# ### After filter

# In[78]:


len(fm_ds)


# ## U0 Plot market data in USA map- no data cleaning is required (U0)

# In[79]:


# @BEGIN plot_u0
# @IN  fm_ds @AS fm_loc_filter
# @OUT u0_farmers_market_plot
# @END plot_u0
# Create a map of U.S. farmers markets using latitude and longitude values
map_markets = folium.Map(location=[39.8283, -98.5795], zoom_start=5, popup='Portland, OR')

# add markers to map
for  lng,lat, market, state in zip(fm_ds['x'],fm_ds['y'], fm_ds['MarketName'], fm_ds['State']):
    label = '{}, {}'.format(market, state)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=1,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#31cc34',
        fill_opacity=0.5,
        parse_html=False).add_to(map_markets)

map_markets


# ## Generate Has Social media grouped columns

# In[ ]:


# @BEGIN populate_social_media
# @IN  fm_ds @AS fm_loc_filter
# @OUT fm_ds @AS ds_social_media
# @END populate_social_media
fm_ds['has_social_media']=fm_ds.apply(lambda x:  pd.isna(x.Facebook) is False or pd.isna(x.Twitter) is False or  pd.isna(x.Youtube) is False or pd.isna(x.Website) is False or pd.isna(x.OtherMedia) is False,axis=1)


# In[ ]:


fm_ds.has_social_media.value_counts()


# ## Address Cleaning Rules

# In[ ]:


# @BEGIN address_cleaning_fields_split
# @IN  fm_ds @AS ds_social_media
# @OUT fm_subset @AS fm_ds_splits
# @END address_cleaning_fields_split
fm_subset=fm_ds[["FMID",'MarketName',"Facebook","Twitter","Youtube","Website",'has_social_media',"city","State","street","County","x","y",'Credit','WIC','WICcash','SFMNP','Organic','Flowers','Vegetables','Meat','Nursery','Wine','Coffee','Fruits','PetFood','WildHarvested','updateTime']]


# In[ ]:


fm_subset=pandas_usaddress.tag(fm_subset, ['street'], granularity='medium', standardize=False)


# In[ ]:


fm_subset.columns


# ## AddressNumber cleanup
# ### Before update AddressNumber

# In[ ]:


# @BEGIN address_number_cleaning
# @IN  fm_subset @AS fm_ds_splits
# @OUT fm_subset @AS farmers_address_number
# @END address_number_cleaning


# In[ ]:


def address_number_sumamry(fm_subset):
    print(fm_subset['AddressNumber'].apply(lambda x: re.search('[^\d]+',str(x)) is None).sum())


# In[ ]:


address_number_sumamry(fm_subset)


# In[ ]:


def address_number_fun(strr):
    if pd.isna(strr) :
        return strr
    p=re.compile('(\d+)?[^0-9]*')
    m=p.match(strr)
    grps = m.groups()
    return grps[0] if len(grps)>0 else pd.NaT


# In[ ]:


fm_subset['AddressNumber']=fm_subset['AddressNumber'].apply(address_number_fun)


# ### After Cleanup

# In[ ]:


address_number_sumamry(fm_subset)


# ## Street Suffx Cleanup

# In[ ]:


#Prepare street suffix
# @BEGIN load_address_suffix
# @IN address_suffx @URI file:{DATASET_LOC}/input/street_suffix_abbvr.csv
# @OUT str_sfx
# @END load_address_suffix
str_sfx=pd.read_csv(f"{DATASET_LOC}/input/street_suffix_abbvr.csv")
str_sfx.fillna(method='ffill',inplace=True)
str_sfx = str_sfx.applymap(lambda s: s.lower() if type(s) == str else s)
#str_sfx.set_index('abbvr',inplace=True).to_dict()


# In[ ]:


str_sfx={'allee': 'aly','alley': 'aly','ally': 'aly','aly': 'aly','anex': 'anx','annex': 'anx','annx': 'anx','anx': 'anx','arc': 'arc','arcade': 'arc','av': 'ave','ave': 'ave','aven': 'ave','avenu': 'ave','avenue': 'ave','avn': 'ave','avnue': 'ave','bayoo': 'byu','bayou': 'byu','bch': 'bch','beach': 'bch','bend': 'bnd','bnd': 'bnd','blf': 'blf','bluf': 'blf','bluff': 'blf','bluffs': 'blfs','bot': 'btm','btm': 'btm','bottm': 'btm','bottom': 'btm','blvd': 'blvd','boul': 'blvd','boulevard': 'blvd','boulv': 'blvd','br': 'br','brnch': 'br','branch': 'br','brdge': 'brg','brg': 'brg','bridge': 'brg','brk': 'brk','brook': 'brk','brooks': 'brks','burg': 'bg','burgs': 'bgs','byp': 'byp','bypa': 'byp','bypas': 'byp','bypass': 'byp','byps': 'byp','camp': 'cp','cp': 'cp','cmp': 'cp','canyn': 'cyn','canyon': 'cyn','cnyn': 'cyn','cape': 'cpe','cpe': 'cpe','causeway': 'cswy','causwa': 'cswy','cswy': 'cswy','cen': 'ctr','cent': 'ctr','center': 'ctr','centr': 'ctr','centre': 'ctr','cnter': 'ctr','cntr': 'ctr','ctr': 'ctr','centers': 'ctrs','cir': 'cir','circ': 'cir','circl': 'cir','circle': 'cir','crcl': 'cir','crcle': 'cir','circles': 'cirs','clf': 'clf','cliff': 'clf','clfs': 'clfs','cliffs': 'clfs','clb': 'clb','club': 'clb','common': 'cmn','commons': 'cmns','cor': 'cor','corner': 'cor','corners': 'cors','cors': 'cors','course': 'crse','crse': 'crse','court': 'ct','ct': 'ct','courts': 'cts','cts': 'cts','cove': 'cv','cv': 'cv','coves': 'cvs','creek': 'crk','crk': 'crk','crescent': 'cres','cres': 'cres','crsent': 'cres','crsnt': 'cres','crest': 'crst','crossing': 'xing','crssng': 'xing','xing': 'xing','crossroad': 'xrd','crossroads': 'xrds','curve': 'curv','dale': 'dl','dl': 'dl','dam': 'dm','dm': 'dm','div': 'dv','divide': 'dv','dv': 'dv','dvd': 'dv','dr': 'dr','driv': 'dr','drive': 'dr','drv': 'dr','drives': 'drs','est': 'est','estate': 'est','estates': 'ests','ests': 'ests','exp': 'expy','expr': 'expy','express': 'expy','expressway': 'expy','expw': 'expy','expy': 'expy','ext': 'ext','extension': 'ext','extn': 'ext','extnsn': 'ext','exts': 'exts','fall': 'fall','falls': 'fls','fls': 'fls','ferry': 'fry','frry': 'fry','fry': 'fry','field': 'fld','fld': 'fld','fields': 'flds','flds': 'flds','flat': 'flt','flt': 'flt','flats': 'flts','flts': 'flts','ford': 'frd','frd': 'frd','fords': 'frds','forest': 'frst','forests': 'frst','frst': 'frst','forg': 'frg','forge': 'frg','frg': 'frg','forges': 'frgs','fork': 'frk','frk': 'frk','forks': 'frks','frks': 'frks','fort': 'ft','frt': 'ft','ft': 'ft','freeway': 'fwy','freewy': 'fwy','frway': 'fwy','frwy': 'fwy','fwy': 'fwy','garden': 'gdn','gardn': 'gdn','grden': 'gdn','grdn': 'gdn','gardens': 'gdns','gdns': 'gdns','grdns': 'gdns','gateway': 'gtwy','gatewy': 'gtwy','gatway': 'gtwy','gtway': 'gtwy','gtwy': 'gtwy','glen': 'gln','gln': 'gln','glens': 'glns','green': 'grn','grn': 'grn','greens': 'grns','grov': 'grv','grove': 'grv','grv': 'grv','groves': 'grvs','harb': 'hbr','harbor': 'hbr','harbr': 'hbr','hbr': 'hbr','hrbor': 'hbr','harbors': 'hbrs','haven': 'hvn','hvn': 'hvn','ht': 'hts','hts': 'hts','highway': 'hwy','highwy': 'hwy','hiway': 'hwy','hiwy': 'hwy','hway': 'hwy','hwy': 'hwy','hill': 'hl','hl': 'hl','hills': 'hls','hls': 'hls','hllw': 'holw','hollow': 'holw','hollows': 'holw','holw': 'holw','holws': 'holw','inlt': 'inlt','is': 'is','island': 'is','islnd': 'is','islands': 'iss','islnds': 'iss','iss': 'iss','isle': 'isle','isles': 'isle','jct': 'jct','jction': 'jct','jctn': 'jct','junction': 'jct','junctn': 'jct','juncton': 'jct','jctns': 'jcts','jcts': 'jcts','junctions': 'jcts','key': 'ky','ky': 'ky','keys': 'kys','kys': 'kys','knl': 'knl','knol': 'knl','knoll': 'knl','knls': 'knls','knolls': 'knls','lk': 'lk','lake': 'lk','lks': 'lks','lakes': 'lks','land': 'land','landing': 'lndg','lndg': 'lndg','lndng': 'lndg','lane': 'ln','ln': 'ln','lgt': 'lgt','light': 'lgt','lights': 'lgts','lf': 'lf','loaf': 'lf','lck': 'lck','lock': 'lck','lcks': 'lcks','locks': 'lcks','ldg': 'ldg','ldge': 'ldg','lodg': 'ldg','lodge': 'ldg','loop': 'loop','loops': 'loop','mall': 'mall','mnr': 'mnr','manor': 'mnr','manors': 'mnrs','mnrs': 'mnrs','meadow': 'mdw','mdw': 'mdws','mdws': 'mdws','meadows': 'mdws','medows': 'mdws','mews': 'mews','mill': 'ml','mills': 'mls','missn': 'msn','mssn': 'msn','motorway': 'mtwy','mnt': 'mt','mt': 'mt','mount': 'mt','mntain': 'mtn','mntn': 'mtn','mountain': 'mtn','mountin': 'mtn','mtin': 'mtn','mtn': 'mtn','mntns': 'mtns','mountains': 'mtns','nck': 'nck','neck': 'nck','orch': 'orch','orchard': 'orch','orchrd': 'orch','oval': 'oval','ovl': 'oval','overpass': 'opas','park': 'park','prk': 'park','parks': 'park','parkway': 'pkwy','parkwy': 'pkwy','pkway': 'pkwy','pkwy': 'pkwy','pky': 'pkwy','parkways': 'pkwy','pkwys': 'pkwy','pass': 'pass','passage': 'psge','path': 'path','paths': 'path','pike': 'pike','pikes': 'pike','pine': 'pne','pines': 'pnes','pnes': 'pnes','pl': 'pl','plain': 'pln','pln': 'pln','plains': 'plns','plns': 'plns','plaza': 'plz','plz': 'plz','plza': 'plz','point': 'pt','pt': 'pt','points': 'pts','pts': 'pts','port': 'prt','prt': 'prt','ports': 'prts','prts': 'prts','pr': 'pr','prairie': 'pr','prr': 'pr','rad': 'radl','radial': 'radl','radiel': 'radl','radl': 'radl','ramp': 'ramp','ranch': 'rnch','ranches': 'rnch','rnch': 'rnch','rnchs': 'rnch','rapid': 'rpd','rpd': 'rpd','rapids': 'rpds','rpds': 'rpds','rest': 'rst','rst': 'rst','rdg': 'rdg','rdge': 'rdg','ridge': 'rdg','rdgs': 'rdgs','ridges': 'rdgs','riv': 'riv','river': 'riv','rvr': 'riv','rivr': 'riv','rd': 'rd','road': 'rd','roads': 'rds','rds': 'rds','route': 'rte','row': 'row','rue': 'rue','run': 'run','shl': 'shl','shoal': 'shl','shls': 'shls','shoals': 'shls','shoar': 'shr','shore': 'shr','shr': 'shr','shoars': 'shrs','shores': 'shrs','shrs': 'shrs','skyway': 'skwy','spg': 'spg','spng': 'spg','spring': 'spg','sprng': 'spg','spgs': 'spgs','spngs': 'spgs','springs': 'spgs','sprngs': 'spgs','spur': 'spur','spurs': 'spur','sq': 'sq','sqr': 'sq','sqre': 'sq','squ': 'sq','square': 'sq','sqrs': 'sqs','squares': 'sqs','sta': 'sta','station': 'sta','statn': 'sta','stn': 'sta','stra': 'stra','strav': 'stra','straven': 'stra','stravenue': 'stra','stravn': 'stra','strvn': 'stra','strvnue': 'stra','stream': 'strm','streme': 'strm','strm': 'strm','street': 'st','strt': 'st','st': 'st','str': 'st','streets': 'sts','smt': 'smt','sumit': 'smt','sumitt': 'smt','summit': 'smt','ter': 'ter','terr': 'ter','terrace': 'ter','throughway': 'trwy','trace': 'trce','traces': 'trce','trce': 'trce','track': 'trak','tracks': 'trak','trak': 'trak','trk': 'trak','trks': 'trak','trafficway': 'trfy','trail': 'trl','trails': 'trl','trl': 'trl','trls': 'trl','trailer': 'trlr','trlr': 'trlr','trlrs': 'trlr','tunel': 'tunl','tunl': 'tunl','tunls': 'tunl','tunnel': 'tunl','tunnels': 'tunl','tunnl': 'tunl','trnpk': 'tpke','turnpike': 'tpke','turnpk': 'tpke','underpass': 'upas','un': 'un','union': 'un','unions': 'uns','valley': 'vly','vally': 'vly','vlly': 'vly','vly': 'vly','valleys': 'vlys','vlys': 'vlys','vdct': 'via','via': 'via','viadct': 'via','viaduct': 'via','view': 'vw','vw': 'vw','views': 'vws','vws': 'vws','vill': 'vlg','villag': 'vlg','village': 'vlg','villg': 'vlg','villiage': 'vlg','vlg': 'vlg','villages': 'vlgs','vlgs': 'vlgs','ville': 'vl','vl': 'vl','vis': 'vis','vist': 'vis','vista': 'vis','vst': 'vis','vsta': 'vis','walk': 'walk','walks': 'walk','wall': 'wall','wy': 'way','way': 'way','ways': 'ways','well': 'wl','wells': 'wls','wls': 'wls'}


# ### Before suffix cleanup

# In[ ]:


# @BEGIN address_suffix_cleanup
# @IN fm_subset @AS fm_ds_splits
# @IN str_sfx
# @OUT fm_subset @AS street_name_suffix
# @END address_suffix_cleanup
fm_subset.StreetNameSuffix.value_counts()


# In[ ]:


fm_subset.replace({'StreetNameSuffix':str_sfx},inplace=True)


# ### After Cleanup

# In[ ]:


fm_subset['StreetNameSuffix'].value_counts()


# ## Street Name direction
# ### Before Cleanup

# In[ ]:


# @BEGIN street_suffix_direction_cleanup
# @IN fm_subset @AS fm_ds_splits
# @OUT fm_subset @AS street_name_direction
# @END street_suffix_direction_cleanup
fm_subset.StreetNamePreDirectional.value_counts()


# In[ ]:


dir_suffix={'n':"north",'s':'south','e':'east','w':'west','ne':'northeast','se':'southeast','nw':"northwest",'sw':'southwest'}


# In[ ]:


fm_subset.replace({'StreetNamePreDirectional':dir_suffix},inplace=True)


# ### After Cleanup

# In[ ]:


fm_subset.StreetNamePreDirectional.value_counts()


# ## Join Columns and remove multiple spaces

# In[ ]:


# @BEGIN join_address_entities
# @IN  fm_subset @AS farmers_address_number
# @IN  fm_subset @AS street_name_suffix
# @IN  fm_subset @AS street_name_direction
# @OUT fm_subset @AS fm_subset_address_joined
# @END street_suffix_direction_cleanup
fm_subset['street']=fm_subset[['AddressNumber',
       'PlaceName', 'StateName', 'StreetName', 'StreetNamePreDirectional',
       'StreetNamePostDirectional', 'ZipCode', 'StreetNamePrefix',
       'StreetNameSuffix', 'USPSBox', 'OccupancySuite']].fillna('').astype(str).apply(lambda x: re.sub('\s+',' ',' '.join(x)).strip(), axis=1)


# In[ ]:


fm_subset.drop(['AddressNumber',
       'PlaceName', 'StateName', 'StreetName', 'StreetNamePreDirectional',
       'StreetNamePostDirectional', 'ZipCode', 'StreetNamePrefix',
       'StreetNameSuffix', 'USPSBox', 'OccupancySuite'],axis=1,inplace=True)


# In[83]:


fm_subset.head()


# ## Market Name Cleanup
# ### Cleanup alpha Numeric Texts

# In[85]:


# @BEGIN market_name_cleanup_non_numeric
# @IN fm_subset @AS fm_subset_address_joined
# @OUT fm_subset @AS fm_subset_mkt
# @END market_name_cleanup_non_numeric
fm_subset['MarketName'] = fm_subset['MarketName'].apply(lambda x: re.sub('[^a-zA-Z\d\s:]', '', x))


# ### Remove Farmers Market from Name if Name is already more than 3 words

# In[89]:


# @BEGIN market_name_cleanup_dups
# @IN fm_subset @AS fm_subset_mkt
# @OUT fm_subset @AS fm_subset_mkt_dedup
# @END market_name_cleanup_dups
def market_name_subs(fm):
    words = fm.split('\s')
    if len(words ) >3:
        return re.sub("((Farm)|Farmer)|(market)",'',fm,re.IGNORECASE)
    else:
        return fm


# In[90]:


fm_subset['MarketName']=fm_subset.MarketName.apply(market_name_subs)


# In[91]:


fm_subset['MarketName'].head()


# In[95]:


# @BEGIN save_farmers_data
# @IN fm_subset @AS fm_subset_mkt_dedup
# @OUT fm_subset_joined  @AS result_farmers_market  @URI file:{DATASET_LOC}/output/farmers_market.csv
# @END save_farmers_data
fm_subset.to_csv(f'{DATASET_OUTPUT_LOC}')


# ## Export table to SQL Lite For data normalization

# In[99]:


# @BEGIN export_db
# @IN fm_subset @AS fm_subset_mkt_dedup
# @OUT database_export @URI file:{DATASET_LOC}/../database/farmers_market.db
# @END export_db
# @END main
conn = sqlite3.connect(f"{DATASET_LOC}/../database/farmers_market.db")
fm_ds.to_sql("farmers_market", conn, if_exists="replace")
conn.cursor().execute(
    """
    select count(*) from farmers_market
    """).fetchall()


# In[ ]:




