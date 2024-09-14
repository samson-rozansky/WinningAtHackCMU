from typing import NamedTuple

class AbstractTransaction(NamedTuple):
  name: str
  id: str
  payment_method: str
  time: str

class BuyTransaction(AbstractTransaction):
  max_price: float

class SellTransaction(AbstractTransaction):
  min_price: float

class Matcher:

  def __init__(self):
    self._queued_buyers = []
    self._queued_sellers = []

  def reduce_matches(self) -> : 

