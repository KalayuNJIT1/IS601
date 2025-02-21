import json

class midterm_project():
 def __init__(self,filename):
  with open(filename) as file:
   self.data=json.load(file)