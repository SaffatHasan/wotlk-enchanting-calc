import json
from dataclasses import dataclass
from typing import Dict, List
from gold_amount import GoldAmount
from nexushub_api import NexusHubApi, Reagent

"""
Sample
{
    "colors": [
        300,
        310,
        325,
        340
    ],
    "id": 25086,
    "learnedat": 300,
    "name": "Enchant Cloak - Dodge",
    "reagents": [
        [
            22448,
            3
        ],
        [
            22446,
            3
        ],
        [
            22452,
            8
        ]
    ]
}
"""
def load_enchanting_data():
    with open("enchanting.json", "r") as f:
        return json.load(f)


@dataclass
class Recipe:
    id: int
    name: str
    reagents: Dict[Reagent, int]
    colors: List[int]  # exactly 4: orange, yellow, green, gray
    price: GoldAmount

    @staticmethod
    def load_all():
        BROKEN_RECIPES = [
            42615,
            28022,
            45765,
            7421,
        ]
        recipes = []
        for enchanting_recipe_data in load_enchanting_data():
            recipe = Recipe.from_json(enchanting_recipe_data)
            if not recipe:
                continue
            if recipe.id in BROKEN_RECIPES:
                continue
            recipes.append(recipe)
        return recipes

    @staticmethod
    def from_json(json, nexus_hub_api: NexusHubApi):
        # https://www.wowhead.com/wotlk/spells/professions/engineering
        # Search for "var listviewspells = [...]" in the DOM
        # Ignore recipes that have no reagents
        if "reagents" not in json:
            return None
        reagents = {nexus_hub_api.get_item(item_id): quantity for (item_id, quantity) in json["reagents"]}
        return Recipe(
            int(json["id"]),
            json["name"],
            reagents,
            json["colors"],
            Recipe.price(reagents),
        )

    @staticmethod
    def price(reagents: Dict[Reagent, int]) -> GoldAmount:
        return sum((reagent.price * quantity for reagent, quantity in reagents.items()), GoldAmount.from_copper(0))
    
    def __hash__(self):
        return self.id
    
    def __dict__(self):
        return {"id": self.id, "name": self.name, "reagents": [dict(r.__dict__(), **{"quantity": self.quantity(r)}) for r in self.reagents]}
    
    def reagent_item_ids(self):
        return list(map(lambda r: r.id, self.reagents.keys()))

    def can_use(self, skill_level):
        return skill_level > self.colors[0]

    def can_receive_skillup(self, skill_level):
        return skill_level < self.colors[3]

    def cost_for_skillup(self, skill_level):
        if self.levelup_probability(skill_level) == 0:
            return GoldAmount.from_copper(2**31-1)
        return self.price / self.levelup_probability(skill_level)
    
    def expected_times_per_skillup(self, skill_level: int):
        return round(1 / self.levelup_probability(skill_level))

    def quantity(self, reagent):
        return self.reagents[reagent]

    def levelup_probability(self, skill_level):
        # https://www.reddit.com/r/woweconomy/comments/9epibc/crafting_skillups_exact_skillup_chance/
        if skill_level == self.colors[0]:
            return 1
        try:
            return (self.colors[3] - skill_level) / (self.colors[3] - self.colors[1])
        except ZeroDivisionError as e:
            print(f"Failed to get level_up probability for {self.name}.")
            raise e
