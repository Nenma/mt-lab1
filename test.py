text = input('Please type your sentence: ')
sentence = text.split()
word = input('Thank-you, now type your word: ')

if word in sentence:
    print('This word occurs in the places:')
    print([i+1 for i, w in enumerate(sentence) if w.lower() == word.lower()])
elif word not in sentence:
    print('Sorry, ' + word + ' does not appear in the sentence.')
