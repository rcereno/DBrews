from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

# CAPACITY IS HERE SO ADJUST CAPACITY

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ find total num potions total num ml and return those two quants and gold"""
    with db.engine.begin() as connection:
        amt_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        amt_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        amt_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()

        amt_green_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=2")).scalar_one()
        amt_red_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE Potion_id=1")).scalar_one()
        amt_blue_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=3")).scalar_one()

        amt_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

    print(f"number of potions: {amt_green_potions + amt_blue_potions + amt_red_potions}")
    return {"number_of_potions": amt_green_potions + amt_blue_potions + amt_red_potions, "ml_in_barrels": amt_green_ml + amt_red_ml + amt_blue_ml, "gold": amt_gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    THIS IS WHERE YOU CHANGE THE CAPACITY 
    """

    with db.engine.begin() as connection:
        amt_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        amt_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        amt_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()

        amt_green_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=2")).scalar_one()
        amt_red_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE Potion_id=1")).scalar_one()
        amt_blue_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=3")).scalar_one()

        amt_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

        

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
