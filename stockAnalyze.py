import yfinance as yf
import requests
from datetime import datetime
from bs4 import BeautifulSoup


def extractBasicInfo(data):
    keysToExtract = [
        'longName',
        'website',
        'sector',
        'fullTimeEmployees',
        'marketCap',
        'totalRevenue',
        'trailingEps'
    ]
    basicInfo = {}

    for key in keysToExtract:
        basicInfo[key] = data.get(key, '')

    return basicInfo


def getPriceHistory(company):
    historyDf = company.history(period='12mo')

    prices = historyDf['Open'].tolist()
    dates = historyDf.index.strftime('%Y-%m-%d').tolist()

    return {
        'price': prices,
        'date': dates
    }


def getEarningsDates(company):
    earningsDatesDf = company.earnings_dates

    allDates = earningsDatesDf.index.strftime('%Y-%m-%d').tolist()
    dateObjects = [datetime.strptime(date, '%Y-%m-%d') for date in allDates]

    currentDate = datetime.now()
    futureDates = [
        date.strftime('%Y-%m-%d')
        for date in dateObjects
        if date > currentDate
    ]

    return futureDates


def getCompanyNews(company):
    newsList = company.news
    allNewsArticles = []

    for newsDict in newsList:
        allNewsArticles.append({
            'title': newsDict.get('title', ''),
            'link': newsDict.get('link', '')
        })

    return allNewsArticles
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def extractCompanyNewsArticles(newsArticles):
    url = newsArticles[0]['link']
    page = requests.get(url, headers=headers)
    print(page.text)

# def extractCompanyNewsArticles(newsArticles):
# 	if not newsArticles:
# 		print("No news articles found")
# 		return

# 	url = newsArticles[0].get('link', '')

# 	if not url or not url.startswith('http'):
# 		print("News article has no valid URL")
# 		return

# 	try:
# 		response = requests.get(url, headers=headers, timeout=10)
# 		response.raise_for_status()

# 		soup = BeautifulSoup(response.text, 'html.parser')

# 		# Get all paragraph text
# 		paragraphs = soup.find_all('p')
# 		article_text = '\n'.join(p.get_text() for p in paragraphs)

# 		print("\n===== ARTICLE TEXT =====\n")
# 		print(article_text)

# 	except requests.RequestException as e:
# 		print("Failed to fetch article:", e)


def getCompanyStockInfo(tickerSymbol):
    # Get data from Yahoo Finance
    company = yf.Ticker(tickerSymbol)

    basicInfo = extractBasicInfo(company.info)
    priceHistory = getPriceHistory(company)
    futureEarningsDates = getEarningsDates(company)
    newsArticles = getCompanyNews(company)
    extractCompanyNewsArticles(newsArticles)

    return {
        'basicInfo': basicInfo,
        'priceHistory': priceHistory,
        'futureEarningsDates': futureEarningsDates,
        'news': newsArticles
    }


# Example usage
data = getCompanyStockInfo('MSFT')
print(data)
