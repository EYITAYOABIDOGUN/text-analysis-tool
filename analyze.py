from random_username.generate import generate_username
import re, nltk, json
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('vader_lexicon')

wordLemmatizer = WordNetLemmatizer()
stopWords = set(stopwords.words('english'))
sentimentAnalyzer = SentimentIntensityAnalyzer()


# Welcome User
def welcomeUser():
    print("\nWelcome to the text analysis tool, I will mine and analyze a body of text from a file you give me!")


# Get Username
def getUsername():
    maxAttempts = 3
    attempts = 0

    while attempts < maxAttempts:
        if attempts == 0:
            inputPrompt = "\nTo begin, please enter your username:\n"
        else:
            inputPrompt = "\nPlease try again:\n"

        usernameFromInput = input(inputPrompt)

        if len(usernameFromInput) < 5 or not usernameFromInput.isidentifier():
            print(
                "Your username must be at least 5 characters long, "
                "alphanumeric only (a-z/A-Z/0-9), have no spaces, "
                "and cannot start with a number!"
            )
        else:
            return usernameFromInput

        attempts += 1

    print(f"\nExhausted all {maxAttempts} attempts, assigning username instead...")
    return generate_username()[0]


# Greet the user
def greetUser(name):
    print("Hello, " + name)


# Get text from file
def getArticleText():
    f = open("files/article.txt", "r")
    rawText = f.read()
    f.close()
    return rawText.replace("\n", " ").replace("\r", "")


# Extract Sentences
def tokenizeSentences(rawText):
    return sent_tokenize(rawText)


# Extract Words
def tokenizeWords(sentences):
    words = []
    for sentence in sentences:
        words.extend(word_tokenize(sentence))
    return words


# Extract Key Sentences
def extractKeySentences(sentences, searchPattern):
    matchedSentences = []
    for sentence in sentences:
        if re.search(searchPattern, sentence.lower()):
            matchedSentences.append(sentence)
    return matchedSentences


# Average words per sentence
def getWordsPerSentence(sentences):
    totalWords = 0
    for sentence in sentences:
        totalWords += len(sentence.split(" "))
    return totalWords / len(sentences)


# POS mapping
posToWordnetTag = {
    "J": wordnet.ADJ,
    "V": wordnet.VERB,
    "N": wordnet.NOUN,
    "R": wordnet.ADV
}


def treebankPosToWordnetPos(partOfSpeech):
    posFirstChar = partOfSpeech[0]
    if posFirstChar in posToWordnetTag:
        return posToWordnetTag[posFirstChar]
    return wordnet.NOUN


# Cleanse words
def cleanseWordList(posTaggedWordTuples):
    cleansedWords = []
    invalidWordPattern = "[^a-zA-Z-+]"
    for word, pos in posTaggedWordTuples:
        cleansedWord = word.replace(".", "").lower()
        if (
            not re.search(invalidWordPattern, cleansedWord)
            and len(cleansedWord) > 1
            and cleansedWord not in stopWords
        ):
            cleansedWords.append(
                wordLemmatizer.lemmatize(cleansedWord, treebankPosToWordnetPos(pos))
            )
    return cleansedWords


# MAIN ANALYSIS FUNCTION (this is what stockAnalyze.py uses)
def analyzeText(textToAnalyze):
    articleSentences = tokenizeSentences(textToAnalyze)
    articleWords = tokenizeWords(articleSentences)

    stockSearchPattern = "[0-9]|[%$€£]|thousand|million|billion|trillion|profit|loss"
    keySentences = extractKeySentences(articleSentences, stockSearchPattern)
    wordsPerSentence = getWordsPerSentence(articleSentences)

    wordsPosTagged = nltk.pos_tag(articleWords)
    articleWordsCleansed = cleanseWordList(wordsPosTagged)

    separator = " "
    wordCloudFilePath = "results/wordcloud.png"
    WordCloud(
        width=1000,
        height=700,
        background_color="white",
        colormap="Set3",
        collocations=False
    ).generate(separator.join(articleWordsCleansed))

    sentimentResult = sentimentAnalyzer.polarity_scores(textToAnalyze)

    finalResult = {
        "data": {
            "keySentences": keySentences,
            "wordsPerSentence": round(wordsPerSentence, 1),
            "sentiment": sentimentResult,
            "wordCloudFilePath": wordCloudFilePath
        },
        "metadata": {
            "sentencesAnalyzed": len(articleSentences),
            "wordsAnalyzed": len(articleWordsCleansed)
        }
    }

    return finalResult


def runAsFile():
    welcomeUser()
    username = getUsername()
    greetUser(username)

    articleTextRaw = getArticleText()
    articleTextRaw = articleTextRaw.encode("ascii", "ignore").decode()
    analyzeText(articleTextRaw)
