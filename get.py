#!/usr/bin/env python3
# ~~ coding: utf-8 ~~

from flask import Flask, render_template, jsonify
import boto3
import random
import json
import yaml

app = Flask(__name__)

# Leer configuración desde YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Configuración del cliente S3 (MinIO)
s3 = boto3.client(
    's3',
    endpoint_url=config['s3']['endpoint_url'],
    aws_access_key_id=config['s3']['aws_access_key_id'],
    aws_secret_access_key=config['s3']['aws_secret_access_key'],
    region_name=config['s3']['region_name']
)

bucket_name = config['s3']['bucket_name']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_data')
def get_data():
    # Obtener la lista de todos los archivos en el bucket
    objects = s3.list_objects(Bucket=bucket_name)
    all_files = [content['Key'] for content in objects['Contents']]

    # Seleccionar aleatoriamente 32 archivos
    random_files = random.sample(all_files, 32)

    data = []
    for file in random_files:
        # Leer cada archivo
        obj = s3.get_object(Bucket=bucket_name, Key=file)
        content = obj['Body'].read().decode('utf-8')
        data.append(json.loads(content))

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=32500, threaded=True)
