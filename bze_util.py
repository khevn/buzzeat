import pandas as pd
import numpy as np
import config
from geopy.distance import vincenty
import os
import folium


def cluster_map(posts,
                eps=0.15, min_samples=10,
                max_cluster_size=float('inf')):


    print 'Clustering %i points: ' % posts.shape[0]

    from sklearn.cluster import DBSCAN
    from sklearn import metrics
    from sklearn.datasets.samples_generator import make_blobs
    from sklearn.preprocessing import StandardScaler

    standardized = StandardScaler().fit_transform(posts[['lat', 'lng']].values)

    db = DBSCAN(eps=eps, min_samples=min_samples).fit(standardized)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    cluster_labels = db.labels_

    n_clust = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)

    print('Estimated number of clusters: %d' % n_clust)
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(posts[['lat', 'lng']].values, cluster_labels))

    for clust in list(set(cluster_labels[cluster_labels>=0])):
        # dat = posts
        geo_mean = posts.loc[cluster_labels == clust, ['lat', 'lng']].mean()
        geo_std = posts.loc[cluster_labels == clust, ['lat', 'lng']].std()

        lat_range = vincenty((geo_mean['lat'] - 2*geo_std['lat'], geo_mean['lng']),
                             (geo_mean['lat'] + 2*geo_std['lat'], geo_mean['lng'])).miles
        long_range = vincenty((geo_mean['lat'], geo_mean['lng'] - 2*geo_std['lng']),
                             (geo_mean['lat'], geo_mean['lng'] + 2*geo_std['lng'])).miles

        if (lat_range * long_range) > max_cluster_size:
            print 'cluster %i is %.3f, removing' % (clust, lat_range * long_range)
            cluster_labels[cluster_labels == clust] = -1 # remove cluster

    return cluster_labels


def create_map(map_center, posts, cluster_labels, map_name='map'):

    col = ['#6E6E6E','#FF0202','#FF4A02','#FFB002','#FFF302','#A7FF02','#40FF00','#167139','#00FFDE','#00B3FF','#1456FC','#6072E8','#1C1CFD','#761CFD','#B453E9','#F300FF','#55541C','#463011','#284100']
    marker_col = [col[ic] for ic in cluster_labels]

    # Check if map file already exists
    if os.path.exists('%s/%s.html' % (config.paths['templates'], map_name)):
        # print 'removing file'
        os.remove('%s/%s.html' % (config.paths['templates'], map_name))

    map = folium.Map(location=map_center, zoom_start=12, width='100%', height=500, 
                    tiles ='MapBox', API_key='examples.map-i80bb8p3')


    # markers
    for ind, row in enumerate(posts.iterrows()):
        img = '<a href="'+row[1]['post_url']+'"><img src='+row[1]['image_url']+' height="250px" width="250px"></a>'

        if cluster_labels[ind] == -1:
            map.circle_marker([row[1]['lat'], row[1]['lng']],
                              radius=18,
                              line_color='#000000',
                              fill_color='#000000',
                              popup=img)
        else:
            map.circle_marker([row[1]['lat'], row[1]['lng']],
                              radius=18,
                              line_color=marker_col[ind],
                              fill_color=marker_col[ind],
                              popup=img) # str(cluster_labels[ind])


    map.create_map(path='%s/%s' % (config.paths['templates'], map_name))

    return col

def top_posts(posts, n_photos=8):

    photos = []
    top_posts = posts.sort('likes', ascending = False)[['image_url','lat','lng','post_url']].head(n_photos)
    photos.extend([{'posturl':row[1]['post_url'], 'loc':[row[1]['lat'],row[1]['lng']], 'url':row[1]['image_url']} for row in top_posts.iterrows()])
    return photos
