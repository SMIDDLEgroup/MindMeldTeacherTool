import pymorphy2
import re

tones = {}

morph = pymorphy2.MorphAnalyzer(lang='uk')

with open('./tone-dict-uk.tsv') as tone_dict:
    for line in tone_dict.readlines():
        line = line.split('\t')
        normal_form = morph.parse(line[0])[0].normal_form
        tones[normal_form] = int(line[1])

with open('./tone-dict-uk.tsv', 'a') as tone_dict:
    for word in tones:
        if word.endswith('ий'):
            other_form = word.replace('ий', 'о')
            if other_form not in tones:
                new_record = '\t'.join([other_form, str(tones[word])]) + '\n'
                tone_dict.write(new_record)
