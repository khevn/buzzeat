from flask import render_template, request
from app import app
import config
import pandas as pd
import bze_util as bze
import sqlalchemy
import geo_func
import string
import random
import numpy as np
import os
import folium
import pickle
import unidecode
from datetime import datetime, timedelta
import gensim, logging
from gensim.models import Word2Vec
import folium

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

model = Word2Vec.load("buzzeat_400features_30minwords_12context")


@app.route('/')
@app.route('/index')
def input():
	return render_template("input.html", title='Home')


@app.route('/output')
def output():
	# pull 'ID' from input field and store it
	city = request.args.get('cityname', 'San Francisco, CA')
	food = request.args.get('foodname')

	# info about the location using google maps API
	search_loc = geo_func.google_api(city)
	geo_area = geo_func.geo_bounds([search_loc['lat'], search_loc['lng']], distance=10)
	search_loc['formatted_address'] = unidecode.unidecode(search_loc['formatted_address'])

	# get the data from SQL database
	engine = sqlalchemy.create_engine(
		'mysql://%(user)s:%(pass)s@%(host)s' % config.database)
	engine.execute('use %s' % config.database['name'])  # select db
	recent_data = (datetime.now() - timedelta(weeks=52)).strftime("%Y-%m-%d")
	sql_query = '''SELECT post_date, latitude, longitude, image_url, likes, caption, post_url 
				FROM instagram
              	WHERE post_date > '%s'
              	AND latitude between %s AND %s
              	AND longitude between %s AND %s
              	ORDER BY post_date DESC, likes DESC
              	''' % (recent_data, geo_area[0], geo_area[1],  geo_area[2],  geo_area[3])

	posts = pd.read_sql_query(sql_query, engine, parse_dates=['post_date'])
	# find food that is similar to user's search term 
	try:
		if food == "": #for finding best trending dishes (no search term specified)
			similar_food = []
			final_posts = posts.sort('likes', ascending = False)[['image_url','latitude','longitude','post_url','likes']].head(200)
		else:
			similar_food = model.most_similar(food.replace(' ','').lower())
			search_terms = '%s|%s|%s|%s|%s|%s|%s' % (food, similar_food[0][0], similar_food[1][0], similar_food[2][0],
				similar_food[3][0], similar_food[4][0], similar_food[5][0])
			final_posts = posts[posts['caption'].str.contains(search_terms, na=False)]
	except:
		return render_template("error.html")
		
	try:
		rest_clusters = bze.cluster_map(final_posts, eps=0.13, min_samples=6)
		name_rand = ''.join(random.choice(string.letters + string.digits) for i in range(20))
		map_name = 'maps/map_%s.html' % name_rand
		cols = bze.create_map([search_loc['latitude'], search_loc['lng']], 
			final_posts, rest_clusters, map_name=map_name)
		final_posts['cluster_num'] = rest_clusters
		ranked_clusters = bze.rank_clusters(final_posts)
		photos = bze.top_posts(final_posts, n_photos=18)

	except:
		# #print error: word not in vocabulary, please try again'
		#return render_template("error.html")

		rest_clusters = np.array([-1] * posts.shape[0])
		name_rand = ''.join(random.choice(string.letters + string.digits) for i in range(20))
		map_name = 'maps/map_%s.html' % name_rand
		cols = bze.create_map([search_loc['latitude'], search_loc['lng']], 
			final_posts, rest_clusters, map_name=map_name)
		ranked_clusters = []
		photos = bze.top_posts(final_posts, n_photos=18)
		

	return render_template("output.html", 
		loc_name=search_loc['formatted_address'],
		map_name = map_name,
		similar_food = similar_food,
		ranked_clusters = ranked_clusters,
		cols = cols,
		photos = photos)

if '__name__' == '__main__':
    app.run()


