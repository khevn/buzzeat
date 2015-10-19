import config
import sqlalchemy
import pandas as pd
import numpy as np
import requests
import geo_func
from datetime import datetime, timedelta
import bze_util as bze
import ftfy
import spacy
import gensim, logging
import re
from nltk.corpus import stopwords
import nltk.data

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

# Load the punkt tokenizer
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def add_space_symbol(caption):
    # add a spce between ): ! ? etc so they are their own symbols
    rem_list = ['\'','"','/'," \ ",'|','}','{','[',']','@','^','*','+','-','.','`','!','?',"'",'=',':',')','()'] # ':!)(;#$%'
    
    for ch in rem_list:
        caption = str.replace(caption,ch.strip(),' '+ch.strip()+' ')
    
    return caption

def caption_to_wordlist( caption, remove_stopwords=False ):
    # Convert a document to a sequence of words, returning a list of words
 
    caption = add_space_symbol(caption)
    caption_nohash = re.sub("#", "", caption)
    words = fix_text(caption_nohash.lower().split())
 
    if remove_stopwords:
        stops = set(stopwords.words("english"))
 
        words = [w for w in words if not w in stops]
 
    return(words)

def caption_to_sentences( caption, tokenizer, remove_stopwords=False ):
    # split captions into parsed sentences. 

    # Use the NLTK tokenizer to split the paragraph into sentences
    raw_sentences = tokenizer.tokenize(caption.strip())

    sentences = []
    for raw_sentence in raw_sentences:
        # If a sentence is empty, skip it
        if len(raw_sentence) > 0:
            sentences.append( caption_to_wordlist( raw_sentence, \
              remove_stopwords ))
 
    return sentences

# selecting all posts from US
geo_box = (18.005611, 48.987386, -124.626080, -62.361014)

# connect to server
engine = sqlalchemy.create_engine(
	'mysql://%(user)s:%(pass)s@%(host)s' % config.database)
engine.execute('use %s' % config.database['name'])  # select db
recent_data = (datetime.now() - timedelta(weeks=12)).strftime("%Y-%m-%d")
sql_query = '''select date, lat, `long`, image_url, likes, text, post_url
			from instagram
			where `date` > '%s'
			and lat between %s and %s
			and `long` between %s and %s
			order by `date` desc, likes desc
			''' % (recent_data, geo_box[0], geo_box[1],  geo_box[2],  geo_box[3])

posts = pd.read_sql_query(sql_query, engine, parse_dates=['date'])
n_points = posts.shape[0]

posts = posts[posts['text'].notnull()]
posts.reset_index(drop = True)

sentences = []  # Initialize an empty list of sentences

print "Parsing sentences from training set"
for caption in posts["text"]:
    sentences += caption_to_sentences(caption, tokenizer)

# Set values for various parameters
num_features = 400    # Word vector dimensionality                      
min_word_count = 30   # Minimum word count                        
num_workers = 4       # Number of threads to run in parallel
context = 12          # Context window size                                                                                    
downsampling = 1e-3   # Downsample setting for frequent words

from gensim.models import word2vec

model = word2vec.Word2Vec(sentences, workers=num_workers, \
            size=num_features, min_count = min_word_count, \
            window = context, sample = downsampling)

model.init_sims(replace=True)
model_name = "buzzeat_400features_30minwords_12context"
model.save(model_name)
