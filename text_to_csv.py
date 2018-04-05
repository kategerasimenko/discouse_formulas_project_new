from feature_extraction import *
from nltk.tokenize.treebank import TreebankWordTokenizer
from nltk.tokenize import sent_tokenize
import pandas as pd
import pymorphy2
import html
import csv
import re
import os

CONTEXT_WINDOW = (-5, 5)

class CustomizedTreebankWordTokenizer():
    def __init__(self):
        self.tokenizer = TreebankWordTokenizer()
        self.tokenizer.PARENS_BRACKETS = (re.compile(r'[\]\[\(\)\<\>]|[\{\}]+'), r' \g<0> ')

        # See discussion on https://github.com/nltk/nltk/pull/1437
        # Adding to TreebankWordTokenizer, the splits on
        # - chervon quotes u'\xab' and u'\xbb' .
        # - unicode quotes u'\u2018', u'\u2019', u'\u201c' and u'\u201d'
        
        improved_open_quote_regex = re.compile(u'([«“‘])', re.U)
        improved_close_quote_regex = re.compile(u'([»”’])', re.U)
        improved_punct_regex = re.compile(r'([^\.])(\.)([\]\)}>"\'' u'»”’ ' r']*)\s*$', re.U)
        self.tokenizer.STARTING_QUOTES.insert(0, (improved_open_quote_regex, r' \1 '))
        self.tokenizer.ENDING_QUOTES.insert(0, (improved_close_quote_regex, r' \1 '))
        self.tokenizer.PUNCTUATION.insert(0, (improved_punct_regex, r'\1 \2 \3 '))


    def tokenize(self,text):
        return [x for y in sent_tokenize(text) for x in self.tokenizer.tokenize(y)]


def annotate_tokens(tokens,filename):
    """
    POS tagging (pymorphy2)
    Target array - BILOU:
        B for beginning
        I for in the middle
        L for ending
        U for one word being a formula
        O for non-entity tokens
    """
    formula = False
    formula_length = 0
    word_num = 1
    annotated_tokens = []
    target = []
    for token in tokens:
        if token == '{{':
            formula = True
            continue
        elif token == '}}':
            if formula:
                if formula_length == 1:
                    target[-1] = 'U'
                else:
                    target[-1] = 'L'
                formula = False
                formula_length = 0
            continue
        elif token == '_SPEAKER_':
            word_num = 1
            continue
        token_ana = morph.parse(token.lower())[0]
        token_pos = token_ana.tag.POS
        if not token_pos:
            token_pos = str(token_ana.tag).split(',')[0]
        annotated_tokens.append((token.lower(),token_ana.normal_form,token_pos,word_num,filename))
        word_num += 1
        if formula:
            if not formula_length:
                target.append('B')
            else:
                target.append('I')
            formula_length += 1
        else:
            target.append('O')
    return annotated_tokens,target
                
    
        

tokenizer = CustomizedTreebankWordTokenizer()
morph = pymorphy2.MorphAnalyzer()

delete_speakers = input('Delete speakers? [y/n]')


#открыть и закрыть файлы для записи, чтобы при новом запуске программы файл создавался с нуля, а не добавлялся к старому
csvtarget = open('train_target.csv', 'w', encoding='utf-8-sig')
row0 = ['Target']
writer = csv.writer(csvtarget, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
writer.writerow(row0)
csvtarget.close()

filenames = os.listdir('./texts')
all_features = []

for filename in filenames:
    if filename.endswith('.txt'):
        try:
            filein = open('./texts/'+filename, 'r', encoding='cp1251')
            rawtext = filein.read()
            filein.close()
        except:
            filein = open('./texts/'+filename, 'r', encoding='utf-8-sig')
            rawtext = filein.read()
            filein.close()
        print(filename)
        rawtext = html.unescape(rawtext)
        rawtext = rawtext.replace('¬','')
        rawtext = PREP_delete_speakers(rawtext,delete_speakers)
        tokens = tokenizer.tokenize(rawtext)
        annotated_tokens,target = annotate_tokens(tokens,filename)
        features = get_features(annotated_tokens,target,context_window=CONTEXT_WINDOW)
        all_features.append(features)


        # формируется целевой вектор
        csvtarget = open('train_target.csv', 'a', encoding='utf-8-sig')
        writer = csv.writer(csvtarget, delimiter=';', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_NONNUMERIC)
        for i in target:
            row = [i]
            writer.writerow(row)
        csvtarget.close()

full_data = pd.concat(all_features,ignore_index=True)
full_data.to_csv('train_data.csv',encoding='utf-8-sig')
