"""Replay analysis for Kaggriculture.

Score is set mostly by the town shop draw rather than by farming
quality. These functions measure that from downloaded replays.
"""
import collections
import json

SHOP_PRODUCTS = {
    "BAKERY": ("EGG", "WHEAT"),
    "PIZZA_SHOP": ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT": ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}


def load(path):
    raw = json.load(open(path))
    return raw["steps"] if isinstance(raw, dict) and "steps" in raw else raw


def shop_demand(steps):
    """Total shop demand per product. Single-product shops count 2x."""
    last = steps[-1][0].get("observation") or {}
    shops = list((last.get("town") or {}).get("unlocked_shops") or [])
    demand = collections.Counter()
    for shop in shops:
        products = SHOP_PRODUCTS.get(shop, ())
        for product in products:
            demand[product] += 2 if len(products) == 1 else 1
    return demand


def final_prices(steps):
    last = steps[-1][0].get("observation") or {}
    return (last.get("market") or {}).get("prices") or {}


def sold_by_player(steps, player):
    """Units sold per product, read from the action stream."""
    sold = collections.Counter()
    for step in steps:
        action = (step[player] or {}).get("action") if player < len(step) else None
        if not isinstance(action, dict):
            continue
        for order in action.get("market") or []:
            if order and order[0] == "SELL" and len(order) > 2:
                sold[order[1]] += order[2]
    return sold