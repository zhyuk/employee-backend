import uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, create_admin, get_db
from routers import login, employee, mypage

app = FastAPI()    

app.include_router(login.router)
app.include_router(employee.router)
app.include_router(mypage.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://employee-frontend-admin-git-main-zhyuks-projects.vercel.app", "https://employee-frontend-admin.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.on_event("startup")
def startup_event():
    create_tables()
    create_admin()

@app.get("/cron")
async def cron_check(db: Session = Depends(get_db)):
    """
    ----------------------------------------
    서버에 10분마다 호출하는 cron용 API
    ----------------------------------------
    """

    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)