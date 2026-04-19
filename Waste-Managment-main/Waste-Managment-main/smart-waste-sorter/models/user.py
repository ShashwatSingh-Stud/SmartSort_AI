from datetime import datetime

class UserGreenCoins:
    def __init__(self, user_name, organization="Smart Environment Corp", coins=0):
        self.user_name = user_name
        self.organization = organization
        self.green_coins = coins
        self.rank = "Bronze"
        self.total_items_sorted = 0
        self.joined_date = datetime.utcnow()
        self.last_active = datetime.utcnow()

    def to_dict(self):
        return {
            "user_name": self.user_name,
            "organization": self.organization,
            "green_coins": self.green_coins,
            "rank": self.rank,
            "total_items_sorted": self.total_items_sorted,
            "joined_date": self.joined_date,
            "last_active": self.last_active
        }
