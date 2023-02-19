import re
import numpy as np

#LISTE DEI BRAND
all_brands_tags = []
alfaromeo_tags = ["car", "sporty", "italian"]
all_brands_tags.extend(alfaromeo_tags)
samsung_tags = ["technology", "computer", "household appliances"]
all_brands_tags.extend(samsung_tags)
lavazza_tags = ["coffee", "italian", "scent"]
all_brands_tags.extend(lavazza_tags)
armani_tags = ["clothing", "fashion", "italian"]
all_brands_tags.extend(armani_tags)
adidas_tags = ["clothing", "sporty", "fashion"]
all_brands_tags.extend(adidas_tags)
microsoft_tags = ["technology", "computer", "office"]
all_brands_tags.extend(microsoft_tags)
barilla_tags = ["italian", "pasta", "home"]
all_brands_tags.extend(barilla_tags)
ferrero_tags = ["chocolate", "italian", "baby"]
all_brands_tags.extend(ferrero_tags)
delonghi_tags = ["household appliances", "home", "coffee"]
all_brands_tags.extend(delonghi_tags)
amarelli_tags = ["chocolate", "licorice", "baby"]
all_brands_tags.extend(amarelli_tags)

#Tag di tutti i brand presi una volta sola (K=16)
all_brands_tags = np.unique(all_brands_tags)


#LISTE DEI SINONIMI DEI TAGs (per ampliare le ricerche)
car_synonyms = ["auto", "automobile", "jeep", "station wagon", "van", "pickup"]	
sporty_synonyms = ["sports", "sport", "athletic", "fit", "outdoor"]
italian_synonyms = ["italy", "italians"]
technology_synonyms = ["technological", "hitech", "high tech"]
computer_synonyms = ["pc", "mac", "calculator", "laptop", "notebook"]
household_appliances_synonyms = ["domestic appliances", "home appliances", "vacuum cleaner", "microware", "refrigerator", "washer dryer", "washing machine", "washing machines"]
coffee_synonyms = ["caffeine", "cappuccino", "mocha", "decaf", "espresso"]
clothing_synonyms = ["clothes", "cloth", "clothe", "dress", "dresses", "outfit", "costume", "garments", "raiment", "jeans", "shirt", "t-shirt", "pant", "sweatshirt", "skirt" ]
fashion_synonyms = ["vouge", "trend", "style", "fad"]
office_synonyms	= ["workplace", "studio", "workroom", "workstead"]
pasta_synonyms = ["linguine", "macaroni","ravioli", "spaghetti", "lasagna", "rigatoni", "tortellini", "fettuccini", "cannelloni"]	
home_synonyms = ["house", "homes", "residence", "mansion", "apartment", "suite", "flat", "lodging"]
chocolate_synonyms = ["cocoa"]
baby_synonyms = ["babies", "child", "children", "youngster", "teenager", "adolescent", "young", "infant", "pamper", "kid", "kids"] 
licorice_synonyms = ["glycyrrhiza glabra", "liquorice"]
scent_synonyms = ["smell", "fragrance", "perfume", "redolence", "odour"]

#creazione dizionario dei brands
brands_dict = {}
brands_dict["alfaromeo"] = alfaromeo_tags
brands_dict["samsung"] = samsung_tags
brands_dict["lavazza"] = lavazza_tags
brands_dict["armani"] = armani_tags
brands_dict["adidas"] = adidas_tags
brands_dict["microsoft"] = microsoft_tags
brands_dict["barilla"] = barilla_tags
brands_dict["ferrero"] = ferrero_tags
brands_dict["delonghi"] = delonghi_tags
brands_dict["amarelli"] = amarelli_tags


#creazione dizionario dei sinonimi
synonyms_dict = {}
synonyms_dict["car"] = car_synonyms
synonyms_dict["sporty"] = sporty_synonyms
synonyms_dict["italian"] = italian_synonyms
synonyms_dict["technology"] = technology_synonyms
synonyms_dict["computer"] = computer_synonyms
synonyms_dict["household appliances"] = household_appliances_synonyms
synonyms_dict["coffee"] = coffee_synonyms
synonyms_dict["clothing"] = clothing_synonyms
synonyms_dict["fashion"] = fashion_synonyms
synonyms_dict["office"] = office_synonyms
synonyms_dict["pasta"] = pasta_synonyms
synonyms_dict["home"] = home_synonyms
synonyms_dict["chocolate"] = chocolate_synonyms
synonyms_dict["baby"] = baby_synonyms
synonyms_dict["licorice"] = licorice_synonyms
synonyms_dict["scent"] = scent_synonyms


"""#sostituisce, all'interno di un testo, i sinonimi di un tag con il tag stesso
def synonym_to_tag(tag, text):
    synonyms = synonyms_dict[tag]
    for synonym in synonyms:
        text = re.sub(r'\b'+synonym+r'\b', tag, text, flags=re.IGNORECASE)
    return text

#sostituisce, all'interno di un testo, tutti i sinonimi di tutti i tags
def replace_all_synonyms(text):
    print("test")
    for tag in all_brands_tags:
        text = synonym_to_tag(tag, text)
    return text"""

#dizionario inverso dei sinonimi (utile per la sostituzione dei sinonimi)
inverse = { v: k for k, l in synonyms_dict.items() for v in l } 

#sostituisce, all'interno di un testo, tutti i sinonimi di tutti i tags
def replace_all_synonyms(text):
    for key in inverse:
        text = re.sub(r'\b'+key+r'\b', inverse[key], text, flags=re.IGNORECASE)
    return text