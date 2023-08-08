from fastapi import FastAPI
from enum import Enum
from typing import Union

class ModelName(str, Enum):
  alexnet = 'alexnet'
  resnet = 'resnet'
  lenet = 'lenet'

app = FastAPI()
fake_items_db = [
  {'item_name':'Foo'},
  {'item_name':'Bar'},
  {'item_name':'Bax'}
]

@app.get('/')
async def root():
  return {'message': 'Hello World'}

@app.get('/items/')
async def read_item_q(skip: int = 0, limit: int = 10):
  return fake_items_db[skip:skip+limit]

@app.get('/items/{item_id}')
async def read_item(item_id: int, q: Union[str, None] = None):
  return {'item_id':item_id, 'q': q}

@app.get('/users/{user_id}/items/{item_id}')
async def read_user_item(user_id: int, item_id: int, q: Union[str, None] = None, short: bool = False):
  item = {'item_id':item_id, 'owner_id':user_id}
  if q:
    item.update({'q':q})
  if not short:
    item.update(
      {'description': 'This is an amazing item'}
    )
  return item
  
@app.get('/users/me')
async def read_user_me():
  return {'user_id':'the current user'}

@app.get('/users/{user_id}')
async def read_user(user_id: str):
  return {'user_id': user_id}

@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
  if model_name == ModelName.alexnet:
    return {'model_name':model_name, 'message':'Deep Learning FTW'}
  if model_name.value is 'lenet':
    return {'model_name':model_name, 'message':'LeCNN all the images'}
  return {'model_name':model_name, 'message':'Have some residuals'}

@app.get('/files/{file_path:path}')
async def read_file(file_path: str):
  return {'file_path': file_path}
