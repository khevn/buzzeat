import pandas as pd
import sqlalchemy

engine = sqlalchemy.create_engine('mysql://root@localhost')
engine.execute('use buzzeat')

# action = 0: create SQL database and schema
# action = 1: update the database
action = 0

if action == 0:
	engine.execute('''
	drop table if exists instagram;
	create table instagram (
	    created_time bigint,
	    post_id varchar(255),
	    image_url varchar(255),
	    latitude double,
	    likes int,
	    longitude double,
	    post_url varchar(255),
	    caption varchar(5000),
	    user_id bigint,
	    post_date datetime,
	    date_year varchar(255),
	    date_month varchar(255),
	    date_day varchar(255),
	    date_week varchar(255)
	);
	''')
else:
	filename = './data/instagram_data_2015-07-22T17_46_07.399647.tsv'
	new_posts = pd.read_csv(filename, sep='\t')
	new_posts['post_date'] = pd.to_datetime(new_posts.created_time, unit='s')
	new_posts['date_year'] = new_posts['post_date'].apply(lambda x: str(x)[:4])
	new_posts['date_month'] = new_posts['post_date'].apply(lambda x: str(x)[:7])
	new_posts['date_week'] = new_posts['post_date'].apply(lambda x: x.isocalendar()[1])

	new_posts.to_sql('instagram', engine,
	                 schema='buzzeat',
	                 if_exists='append',
	                 chunksize=1000,
	                 index=False)
