import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from analyze import analyzeText


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
        'price': history['Open'].tolist(),
        'date': history.index.strftime('%Y-%m-%d').tolist()
    }


def getEarningsDates(company):
    try:
        earnings = company.earnings_dates
        now = datetime.now(timezone.utc)
        return [
            date.strftime('%Y-%m-%d')
            for date in earnings.index
            if date.to_pydatetime().replace(tzinfo=timezone.utc) > now
        ]
    except:
        return []


def getCompanyNews(company):
    return company.news or []


def extractCompanyNewsArticles(news):
    text = ""
    for article in news:
        try:
            response = requests.get(article['link'], timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text += p.get_text() + " "
        except:
            continue
    return text


def getCompanyStockInfo(tickerSymbol):
    company = yf.Ticker(tickerSymbol)

    basicInfo = extractBasicInfo(company.info)
    priceHistory = getPriceHistory(company)
    futureEarningsDates = getEarningsDates(company)
    newsArticles = getCompanyNews(company)
    newsText = extractCompanyNewsArticles(newsArticles)

    textAnalysis = analyzeText(newsText)

    return {
        "ticker": tickerSymbol,
        "basicInfo": basicInfo,
        "priceHistory": priceHistory,
        "futureEarningsDates": futureEarningsDates,
        "analysis": textAnalysis
    }
