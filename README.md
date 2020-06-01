# Aws_transcribe_parser
Parses .json files into word-level, sentence-level etc. files by making use of the timestamps.

### Usage
```
usage: aws_transcribe_parser.py [-h] [-d DATA_PATH]

Parser of AWS .jsons to .csv on sentence- and word-level

optional arguments:
  -h, --help            show this help message and exit
  -d DATA_PATH, --data_path DATA_PATH
                        specify the source data path to the .jsons
```
Example
```
   python aws_transcribe_parser.py -d './aws_transcribe/' 
```
For Windows replace by '.\aws_transcribe\'

### Requirements
Standard libraries: re, os, glob, json, numpy, pandas, interval, collections

### Output
Produces one file for each .json and section.
#### word-level.csv
```
start,end,confidence,word,speaker
22.94,23.07,0.841,Wenn,spk_1
23.07,23.17,0.994,ich,spk_1
23.17,23.41,0.984,aber,spk_1

,,0.0,.,
```
#### sentence-level.csv
```
start,end,sentences,speaker
22.94,74.35,"Wenn ich aber schon, ....",spk_1
75.14,79.92,Der Grund warum die,spk_1
```
Plus speaker detection .csv and plain text as .txt
