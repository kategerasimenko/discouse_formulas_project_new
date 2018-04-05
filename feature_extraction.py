import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()

def PREP_delete_speakers(text,delete_speakers):
    if delete_speakers == 'y':
        new_text = re.sub('\n *[А-ЯЁ ]+?(?: ?\(.+?\))? ?[.:]', '\n_SPEAKER_ ', text)
        if len(new_text) > len(text) - 500:
            new_text = re.sub('\n *[А-яЁё]+?(?: ?\(.+?\))? ?[.:]','\n_SPEAKER_ ',text)
            if len(new_text) > len(text) - 500:
                print('speakers deleted earlier')
                new_text = text.replace('\n\t','\n_SPEAKER_ ')
            else:
                print('speakers not in uppercase')
    else:
        new_text = text.replace('\n','\n_SPEAKER_ ')
    return new_text

def get_features(tokens,target):
    pass
