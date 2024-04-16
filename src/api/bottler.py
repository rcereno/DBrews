from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

# have enough ml then make

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    for potion in potions_delivered:
        res_green_ml = res_green_ml - (100*potion.quantity)
        res_green_potions = res_green_potions + potion.quantity
        res_red_ml = res_red_ml - (100*potion.quantity)
        res_red_potions = res_red_potions + potion.quantity
        res_blue_ml = res_blue_ml - (100*potion.quantity)
        res_blue_potions = res_blue_potions + potion.quantity

    with db.engine.begin() as connection: 
        amt_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        amt_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar()
        total_green_ml = amt_green_ml - res_green_ml
        total_green_potions = amt_green_potions + res_green_potions
        update_green_ml = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = {total_green_ml}"))
        update_green_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = {total_green_potions}"))

        amt_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        amt_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar()
        total_red_ml = amt_red_ml - res_red_ml
        total_red_potions = amt_red_potions + res_red_potions
        update_red_ml = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = {total_red_ml}"))
        update_red_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = {total_red_potions}"))

        amt_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        amt_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar()
        total_blue_ml = amt_blue_ml - res_blue_ml
        total_blue_potions = amt_blue_potions + res_blue_potions
        update_blue_ml = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = {total_blue_ml}"))
        update_blue_potions = connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = {total_blue_potions}"))

    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into red potions.
    bottler_plan = []
    with db.engine.begin() as connection: 
        amt_green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar()
        if(amt_green_ml >= 100):
            bottler_plan.append(
            {
                "potion_type": [0, 100, 0, 0],
                # "quantity": 5,
                "quantity": amt_green_ml // 100
            })

        amt_red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar()
        if(amt_red_ml >= 100):
            bottler_plan.append(
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": amt_red_ml // 100
            })

        amt_blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar()
        if(amt_blue_ml >= 100):
            bottler_plan.append(
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": amt_blue_ml // 100
            })
    
    return bottler_plan

if __name__ == "__main__":
    print(get_bottle_plan())