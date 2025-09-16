from fastapi import FastAPI
from app.account import models as account_models
# from app.buy import models as buy_models
# from app.sell import models as sell_models
from app.database import engine, Base
from app.account.router import router as account_router
# from app.buy.router import router as buy_router
# from app.sell.router import router as sell_router

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketplace API")

# Register routers
app.include_router(account_router, prefix="/account", tags=["Account"])
# app.include_router(buy_router, prefix="/buy", tags=["Buy"])
# app.include_router(sell_router, prefix="/sell", tags=["Sell"])