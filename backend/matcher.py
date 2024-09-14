from datetime import datetime
from typing import Optional

def get_time():
  return datetime.now()


class AbstractTransaction:
  def __init__(self, name: str, id: str, payment: str,
               time: str):
    self.name = name
    self.id = id
    self.payment = payment
    self.time = time

  def to_str(self):
    return f"[{self.time}]: {self.payment}"
  
  def get_info(self):
    return {
      "name": self.name,
      "id": self.id,
      "payment": self.payment,
      "time": self.time,
    }

class Buyer(AbstractTransaction):
  def __init__(self, name: str, id: str, payment: str, 
               time: str, max_price: float, contactInfo: dict):
    super().__init__(name, id, payment, time)
    self.max_price = max_price


class Seller(AbstractTransaction):
  def __init__(self, name: str, id: str, payment: str, 
               time: str, min_price: float, contactInfo: dict):
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
    self._log.append(f"[{seller.time}]: {seller.name} ({seller.id}) is selling for ${seller.min_price}")

  def remove_buyer(self, buyer: Buyer):
    self._queued_buyers.remove(buyer)
    self._log.append(f"[{get_time()}]: {buyer.name} ({buyer.id}) cancelled offer.")

  def remove_seller(self, seller: Seller):
    self._queued_sellers.remove(seller)
    self._log.append(f"[{get_time()}]: {seller.name} ({seller.id}) cancelled offer.")

  def log(self):
    return self._log
  
  def process_transaction(self, buyer: Buyer, seller: Seller, price: float):
    self._queued_buyers.remove(buyer)
    self._queued_sellers.remove(seller)
    self._log.append(f"[{get_time()}]: {seller.name} ({seller.id}) sold a block to {buyer.name} ({buyer.id}) for ${price}.")
