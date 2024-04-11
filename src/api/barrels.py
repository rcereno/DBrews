from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    """ """
    total_ml_val = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
    total_price_val = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()

    for barrel in barrels_delivered:
        amt_of_ml = barrel.ml_per_barrel * barrel.quantity
        total_ml_val = total_ml_val + amt_of_ml
        gold_price = barrel.quantity * barrel.price
        total_price_val = total_price_val + gold_price

        with db.engine.begin() as connection: 
            set_ml = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + {total_ml_val}"))
            set_gold = connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - {total_price_val}"))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """


    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

