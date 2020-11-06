import yaml

class Conf:
  PATH = 'conf.yaml'
  _instance = None
  
  def __init__(self):
    if Conf._instance == None:
      Conf._instance = self
      # Retrieve properties from configuration file
      self.prop = self.read_file()
    else:
      raise Exception("class is singleton; cannot be instantiated")

  @staticmethod
  def get_instance():
    if Conf._instance == None:
      Conf()
    return Conf._instance

  def read_file(self):
    with open(self.PATH, 'r') as stream:
      try:
        return yaml.safe_load(stream)
      except yaml.YAMLError as err:
        print(err)
  
  def get_property(self, property_name):
    # If properties are never set, retrieve from configuration file
    if self.prop == None:
      self.read_file()
    # If property is not found in properties
    if property_name not in self.prop.keys():
      return None
    # Otherwise return the found property
    return self.prop[property_name]
<<<<<<< HEAD
=======

>>>>>>> d1151f09496f6d87eef836f26f9ab2d5bc8d3eb7
