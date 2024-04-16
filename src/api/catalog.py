from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """

    catalog = []
    with db.engine.begin() as connection:
        green_quantity = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory")).scalar_one()
        red_quantity = connection.execute(sqlalchemy.text("SELECT num_red_potions FROM global_inventory")).scalar_one()
        blue_quantity = connection.execute(sqlalchemy.text("SELECT num_blue_potions FROM global_inventory")).scalar_one()
        # scalar_one: changes it from the object to a number 
        # do same process with other colors 
        if green_quantity > 0:
            catalog.append(
                {
                    "sku": "GREEN_POTION_0",
                    "name": "green potion",
                    "quantity": green_quantity,
                    "price": 50,
                    "potion_type": [0, 100, 0, 0],
                })
        
        if red_quantity > 0:
            catalog.append(
                {
                    "sku": "RED_POTION_0",
                    "name": "red potion",
                    "quantity": red_quantity,
                    "price": 50,
                    "potion_type": [100, 0, 0, 0],
                })
            
        if blue_quantity > 0:
            catalog.append(
                {
                    "sku": "BLUE_POTION_0",
                    "name": "blue potion",
                    "quantity": blue_quantity,
                    "price": 50,
                    "potion_type": [0, 0, 100, 0],
                })
            
    return catalog        
