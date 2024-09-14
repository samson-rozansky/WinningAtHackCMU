import json
import re
from typing import Optional

def get_block_seller_amount(message) -> Optional[int]: 
  print(message)
  block_role_id = "1275913207529345166"
  if block_role_id in message["mention_roles"]:
    numbers = re.findall(r"\d+\.\d+|\d+\.?", message["content"])
    print(numbers)
    if len(numbers) == 0:
      return None
    numbers = [int(x) for x in numbers]
    closest = min(numbers, key=lambda x: abs(x - 8.0))
    return closest
  return None

if __name__=="__main__":
  with open("discord_24_data.json") as f: 
    requests = f.readlines()
  
  processed_data = []
  for request in requests:
    processed_request = request.replace("'", '"')
    try: 
      data = json.loads(processed_request)
    except Exception as e:
      print("request: ", processed_request)
      print(e)
      continue
    messages = data["messages"]

    for _message in messages:
      message = _message[0]
      # print(message)
      amount = get_block_seller_amount(message)
      if amount is not None:
        processed_data.append((amount, message["timestamp"]))
  print(processed_data)
