import time
from typing import Annotated, Any
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
   'http://localhost.ghpi.com',
   'https://localhost.ghpi.com',
   'http://localhost',
   'http://localhost:8080',
]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=['*'],
                   allow_headers=['*'])


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

class CommonQueryParams:
    def __init__(self, 
                 q: str | None = None, 
                 skip: int = 0, 
                 limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key

async def common_parameters(q: str | None = None,
                            skip: int = 0,
                            limit: int = 100):
    return {'q': q, 'skip': skip, 'limit': limit}

class DBSession:
  def close():
    pass

async def get_db():
  db = DBSession()
  try:
    yield db
  finally:
    db.close()  # executed after the response has been delivered

  
# Global dependencies
# app_with_dep = FastAPI(dependencies=[Depends(verify_key), Depends(verify_token)])
CommonsDep = Annotated[dict, Depends(common_parameters)]

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
   start_time = time.time()
   response = await call_next(request)
   process_time = time.time() - start_time
   response.headers['X-Process-Time'] = str(process_time)
   return response
  
@app.get('/')
async def main():
   return {'message': 'hello world'}

@app.get('/items/', dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items(commons: Annotated[CommonQueryParams, Depends()]):
  response = {}
  if commons.q:
    response.update({'q': commons.q})
  items = fake_items_db[commons.skip : commons.skip + commons.limit]
  response.update({'item':items})
  return response

@app.get('/users/')
async def read_users(commons: Annotated[Any, Depends(CommonQueryParams)]):
    return commons