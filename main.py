import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, create_admin
from routers import login, employee, mypage

app = FastAPI()    

app.include_router(login.router)
app.include_router(employee.router)
app.include_router(mypage.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://employee-frontend-admin.vercel.app","http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup_event():
    create_tables()
    create_admin()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)