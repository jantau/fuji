# -*- coding: utf-8 -*-
from fuji_server.helper.catalogue_helper_google_datasearch import MetaDataCatalogueGoogleDataSearch

g = MetaDataCatalogueGoogleDataSearch()

# Step 1 visit: https://www.kaggle.com/googleai/dataset-search-metadata-for-datasets
# Step 2 download the latest Dataset Search corpus file
# Step 3 indicate the location of the file below
google_file_location = '/Users/jan/Documents/R-Projekte/fuji/dataset_metadata_2020_10_16.csv'
# google_file_location = 'C:\\Users\\Robert\\Documents\\dataset_metadata_2020_10_16.csv'

# Step 4 run the script
if google_file_location is not None:
    print('Starting to create Google Dataset Search DB')
    g.create_cache_db(google_file_location)
    print('Finished...')
else:
    print('No google_file_location provided, FUJI is not properly installed.')
