from typing import Optional

class AbstractTransaction:
  def __init__(self, name: str, id: str, payment: str,
               time: str):
    self.name = name
    self.id = id
    self.payment = payment
    self.time = time

class Buyer(AbstractTransaction):
  def __init__(self, name: str, id: str, payment: str, 
               time: str, max_price: float):
    super().__init__(name, id, payment, time)
    self.max_price = max_price


class Seller(AbstractTransaction):
  def __init__(self, name: str, id: str, payment: str, 
               time: str, min_price: float):
    super().__init__(name, id, payment, time)
    self.min_price = min_price

class Matcher:

  def __init__(self):
    self._queued_buyers = []
    self._queued_sellers = []
    self._log = []

  def get_min_seller(self) -> Optional[Seller]:
    min_price = 1000
    min_seller = None
    for seller in self._queued_sellers:
      if seller.min_price < min_price:
        min_price = seller.min_price
        min_seller = seller
    return min_seller
  
  def get_max_buyer(self) -> Optional[Buyer]:
    max_price = 0
    max_buyer = None
    for buyer in self._queued_buyers:
      if buyer.max_price > max_price:
        max_price = buyer.max_price
        max_buyer = buyer
    return max_buyer
  
  def add_buyer(self, buyer: Buyer):
    self._queued_buyers.append(buyer)
    self._log.append(f"[{buyer.time}]: {buyer.name} ({buyer.id}) is buying for ${buyer.max_price}")

  def add_seller(self, seller: Seller):
    self._queued_sellers.append(seller)
    self._log.append(f"[{buyer.time}]: {seller.name} ({seller.id}) is selling for ${seller.min_price}")

  def log(self):
    return self._log
