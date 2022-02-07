import logging

from fastapi import FastAPI

from server.routes.user import router as UserRouter
from server.routes.authenticate import router as AuthenticationRouter

logger = logging.getLogger('api')
app = FastAPI()

app.include_router(UserRouter, tags=['User'], prefix='/user')
app.include_router(AuthenticationRouter, tags=['Authentication'])

@app.get('/')
def read_root():
    logger.debug('this is a debug log')
    return {
        'message': 'Hello!'
    }

