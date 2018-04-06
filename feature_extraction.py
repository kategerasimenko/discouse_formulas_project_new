import re
import pandas as pd


def PREP_delete_speakers(text, delete_speakers):
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


def get_possible_window(current_index, window, len_list):
    if current_index + window[0] < 0:
        start = 0
    else:
        start = current_index + window[0]
    if current_index + window[-1]+1 > len_list:
        finish = len_list
    else:
        finish = current_index+window[-1]+1
    return range(start, finish)


def make_column_names(feature_names, part_window):
    result_names = []
    for i in part_window:
        for name in feature_names:
            result_names.append('_'.join([name, str(i)]))
    return result_names


def get_features(tokens, target, context_window):
    window = range(context_window[0], context_window[1] + 1)
    token_zero_index = window.index(0)
    window_left = window[0:token_zero_index]
    window_right = window[token_zero_index+1: len(window)]
    left_names = ['Text', 'Lemma', 'POS', 'Target']
    left_columns = make_column_names(left_names, window_left)
    right_names = ['Text', 'Lemma', 'POS']
    right_columns = make_column_names(right_names, window_right)
    current_columns = ['Text', 'Lemma', 'POS', 'Word_num', 'Text_id']
    all_columns = left_columns+current_columns+right_columns
    all_feats = []
    for i in range(len(tokens)):
        possible_window = get_possible_window(i, window, len(tokens))
        left_features = []
        right_features = []
        current_features = list(tokens[i])
        for n in window_left:
            token_index = i + n
            if token_index not in possible_window:
                left_features.extend([None]*len(left_names))
            else:
                left_features.extend([tokens[token_index][j] for j in range(0, 3)])
                left_features.append(target[i + n])
        for n in window_right:
            token_index = i + n
            if token_index not in possible_window:
                right_features.extend([None]*len(right_names))
            else:
                right_features.extend([tokens[token_index][j] for j in range(0, 3)])
        all_feats.append(left_features+current_features+right_features)
    result_df = pd.DataFrame(all_feats,columns=all_columns)
    return result_df
