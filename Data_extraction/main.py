import os
import requests
from fastapi import FastAPI, Form
from typing import Optional
from pydantic import BaseModel
import gzip
import shutil
import psycopg2.extras
import configparser

app = FastAPI()

class Link(BaseModel):
    url: str
    name: str
    
config = configparser.ConfigParser()
config.read('config')
connection = psycopg2.connect(
    host=config['config']['host'],
    database=config['config']['clickstream'],
    user=config['config']['user'],
    password=config['config']['password'],
)
connection.autocommit = True

@app.get("/")
async def get():
    return {'response': 'This is click stream API'}

@app.get("/click_from_title/{title}/{count}")
def get_most_end_link(title: str, count: int):
    cursor = connection.cursor()
    sql_query = "SELECT TOP(%(count)d) End FROM click_count ORDER BY Count DESC WHERE Start=%(title)s"
    try:
        cursor.execute(sql_query, {count: count, title: title})
        result = cursor.fetchall()
        return {"most_end": result}
    except Exception as e:
        cursor.close()
        return {"most_end": e}
    
@app.get("/click_to_title/{title}/{count}")
def get_most_start_link(title: str, count: int):
    cursor = connection.cursor()
    sql_query = "SELECT TOP(%(count)d) Start FROM click_count ORDER BY Count DESC WHERE End=%(title)s"
    try:
        cursor.execute(sql_query, {count: count, title: title})
        result = cursor.fetchall()
        return {"most_start": result}
    except Exception as e:
        cursor.close()
        return {"most_start": e}
    
@app.get("/click_to_title_internal/{title}/{count}")
def get_most_start_link(title: str, count: int):
    cursor = connection.cursor()
    sql_query = "SELECT TOP(%(count)d) Start FROM click_count ORDER BY Count DESC WHERE End=%(title)s AND TYPE=link"
    try:
        cursor.execute(sql_query, {count: count, title: title})
        result = cursor.fetchall()
        return {"most_start": result}
    except Exception as e:
        cursor.close()
        return {"most_start": e}
    
@app.get("/click_to_title_internal/{title}/{count}")
def get_most_start_link(title: str, count: int):
    cursor = connection.cursor()
    sql_query = "SELECT TOP(%(count)d) End FROM click_count ORDER BY Count DESC WHERE Start=%(title)s AND TYPE=link"
    try:
        cursor.execute(sql_query, {count: count, title: title})
        result = cursor.fetchall()
        return {"most_end": result}
    except Exception as e:
        cursor.close()
        return {"most_end": e}


@app.post("/load_data")
async def load_data_from_web(link: Link):
    try:
        resp = requests.get(link.url)
        with open(link.name, "wb") as f:
            f.write(resp.content)
        cursor = connection.cursor()
        zip_name = link.name + '.tsv.gz'
        with gzip.open(zip_name, 'rb') as f_in:
            with open(link.name, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        f = open(link.name)
        await cursor.copy_from(f, 'click_count', sep = '\t')
        return {'result': 'Successfully extract file'}
    except Exception as e:
        cursor.close()
        return {'result': e}