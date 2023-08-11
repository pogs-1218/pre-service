from fastapi import FastAPI, Path, Query, Body, Cookie, Header, Response, status, Form, File, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel, Field, FilePath
from enum import Enum
from typing import Union, Annotated, Any

class BaseUser(BaseModel):
  usernanme: str
  email: str
  full_name: str | None = None

class UserIn(BaseUser):
  password: str

class UserInDB(BaseUser):
  hashed_password: str

class UserOut(BaseUser):
  pass

class Image(BaseModel):
  url: FilePath 
  name: str

class Item(BaseModel):
  name: str = Field(
    examples=['Foo']
  )
  description: str | None = Field(
    default=None, title='The description of the item', max_length=300
  )
  price: float = Field(
    gt=0, description='The price must be greater then zero', examples=[35.4]
  )
  tax: float | None = Field(
    default=None, examples=[3.2]
  )
  tags: list[str] = []
  images: list[Image] | None = None

class Offer(BaseModel):
  name: str
  description: str | None = None
  price: float
  items: list[Item]

class User(BaseModel):
  username: str
  full_name: str | None = None

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

def fake_password_hasher(raw_password: str):
  return 'supersecret' + raw_password

def fake_save_user(user_in: UserIn):
  hashed_password = fake_password_hasher(user_in.password)
  user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
  return user_in_db

@app.post('/file/')
async def create_file(file: Annotated[bytes, File()]):
  return {'file_size': len(file)}

@app.post('/files/')
async def create_files(files: Annotated[list[UploadFile], File(description='files')]):
  return {'filename': [file.filename for file in files]}

@app.post('/uploadfile/')
async def create_upload_file(file: Annotated[UploadFile | None, File(description='A file read as UploadFile')]):
  if not file:
    return {'filename':'no file'}
  contents = await file.read()
  return {'filename': file.filename}

@app.post('/login/')
async def login(username: Annotated[str, Form()],
                password: Annotated[str, Form()]):
  return {'username':username}

@app.get('/portal', response_model=None)
async def get_portal(teleport: bool = False) -> Response | dict:
  if teleport:
    return RedirectResponse(url='https://www.google.com')
  return {'message':'json message'}

@app.post('/user/', status_code=201, response_model=UserOut)
async def create_user(user_in: UserIn):
  user_saved = fake_save_user(user_in)
  return user_saved

@app.post('/user2/')
async def create_user2(user: UserIn) -> UserOut:
  return user

@app.post('/offers/', status_code=status.HTTP_201_CREATED)
async def create_offer(offer: Offer):
  return offer

@app.post('/images/multiple/')
async def create_multiple_images(images: list[Image]):
  return images

@app.post('/index-weights/')
async def create_index_weights(weights: dict[int, float]):
  return weights

@app.get('/')
async def root():
  return {'message': 'Hello World'}

@app.get('/items/', response_model=list[Item])
async def read_items(
  q: Annotated[str | None, Query(title='Query String', description='Query string for the items to search in the database', min_length=3, max_length=5, deprecated=True,) ],
  user_agent: Annotated[str | None, Header()]= None,
  ads_id: Annotated[str | None, Cookie()] = None
) -> Any:
  results = {'items': 
             [
             {'item_id': 'foo'},
             {'item_id': 'bar'}
             ]}
  if q:
    results.update({'q': q})
  return results

@app.get('/items/{item_id}')
async def read_item(
  item_id: Annotated[int, Path(title = 'The ID of the item to get', gt=0, le=100)],
  size: Annotated[float, Query(ge=0, lt=10.5)],
  q: Annotated[str | None, Query(alias='item-query')] = None,
):
  return {'item_id':item_id, 'q': q}

@app.post('/items/{item_id}')
async def create_item(
  item_id: int, 
  item: Item, 
  q: str | None = None
) -> Item:
  item_dict = item.dict()
  if item.tax:
    price_with_tax = item.price + item.tax
    item_dict.update({'price_with_tax': price_with_tax})
  if q:
    item_dict.update({'q': q})
  return {'item_id': item_id, **item_dict}

@app.put('/items/{item_id}')
async def update_item(
  item_id: Annotated[int, Path()],
  user: Annotated[User, Body(title="user info")],
  importance: Annotated[int, Body()],
  q: str | None = None,
  item: Item | None = None
):
  results = {'item_id': item_id, 'user':user, 'importance':importance}
  if q:
    results.update({'q': q})
  if item:
    results.update({'item': item})
  return results

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
  if model_name.value == 'lenet':
    return {'model_name':model_name, 'message':'LeCNN all the images'}
  return {'model_name':model_name, 'message':'Have some residuals'}

@app.get('/files/{file_path:path}')
async def read_file(file_path: str):
  return {'file_path': file_path}
