from dataclasses import dataclass
import json
import os
from typing import Union
import requests

from gold_amount import GoldAmount

class NexusHubApi:
    server: str
    faction: str
    cache: dict

    def __init__(self, server: str, faction: str):
        if faction not in ["horde", "alliance"]:
            raise ValueError(f"{faction} is not a valid faction. Valid factions: [\"horde\", \"alliance\"].")
        self.server = server.lower()
        self.faction = faction.lower()
        self.cache = self.load_cache()

    def get_item_price(self, item_id):
        return GoldAmount.from_copper(self.get_item(item_id).price)
    
    def get_item_name(self, item_id):
        return self.get_item(item_id).name

    def get_item(self, item_id):
        item_data = self.get_item_data(item_id)
        return Reagent(
            id=item_id,
            price=GoldAmount.from_copper(item_data["marketValue"]),
            name=item_data["name"],
        )

    def get_item_data(self, item_id):
        """Returns a dictionary containing the `marketValue` and `name` fields for the given `itemId`.

        If the item data is not in the cache, fetches it from the API and updates the cache.
        """
        if str(item_id) in self.cache:
            return self.cache[str(item_id)]
        else:
            # Fetch the data from the API and update the cache
            api_data = self.fetch_data_from_api(item_id)  # replace with actual API call
            if len(api_data["data"]) == 0:
                cost = 0
            else:
                cost = api_data["data"][0]["marketValue"]
            item_data = { "name": api_data["name"], "marketValue": cost}
            self.cache[str(item_id)] = item_data
            self.save_cache()
            print(f"Fetched data for {item_data['name']} ({item_id}) on {self.server}-{self.faction}")
            return item_data
    
    def load_cache(self):
        """Loads the item cache from disk, or returns an empty dict if the file does not exist."""
        cache_path = self.cache_path()
        if not os.path.exists(cache_path):
            return {}
        with open(cache_path, "r") as f:
            return json.load(f)

    def save_cache(self):
        """Saves the item cache to disk."""
        with open(self.cache_path(), "w") as f:
            json.dump(self.cache, f)

    def cache_path(self):
        return f"item_cache_{self.server}_{self.faction}.json"

    """
    Sample response:
    {
        "slug": "sulfuras-horde",
        "itemId": 34052,
        "name": "Dream Shard",
        "uniqueName": "dream-shard",
        "timerange": 7,
        "data": [
            {
            "marketValue": 154358,
            "minBuyout": 150000,
            "quantity": 574,
            "scannedAt": "2023-02-26T00:22:18.000Z"
            } 
        ]
    }
    """
    def fetch_data_from_api(self, item_id):
        return requests.get(f"https://api.nexushub.co/wow-classic/v1/items/{self.server}-{self.faction}/{item_id}/prices").json()

    """
    Sample response:
    [
        {
          "slug": "amnennar",
          "name": "Amnennar",
          "region": "EU"
        },
        {
          "slug": "angerforge",
          "name": "Angerforge",
          "region": "US"
        }
    ]
    """
    @staticmethod
    def fetch_servers():
        if not os.path.exists("servers.json"):
            servers = requests.get(f"https://api.nexushub.co/wow-classic/v1/servers/full").json()
            with open("servers.json", "w") as f:
                json.dump(servers, f)
            return servers
        with open("servers.json", "r") as f:
            return map(lambda x: x["slug"], json.load(f))

@dataclass
class Reagent:
    id: int
    price: GoldAmount
    name: str

    def __hash__(self) -> int:
        return self.id
    
    def __init__(self, id, price: Union[GoldAmount, int], name: str):
        self.id = id
        self.price = price if isinstance(price, GoldAmount) else GoldAmount.from_copper(price)
        self.name = name

    def __dict__(self):
        return {"id": self.id, "price": self.price.__dict__(), "name": self.name}

    @staticmethod
    def from_json(json):
        return Reagent(
            id=json["itemId"], 
            price=GoldAmount.from_copper(int(json["data"][0]["marketValue"])),
            name=json["name"],
        )
