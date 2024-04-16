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
    with db.engine.begin() as connection:
        total_green_ml_val = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
        total_green_price_val = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        total_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

        total_red_ml_val = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
        total_red_price_val = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()

        total_blue_ml_val = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
        total_blue_price_val = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()

    for barrel in barrels_delivered:
        if barrel.price <= total_gold:
            if barrel.sku == "SMALL_GREEN_BARREL":
                amt_of_green_ml = barrel.ml_per_barrel * barrel.quantity
                total_green_ml_val = total_green_ml_val + amt_of_green_ml
                gold_price = barrel.quantity * barrel.price
                total_green_price_val = total_green_price_val - gold_price

                with db.engine.begin() as connection: 
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {total_green_ml_val}"))
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_green_price_val}"))

            if barrel.sku == "SMALL_RED_BARREL":
                amt_of_red_ml = barrel.ml_per_barrel * barrel.quantity
                total_red_ml_val = total_red_ml_val + amt_of_red_ml
                gold_price = barrel.quantity * barrel.price
                total_red_price_val = total_red_price_val - gold_price

                with db.engine.begin() as connection: 
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = num_red_ml + {total_red_ml_val}"))
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_red_price_val}"))

            if barrel.sku == "SMALL_BLUE_BARREL":
                amt_of_blue_ml = barrel.ml_per_barrel * barrel.quantity
                total_blue_ml_val = total_blue_ml_val + amt_of_blue_ml
                gold_price = barrel.quantity * barrel.price
                total_blue_price_val = total_blue_price_val - gold_price

                with db.engine.begin() as connection: 
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = num_blue_ml + {total_blue_ml_val}"))
                    connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_blue_price_val}"))

        # with db.engine.begin() as connection: 
        #     set_ml = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {total_green_ml_val}"))
        #     set_gold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_green_price_val}"))

    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """
    - select how many green potions 
    - select gold 
    - check how much gold green barrel costs // check how much gold abt to spend
    - check all conditions to see if u want to buy green barrel (if num_green_potions < 10 and have enough gold)"""
# if barrel is less than gold 

    print(wholesale_catalog)

    wholesale_purchase_list = []

    with db.engine.begin() as connection: 
        amt_green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        amt_red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        amt_blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
        amt_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

    for barrel in wholesale_catalog:
        if barrel.sku == "SMALL_GREEN_BARREL":
            if ((amt_green_potions < 10) and (barrel.price <= amt_gold)):
                amt_gold -= barrel.price
                wholesale_purchase_list.append({"sku": barrel.sku,"quantity": 1,})
                # return [
                    # {
                    #     "sku": barrel.sku,
                    #     "quantity": 1,
                    # }
                # ]
        if barrel.sku == "SMALL_RED_BARREL":
            if ((amt_red_potions < 10) and (barrel.price <= amt_gold)):
                amt_gold -= barrel.price
                wholesale_purchase_list.append({"sku": barrel.sku,"quantity": 1,})
                # return [
                #     {
                #         "sku": barrel.sku,
                #         "quantity": 1,
                #     }
                # ]
        if barrel.sku == "SMALL_BLUE_BARREL":
            if ((amt_blue_potions < 10) and (barrel.price <= amt_gold)):
                amt_gold -= barrel.price
                wholesale_purchase_list.append({"sku": barrel.sku,"quantity": 1,})
                # return [
                #     {
                #         "sku": barrel.sku,
                #         "quantity": 1,
                #     }
                # ]
    return wholesale_purchase_list

