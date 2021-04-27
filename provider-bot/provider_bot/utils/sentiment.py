import pymorphy2
import re

tones = {}

morph = pymorphy2.MorphAnalyzer(lang='uk')

with open('./tone-dict-uk.tsv') as tone_dict:
    for line in tone_dict.readlines():
        line = line.split('\t')
        normal_form = morph.parse(line[0])[0].normal_form
        tones[normal_form] = int(line[1])


def tone(text):
    score = 0
    count = 0
    words = re.sub('\!\?\,\;\.\_', '', text).lower().split(' ')
    for idx, word in enumerate(words):
        normal_form = morph.parse(word)[0].normal_form
        if normal_form in tones:
            #print(normal_form)
            word_score = tones.get(normal_form, 0)
            score += -word_score if idx > 0 and words[idx - 1].lower() == 'не' else word_score
            count += 1
    return score / count if count else 0
