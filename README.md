# Lucia

Designed with privacy at the top of mind, Lucia is an offline virtual assistant that does not record your voice data for targeted advertising. Customize features from changing the tone and speed to creating your voice command.

## Table of Contents

- [Getting Started](#getting-started)
  - [Ready to Use](#ready-to-use)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
  - [List of Voice Commands](#list-of-voice-commands)
- [API](#api)
  - [Brain](#brain)
  - [Creating Voice Command](#creating-new-voice-command)
- [Issues and Contributions](#issues-and-contributions)

## Getting Started

### Ready to Use

Get Lucia with all prerequisites installed at <a href="../../releases">Releases</a>. To start using Lucia, see <a href="#usage">Usage</a>.

### Prerequisites
* Create and activate a virtual environment
```
$ virtualenv -p python $HOME/lucia/tmp/venv
$ source $HOME/lucia/tmp/venv/bin/activate
$ cd $HOME/lucia
```
* Get DeepSpeech pretrained model. For the latest version, refer to <a href="https://github.com/mozilla/deepspeech/releases">DeepSpeech</a>
```
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.pbmm
wget https://github.com/mozilla/DeepSpeech/releases/download/v0.9.1/deepspeech-0.9.1-models.scorer
```
* Install <a href="https://github.com/mozilla/DeepSpeech">DeepSpeech</a>: `pip install -U deepspeech`
* Install <a href="https://www.nltk.org/data.html">NLTK</a>: `pip install -U nltk`
* Download nltk packages from <a href="../../releases">Releases</a>. Configure nltk packages path in <a href="/conf.yaml">conf.yaml</a>:
```yaml
nltk:
  data_dir: /home/<user>/lucia/nltk_data
```
* Install <a href="https://spacy.io/">spaCy</a> and model
```
$ pip install -U spacy
$ python -m spacy download en_core_web_sm
```
* Install <a href="https://pypi.org/project/SpeechRecognition/">SpeechRecognition</a>: `pip install -U speechrecognition`
* Install <a href="http://people.csail.mit.edu/hubert/pyaudio/">PyAudio</a>
```
$ yum install portaudio portaudio-devel
$ pip install -U pyaudio
```
* Install [Duckling](https://github.com/facebook/duckling) [wrapper](https://github.com/FraBle/python-duckling): `pip install -U duckling`
* Install <a href="https://github.com/jpype-project/jpype">jpype</a>: `pip install jpype==0.7.5`
* Install <a href="https://github.com/espeak-ng/espeak-ng/">eSpeak</a>: `yum install espeak-ng`
* Install <a href="https://github.com/yaml/pyyaml">yaml parser</a>: `pip install -U pyyaml`

### Usage

1. Activate virtual environment

```
$ source $HOME/lucia/tmp/venv/bin/activate
```

2. Run the command: `(venv) $ python lucia.py`
3. Say *"Hello, Lucia!"* See <a href="#list-of-voice-commands"> List of Voice Commands</a> for what Lucia can do.

### List of Voice Commands

<details open><summary>List of voice commands</summary>

Task | Module | Command Examples
-|-|-
volume control | volume | "Set the volume to 20", "Volume 20"<br>"Volume up/down", "Increase/decrease volume by 5"<br>"Turn up/down to 10"<br>"Mute/unmute"<br>"Shut up"

</details>


## API

### Brain

<a href="/lucia/brain.py">Brain.py</a> enables Lucia to listen, understand, think and speak.
- listen: Lucia converts speech to text. <!--Lucia is set to activate when hearing the **wake word**. You can change wake word by voice command or in <a href="/conf.yaml">conf.yaml</a>-->
- understand: Lucia assigns grammar tagsets (e.g., <a href="https://www.nltk.org/book/ch05.html#tab-universal-tagset">universal POS tag</a>, IOB tag, NER tag) to words.
- think: Lucia converts text to regular expression.
- decide: Lucia searches for combinations of grammar tags and words and initiates task upon finding match.
- speak: Lucia speaks text out loud. You can change Lucia's voice in <a href="/conf.yaml">conf.yaml</a>
```yaml
espeak:
  gender: f # 'm' for male or 'f' for female
  pitch: 2  # Range 0-7
```

### Creating Voice Command

1. Create new python file in <a href="/lucia/tasks">/lucia/tasks</a> as the following:

```python
class <ClassName>:
  def __init__(self):
    raise NotImplementedError

  def run(self, brain, tag, ne):
    """
    Args:
      brain: A Brain instance
      tag: Spring representation for tagged sentences that consist of POS, IOB, NER tags
      ne: List of named entity tags. Item is formatted as [word, starting position, ending position, NER tag, {parsed data}]
    Return:
      Return self
    """
    raise NotImplementedError
```

2. Add module and class names to the list of <code>tasks</code> in <a href="/conf.yaml">conf.yaml</a>

```yaml
tasks:
  <module_name>.<ClassName>:
    - NOUN  left right
    - (ketchup|mustard)
```

- Filename and class name should be lowercase and contain no whitespace

3. In the following lines with a tab indent, add one or more <i>rule</i> of combinations of POS tags and words  
    <p>
    e.g., the rule <code>NOUN&nbsp;&nbsp;left&nbsp;right</code> is converted to regular expression:<br>
    <code>(?=.*\\bNOUN\\b\\s\\bleft\\b)(?=.*\\bright\\b).*</code>
    <br>If this matches what user said, the associated task is initiated; otherwise, the next rule is scanned
    </p>
- POS tags should be uppercase, whereas words should be lowercase, e.g. `NOUN` is matches one noun
- Single whitespace matches words in any order, whereas double whitespace enforces order. e.g., <code>NOUN&nbsp;&nbsp;left&nbsp;right</code> matches *"Lucia, triangle left right"* and *"Lucia, right square left"*

- Rules are allowed to use regular expression. e.g., `(ketchup|mustard)` matches *"Lucia, ketchup"* and *"Lucia, mustard"*

## Issues and Contributions

If you have a bug or feature request, please create an [issue](https://github.com/jayinsf/sandbox/issues). See the list of [contributors](https://github.com/jayinsf/sandbox/graphs/contributors) who participated in this project.  
Consider donating your voice and validating donated voices at [Common Voice](https://commonvoice.mozilla.org/) that is used to train Lucia's voice recognition engine.
