#!/usr/bin/env python3
"""Rebuild ttms_islandbeer content from C&G Menu 12 PDF only."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

from taxonomies import infer_taxonomies, yaml_list

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"

# Sections that exist on the PDF — everything else is removed.
PDF_SECTIONS = {
    "starters", "sandwiches", "heros", "burgers", "mains",
    "tacos", "pasta", "salads", "plant-forward",
    "hero-cocktails", "zero-proof",
    "spirits", "beers", "drinks", "shots", "wines", "cocktails",
}


def slug(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    return s.strip("_")


def write_item(section, filename, title, weight, prices, body="", tags=None,
               ingredients=None, cookingmethods=None, types=None, events=None):
    tags = tags or []
    meta = infer_taxonomies(section, title, body, tags)
    if ingredients is not None:
        meta["ingredients"] = ingredients
    if cookingmethods is not None:
        meta["cookingmethods"] = cookingmethods
    if types is not None:
        meta["types"] = types
    if events is not None:
        meta["events"] = events

    lines = ["---", f"title: {title}", f"weight: {weight}", "",
             "additions: []", "modifications: []", "side_categories: []", "prices:"]
    for p in prices:
        lines += [f"  - variable1: \"{p['v1']}\"", f"    price: {p['price']}", f"    variable2: \"{p.get('v2', '-')}\""]
    lines.extend(yaml_list("tags", meta["tags"]))
    lines.extend(yaml_list("ingredients", meta["ingredients"]))
    lines.extend(yaml_list("cookingmethods", meta["cookingmethods"]))
    lines.extend(yaml_list("types", meta["types"]))
    lines.extend(yaml_list("events", meta["events"]))
    lines.append("---")
    if body:
        lines += ["", body]
    path = CONTENT / section / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_index(section, title, weight, icon, image_top=None, body=""):
    d = CONTENT / section
    d.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"title: {title}", f"weight: {weight}", f"icon: {icon}"]
    if image_top:
        lines += ["images:", f"  top: {image_top}"]
    lines.append("---")
    text = "\n".join(lines)
    if body:
        text += f"\n\n{body}\n"
    else:
        text += "\n"
    (CONTENT / section / "_index.md").write_text(text, encoding="utf-8")


def clear_section(section):
    d = CONTENT / section
    if d.exists():
        shutil.rmtree(d)


def single(p):
    return [{"v1": "-", "price": p}]


def glass_bottle(g, b):
    return [{"v1": "Glass", "price": g}, {"v1": "Bottle", "price": b}]


def imported_draught(a, b, c):
    return [{"v1": "1/2 Pint", "price": a}, {"v1": "Taster", "price": b}, {"v1": "Pint", "price": c}]


def local_draught(m, p, t):
    return [{"v1": "Mug", "price": m}, {"v1": "Pitcher", "price": p}, {"v1": "Tower", "price": t}]


def remove_non_pdf_sections():
    for d in CONTENT.iterdir():
        if not d.is_dir():
            continue
        if d.name not in PDF_SECTIONS:
            shutil.rmtree(d)
            print(f"Removed section: {d.name}")


def sync_food():
    write_index("starters", "Starters & Shareables", 4,
                "https://ct.ttmenus.com/icons/food/icon-wing.webp",
                image_top="images/food1.webp")
    starters = [
        ("Crunch Time Tenders", 89, "Crispy hand-breaded chicken tenders served with honey mustard or garlic sauce."),
        ("Jalapeño Poppers", 85, "Golden-fried jalapeño bites with cheddar cheese filling, served with honey mustard."),
        ("Signature Smoked Wings", 119, "Slow-smoked wings finished to order, served with celery, carrots and your choice of house sauce.", True),
        ("Mozzarella Sticks", 65, "Crispy mozzarella sticks served with marinara sauce."),
        ("Maracas Fried Shrimp", 99, "Coconut-crusted shrimp served with tamarind dipping sauce."),
        ("Red Card Fries", 40, "Fries tossed with scotch bonnet pepper and house seasoning."),
    ]
    for i, row in enumerate(starters, 1):
        name, price, body = row[0], row[1], row[2]
        tags = ["Appetizers", "Signature"] if len(row) > 3 else ["Appetizers"]
        extras = {}
        if name == "Signature Smoked Wings":
            write_item("starters", f"{slug(name)}.md", name, i, single(price), body, tags)
            path = CONTENT / "starters" / f"{slug(name)}.md"
            text = path.read_text(encoding="utf-8")
            text = text.replace("additions: []", "additions:\n  - name: Wrap it in bacon\n    price: 20")
            path.write_text(text, encoding="utf-8")
        else:
            write_item("starters", f"{slug(name)}.md", name, i, single(price), body, tags)

    write_index("sandwiches", "Sandwiches", 5,
                "https://ct.ttmenus.com/icons/food/icon-sandwich.webp",
                image_top="images/food3.webp",
                body="### Served with Potato Medley Crisps")
    sandwiches = [
        ("House Steak Sandwich", 149, "Marinated grilled steak, Swiss cheese, caramelized onions and house-made aioli, served with cowboy butter.", True),
        ("Bacon Pulled Pork Sandwich", 99, "Slow-cooked BBQ pulled pork, crispy bacon and creamy coleslaw."),
        ("Fish n' Chill Sandwich", 99, "Crispy fried fish with coleslaw, tartar sauce and grilled onions."),
        ("New Orleans Chicken Sandwich", 99, "Crispy fried chicken, pickles, Cajun sauce, coleslaw and drizzled with Hot Honey."),
    ]
    for i, row in enumerate(sandwiches, 1):
        name, price, body = row[0], row[1], row[2]
        tags = ["Sandwich", "Signature"] if len(row) > 3 else ["Sandwich"]
        write_item("sandwiches", f"{slug(name)}.md", name, i, single(price), body, tags)
    p = CONTENT / "sandwiches" / "new_orleans_chicken_sandwich.md"
    t = p.read_text(encoding="utf-8").replace("modifications: []",
        "modifications:\n  - name: Make it Scorpion\n    price: 5")
    p.write_text(t, encoding="utf-8")

    write_index("heros", "The Heros", 6,
                "https://ct.ttmenus.com/icons/food/icon-burger.webp",
                image_top="images/food2.webp",
                body="### Our most loved dishes")
    heros = [
        ("Loaded Smash Burger", 135, "Double-smashed beef patties, crispy bacon, sautéed mushrooms, American cheddar, fried egg and house sauce on a toasted brioche bun."),
        ("Signature Beef Sliders (3)", 99, "Juicy beef patties topped with American cheddar, pickles, cowboy mayo, served on soft brioche sliders."),
        ("Cassava Fries", 42, "Crispy cassava fries, lightly seasoned and served with roasted garlic aioli."),
        ("Extra Time Cheese", 69, "Crispy fries or tortilla nachos served with warm cheese fondue and fresh pico de gallo for dipping."),
    ]
    for i, (n, p, b) in enumerate(heros, 1):
        write_item("heros", f"{slug(n)}.md", n, i, single(p) if n != "Extra Time Cheese" else [
            {"v1": "Fries", "price": 69}, {"v1": "Nachos", "price": 69}
        ], b, ["Hero"])
    p = CONTENT / "heros" / "extra_time_cheese.md"
    t = p.read_text(encoding="utf-8").replace("additions: []",
        "additions:\n  - name: Chicken\n    price: 20\n  - name: Chili\n    price: 25\n  - name: Bacon\n    price: 15\n  - name: Go All In\n    price: 50")
    p.write_text(t, encoding="utf-8")

    write_index("burgers", "Gourmet Burgers", 7,
                "https://ct.ttmenus.com/icons/food/icon-burger.webp",
                image_top="images/food2.webp",
                body="### Served with Potato Medley Crisps")
    burgers = [
        ("Big Man Burger", 169, "Three smashed beef patties, crispy fried chicken, bacon, double cheese and special house sauce.", True),
        ("Bypass Burger", 159, "8oz beef patty, cheddar, fried cheese pillow, grilled jalapeños and crispy onions."),
        ("CnG Classic Burger", 154, "8oz beef patty topped with Swiss cheese, bacon and caramelized onions."),
        ("Devil May Cry Burger", 159, "8oz beef patty with fried jalapeños, Swiss cheese, chimichurri and Scotch bonnet aioli."),
    ]
    for i, row in enumerate(burgers, 1):
        name, price, body = row[0], row[1], row[2]
        tags = ["Burger", "Signature"] if len(row) > 3 else ["Burger"]
        write_item("burgers", f"{slug(name)}.md", name, i, single(price), body, tags)

    write_index("mains", "Mains", 8, "https://ct.ttmenus.com/icons/food/icon-trailblazers.webp",
                image_top="images/food9.webp")
    mains = [
        ("BBQ Chicken", 139, "Grilled BBQ boneless breast served with mashed potatoes and garlic vegetables."),
        ("Grilled Pork Loin", 140, "Tender pork loin with smashed potatoes, roasted vegetables and creamy mushroom sauce."),
        ("Cowboy Butter Striploin (8oz)", 259, "Grilled striploin served with Parmesan-crusted potatoes and broccoli, finished with chimichurri and cowboy butter.", True),
        ("Smoked BBQ Ribs", None, "Slow-cooked BBQ ribs served with herb-roasted potatoes and vegetables."),
        ("Fresh Catch of the Day", 169, "Ask your server about today's fresh fish selection."),
        ("Teriyaki Chicken Poke Bowl", 129, "Rice bowl with teriyaki chicken, pickled red onions, shredded carrots, marinated cucumbers, cabbage, edamame and spicy mayo."),
    ]
    for i, row in enumerate(mains, 1):
        name, price, body = row[0], row[1], row[2]
        if name == "Smoked BBQ Ribs":
            write_item("mains", "smoked_bbq_ribs.md", name, i,
                       [{"v1": "Half Rack", "price": 199}, {"v1": "Full Rack", "price": 399}], body, ["Main"])
        else:
            tags = ["Main", "Signature"] if len(row) > 3 else ["Main"]
            write_item("mains", f"{slug(name)}.md", name, i, single(price), body, tags)
    p = CONTENT / "mains" / "cowboy_butter_striploin_8oz.md"
    if p.exists():
        t = p.read_text(encoding="utf-8").replace("additions: []",
            "additions:\n  - name: Upgrade to 10 oz Ribeye\n    price: 99")
        p.write_text(t, encoding="utf-8")

    write_index("tacos", "Street Tacos", 9, "https://ct.ttmenus.com/icons/food/icon-taco.webp",
                image_top="images/food16.webp",
                body="### 2 Soft-Shell Tacos")
    tacos = [
        ("Bang Bang Shrimp Tacos", 89, "Sautéed shrimp tossed in chili mayo, shredded cabbage, lettuce, tomatoes and cilantro."),
        ("Carne Asada Tacos", 119, "Marinated steak, diced onions, lettuce, guacamole, sour cream and cilantro.", True),
        ("Blackened Fish Tacos", 69, "Blackened white fish, shredded cabbage, lettuce, Cajun aioli and fresh cilantro."),
        ("Chimichurri Chicken Tacos", 69, "Tender pulled chicken with creamy chimichurri, guacamole and lettuce."),
    ]
    for i, row in enumerate(tacos, 1):
        name, price, body = row[0], row[1], row[2]
        tags = ["Tacos", "Signature"] if len(row) > 3 else ["Tacos"]
        write_item("tacos", f"{slug(name)}.md", name, i, single(price), body, tags)

    write_index("pasta", "Pastas & Salads", 11, "https://ct.ttmenus.com/icons/food/icon-pasta.webp",
                image_top="images/food7.webp",
                body="### Add-ons: Chicken $59 | Shrimp $79 | Steak $129 | Go All In $221")
    write_item("pasta", "build_your_pasta.md", "Build Your Pasta", 1, single(85),
               "Choose fettuccine or penne with Alfredo, Pesto or Marinara sauce.", ["Pasta", "Signature"])
    p = CONTENT / "pasta" / "build_your_pasta.md"
    t = p.read_text(encoding="utf-8").replace("additions: []",
        "additions:\n  - name: Chicken\n    price: 59\n  - name: Shrimp\n    price: 79\n  - name: Steak\n    price: 129\n  - name: Go All In\n    price: 221")
    p.write_text(t, encoding="utf-8")

    write_index("salads", "Salads", 12, "https://ct.ttmenus.com/icons/food/icon-salads.webp",
                image_top="images/food8.webp")
    write_item("salads", "cng_house_salad.md", "CnG House Salad", 1, single(60),
               "Fresh lettuce, tomato, onion, corn, shredded carrots and cabbage with honey mustard dressing.", ["Salad"])
    p = CONTENT / "salads" / "cng_house_salad.md"
    t = p.read_text(encoding="utf-8").replace("additions: []",
        "additions:\n  - name: Chicken\n    price: 59\n  - name: Shrimp\n    price: 79\n  - name: Steak\n    price: 129\n  - name: Go All In\n    price: 221")
    p.write_text(t, encoding="utf-8")

    write_index("plant-forward", "Plant-Forward", 10, "https://ct.ttmenus.com/icons/food/icon-salads.webp",
                image_top="images/food8.webp")
    plants = [
        ("BBQ Tofu Sandwich", 109, "BBQ-glazed tofu with pickled onions, cucumbers and smashed avocado."),
        ("Avocado Mushroom Toast", 79, "Sautéed mushrooms, smashed avocado and balsamic glaze on toasted bread."),
        ("Teriyaki Tofu Poke Bowl", 129, "Rice, teriyaki tofu, pickled red onions, marinated cucumbers, shredded carrots, cabbage and edamame.", True),
        ("Pepper Tofu Bites", 119, "Crispy tofu tossed in pepper sauce, served with stir-fried vegetables and fried rice."),
    ]
    for i, row in enumerate(plants, 1):
        name, price, body = row[0], row[1], row[2]
        tags = ["Plant-Forward", "Signature"] if len(row) > 3 else ["Plant-Forward"]
        write_item("plant-forward", f"{slug(name)}.md", name, i, single(price), body, tags)

    write_index("hero-cocktails", "Hero Cocktails", 13, "https://ct.ttmenus.com/icons/food/icon-cocktails.webp",
                image_top="images/food14.webp",
                body="### Signature cocktails designed by our bar team")
    heroes = [
        ("2 Nuts", 65, "Smooth Amaretto and coconut rum, lifted with fresh lemon and topped with Sprite."),
        ("Lemon Cheesecake Martini", 75, "Limoncello and fresh lemon, shaken with house-made vanilla syrup and heavy cream for a silky, dessert-style martini.", True),
        ("Beachside Mojito", 50, "Coconut rum and cream muddled with fresh mint and lime, topped with soda and finished with toasted coconut."),
        ("Kiss on the Lips", 45, "Frozen peach schnapps and rum blended with mango and lime, finished with a fresh mint sprig."),
        ("Malibu Dream", 50, "Malibu rum with floral Hibiscus syrup, citrus and pineapple, rimmed with pink sugar."),
        ("Sanpellegrino Mojito", 60, "A refreshing twist on the classic, served in a signature mason jar. Choose Melograno or Clementina."),
    ]
    for i, row in enumerate(heroes, 1):
        name, price, body = row[0], row[1], row[2]
        if name == "Sanpellegrino Mojito":
            write_item("hero-cocktails", f"{slug(name)}.md", name, i,
                       [{"v1": "Melograno", "price": 60}, {"v1": "Clementina", "price": 60}], body, ["Cocktails"])
        else:
            tags = ["Cocktails", "Signature"] if len(row) > 3 else ["Cocktails"]
            write_item("hero-cocktails", f"{slug(name)}.md", name, i, single(price), body, tags)

    write_index("zero-proof", "Zero-Proof Heroes", 14, "https://ct.ttmenus.com/icons/food/icon-drinks.webp",
                image_top="images/food15.webp",
                body="### Premium alcohol-free creations")
    zeros = [
        ("Cucumber Mint Cooler", 45, "Crisp cucumber, fresh mint and lime, lightly sweetened for a clean, ultra-refreshing sip."),
        ("Strawberry Basil Lemonade", 45, "Fresh strawberries and fragrant basil muddled into our house lemonade for a bright, refreshing finish."),
        ("Peachyrose Spritz", 45, "Peach purée and house-made rosemary syrup topped with sparkling soda for a lightly floral, elegant refresher."),
        ("Spiced Orange Mule", 45, "Fresh orange and ginger beer with a hint of warm spice and grated nutmeg."),
        ("Golden Glow", 45, "Mango purée with San Pellegrino Clementina and a touch of vanilla for a smooth, tropical refresher."),
    ]
    for i, (n, p, b) in enumerate(zeros, 1):
        write_item("zero-proof", f"{slug(n)}.md", n, i, single(p), b, ["Mocktails"])


def sync_spirits():
    clear_section("spirits")
    write_index("spirits", "Spirits", 18, "https://ct.ttmenus.com/icons/white/icon-scotch.webp",
                image_top="images/food13.webp")
    w = 1
    gin = [
        ("Beefeater Dry", 65, 700), ("Beefeater Pink", 60, 650), ("Bombay Sapphire", 70, 950),
        ("Gordons", 60, 750), ("Greenall's Gin Blueberry", 50, 630), ("Greenall's Gin Pineapple", 50, 630),
        ("Greenall's Gin Wildberry", 50, 630), ("Greenall's Original", 50, 820),
        ("Tanqueray", 70, 750), ("Tanqueray 10", 95, 995),
    ]
    for n, g, b in gin:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Gin"]); w += 1
    tequila = [
        ("1800 Cristalino", 90, 795), ("Maestro Dobel Diamante Cristalino", 90, 795),
        ("Casamigos Reposado", 85, 1095), ("Casamigos Blanco", 90, 995),
        ("Don Julio Anejo", 90, 1190), ("Don Julio Blanco", 80, 995), ("Don Julio Reposado", 85, 1095),
        ("Jose Cuervo Gold / Silver", 50, 650),
        ("Patron Anejo", 80, 995), ("Patron Café", 75, 940), ("Patron Silver", 70, 840),
    ]
    for n, g, b in tequila:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Tequila"]); w += 1
    liqueurs = [
        ("Baileys", 88, 995), ("El Dorado Rum Cream", 50, 600), ("Campari", 40, 600),
        ("Chambord", 85, 850), ("Disaronno Amaretto", 80, 850), ("Frangelico Litre", 60, 950),
        ("Goldschlager", 65, 950), ("Grand Marnier", 65, 950), ("Jagermaister", 75, 940),
        ("Jagermaister Cold Brew", 55, 750), ("Kahlua", 65, 800), ("Limoncello Di Capri", 70, 850),
        ("Molinari Sambuca", 70, 950), ("Shanky's Whip", 75, 800), ("St. Germain", 90, 990),
    ]
    for n, g, b in liqueurs:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Liqueurs"]); w += 1
    vodka = [
        ("Absolut", 55, 650), ("Absolut Flavours", 60, 700), ("Absolut Citron", 55, 780),
        ("Belvedere", 85, 890), ("Grey Goose", 90, 995), ("Ketel 1", 75, 800),
        ("Smirnoff Flavours", 60, 650), ("Smirnoff Flavours Litre", 60, 800),
        ("Smirnoff Red", 50, 550), ("Smirnoff Red Litre", 50, 750),
        ("Titos", 60, 650), ("Titos Litre", 60, 800),
    ]
    for n, g, b in vodka:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Vodka"]); w += 1
    rum = [
        ("Angostura 1787", 80, 995), ("Angostura 1824", 75, 850), ("Angostura 1919", 60, 700),
        ("Angostura 7 yr", 50, 600), ("Black Label Rum", 25, 425), ("Cachaca 51", 50, 800),
        ("Diamond Reserve Flavours", 25, 350), ("Diamond Reserve Dark", 25, 350),
        ("Diamond Reserve Gold", 25, 350), ("Diamond Reserve White Rum", 25, 350),
        ("Diplomatico Mantuano", 70, 620), ("Diplomatico Reserva Exclusiva", 95, 720),
        ("El Dorado 12yr", 55, 600), ("El Dorado 15yr", 55, 750),
        ("Forres Park Puncheon", 40, 700), ("Malibu Litre", 50, 750), ("Malibu", 50, 650),
        ("Ron Zacapa 23yr", 110, 1100), ("Shakers Signature 7", 60, 700),
        ("Single Barrel", 45, 520), ("Tamboo", 40, 500), ("White Oak", 25, 425),
    ]
    for n, g, b in rum:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Rum"]); w += 1
    scotch = [
        ("Black & White", 55, 580), ("Chivas Regal 12yrs", 80, 725), ("Chivas Regal 18yrs", 120, 1225),
        ("Crown Royal", 70, 750), ("Dewar's 12yrs", 70, 700), ("Dewar's 15yrs", 80, 850),
        ("Dewar's 8yrs", 65, 650), ("Dewar's White Label", 60, 600),
        ("Evan Williams", 45, 500), ("Evan Williams Apple / Honey", 45, 500),
        ("Fireball Whisky", 35, 450), ("Gentleman Jack", 80, 850),
        ("Glenlivet 12yrs", 95, 1200), ("Glenlivet 18yr Single Malt", 195, 1900),
        ("Glenlivet Founders Reserve", 90, 900), ("Glenmorangie 10yr Single Malt", 120, 995),
        ("Grand Old Parr", 80, 800), ("Jack Daniels", 70, 700), ("Jack Daniels Apple", 70, 700),
        ("Jack Daniels Blackberry", 70, 700), ("Jack Daniels Fire", 70, 700), ("Jack Daniels Honey", 70, 700),
        ("Jameson Irish Whiskey", 75, 800), ("Johnnie Double Black Litre", 55, 580),
        ("Johnnie Walker Black", 55, 580), ("Johnnie Walker Black Litre", 75, 920),
        ("Johnnie Walker Gold", 105, 1225), ("Johnnie Walker Green", 99, 1175),
        ("Macallan 18yrs Single Malt", 290, 3500), ("Monkey Shoulder", 55, 850),
        ("Screwball Peanut Butter", 80, 850), ("Uncle Nearest Small Batch", 85, 850),
        ("Woodford Reserve Kentucky Bourbon", 80, 800), ("Hennessy VS", 88, 890), ("Woodford Rye", 90, 900),
    ]
    for n, g, b in scotch:
        write_item("spirits", f"{slug(n)}.md", n, w, glass_bottle(g, b), tags=["Spirits", "Scotch & Whiskey"]); w += 1


def sync_beers():
    clear_section("beers")
    write_index("beers", "Beers", 20, "https://ct.ttmenus.com/icons/food/icon-beer.webp",
                image_top="images/food15.webp")
    imported = [
        ("Guinness - Ireland", 25, 55, 99), ("Bonfire Brown", 20, 50, 95),
        ("Cottonmouth Crusher", 20, 50, 95), ("Lake Street Lager", 20, 50, 95),
        ("Melon Ball", 25, 55, 99), ("Neapolitan Milk Stout", 25, 55, 99), ("Oval Beach Blonde", 20, 50, 95),
    ]
    for i, (n, a, b, c) in enumerate(imported, 1):
        write_item("beers", f"imported_{slug(n)}.md", n, i, imported_draught(a, b, c), tags=["Beers", "Imported Draught"])
    for i, (n, m, p, t) in enumerate([
        ("Carib", 28, 110, 215), ("Stag", 28, 110, 215), ("Pilsner", 28, 110, 215),
        ("Heineken", 40, 158, 315), ("Guinness", 40, 158, 315),
    ], 10):
        write_item("beers", f"draught_{slug(n)}.md", f"Draught {n}", i, local_draught(m, p, t), tags=["Beers", "Local Draught"])
    for i, (n, p) in enumerate([
        ("Carib Blue", 28), ("Carib", 22), ("Stag", 22), ("Pilsner", 22), ("Coors Light", 22),
        ("Guinness Local", 30), ("Guinness Smooth", 30), ("Mackeson", 28), ("Corona", 30),
    ], 20):
        write_item("beers", f"bottle_{slug(n)}.md", n, i, single(p), tags=["Beers", "Local Bottles"])
    buckets = [
        ("Carib/Stag/Pilsner", 110), ("Coors Light", 120), ("Corona", 149),
        ("Heineken/Light", 175), ("Modelo/Modelo Negra", 149),
    ]
    write_item("beers", "beer_buckets.md", "Beer Buckets", 30,
               [{"v1": "-", "price": p, "v2": n} for n, p in buckets], tags=["Beers", "Beer Buckets"])


def sync_drinks():
    clear_section("drinks")
    write_index("drinks", "Drinks", 21, "https://ct.ttmenus.com/icons/food/icon-can.webp",
                image_top="images/food12.webp")
    cold = [("Coconut Water", 25), ("LLB", 20), ("Monster", 22), ("Red Bull", 30),
            ("Perrier Sparkling Water (LG)", 65), ("Perrier Sparkling Water (SM)", 30),
            ("Dasani Water", 5), ("Coke / Sprite / Ginger Ale", 20)]
    for i, (n, p) in enumerate(cold, 1):
        write_item("drinks", f"cold_{slug(n)}.md", n, i, single(p), tags=["Cold Drinks"])
    soft = [("Malta", 18), ("Ginseng", 15), ("420 Haze Passion", 30), ("420 OG", 30), ("Caribe", 32),
            ("Rude Boy", 30), ("Rude Boy Extreme", 34), ("Rude Boy Passion", 30), ("Shandy Sorrel", 20),
            ("Smirnoff", 32), ("Cranberry", 20), ("Fruit Punch", 18), ("Grapefruit", 18), ("Orange", 18),
            ("Pineapple", 18), ("Passion Fruit", 18)]
    for i, (n, p) in enumerate(soft, 20):
        write_item("drinks", f"soft_{slug(n)}.md", n, i, single(p), tags=["Soft & Juice"])
    hot = [("Americano", 22), ("Caffe Latte", 26), ("Cappuccino", 30), ("Double Espresso", 39),
           ("Espresso", 20), ("Tea", 20)]
    for i, (n, p) in enumerate(hot, 40):
        write_item("drinks", f"hot_{slug(n)}.md", n, i, single(p),
                   "Assorted selection." if n == "Tea" else "", tags=["Hot Beverages"])
    coffee = [("Affogato & Chill", 70), ("The Emperor", 60), ("Irish Coffee", 75), ("Screwed Up Coffee", 75)]
    for i, (n, p) in enumerate(coffee, 50):
        write_item("drinks", f"coffee_{slug(n)}.md", n, i, single(p), tags=["Coffee Cocktails"])


def sync_shots():
    clear_section("shots")
    write_index("shots", "Shots", 16, "https://ct.ttmenus.com/icons/white/icon-shots.webp",
                image_top="images/food13.webp")
    shots = [
        ("Apple Jack", 35, "Jack Daniel's, Sour Apple Liqueur"),
        ("Alien Brain Hemorage", 50, "Peach Liqueur, Baileys & Grenadine"),
        ("Flaming B52", 55, "Kahlua, Baileys, Grand Marnier & Fire"),
        ("Blue Kamikaze", 35, "Vodka, Blue Curaçao, Lime"),
        ("Baby Guinness", 45, "Baileys & Kahlua"),
        ("Blow Job", 45, "Amaretto, Mokatika, Baileys & whipped Cream"),
        ("Bubble Gum", 45, "Baileys, Banana Liqueur, Blue Curaçao"),
        ("Buttery Nipple", 45, "Butterscotch, Baileys"),
        ("Depth Charge", 55, "Shot of Tequila dropped into a mug of Local Draught beer"),
        ("Helium", 70, "Sambuca, Blue Curaçao, Fire & Cinnamon"),
        ("Jager Bomb", 60, "Jägermeister, Red Bull"),
        ("Lemon Drop", 40, "Limoncello, Vodka, Lime"),
        ("Lil Devil", 40, "Puncheon, Triple Sec, Grenadine"),
        ("Liquid Cocaine", 60, "Jägermeister, Cinnamon Liqueur"),
        ("Melon Ball", 30, "Vodka, Melon Liqueur, Pineapple"),
        ("Peach Bunny", 35, "Peach Liqueur, Overproof Rum"),
        ("Salt Prune Tequila", 50, "Peach Liqueur, Overproof Rum"),
        ("Woo Woo", 35, "Peachtree, Vodka, Cranberry"),
        ("Shot Flight", 99, "Peachtree, Vodka, Cranberry"),
    ]
    for i, (n, p, b) in enumerate(shots, 1):
        write_item("shots", f"{slug(n)}.md", n, i, single(p), b, ["Shots"])


def sync_wines():
    clear_section("wines")
    write_index("wines", "Wines", 19, "https://ct.ttmenus.com/icons/white/icon-wine.webp",
                image_top="images/food13.webp")
    wines = [
        ("19 Crimes Uprising Rum Barrel Aged", [{"v1": "Bottle", "price": 395}], "Red Wine"),
        ("Birds & Bees Sweet Malbec", glass_bottle(60, 250), "Red Wine"),
        ("Casillero del Diablo Cabernet Sauvignon", glass_bottle(69, 275), "Red Wine"),
        ("Hardy's Merlot", glass_bottle(55, 230), "Red Wine"),
        ("Robert Mondavi Private Selection Pinot Noir", [{"v1": "Bottle", "price": 425}], "Red Wine"),
        ("Scarlett Dark Red Blend", glass_bottle(70, 280), "Red Wine"),
        ("Beringer MV Pink Moscato", glass_bottle(60, 250), "White Wine"),
        ("Beringer MV White Moscato", glass_bottle(60, 250), "White Wine"),
        ("Hardy's Pinot Grigio", glass_bottle(55, 230), "White Wine"),
        ("Woodbridge Chardonnay", glass_bottle(65, 270), "White Wine"),
        ("Dow's Fine Ruby", glass_bottle(60, 400), "Port"),
        ("Da Luca Prosecco", [{"v1": "Bottle", "price": 560}], "Champagne & Prosecco"),
        ("Danzante Prosecco", [{"v1": "Bottle", "price": 480}], "Champagne & Prosecco"),
        ("Gemma di Luna Prosecco 187ml Mini", [{"v1": "Bottle", "price": 130}], "Champagne & Prosecco"),
        ("Gemma di Luna Prosecco Spumante", [{"v1": "Bottle", "price": 510}], "Champagne & Prosecco"),
        ("Moet Imperial Rose/Ice", [{"v1": "Bottle", "price": 1400}], "Champagne & Prosecco"),
        ("Moet Imperial Brut", [{"v1": "Bottle", "price": 1200}], "Champagne & Prosecco"),
        ("Moet Nectar Imperial", [{"v1": "Bottle", "price": 1300}], "Champagne & Prosecco"),
    ]
    for i, (n, prices, tag) in enumerate(wines, 1):
        write_item("wines", f"{slug(n)}.md", n, i, prices, tags=["Wine", tag])


def sync_cocktails():
    clear_section("cocktails")
    write_index("cocktails", "Cocktails", 15, "https://ct.ttmenus.com/icons/food/icon-cocktails.webp",
                image_top="images/food14.webp")
    cocktails = [
        ("Manhattan", 119, "Woodford Res Bourbon or Rye Whiskey, Sweet Vermouth, Angostura bitters."),
        ("Absolut Lime Mojito", 65, "Absolut Lime muddled with fresh mint & lime, topped with soda or Sprite. Crisp & clean."),
        ("Amaretto Sour", 69, "Amaretto shaken with fresh lime over ice — almond-forward with optional egg white for a silky foam."),
        ("Basil Gin Smash", 70, "Gin, fresh basil with elderflower Liqueur, lime and topped with soda."),
        ("Black Russian", 70, "Vodka, Kahlua"),
        ("Daiquiri", 50, "Lime/raspberry/Peach/Guava/Mango/Strawberry/Hibiscus."),
        ("Whiskey Sour", 75, "Whisky shaken with fresh lime & simple syrup, poured over ice. Sharp, smooth, timeless."),
        ("Long Island Ice Tea", 75, "Vodka, gin, tequila, white rum & triple sec with fresh lime, topped with Coke. Don't let the smoothness fool you."),
        ("Love Story", 65, "Pear Vodka, Mango puree, Lemon, lime."),
        ("Mai Tai", 60, "Single Barrel & Tamboo Rum, Amaretto, Triple Sec, lime, served over crushed ice."),
        ("Moscow Mule", 60, "Vodka, Ginger beer, fresh mint, lime served over crushed ice in the signature metal mug."),
        ("Old Fashioned", 75, '"The 1st Cocktail" Bourbon/Whiskey/Rum.'),
        ("Purple Rain", 65, "Peach Vodka, Peach & Passion puree, with a Merlot float."),
        ("Queen's Park Swizzle", 60, "Angostura 7yr Rum, Demerara Syrup, Mint leaves, Lime, crushed ice & Bitters."),
        ("Rum Punch", 40, "Planters Rum Punch."),
        ("Rum Sour", 45, "Angostura Single Barrel shaken with fresh lime & simple syrup. Caribbean soul in a glass."),
        ("Scanning for Mexican", 60, "Tequila, Raspberry, Grapefruit, Jalapeno, Lime, Pepper Flakes."),
        ("Smokin' Peach", 60, "Perfect blend of smokey Bourbon and summer Peaches."),
        ("Tom Collins", 65, "Gin, Sparkling water, Lime."),
        ("Zombie", 55, "Light & Dark Rum, Guava puree, Orange juice, lime & garnished with a flaming lime dusted with cinnamon."),
        ("Tiramisu Martini", 85, "Chocolate Vodka, Disaronno Amaretto, Espresso & mascarpone dusted with cinnamon."),
        ("Baileys Martini", 95, "Baileys, Vodka, Kahlua, Chocolate syrup."),
        ("Espresso Martini", 80, "Vodka, Kahlua, Espresso."),
        ("Melon Breeze Martini", 60, "Fresh pressed watermelon puree mixed with Melon Vodka & Vermouth."),
        ("Sour Apple Martini", 60, "Green apple vodka shaken with sour apple liqueur & apple mix, served up. Crisp and unapologetic."),
        ("Porn Star Martini", 80, "Vanilla Vodka, Passion Fruit puree, Lemon, accompanied with a shot glass of Prosecco."),
        ("Vodka Sour", 55, "Vodka shaken with fresh lime & simple syrup, poured over ice. Clean, bright, honest."),
        ("Martini", 55, "Gin/Vodka."),
        ("Mudslide", 95, "Vodka, Mokatika coffee liqueur & rum cream blended with ice cream, drizzled with chocolate & topped with whipped cream. Dessert, basically."),
        ("Pink Margarita", 70, "House tequila silver with triple sec, fresh lime & pink grapefruit, salted rim. Bright & refreshing."),
        ("Spicy Margarita", 70, "Tequila silver with fresh lime, triple sec & a pepper-kissed kick. Salted rim, serious heat."),
        ("Traditional Lime Margarita", 65, "Classic lime margarita with salted rim."),
        ("Ultimate Long Island", 99, "Double pours of vodka, gin, tequila, white rum & triple sec, topped with Coke. Share it. Or don't."),
        ("Ultimate Mudslide", 149, "Double Mudslide — 2oz vodka, rum cream & Mokatika blended with ice cream, chocolate drizzle, whipped cream & a cherry. Bring a friend."),
        ("Ultimate Rum Punch", 99, "Planter's rum punch, generously poured — rum, citrus, bitters & a float."),
        ("Guava Berry", 99, "Frozen margarita blended with guava & strawberry, finished with a Coronita tipped in. Pink, playful, generous."),
        ("Original Lime Marg", 99, "Frozen lime margarita with a Coronita tipped upside-down in the glass. Fun, tart, and yes — you drink them both."),
        ("Peachy Passion", 99, "Frozen margarita blended with peach & passion fruit, finished with a Coronita tipped in. Island sunset in a glass."),
        ("Mojito", 50, "Choose: Lime, Mango, Peach, Raspberry, Strawberry, Guava or Hibiscus."),
    ]
    for i, (n, p, b) in enumerate(cocktails, 1):
        write_item("cocktails", f"{slug(n)}.md", n, i, single(p), b, ["Cocktails"])


def sync_home():
    (CONTENT / "_index.md").write_text(
        "---\ntitle: Island Beer Chill and Grill\nimage: \"\"\nimages: []\nslideshow: []\n---\n\n"
        "## ALL PRICES SUBJECT TO VAT & S.C\n\nPlease inform your server about any allergies.\n",
        encoding="utf-8",
    )


def main():
    remove_non_pdf_sections()
    sync_food()
    sync_spirits()
    sync_beers()
    sync_drinks()
    sync_shots()
    sync_wines()
    sync_cocktails()
    sync_home()
    print("Menu rebuilt from PDF only.")


if __name__ == "__main__":
    main()
