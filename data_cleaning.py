import json
import pandas as pd
from textblob import TextBlob

import yake

def get_kw_extractor():
    language = 'en'
    max_ngram_size = 2
    deduplication_threshold = 0.9
    num_keywords = 20
    kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=num_keywords, features=None)
    return kw_extractor

def get_polarity(text):
    return TextBlob(text).sentiment.polarity

def get_sentiment(polarity):
    sentiment=None
    if polarity > 0:
        sentiment = 'positive'
    elif polarity < 0:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    return sentiment

def extract_top_kw(extractor, n, text):
    """
    Extract top n key words in provided text
    Args:
        extractor: predefined yake extractor
        n: top n keywords to extract
    Return:
        a list of keywords, None if text is empty
    """
    if not text:
        return None
    keywords = extractor.extract_keywords(text)
    keywords.sort(key=lambda x: x[1], reverse=True)
    top_kw = [key for key, weight in keywords[:n]]
    return top_kw

def clean(path, extractor):
    with open(path, 'r') as f:
        data=f.read()

    df = pd.DataFrame(json.loads(data))

    # convert unix-timestamp and to local time 
    df['timestamp'] = pd.to_datetime(df['created_utc'], unit='s', utc=True).dt.tz_convert('America/New_York')
    df['text_polarity']=df['selftext'].apply(get_polarity)
    df['sentiment'] = df['text_polarity'].apply(get_sentiment) 
    df['text_kw'] = df['selftext'].apply(lambda x: extract_top_kw(extractor=extractor, n=3, text=x))
    df['title_kw'] = df['title'].apply(lambda x: extract_top_kw(extractor=extractor, n=1, text=x))

    cols = ['timestamp', 'id', 'author', 'title', 'num_comments', 'ups', 'upvote_ratio', 
        'is_video', 'selftext', 'text_polarity', 'sentiment', 'text_kw', 'title_kw']
    clean_df = df[cols]
    return clean_df


if __name__ == '__main__':
    kw_extractor = get_kw_extractor()
    path = 'subreddit_2025-01-17.json'
    
    df = clean(path, extractor=kw_extractor)