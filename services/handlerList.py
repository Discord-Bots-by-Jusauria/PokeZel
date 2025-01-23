from services.AttackHandler import AttackHandler
from services.AzurquoraHandler import AzurquoraHandler
from services.MarketHandler import MarketHandler
from services.TrainerHandler import TrainerHandler


ALL_HANDLERS  = {
    "azurquora": AzurquoraHandler,
    "trainer": TrainerHandler,
    "market": MarketHandler,
    "attack": AttackHandler
}