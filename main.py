import dataclasses
from typing import Callable
from nexushub_api import NexusHubApi
from profession import Enchanting, Engineering, Profession

servers = NexusHubApi.fetch_servers()
factions = ["horde", "alliance"]

nexus_hub_api = NexusHubApi("sulfuras", "horde")
professions = {
    "enchanting": Enchanting,
    "engineering": Engineering,
}

import argparse
import json

def main():
    parser = argparse.ArgumentParser(description='Select a server and a faction')
    parser.add_argument('--server', type=str, default="faerlina", choices=servers)
    parser.add_argument('--faction', type=str, default="horde", choices=factions)
    parser.add_argument('--profession', type=str, choices=professions.keys(), default="enchanting")
    parser.add_argument('--target_level', type=int, default=450)
    parser.add_argument('--command', type=str, default="reagents", choices=["reagents", "path", "total_cost"])
    parser.add_argument('--format', type=str, default="human-readable", choices=["human-readable", "json"])
    args = parser.parse_args()

    profession = professions[args.profession](
       nexus_hub_api=NexusHubApi(
        server=args.server,
        faction=args.faction,
       ) 
    )

    if args.command == "reagents":
        reagents = profession.reagents_required_to(args.target_level)
        if args.format == "human-readable":
            print(f"Reagents required from 1-{args.target_level}")
            for reagent, quantity in reagents.items():
                print(f"{reagent.name} x{quantity}")
        else:
            print(json.dumps([
                {
                "id": reagent.id,
                "price": reagent.price.to_copper(),
                "name": reagent.name,
                "quantity": quantity,
                } for reagent, quantity in reagents.items()
            ]))
    elif args.command == "path":
        if args.format == "human-readable":
            profession.print_recipe_path(args.target_level)
        else:
            print(json.dumps({
                skill_level: recipe.__dict__() for skill_level, recipe in enumerate(profession.recipe_path[:args.target_level], 1)
            }))

    if args.command == "total_cost":
        if args.format == "human-readable":
            print(f"It costs {profession.total_cost_to(args.target_level)} to go from 1-{args.target_level}")
        else:
            print({"total_cost": profession.total_cost_to(args.target_level).to_copper()})



if __name__ == "__main__":
    main()

