#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import yaml
from faker import Faker
from boto3 import client
from ratelimit import limits, sleep_and_retry
import random

# Leer configuración desde YAML
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Configuración de Faker para Argentina
fake = Faker('es_AR')

# Nombres de las provincias de Argentina
provincias_argentina = [
    'Buenos Aires', 'Catamarca', 'Chaco', 'Chubut',
    'Córdoba', 'Corrientes', 'Entre Ríos', 'Formosa',
    'Jujuy', 'La Pampa', 'La Rioja', 'Mendoza',
    'Misiones', 'Neuquén', 'Río Negro', 'Salta',
    'San Juan', 'San Luis', 'Santa Cruz', 'Santa Fe',
    'Santiago del Estero', 'Tierra del Fuego', 'Tucumán'
]

# Configuración del cliente S3 (MinIO)
s3 = client(
    's3',
    endpoint_url=config['s3']['endpoint_url'],
    aws_access_key_id=config['s3']['aws_access_key_id'],
    aws_secret_access_key=config['s3']['aws_secret_access_key'],
    region_name=config['s3']['region_name']
)

bucket_name = config['s3']['bucket_name']

# Límite de tasa
@sleep_and_retry
@limits(calls=config['rate']['per_second'], period=1)
def generate_and_save_data():
    try:
        customer_id = fake.uuid4()
        first_name = fake.first_name()
        last_name = fake.last_name()
        address = fake.address()
        city = fake.city()
        state = random.choice(provincias_argentina)  # Usar lista estática para las provincias
        country = "Argentina"
        phone_number = fake.phone_number()
        cell_phone = fake.phone_number()
        email = fake.email()
        dni = fake.random_int(min=10000000, max=99999999)
        job = fake.job()

        customer_data = {
            "id_cliente": customer_id,
            "nombre": first_name,
            "apellido": last_name,
            "direccion": address,
            "localidad": city,
            "provincia": state,
            "pais": country,
            "telefono_fijo": phone_number,
            "telefono_movil": cell_phone,
            "email": email,
            "dni": dni,
            "profesion": job
        }

        folder_structure = f"{country}/{state}/{city}"
        file_name = f"{customer_id}.json"
        s3_path = f"{folder_structure}/{file_name}"

        s3.put_object(
            Body=json.dumps(customer_data),
            Bucket=bucket_name,
            Key=s3_path
        )

        print(f"Datos del cliente {customer_id} guardados en S3.")
    except Exception as e:
        print(f"Error: {e}. Reintentando...")
        time.sleep(1)
        generate_and_save_data()

if __name__ == "__main__":
    rate_per_second = config['rate']['per_second']
    sleep_time = 1 / rate_per_second  # Calcula el tiempo de espera entre ejecuciones para cumplir con el límite de tasa.

    while True:  # Bucle infinito
        generate_and_save_data()
        time.sleep(sleep_time)  # Espera el tiempo necesario para cumplir con el límite de tasa.
