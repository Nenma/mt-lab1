import re

groups = ['masc_noun', 'fem_noun', 'verb', 'determiner',
          'adjective', 'conjunction', 'preposition']


def read_vocabulary():
    contents = open('lexicon.txt', 'r').read()
    sections = contents.split('\n\n')
    sections = sections[1:-1]  # get rid of the title and proper nouns

    vocabulary = {
        'masc_noun': {},
        'fem_noun': {},
        'verb': {},
        'determiner': {},
        'adjective': {},
        'conjunction': {},
        'preposition': {}
    }

    for i, section in enumerate(sections):
        section = section.split(' : \n')[1]
        section = section.strip().split('\n')
        for translation in section:
            translation = translation.strip().lower().split(' -> ')
            vocabulary[groups[i]][translation[0]] = translation[1]

    return vocabulary


def read_rules():
    contents = open('rules.txt', 'r').read()

    # replace the known used POS with the internal format
    contents = contents.replace('ADJ', 'adjective') \
        .replace('N', 'noun') \
        .replace('Masc noun', 'masc_noun') \
        .replace('Fem noun', 'fem_noun') \
        .replace('DET', 'determiner') \
        .replace('V', 'verb') \
        .replace('V', 'verb')

    sections = contents.split('\n\n')

    rewriting_rules = sections[0].split('\n')[1:]
    for i, _ in enumerate(rewriting_rules):
        rewriting_rules[i] = rewriting_rules[i].lower(
        ).strip().replace(' ', '')
        rewriting_rules[i] = rewriting_rules[i].replace('+', ' ').split('->')
        rewriting_rules[i] = (rewriting_rules[i][0], rewriting_rules[i][1])

    pos_rules = sections[1].split('\n')[1:]
    for i, _ in enumerate(pos_rules):
        pos_rules[i] = pos_rules[i].lower().strip().replace(' ', '')
        pos_rules[i] = pos_rules[i].replace('+', ' ').split('->')
        pos_rules[i] = (pos_rules[i][0], pos_rules[i][1])

    return rewriting_rules, pos_rules


def is_in_vocabulary(vocabulary, word):
    word = word.lower()
    for i in range(7):
        if word in vocabulary[groups[i]]:
            return True
    return False


# If the word is in the vocabulary, get the translation and POS
# If not, we assume it's a proper noun and return it by itself
def get_translation_and_pos(vocabulary, word):
    word = word.lower()
    for i in range(7):
        if word in vocabulary[groups[i]]:
            return vocabulary[groups[i]][word], groups[i]
    return word, 'proper_noun'


def morph_sentence(rewriting_rules, pos_rules, vocabulary, sentence):
    original_sentence = sentence[:-1].lower()
    original_sentence_list = original_sentence.split()

    rewritten_ver = []
    for word in original_sentence_list:
        _, pos = get_translation_and_pos(vocabulary, word)
        rewritten_ver.append(pos)
    rewritten_ver = ' '.join(rewritten_ver)

    for pos_rule in pos_rules:
        right_side = pos_rule[0].split()
        if is_in_vocabulary(vocabulary, right_side[0]):
            occurences = [
                i for i, w in enumerate(original_sentence_list)
                if w == right_side[0]
            ]
            print('first', right_side[0], occurences)
        else:
            occurences = [
                i for i, w in enumerate(original_sentence_list)
                if w == right_side[1]
            ]
            print('second', right_side[1], occurences)


def translate_sentence(vocabulary, sentence):
    full_translation = ''
    for word in sentence[:-1].lower().split():
        translation, _ = get_translation_and_pos(vocabulary, word)
        full_translation += translation + ' '
    return full_translation


if __name__ == '__main__':
    vocabulary = read_vocabulary()
    rewriting_rules, pos_rules = read_rules()
    print(rewriting_rules)
    print(pos_rules)
    print()

    sentence = str(input('Sentence to translate: '))
    # translation = translate_sentence(vocabulary, sentence)
    # print('Translation:', translation)
    test = morph_sentence(rewriting_rules, pos_rules, vocabulary, sentence)
