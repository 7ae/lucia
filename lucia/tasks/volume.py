import alsaaudio
import re
from conf import Conf

conf = Conf.get_instance()

class Volume:
  VOLUME_MAX = 100
  VOLUME_MIN = 0
  VOLUME_STEP = 10
  VOLUME_RULES = ['to  NUM']
  VOLUME_UP_RULES = ['raise', 'increase', 'up', 'louder']
  VOlUME_DOWN_RULES = ['lower', 'decrease', 'down', 'softer']
  VOLUME_ON_RULES = ['unmute', 'on']
  VOLUME_OFF_RULES = ['mute', 'off', 'shut  up']

  def __init__(self):
    self.m = alsaaudio.Mixer(alsaaudio.mixers()[0])
    self.curr_volume = self.m.getvolume()[0]
    self.prev_volume = self.curr_volume
    self.is_muted = self.curr_volume == self.VOLUME_MIN

  def run(self, brain, tag, ne):
    self.brain = brain
    self.tag = tag
    self.ne = ne
    
    step = self.get_step()

    # Set volume to NUM
    if self.search_rule(self.VOLUME_RULES):
      self.set_volume(step)
    # Unmute
    elif self.is_muted and self.search_rule(self.VOLUME_ON_RULES):
      self.set_volume(self.prev_volume)
      self.is_muted = False
    # Mute
    elif not self.is_muted and self.search_rule(self.VOLUME_OFF_RULES):
      # Remember current volume
      self.prev_volume = self.m.getvolume()[0]
      self.set_volume(self.VOLUME_MIN)
      self.is_muted = True
    # Volume up
    elif self.search_rule(self.VOLUME_UP_RULES):
      self.set_volume(self.curr_volume + step)
    # Volume down
    elif self.search_rule(self.VOlUME_DOWN_RULES):
      self.set_volume(self.curr_volume - step)
    # Increase/decrease volume by NUM
    else:
      self.set_volume(step)

    #self.m.close()
    return self

  def search_rule(self, rules):
    for r in rules:
      if self.brain.think(r, self.tag):
        return True
    return False

  def get_step(self):
    # Search whether user said step, e.g., raise volume by CARDINAL
    try:
      _ = next(_ for _ in self.ne if 'CARDINAL' in _)[-1]['number']
      return _
    except:
      # If not, use default step, e.g., raise volume
      return self.VOLUME_STEP

  def set_volume(self, volume):
    volume = int(volume)
    if (volume < self.VOLUME_MIN):
      self.m.setvolume(self.VOLUME_MIN)
      self.curr_volume = self.VOLUME_MIN
    elif (volume > self.VOLUME_MAX):
      self.m.setvolume(self.VOLUME_MAX)
      self.curr_volume = self.VOLUME_MAX
    else:
      self.m.setvolume(volume)
      self.curr_volume = volume

