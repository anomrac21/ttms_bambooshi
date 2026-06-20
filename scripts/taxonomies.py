"""Infer menu taxonomies (tags, ingredients, cookingmethods, types, events)."""
from __future__ import annotations

import re
from typing import Iterable

SECTION_TYPES: dict[str, list[str]] = {
    "starters": ["Starter"],
    "sandwiches": ["Main", "Sandwich"],
    "heros": ["Main"],
    "burgers": ["Main", "Burger"],
    "mains": ["Main"],
    "tacos": ["Main", "Mexican"],
    "pasta": ["Main", "Pasta"],
    "salads": ["Starter", "Salad"],
    "plant-forward": ["Main", "Vegetarian"],
    "hero-cocktails": ["Beverage", "Cocktail"],
    "zero-proof": ["Beverage", "Mocktail"],
    "spirits": ["Beverage", "Spirit"],
    "beers": ["Beverage", "Beer"],
    "drinks": ["Beverage"],
    "shots": ["Beverage", "Shot"],
    "wines": ["Beverage", "Wine"],
    "cocktails": ["Beverage", "Cocktail"],
}

SECTION_TAGS: dict[str, list[str]] = {
    "starters": ["Appetizers"],
    "sandwiches": ["Sandwich"],
    "heros": ["Hero"],
    "burgers": ["Burger"],
    "mains": ["Main"],
    "tacos": ["Tacos"],
    "pasta": ["Pasta"],
    "salads": ["Salad"],
    "plant-forward": ["Plant-Forward", "Vegetarian"],
    "hero-cocktails": ["Cocktails"],
    "zero-proof": ["Mocktails"],
    "spirits": ["Spirits"],
    "beers": ["Beers"],
    "drinks": ["Drinks"],
    "shots": ["Shots"],
    "wines": ["Wine"],
    "cocktails": ["Cocktails"],
}

COOKING_PATTERNS: list[tuple[str, str]] = [
    (r"\b(slow-smoked|smoked)\b", "Smoked"),
    (r"\b(slow-cooked)\b", "Slow-Cooked"),
    (r"\b(marinated grilled|grilled)\b", "Grilled"),
    (r"\b(golden-fried|hand-breaded|deep-fried|crispy fried|fried|crispy)\b", "Fried"),
    (r"\b(saut[ée]ed|sauteed)\b", "Sautéed"),
    (r"\b(blackened)\b", "Blackened"),
    (r"\b(baked|roasted)\b", "Baked"),
    (r"\b(stir-fried)\b", "Stir-Fried"),
    (r"\b(shaken|shake)\b", "Shaken"),
    (r"\b(blended|blend|frozen)\b", "Blended"),
    (r"\b(muddled|muddle)\b", "Muddled"),
    (r"\b(tossed)\b", "Tossed"),
    (r"\b(boiled|steamed)\b", "Steamed"),
]

FOOD_INGREDIENTS = [
    "beef", "chicken", "pork", "bacon", "shrimp", "fish", "salmon", "tuna", "steak",
    "cheese", "mozzarella", "cheddar", "swiss", "parmesan", "cream cheese",
    "jalapeño", "jalapeno", "mushroom", "avocado", "tofu", "rice", "pasta",
    "lettuce", "tomato", "onion", "onions", "cabbage", "carrot", "cucumber", "edamame",
    "egg", "brioche", "tortilla", "guacamole", "coleslaw", "chimichurri",
    "potato", "cassava", "broccoli", "corn", "lime", "lemon", "mint", "basil",
    "rum", "vodka", "gin", "tequila", "whiskey", "whisky", "bourbon",
]

DRINK_SECTIONS = {
    "spirits", "beers", "drinks", "shots", "wines", "cocktails",
    "hero-cocktails", "zero-proof",
}

SKIP_INGREDIENT_TAGS = {
    "Spirits", "Beers", "Drinks", "Shots", "Wine", "Cocktails", "Mocktails",
    "Alcoholic", "Non-Alcoholic", "Appetizers", "Sandwich", "Burger", "Main",
    "Tacos", "Pasta", "Salad", "Plant-Forward", "Hero", "Signature", "Spicy",
    "Vegetarian", "Frozen", "Cold Drinks", "Soft & Juice", "Hot Beverages",
    "Coffee Cocktails", "Imported Draught", "Local Draught", "Local Bottles",
    "Beer Buckets", "Red Wine", "White Wine", "Port", "Champagne & Prosecco",
    "Gin", "Tequila", "Liqueurs", "Vodka", "Rum", "Scotch & Whiskey",
}


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        key = item.strip()
        if not key:
            continue
        norm = key.lower()
        if norm in seen:
            continue
        seen.add(norm)
        out.append(key)
    return out


def _title_case_phrase(text: str) -> str:
    text = text.strip(" .,-")
    if not text:
        return ""
    if text.isupper() and len(text) <= 4:
        return text
    return text[0].upper() + text[1:]


def parse_ingredient_list(body: str, section: str = "") -> list[str]:
    if section not in {"cocktails", "shots"}:
        return []
    if not body or len(body) > 120:
        return []
    text = body.strip().rstrip(".")
    if re.search(
        r"\b(served|finished|topped|tossed|with your|choose|ask|slow-|marinated|"
        r"crispy|golden|juicy|tender|fresh|house-|signature|lifted|shaken|muddled)\b",
        text,
        re.I,
    ):
        return []
    if not re.search(r"[,;&]", text):
        return []
    parts = re.split(r"\s*(?:,|&|\band\b)\s*", text, flags=re.I)
    cleaned = [_title_case_phrase(p) for p in parts if p.strip()]
    if any(len(p) > 35 for p in cleaned):
        return []
    return _unique(cleaned)


def extract_food_ingredients(title: str, body: str) -> list[str]:
    text = f"{title} {body}".lower()
    found = []
    for word in FOOD_INGREDIENTS:
        if re.search(rf"\b{re.escape(word)}\b", text):
            found.append(_title_case_phrase(word))
    return _unique(found)


def infer_cookingmethods(title: str, body: str) -> list[str]:
    text = f"{title} {body}".lower()
    methods = []
    for pattern, label in COOKING_PATTERNS:
        if re.search(pattern, text, re.I):
            methods.append(label)
    return _unique(methods)


def infer_extra_tags(section: str, title: str, body: str, tags: list[str]) -> list[str]:
    text = f"{title} {body}".lower()
    extras = []
    if section == "plant-forward" or re.search(r"\b(tofu|plant-forward|vegetarian)\b", text):
        extras.append("Vegetarian")
    if re.search(r"\b(spicy|scotch bonnet|jalape|pepper-kissed|scorpion)\b", text):
        extras.append("Spicy")
    if "Signature" in tags or re.search(r"\b(signature|hero)\b", text):
        extras.append("Signature")
    if section in {"cocktails", "hero-cocktails", "spirits", "beers", "wines", "shots"}:
        extras.append("Alcoholic")
    if section == "zero-proof":
        extras.append("Non-Alcoholic")
    if re.search(r"\b(frozen|blended)\b", text):
        extras.append("Frozen")
    return extras


def infer_ingredients(section: str, title: str, body: str, tags: list[str]) -> list[str]:
    listed = parse_ingredient_list(body, section)
    if listed:
        return listed
    if section in DRINK_SECTIONS:
        items = [title]
        for tag in tags:
            if tag not in SKIP_INGREDIENT_TAGS:
                items.append(tag)
        return _unique(items)
    return extract_food_ingredients(title, body)


def infer_taxonomies(
    section: str,
    title: str,
    body: str = "",
    tags: list[str] | None = None,
) -> dict[str, list[str]]:
    tags = list(tags or [])
    base_tags = SECTION_TAGS.get(section, [])
    extra_tags = infer_extra_tags(section, title, body, tags)
    merged_tags = _unique(base_tags + tags + extra_tags)

    return {
        "tags": merged_tags,
        "ingredients": infer_ingredients(section, title, body, merged_tags),
        "cookingmethods": infer_cookingmethods(title, body),
        "types": list(SECTION_TYPES.get(section, ["Main"])),
        "events": [],
    }


def yaml_list(key: str, items: list[str]) -> list[str]:
    if not items:
        return [f"{key}: []"]
    lines = [f"{key}:"]
    lines.extend(f"  - {item}" for item in items)
    return lines
