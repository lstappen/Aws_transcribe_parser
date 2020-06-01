#!/usr/bin/env python
# coding: utf-8
# created by Lukas Stappen - check licence file for usage and duplication

import re,os,glob,json
import numpy as np
import pandas as pd
from interval import Interval as I
from collections import defaultdict


import argparse
parser = argparse.ArgumentParser(description = 'Parser of AWS .jsons to .csv on sentence- and word-level')
parser.add_argument('-d', '--data_path', type = str, dest = 'data_path', required = False, action = 'store', 
                    default = './aws_transcribe/', 
                    help = 'specify the source data path to the .jsons')   #Windows: '.\aws_transcribe\'          
args = parser.parse_args()

jsons = sorted(glob.glob(args.data_path+'*.json'))
if len(jsons) < 1:
    print("No .jsons found. Make sure your .json files are in ", args.data_path)
    exit()

# Output folders
for dir_ in ['aws_transcription', 'word_timestamp','speaker_ident','sentence_timestamp' ]:
    path = '.'+os.path.sep+dir_
    if not os.path.exists(path):
        print("Create {}".format(path))
        os.makedirs(path)

print("json files to transform: ", jsons)
for json_path in jsons:
    trans_path = json_path.replace('aws_transcribe','aws_transcription').replace('.json','.txt')
    word_path = json_path.replace('aws_transcribe','word_timestamp').replace('.json','.csv').replace('custom','word')
    speaker_path = json_path.replace('aws_transcribe','speaker_ident').replace('.json','.csv').replace('custom','speaker')
    sen_path = json_path.replace('aws_transcribe','sentence_timestamp').replace('.json','.csv').replace('custom','sentence')

    word_folder = os.path.sep.join(word_path.split(os.path.sep)[:-1])
    spk_folder = os.path.sep.join(speaker_path.split(os.path.sep)[:-1])
    sen_folder = os.path.sep.join(sen_path.split(os.path.sep)[:-1])
    if not os.path.exists(word_folder):
        os.mkdir(word_folder)
    if not os.path.exists(spk_folder):
        os.mkdir(spk_folder)
    if not os.path.exists(sen_folder):
        os.mkdir(sen_folder)
        
    # read in the aws json file
    with open(json_path,encoding='utf-8') as json_file:
        data = json.load(json_file)

    # extract the transcription part with recovering the custom pronunciation vocabulary    
    with open(trans_path, "w",encoding='utf-8') as text_file:
        trans = data['results']['transcripts'][0]['transcript']
        text_file.write(trans)

    # word and it's timestamp
    word_timestamp_dict = defaultdict(list)
    count = 0 # for correspondence/alignment with word-weise speaker label
    speaker_items = [i for dic in data['results']['speaker_labels']['segments'] for i in dic['items']]

    for item in data['results']['items']:
        if item['type'] == 'pronunciation':
            word_timestamp_dict['start'].append(item['start_time'])
            word_timestamp_dict['end'].append(item['end_time'])
            word_timestamp_dict['confidence'].append(item['alternatives'][0]['confidence'])
            word = item['alternatives'][0]['content'] 
            word_timestamp_dict['word'].append(word)
            # align the timestamp
            assert item['start_time'] == speaker_items[count]['start_time'] and item['end_time'] == speaker_items[count]['end_time']
            word_timestamp_dict['speaker'].append(speaker_items[count]['speaker_label'])
            count += 1
        else:
            word_timestamp_dict['start'].append('')
            word_timestamp_dict['end'].append('')
            word_timestamp_dict['confidence'].append(item['alternatives'][0]['confidence'])
            word_timestamp_dict['word'].append(item['alternatives'][0]['content'])
            word_timestamp_dict['speaker'].append('')

    word_timestamp_df = pd.DataFrame(word_timestamp_dict)
    word_timestamp_df.to_csv(word_path,index=False)

    #sentence and it's timestamp and label
    index_sep = sorted(set([0]+[i for i in word_timestamp_df.index if word_timestamp_df.iloc[i]['word'] in ['.','!','?']]+[word_timestamp_df.index[-1]]))
    sen_timestamp_dict = defaultdict(list)
    for ii, index in enumerate(index_sep):
            if index==0:
                sen = ' '.join(word_timestamp_df.iloc[index_sep[ii]:index_sep[ii+1]+1]['word'])
                start = word_timestamp_df.iloc[index_sep[ii]]['start']
                end = word_timestamp_df.iloc[index_sep[ii+1]-1]['end']
                speaker = word_timestamp_df.iloc[index_sep[ii]]['speaker']
            elif index != word_timestamp_df.index[-1]:
                sen = ' '.join(word_timestamp_df.iloc[index_sep[ii]+1:index_sep[ii+1]+1]['word'])
                start = word_timestamp_df.iloc[index_sep[ii]+1]['start']
                flop_1st_end = word_timestamp_df.iloc[index_sep[ii+1]]['end'] 
                end = word_timestamp_df.iloc[index_sep[ii+1]-1]['end'] if flop_1st_end=='' else flop_1st_end
                speaker = word_timestamp_df.iloc[index_sep[ii]+1]['speaker']
            sen = sen.replace(' ,',',').replace(' .','.').replace(' !','!').replace(' ?','?')
            sen_timestamp_dict['sentences'].append(sen)
            sen_timestamp_dict['start'].append(float(start))
            sen_timestamp_dict['end'].append(float(end))
            sen_timestamp_dict['speaker'].append(speaker)
    sen_timestamp_df = pd.DataFrame(sen_timestamp_dict).drop_duplicates('sentences')
    sen_timestamp_df.to_csv(sen_path, index=False,columns=['start','end','sentences','speaker'])
    
    # speaker info extraction
    speaker_ident_dict = defaultdict(list)
    for item in data['results']['speaker_labels']['segments']:
        speaker_ident_dict['start'].append(item['start_time'])
        speaker_ident_dict['end'].append(item['end_time'])
        speaker_ident_dict['speaker'].append(item['speaker_label'])

    speaker_ident_df = pd.DataFrame(speaker_ident_dict)
    speaker_ident_df.to_csv(speaker_path,index=False)   
    
    print(json_path.split(os.path.sep)[-1], 'finished.')

