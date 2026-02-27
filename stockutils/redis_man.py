
import redis

class redisman:
 def __init__(self):

  self.r = redis.Redis(
    host='redis-11972.c241.us-east-1-4.ec2.cloud.redislabs.com',
    port=11972,
    decode_responses=True,
    username="default",
    password="DNqKItilJwjmg6jtLKXQoUlHvSwaOSlP",
)

 def set_a_value(self,key):
     self.r.set(key,1)

 def get_all_keys(self):
  all_keys = []
  for key in self.r.scan_iter():
    all_keys.append(key)
  return all_keys
 def delete_a_key(self,key):
    cnt=self.r.delete(key)
    if cnt==1:
        return 0
    return 1
res=redisman()
