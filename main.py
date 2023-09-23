from src.application import app 
from src.connect import db
import uvicorn
import asyncio

if __name__ == '__main__':
    asyncio.run(db.create_all())
    uvicorn.run('main:app', host='0.0.0.0', port=5000, reload=True)