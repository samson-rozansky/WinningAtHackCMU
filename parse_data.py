import json
import re
from typing import Optional

def get_block_seller_amount(message) -> Optional[int]: 
  block_role_id = "1275913207529345166"
  if block_role_id in message["mention_roles"]:
    numbers = re.findall(r"\d+\.\d+|\d+", message["content"])
    if len(numbers) == 0:
      return None
    numbers = [int(x) for x in numbers]
    closest = min(numbers, key=lambda x: abs(x - 8.0))
    return closest
  return None

if __name__=="__main__":
  with open("discord_24_data.json") as f: 
    data = json.load(f)

  messages = data["messages"]
  data = []
  for message in messages:
    amount = get_block_seller_amount(message)
    if amount is not None:
      data.append((amount, message["timestamp"]))
  print(data)
