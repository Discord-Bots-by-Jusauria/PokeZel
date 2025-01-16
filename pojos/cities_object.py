from dataclasses import dataclass, field
from typing import List, Optional
import json

@dataclass
class Gym:
    has_gym: bool
    gym_type: str
    gym_requirement: str = ""

@dataclass
class TownHighlight:
    location_name: str
    description: str
    investigation_hint: str
    investigation_result: str

@dataclass
class PokemonSpawn:
    pokemon: str
    level_range: str

@dataclass
class PokemonField:
    is_field_available: bool
    spawn_list: List[PokemonSpawn] = field(default_factory=list)

@dataclass
class Shop:
    items_to_buy: List[str] = field(default_factory=list)

@dataclass
class HealingService:
    available: bool
    description: str

@dataclass
class AdditionalFeatures:
    seasonal_event: str
    famous_resident: str
    local_quest_giver: str

@dataclass
class City:
    city_name: str
    town_overview: str
    gym: Gym
    town_highlights: List[TownHighlight] = field(default_factory=list)
    pokemon_field: Optional[PokemonField] = None
    shop: Optional[Shop] = None
    healing_service: Optional[HealingService] = None
    additional_features: Optional[AdditionalFeatures] = None

    def to_dict(self) -> dict:
        """
        Convert this City object (and its nested structures) into a dictionary.
        """
        return {
            "cityName": self.city_name,
            "townOverview": self.town_overview,
            "gym": {
                "hasGym": self.gym.has_gym,
                "gymType": self.gym.gym_type,
                "gymRequirement": self.gym.gym_requirement
            },
            "townHighlights": [
                {
                    "locationName": th.location_name,
                    "description": th.description,
                    "investigationHint": th.investigation_hint,
                    "investigationResult": th.investigation_result
                } for th in self.town_highlights
            ],
            "pokemonField": {
                "isFieldAvailable": self.pokemon_field.is_field_available,
                "spawnList": [
                    {
                        "pokemon": ps.pokemon,
                        "levelRange": ps.level_range
                    } for ps in self.pokemon_field.spawn_list
                ]
            } if self.pokemon_field else None,
            "shop": {
                "itemsToBuy": self.shop.items_to_buy
            } if self.shop else None,
            "healingService": {
                "available": self.healing_service.available,
                "description": self.healing_service.description
            } if self.healing_service else None,
            "additionalFeatures": {
                "seasonalEvent": self.additional_features.seasonal_event,
                "famousResident": self.additional_features.famous_resident,
                "localQuestGiver": self.additional_features.local_quest_giver
            } if self.additional_features else None
        }

    def to_json(self) -> str:
        """
        Convert this City object into a pretty-printed JSON string.
        """
        return json.dumps(self.to_dict(), indent=2)

    @staticmethod
    def from_dict(data: dict) -> "City":
        """
        Create a City object from a dictionary.
        """
        # Extract gym data
        gym_data = data.get("gym", {})
        gym = Gym(
            has_gym=gym_data.get("hasGym", False),
            gym_type=gym_data.get("gymType", ""),
            gym_requirement=gym_data.get("gymRequirement", "")
        )

        # Extract town highlights
        highlights_data = data.get("townHighlights", [])
        highlights = [
            TownHighlight(
                location_name=h.get("locationName", ""),
                description=h.get("description", ""),
                investigation_hint=h.get("investigationHint", ""),
                investigation_result=h.get("investigationResult", "")
            )
            for h in highlights_data
        ]

        # Extract pokemon field
        pokemon_field_data = data.get("pokemonField")
        if pokemon_field_data:
            spawn_list_data = pokemon_field_data.get("spawnList", [])
            spawn_list = [
                PokemonSpawn(
                    pokemon=ps.get("pokemon", ""),
                    level_range=ps.get("levelRange", "")
                ) for ps in spawn_list_data
            ]
            pokemon_field = PokemonField(
                is_field_available=pokemon_field_data.get("isFieldAvailable", False),
                spawn_list=spawn_list
            )
        else:
            pokemon_field = None

        # Extract shop
        shop_data = data.get("shop")
        shop = Shop(items_to_buy=shop_data.get("itemsToBuy", [])) if shop_data else None

        # Extract healing service
        healing_data = data.get("healingService")
        healing_service = (
            HealingService(
                available=healing_data.get("available", False),
                description=healing_data.get("description", "")
            )
            if healing_data else None
        )

        # Extract additional features
        add_feat_data = data.get("additionalFeatures")
        additional_features = (
            AdditionalFeatures(
                seasonal_event=add_feat_data.get("seasonalEvent", ""),
                famous_resident=add_feat_data.get("famousResident", ""),
                local_quest_giver=add_feat_data.get("localQuestGiver", "")
            )
            if add_feat_data else None
        )

        return City(
            city_name=data.get("cityName", ""),
            town_overview=data.get("townOverview", ""),
            gym=gym,
            town_highlights=highlights,
            pokemon_field=pokemon_field,
            shop=shop,
            healing_service=healing_service,
            additional_features=additional_features
        )

    @staticmethod
    def from_json(json_str: str) -> "City":
        """
        Create a City object from a JSON string.
        """
        return City.from_dict(json.loads(json_str))
