import yfinance as yf
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import analyze


def extractBasicInfo(data):
    keys = [
        'longName',
        'website',
        'sector',
        'fullTimeEmployees',
        'marketCap',
        'totalRevenue',
        'trailingEps'
    ]
    return {k: data.get(k, '') for k in keys}


def getPriceHistory(company):
    history = company.history(period='12mo')
    return {
        'price': history['Open'].tolist() if not history.empty else [],
        'date': history.index.strftime('%Y-%m-%d').tolist() if not history.empty else []
    }


def getEarningsDates(company):
    try:
        earnings = company.earnings_dates
        if earnings is None:
            return []
        now = datetime.now()
        return [
            d.strftime('%Y-%m-%d')
            for d in earnings.index.to_pydatetime()
            if d > now
        ]
    except:
        return []


def getCompanyNews(company):
    return company.news or []


def extractNewsArticleTextFromHtml(soup):
    text = ''
    for div in soup.find_all('div', {'class': 'caas-body'}):
        text += div.get_text()
    return text


headers = {
    'User-Agent': 'Mozilla/5.0'
}


def extractCompanyNewsArticles(news):
    text = ''
    for article in news:
        try:
            r = requests.get(article['link'], headers=headers, timeout=5)
            soup = BeautifulSoup(r.text, 'html.parser')
            if not soup.findAll(string='Continue reading'):
                text += extractNewsArticleTextFromHtml(soup)
        except:
            continue
    return text


def getCompanyStockInfo(tickerSymbol):
    company = yf.Ticker(tickerSymbol)

    basicInfo = extractBasicInfo(company.info)
    if not basicInfo['longName']:
        raise NameError('Could not find stock info, ticker may be invalid.')

    priceHistory = getPriceHistory(company)
    futureEarningsDates = getEarningsDates(company)
    newsArticles = getCompanyNews(company)
    newsText = extractCompanyNewsArticles(newsArticles)
    textAnalysis = analyze.analyzeText(newsText)

    return {
        "basicInfo": basicInfo,
        "priceHistory": priceHistory,
        "futureEarningsDates": futureEarningsDates,
        "newsArticles": newsArticles,
        "analysis": textAnalysis
    }
