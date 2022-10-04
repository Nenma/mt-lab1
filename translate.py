# Group categories
groups = ['masc_noun', 'fem_noun', 'verb', 'determiner',
          'adjective', 'conjunction', 'preposition']


# Read the translation from the lexicon to determine the vocabulary
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


# Read the rules in two categories: rewriting rules and POS identification rules
# For each of them, keep the rules as an array of tuples
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


# Check whether a word is part of the vocabulary or not
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


# First pass of translating the sentence, applying the POS identification rules
def apply_pos_rules(pos_rules, vocabulary, sentence):
    sentence_list = sentence.split()
    translation_list = sentence.split()

    for rule in pos_rules:
        left = rule[0].split()  # left side of the rule (before ->)
        right = rule[1].split()  # right side of the rule (after ->)
        # For cases like TRANSLATABLE_WORD + GROUP_CATEGORY -> ...
        if is_in_vocabulary(vocabulary, left[0]):
            # list of indexes at which the word is present in the sentence
            occurences = [
                i for i, w in enumerate(sentence_list)
                if w == left[0]
            ]
            if occurences:
                for i in occurences:
                    if i+1 < len(sentence_list):
                        next_word_translation, next_word_pos = get_translation_and_pos(
                            vocabulary, sentence_list[i+1]
                        )
                        # We match on the left side of the rule
                        # (plus account for rules with unspecified noun)
                        if next_word_pos == left[1] \
                                or (next_word_pos in ['masc_noun', 'fem_noun'] and left[1] == 'noun'):
                            # For cases like ... -> TARGET_GROUP_CATEGORY + GROUP_CATEGORY
                            if right[0] in groups or right[0] == 'noun':
                                if right[0] == 'noun':
                                    right[0] = 'masc_noun'
                                pos_translation = vocabulary[right[0]][left[0]]
                                translation_list[i] = pos_translation
                            # For cases like ... -> TRANSLATION + GROUP_CATEGORY
                            else:
                                translation_list[i] = right[0]
                                translation_list[i+1] = next_word_translation
        # For cases like GROUP_CATEGORY + TRANSLATABLE_WORD -> ...
        else:
            occurences = [
                i for i, w in enumerate(sentence_list)
                if w == left[1]
            ]
            if occurences:
                for i in occurences:
                    if i > 0:
                        prev_word_translation, prev_word_pos = get_translation_and_pos(
                            vocabulary, sentence_list[i-1]
                        )
                        # We match on the left side of the rule
                        # (plus account for rules with unspecified noun)
                        if prev_word_pos == left[0] \
                                or (prev_word_pos in ['masc_noun', 'fem_noun'] and left[0] == 'noun'):
                            # For cases like ... -> GROUP_CATEGORY + TARGET_GROUP_CATEGORY
                            if right[1] in groups or right[1] == 'noun':
                                if right[1] == 'noun':
                                    right[1] = 'masc_noun'
                                pos_translation = vocabulary[right[1]][left[1]]
                                translation_list[i] = pos_translation
                            # For cases like ... -> GROUP_CATEGORY + TRANSLATION
                            else:
                                translation_list[i] = right[1]
                                translation_list[i-1] = prev_word_translation

    return ' '.join(translation_list)


# Second pass of translating the sentence, applying the rewriting rules
# (We take for granted that the inversion rule is the only one)
def apply_rewriting_rules(rewriting_rules, vocabulary, sentence):
    sentence_list = sentence.split()
    translation_list = sentence.split()

    # Create sentence equivalent POS list
    # (We do this because we assume all rewriting rules only use POS groups)
    pos_list = []
    for word in sentence_list:
        _, pos = get_translation_and_pos(vocabulary, word)
        pos_list.append(pos)

    for rule in rewriting_rules:
        left = rule[0].split()  # left side of the rule (before ->)

        for i in range(len(sentence_list) - 1):
            if (
                sentence_list[i] == left[0] or (sentence_list[i] in ['masc_noun', 'fem_noun'] and left[0] == 'noun')) \
                and (sentence_list[i+1] == left[1] or (sentence_list[i+1] in ['masc_noun', 'fem_noun'] and left[1] == 'noun')
                     ):
                aux = translation_list[i]
                translation_list[i] = translation_list[i+1]
                translation_list[i+1] = aux

    return ' '.join(translation_list)


# Translate the sentence word-by-word using the vocabulary
# If the word is not found in the vocabulary, it is assumed to already
# have been translated in previous passes, or is a proper noun
def translate_sentence(vocabulary, sentence):
    full_translation = ''
    for word in sentence.split():
        translation, _ = get_translation_and_pos(vocabulary, word)
        full_translation += translation + ' '
    return full_translation


if __name__ == '__main__':
    vocabulary = read_vocabulary()
    rewriting_rules, pos_rules = read_rules()

    sentence = str(input('Sentence to translate: '))
    # sentence = 'Mary reads a book.'
    # sentence = 'A book is under the table.'
    # sentence = 'Mary cut the sugar cane with a saw.'
    # sentence = 'Mary cut the sugar cane and is happy.'
    # sentence = 'The woman with a red cane saw a cat under the table and walks to the cat.'

    sentence = sentence[:-1].lower()  # ignore the dot at the end

    first_pass = apply_pos_rules(pos_rules, vocabulary, sentence)
    second_pass = apply_rewriting_rules(
        rewriting_rules, vocabulary, first_pass)
    final_pass = translate_sentence(vocabulary, second_pass)

    print(first_pass)
    print(second_pass)
    print(final_pass)
