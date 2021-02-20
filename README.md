# StoryGraphBot

Twitter bot based on StoryGraphToolkit 


## Requirement
```
https://github.com/oduwsdl/storygraph-toolkit.git
```

## Usage
### Basic usage:
```
$ cd storygraphbot
$ ./storygraph_bot.py {options}

options:
--start-datetime            "YYYY-mm-DD HH:MM:SS" datetime for filtering graphs based on datetime
--end-datetime              "YYYY-mm-DD HH:MM:SS" datetime for filtering graphs based on datetime
-a, --activation-degree     To set min. avg degree criteria for selecting top story
-ol, --overlap-threshold    To set min. overlap coefficent between stories
```
### Output:
```
The threads(stories) are stored in the output folder. 
```


