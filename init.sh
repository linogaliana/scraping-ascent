pip install -r requirements.txt
mc cp s3/lgaliana/cyclisme/liste.parquet data/liste.parquet
mc cp s3/lgaliana/cyclisme/data/raw/gpx . --recursive
mc cp s3/lgaliana/cyclisme/data/geojson/alpes-nord.geojson data/routes.geojson

# apres nb
mc cp data/derived/ s3/lgaliana/cyclisme/data/geojson/split/ --recursive
mc cp images/ s3/lgaliana/cyclisme/data/images --recursive
mc anonymous set download s3/lgaliana/cyclisme/data/images
mc anonymous set download s3/lgaliana/cyclisme/data/geojson/split/

# apres retrieve.py
# mc cp liste-r6.parquet s3/lgaliana/cyclisme/liste-r6.parquet
# mc cp autres-massifs.geojson s3/lgaliana/cyclisme/data/geojson/autres-massifs.geojson
# cp data/derived data/split -r
# mc cp data/split s3/lgaliana/cyclisme/data/geojson/ --recursive
# mc cp images/ s3/lgaliana/cyclisme/data/images --recursive