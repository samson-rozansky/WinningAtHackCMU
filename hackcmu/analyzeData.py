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
    if abs(closest-8.0)<6.0:
        return closest
  return None
def get_date_time():
    a = []
    b = []
    with open("hackcmu/test.txt") as f: 
        for _ in range(87):
            x = eval(f.readline())
            for i in x:
                if get_block_seller_amount(i) != None:
                    a.append(i['timestamp'])
                    b.append(get_block_seller_amount(i))
                # print(i['content'])
                # print(numbers);
    return a, b

