from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn

from matcher import match_items
from compare import compare_prices
from scraper import scrape_all_stores

app = FastAPI()

class ShoppingItem(BaseModel):
    name: str
    quantity: float = 1.0

class ShoppingList(BaseModel):
    items: List[ShoppingItem]
    allow_substitutions: Optional[bool] = True
    include_tags: Optional[List[str]] = []
    exclude_brands: Optional[List[str]] = []

@app.post("/compare")
async def compare_groceries(list: ShoppingList):
    raw_data = scrape_all_stores(
        [item.name for item in list.items],
        tags=list.include_tags,
        exclude_brands=list.exclude_brands
    )
    matched_data = match_items(list.items, raw_data, allow_subs=list.allow_substitutions)
    comparison = compare_prices(matched_data)
    return comparison

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)