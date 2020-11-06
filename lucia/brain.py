import importlib
import re
import subprocess
import time

import numpy as np
import speech_recognition as sr
from deepspeech import Model
from conf import Conf
import nltk
from nltk import conlltags2tree, pos_tag, tree2conlltags
from nltk.chunk import ne_chunk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import spacy
from duckling import Duckling

# Create configuration instance
conf = Conf.get_instance()

# Specify nltk data directory
nltk.data.path.append(conf.get_property('nltk')['data_dir'])

class Brain:
  MODULE_BASE_PATH = 'lucia.tasks.'

  def __init__(self):
    self.model = None
    self.r = sr.Recognizer()
    self.nlp = spacy.load(conf.get_property('spacy')['model'])
    self.espeak = conf.get_property('espeak')
    
    # Load low-level Duckling model
    self.duckling = Duckling()
    self.duckling.load(languages=conf.get_property('duckling')['languages'])

    # Remember tasks
    self.task_memory = []

  def create_model(self):
    # Create a DeepSpeech model with model path
    self.model = Model(conf.get_property('deepspeech')['model_path'])
    # Enable decoding using an external scorer
    self.model.enableExternalScorer(conf.get_property('deepspeech')['scorer_path'])

  def listen(self, debug_mode=False):
    while True:
      with sr.Microphone(sample_rate=conf.get_property('speech_recognition')['audio_rate']) as source:
        # Listen for a while and adjust the energy threshold to start and stop recording voice to account for ambient noise
        self.r.adjust_for_ambient_noise(source, duration=conf.get_property('speech_recognition')['energy_threshold'])
        self.r.dynamic_energy_threshold = True
        
        if debug_mode is False:
          print("Say something")
          audio = self.r.listen(source)
          # Speech to text
          audio = np.frombuffer(audio.frame_data, np.int16)
          text = self.model.stt(audio)
          self.speak(text)
        else:
          text = input()
        
        # Wake up on hearing the wake word
        #if any(subtext in text for subtext in conf.get_property('wake_words')):
        #  self.understand(text)
        self.understand(text)

  def speak(self, text):
    subprocess.call('espeak-ng -v {}+{}{} "{}"'.format(self.espeak['language'], self.espeak['gender'], self.espeak['pitch'], text), shell=True)

  def understand(self, sentence):
    # Break paragraph into sentences
    tokenized_sentence = sent_tokenize(sentence)

    # Break sentence into words
    for sent in tokenized_sentence:
      tokenized_word = word_tokenize(sent)

      # Tag corpora with universal POS tagset
      # For tag list, read https://www.nltk.org/book/ch05.html#tab-universal-tagset
      pos_tags = nltk.pos_tag(tokenized_word, tagset='universal')

      # Divide sentence into noun phrases with regular expression
      grammar = 'NOUN: {<DET>?<ADJ>*<NOUN>}'
      cp = nltk.RegexpParser(grammar)
      # Find chunk structure
      cs = cp.parse(pos_tags)
      # B-{tag} beginning, I-{tag} inside, O-{tag} outside
      iob_tags = np.asarray(tree2conlltags(cs)).tolist()

      # Recognize named entities
      doc = self.nlp(sent)

      # Parse word into numeral, ordinal, and time
      parse = lambda ne : dict([[_['dim'], _['value']['value']] for _ in self.duckling.parse(ne, dim_filter=conf.get_property('duckling')['dimensions'])])
      # [Word, character positions and entity type]. For all entity types, read https://spacy.io/api/annotation#named-entities
      ne = list([ent.text, ent.start_char, ent.end_char, ent.label_, parse(ent.text)] for ent in doc.ents)

      ne_tags = [_.ent_type_ for _ in doc]
      # Merge iob tags and named entity tags
      tagged_sent = [list(np.append(iob_tags[i], ne_tags[i])) for i in range(len(iob_tags))]
      tagged_sent = ''.join(str(x) for x in tagged_sent)

      self.decide(tagged_sent, ne)

  def think(self, pattern, tagged_sent):
    # Match tagged sentence against combinations of POS tags, words in any order: (?=.*\bword\b)(?=.*\bADJ\bNOUN\b).*
    r = re.compile('(?=.*\\b' + pattern.replace('  ', '\\b.*\\b').replace(' ', '\\b)(?=.*\\b') + '\\b).*')
    return r.search(tagged_sent)

  def decide(self, tagged_sent, named_entity):
    for task in conf.get_property('tasks'):
      for pattern in conf.get_property('tasks')[task]:
        # If sentence matches any pattern, dynamtically create class
        if self.think(pattern, tagged_sent):
          # Split module name and class name with dot
          module = importlib.import_module(self.MODULE_BASE_PATH + task.rsplit('.', 1)[0])
          instance = getattr(module, task.rsplit('.', 1)[1])()
          print(instance)

          # Search whether task_memory contains the same class instance
          _run = False
          for mem in self.task_memory:
            if type(instance) == type(mem):
              mem.run(self, tagged_sent, named_entity)
              _run = True
              break
          if not _run:
            # If not exists, store new class instance in task_memory
            self.task_memory = [instance.run(self, tagged_sent, named_entity)] + self.task_memory
          
          break
