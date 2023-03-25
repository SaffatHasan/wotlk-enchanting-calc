"""Interface to support the following user stories:

- What reagents and how many number of times does it take to gain one level with
    - One skill level
    - All recipes from level X to Y
- What is the price of:
    - One recipe
    - All recipes from level X to Y

as configuration it takes:
    path to profession.json (a list of recipes for this profession)
        +invalid recipe IDs
        +required array of (recipe IDs , skill level)
    an instance of Reagent costs
    
"""

from typing import Dict, List, Optional
from gold_amount import GoldAmount
from nexushub_api import NexusHubApi, Reagent
from recipes import Recipe
import json


class Profession:
    name: str
    recipes: List[Recipe]
    required_recipes: Dict[int,int] # skill_level: recipe.id
    recipe_path: List[Recipe]

    def __init__(self, name: str, nexus_hub_api: NexusHubApi, recipe_json_path: str, broken_recipes: List[int]=[], required_recipes: Dict[int, int]=[]) -> None:
        self.name = name
        self.nexus_hub_api = nexus_hub_api
        self.required_recipes = required_recipes 
        self.broken_recipes = broken_recipes
        with open(recipe_json_path) as f:
            self.recipes = [recipe for recipe in (Recipe.from_json(recipe_data, nexus_hub_api) for recipe_data in json.load(f)) if recipe]
        self.recipe_path = []
        for i in range(1,450):
            result = self.cheapest_way_to_level_at(i)
            if result is None:
                print("Failed to find a suitable recipe for level " + str(i))
                continue
            self.recipe_path.append(result)

    @staticmethod
    def __str__():
        return "fo"

    def print_recipe_path(self, target: int):
        print_combined_recipe(self.recipe_path[:target])

    def cheapest_way_to_max(self) -> List[Recipe]:
        return self.cheapest_way_to(450)

    def cheapest_way_to(self, target: int) -> List[Recipe]:
        return self.recipe_path[:target]

    def cheapest_way_to_level_at(self, skill_level) -> Recipe:
        if skill_level in self.required_recipes:
            recipe_id = self.required_recipes[skill_level]
            return self.recipe_by_id(recipe_id)
        possible_recipes = self.possible_recipes(skill_level)
        if len(possible_recipes) == 0:
            return None
        return min(possible_recipes, key=lambda recipe: recipe.cost_for_skillup(skill_level))
    
    def recipe_by_id(self, recipe_id):
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None

    def possible_recipes(self, skill_level) -> List[Recipe]:
        possible_recipes: List[Recipe] = []
        for recipe in self.recipes:
            if not recipe.can_use(skill_level):
                continue
            if not recipe.can_receive_skillup(skill_level):
                continue
            if recipe.id in self.broken_recipes:
                continue
            possible_recipes.append(recipe)
        return possible_recipes

    def reagents_for_level(self, skill_level: int, recipe: Recipe) -> List[int]:
        multiplier = recipe.expected_times_per_skillup(skill_level)
        return {reagent: recipe.quantity(reagent.id) * multiplier for reagent in recipe.reagents}
    
    def total_cost_to_max(self):
        return self.total_cost_to(450)

    def total_cost_to(self, target: int):
        total_cost = GoldAmount.from_copper(0)
        for skill_level, recipe in enumerate(self.recipe_path, 1):
            if skill_level == target:
                break
            skill_level = skill_level + 1
            total_cost += recipe.price * recipe.expected_times_per_skillup(skill_level)
        return total_cost

    def reagents_required_to_max(self):
        return self.reagents_required_to(450)

    def reagents_required_to(self, target: int) -> Dict[Reagent,int]:
        reagents: Dict[Reagent, int] = {}
        for skill_level, recipe in enumerate(self.recipe_path, 1):
            if skill_level == target:
                break
            reagents = merge_dict(reagents, recipe.reagents)
        return reagents


def merge_dict(dict1, dict2):
    return {k: dict1.get(k, 0) + dict2.get(k, 0) for k in set(dict1) | set(dict2)}


def print_combined_recipe(recipe_path):
    start = None
    prev = None
    result = []
    for i, x in enumerate(recipe_path, 1):
        if x != prev:
            if start is not None:
                result.append((start, i-1, prev, i-start))
            start = i
            prev = x
    if start is not None:
        result.append((start, len(recipe_path)-1, prev, len(recipe_path)-start-1))
    total = GoldAmount.from_copper(0)
    for arr in result:
        start = arr[0]
        end = arr[1]
        recipe = arr[2]
        quantity = arr[3]
        print(f"[{start:3}-{end+1:3}] {recipe.name[:35]:35} (x{quantity:2}). Cost = {recipe.price * quantity}")
        total  += recipe.price * quantity
    print("="*10)
    print(f"Total cost = {total}")

class Enchanting(Profession):
    def __init__(self, nexus_hub_api: NexusHubApi):
        broken_recipes = [
            42613,
            28022,
            45765,
            7421,
        ]

        required_recipes = {
            1: 7421, # Runed Copper Rod
            100: 7795, # Runed Silver Rod
            155: 13628, # Runed Golden Rod
            200: 13702, # Runed Truesilver Rod
            299: 20051, # Runed Arcanite Rod
            300: 32664, # Runed Fel Iron Rod
            350: 32665, # Runed Adamantite Rod
        }
        super().__init__(
            name="enchanting",
            nexus_hub_api=nexus_hub_api,
            recipe_json_path="enchanting.json",
            broken_recipes=broken_recipes,
            required_recipes=required_recipes,
        )

class Engineering(Profession):
    def __init__(self, nexus_hub_api: NexusHubApi):
        super().__init__(
            name="engineering",
            nexus_hub_api=nexus_hub_api,
            recipe_json_path="engineering.json",
        )

        print(self.recipes)