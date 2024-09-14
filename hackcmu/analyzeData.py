import json
import re
from typing import Optional

def get_block_seller_amount(message) -> Optional[int]: 
  block_role_id = "1275913207529345166"
  if block_role_id in message["mention_roles"]:
    numbers = re.findall(r"\d+\.\d+|\d+", message["content"])
    if len(numbers) == 0:
      return None
    numbers = [float(x) for x in numbers]
    closest = min(numbers, key=lambda x: abs(x - 8.0))
    return closest
  return None
with open("test.txt") as f: 
    for _ in range(100):
        x = eval(f.readline())
        for i in x:
            if get_block_seller_amount(i) != None:
                print(i['timestamp'], get_block_seller_amount(i))
            # print(i['content'])
            # print(numbers);

