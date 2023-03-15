
ruDictionary = './data/dictionary/russian.txt'
enDictionary = './data/dictionary/english.txt'
ruGameDictionary = './data/dictionary/game_RU.txt'
enGameDictionary = './data/dictionary/game_EN.txt'
userDictionary = './data/dictionary/user.txt'

dicList = [ruDictionary, enDictionary, ruGameDictionary, enGameDictionary, userDictionary]
wordList = []

for dic in dicList:
    try:
        with open(dic, 'r') as d:
            words = d.readlines()

            for i in range(len(words)):
                words[i] = words[i].replace('\n', '').split('/')[0]

            wordList += words
    except FileNotFoundError: pass

def spellCheck(string4Check):

    splitters = '!\'"@#$%^&*()_-+=}]{[|\\:;?/>.<,\n\t№'

    for sign in splitters:
        string4Check = string4Check.replace(sign, ' ').replace('  ', ' ')

    wordL = string4Check.split(' ')
    errorList = []

    for w in wordL:
        if w.lower() not in wordList and len(w) > 0:
            try:
                float(w)
            except ValueError:
                errorList.append(w)

    return errorList

def addWords(wl):
    for word in wl:
        with open(userDictionary, 'a') as ud:
            ud.write(f'{word.lower()}\n')

        wordList.append(word.lower())
        print(f'Слово {word} добавлено в словарь!')

# print(spellCheck())
