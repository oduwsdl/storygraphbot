# StoryGraphBot

StoryGraphBot is [StoryGraph's](storygraph.cs.odu.edu/) Twitter bot that tracks and tweets about developing stories in near-realtime.

## Requirements/Installation
This bot requires the installation of [storygraph-toolkit](https://github.com/oduwsdl/storygraph-toolkit.git), and can be installed as follows:
```
$ git clone https://github.com/oduwsdl/storygraphbot.git
$ cd storygraphbot/; pip install .; cd ..; rm -rf storygraphbot;
```

## Usage
This bot can be used in two primary ways; the command line and a script
### Command-line (basic) usage:
```
$ sgbot [options]

optional:
-h, --help                            show this help message and exit
--start-datetime=''                   "YYYY-mm-DD HH:MM:SS" datetime for filtering graphs
--end-datetime=''                     "YYYY-mm-DD HH:MM:SS" datetime for filtering graphs
-a, --activation-degree=4.0           The minimum average degree for selected top stories
--cleanup                             Delete cache and intermediate files
-ol, --overlap-threshold=0.9          The similarity threshold for matching two stories
-p, --sgbot-path='./'                 Path for storing all bot-associated files (e.g., storing stories)
```
Output:
Coming soon..
### Python script usage:
Coming soon...
```
from storygraph_bot.backbone import sgbot
...
```