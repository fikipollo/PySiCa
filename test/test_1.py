"""
PySiCa, a simple Python Cache system

v0.2 December 2018
"""

import json
import os
from pysica_api import SimpleCache
from time import sleep

cache = SimpleCache(server="0.0.0.0", port=4444)

data1 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test1.json")))
data2 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test2.json")))

cache.add("1", {"name": "my simple example data", "some_value" : 45}, compress=False)
cache.add("2", {"name": "another example data", "beers": 250, "even_a_list": [1, 2, 3, "asd"]}, user_id="1")
cache.add("3", data1, data_type="superobjects")
cache.add("4", data2, data_type="superobjects")

i=1
result = cache.get("1")  # Should be there
print("Test " + str(i) + ". Get value (valid id, expected) \t" + ("OK" if result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.get("5")  # Should be there
print("Test " + str(i) + ". Get value (not valid id, not expected) \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
sleep(30)
result = cache.get("1", reset_timeout=True, timeout=1)  # Should be there
print("Test " + str(i) + ". Get value and reset timeout (valid id, in time, expected) \t" + ("OK" if result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
sleep(40)
result = cache.get("1")  # Should be there
print("Test " + str(i) + ". Get value after reset timeout (valid id, in time, expected) \t" + ("OK" if result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
sleep(60)
result = cache.get("1")  # Should NOT be there
print("Test " + str(i) + ". Get value after timeout (elem not expected) \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.get("2") # Should NOT be there
print("Test " + str(i) + ". Get value for w/o user_id (not expected) \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.get("2", user_id="1") # Should be there
print("Test " + str(i) + ". Get value with correct user_id (expected) \t" + ("OK" if result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.get("2", user_id="2") # Should NOT be there
print("Test " + str(i) + ". Get value with invalid user_id (not expected) \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.get(data_type="superobjects")
print("Test " + str(i) + ". Get elems by type (expected 2 elems) \t" + ("OK" if result.success and len(result.result) == 2 else "FAIL"))
# print("     " + str(result) + "\n")

i+=1
result = cache.reset("3", timeout=1)
print("Test " + str(i) + ". Reset timeout for valid elem to 1 minute \t" + ("OK" if result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.reset("5", timeout=1)
print("Test " + str(i) + ". Reset timeout for invalid elem to 1 minute \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
sleep(90)
result = cache.get(data_type="superobjects") # Elem 3 should NOT be there
print("Test " + str(i) + ". Get elems by type after timeout (expected 1 elem) \t" + ("OK" if result.success and len(result.result) == 1 else "FAIL"))
# print("     " + str(result) + "\n")

i+=1
result = cache.remove("4")
result2 = cache.get("4")
print("Test " + str(i) + ". Remove elem by valid id \t" + ("OK" if result.success and not result2.success else "FAIL"))
print("     " + str(result))
print("     " + str(result2) + "\n")

i+=1
result = cache.remove("5")
print("Test " + str(i) + ". Remove elem by invalid id \t" + ("OK" if not result.success else "FAIL"))
print("     " + str(result) + "\n")

i+=1
result = cache.remove("2", user_id="1", return_elem=True)
result2 = cache.get("2", user_id="1")
print("Test " + str(i) + ". Remove elem by valid id and user_id \t" + ("OK" if result.success and not result2.success else "FAIL"))
print("     " + str(result))
print("     " + str(result2) + "\n")
