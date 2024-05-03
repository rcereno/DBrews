from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db
from sqlalchemy.exc import IntegrityError

''' simple logic that doesn't look at potions

buy whatever barrel you have the least amount of ml for - write that logic
buy small barrel and itll start with the one you have the least of 

you will query your current ml (see what you have the least of and then buy one barrel of that)

do that - test it
make sure deliver works

do local testing of plan and deliver
'''

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

    print(barrels_delivered)

    with db.engine.begin() as connection:
        try:
            connection.execute(
                sqlalchemy.text(
                    "INSERT INTO processed (job_id, type) VALUES (:order_id, 'barrels')"),
                [{"order_id": order_id}]
            )
        except IntegrityError as e:
            return "OK" 
        
        gold_paid = 0
        red_ml = 0
        blue_ml = 0
        green_ml = 0
        dark_ml = 0

        for barrel_delivered in barrels_delivered:
            gold_paid += barrel_delivered.price * barrel_delivered.quantity
            if barrel_delivered.potion_type == [1,0,0,0]: 
                red_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
            elif barrel_delivered.potion_type == [0,1,0,0]:
                green_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
            elif barrel_delivered.potion_type == [0,0,1,0]:
                blue_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
            elif barrel_delivered.potion_type == [0,0,0,1]:
                dark_ml += barrel_delivered.ml_per_barrel * barrel_delivered.quantity
            else:
                raise Exception("Invalid potion type")
            
        connection.execute(
            sqlalchemy.text(
                "UPDATE global_inventory SET num_red_ml = :red_ml, num_green_ml = :green_ml, num_blue_ml = :blue_ml, num_dark_ml = :dark_ml, gold = gold + :gold_paid"
                ),
            [
                {"red_ml": red_ml, 
                 "green_ml": green_ml, 
                 "blue_ml": blue_ml, 
                 "dark_ml": dark_ml, 
                 "gold_paid": gold_paid 
                }
            ]
        )
    return "OK"

    # with db.engine.begin() as connection:
    #     total_green_ml_val = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory")).scalar_one()
    #     total_green_price_val = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
    #     total_gold = connection.execute(sqlalchemy.text("SELECT gold FROM global_inventory")).scalar_one()

    #     total_red_ml_val = connection.execute(sqlalchemy.text("SELECT num_red_ml FROM global_inventory")).scalar_one()
    #     total_red_price_val = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()

    #     total_blue_ml_val = connection.execute(sqlalchemy.text("SELECT num_blue_ml FROM global_inventory")).scalar_one()
    #     total_blue_price_val = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()

    # for barrel in barrels_delivered:
    #     if barrel.price <= total_gold:
    #         if barrel.sku == "SMALL_GREEN_BARREL":
    #             amt_of_green_ml = barrel.ml_per_barrel * barrel.quantity
    #             total_green_ml_val = total_green_ml_val + amt_of_green_ml
    #             gold_price = barrel.quantity * barrel.price
    #             total_green_price_val = total_green_price_val - gold_price

    #             with db.engine.begin() as connection: 
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {total_green_ml_val}"))
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_green_price_val}"))

    #         if barrel.sku == "SMALL_RED_BARREL":
    #             amt_of_red_ml = barrel.ml_per_barrel * barrel.quantity
    #             total_red_ml_val = total_red_ml_val + amt_of_red_ml
    #             gold_price = barrel.quantity * barrel.price
    #             total_red_price_val = total_red_price_val - gold_price

    #             with db.engine.begin() as connection: 
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_red_ml = num_red_ml + {total_red_ml_val}"))
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_red_price_val}"))

    #         if barrel.sku == "SMALL_BLUE_BARREL":
    #             amt_of_blue_ml = barrel.ml_per_barrel * barrel.quantity
    #             total_blue_ml_val = total_blue_ml_val + amt_of_blue_ml
    #             gold_price = barrel.quantity * barrel.price
    #             total_blue_price_val = total_blue_price_val - gold_price

    #             with db.engine.begin() as connection: 
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_blue_ml = num_blue_ml + {total_blue_ml_val}"))
    #                 connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_blue_price_val}"))

    #     # with db.engine.begin() as connection: 
    #     #     set_ml = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET num_green_ml = num_green_ml + {total_green_ml_val}"))
    #     #     set_gold = connection.execute(sqlalchemy.text(f"UPDATE global_inventory SET gold = gold - {total_green_price_val}"))

    # print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    # return "OK"

# Gets called once a day
# work on first
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
        amt_green_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory where potion_id=2")).scalar_one()
        amt_red_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=1")).scalar_one()
        amt_blue_potions = connection.execute(sqlalchemy.text("SELECT quantity FROM potion_inventory WHERE potion_id=3")).scalar_one()
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

