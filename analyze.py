from random_username.generate import generate_username
import re, nltk
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


def tokenizeSentences(rawText):
    return sent_tokenize(rawText)


def tokenizeWords(sentences):
    words = []
    for sentence in sentences:
        words.extend(word_tokenize(sentence))
    return words


def extractKeySentences(sentences, searchPattern):
    matched = []
    for sentence in sentences:
        if re.search(searchPattern, sentence.lower()):
            matched.append(sentence)
    return matched


def getWordsPerSentence(sentences):
    if not sentences:
        return 0
    totalWords = 0
    for sentence in sentences:
        totalWords += len(sentence.split(" "))
    return totalWords / len(sentences)


posToWordnetTag = {
    "J": wordnet.ADJ,
    "V": wordnet.VERB,
    "N": wordnet.NOUN,
    "R": wordnet.ADV
}


def treebankPosToWordnetPos(pos):
    return posToWordnetTag.get(pos[0], wordnet.NOUN)


def cleanseWordList(posTaggedWordTuples):
    cleansedWords = []
    invalidWordPattern = "[^a-zA-Z-+]"
    for word, pos in posTaggedWordTuples:
        cleaned = word.replace(".", "").lower()
        if (
            not re.search(invalidWordPattern, cleaned)
            and len(cleaned) > 1
            and cleaned not in stopWords
        ):
            cleansedWords.append(
                wordLemmatizer.lemmatize(cleaned, treebankPosToWordnetPos(pos))
            )
    return cleansedWords


def analyzeText(textToAnalyze):
    articleSentences = tokenizeSentences(textToAnalyze)
    articleWords = tokenizeWords(articleSentences)

    stockSearchPattern = "[0-9]|[%$€£]|thousand|million|billion|trillion|profit|loss"
    keySentences = extractKeySentences(articleSentences, stockSearchPattern)
    wordsPerSentence = getWordsPerSentence(articleSentences)

    if not articleWords:
        return {
            "data": {
                "keySentences": [],
                "wordsPerSentence": 0,
                "sentiment": {},
                "wordCloudFilePath": None
            },
            "metadata": {
                "sentencesAnalyzed": 0,
                "wordsAnalyzed": 0
            }
        }

    wordsPosTagged = nltk.pos_tag(articleWords)
    cleansedWords = cleanseWordList(wordsPosTagged)

    WordCloud(
        width=1000,
        height=700,
        background_color="white",
        collocations=False
    ).generate(" ".join(cleansedWords))

    sentimentResult = sentimentAnalyzer.polarity_scores(textToAnalyze)

    return {
        "data": {
            "keySentences": keySentences,
            "wordsPerSentence": round(wordsPerSentence, 1),
            "sentiment": sentimentResult,
            "wordCloudFilePath": "results/wordcloud.png"
        },
        "metadata": {
            "sentencesAnalyzed": len(articleSentences),
            "wordsAnalyzed": len(cleansedWords)
        }
    }
