import pandas as pd
import locGeoUtil
import time
from datetime import datetime, timedelta
import sqlalchemy
import config
import string

metro_population = pd.read_csv('./data/us_metro_pop.csv').dropna()
metro_population.columns = ['rank', 'name', 'population']
metro_population['population'] = metro_population['population'].str.replace(r'[$,]', '').astype('int')
metro_population = metro_population.reset_index(drop = True)
metro_population['lat'] = pd.Series(0.0, index=metro_population.index)
metro_population['lng'] = pd.Series(0.0, index=metro_population.index)
metro_population['n_images'] = pd.Series(0, index=metro_population.index)



engine = sqlalchemy.create_engine('mysql://%(user)s:%(pass)s@%(host)s' % config.database) # connect to server
engine.execute('use %s' % config.database['name']) # select new db

recent_data = (datetime.now() - timedelta(weeks=2)).strftime("%Y-%m-%d")

for i in range(0,metro_population.shape[0]):
    print i
    time.sleep(0.3)
    loc = locGeoUtil.google_geo(metro_population.iloc[i]['name'])
    geo_box = locGeoUtil.geo_bounds([loc['lat'], loc['lng']], distance=9)
    # sql_query = '''select count(*)
    #             from instagram
    #             where `date` > '%s'
    #             and lat between %s and %s
    #             and `long` between %s and %s
    #             limit 1000''' % (recent_data, geo_box[0], geo_box[1],  geo_box[2],  geo_box[3])
    sql_query = '''select count(*)
                from instagram
                where `date` > '%s'
                and lat between %s and %s
                and `long` between %s and %s
                ''' % (recent_data, geo_box[0], geo_box[1],  geo_box[2],  geo_box[3])
    posts = pd.read_sql_query(sql_query, engine)
    metro_population.set_value(i, 'n_images', posts.iloc[0, 0])
    metro_population.set_value(i, 'lat', loc['lat'])
    metro_population.set_value(i, 'lng', loc['lat'])
metro_population.to_csv('./data/us_metro_population.csv')
