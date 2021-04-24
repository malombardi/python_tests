import nltk
from newspaper import Article
from neuralintents import GenericAssistant
import feedparser
import speech_recognition
import pyttsx3 as tts
import sys
import datetime as dt

rss_sources = ['https://www.cnbc.com/id/10000664/device/rss/rss.html',
               'https://www.cnbc.com/id/10001147/device/rss/rss.html',
               'https://www.cnbc.com/id/20910258/device/rss/rss.html',
               'https://www.cnbc.com/id/15839069/device/rss/rss.html']

sources_last_date = []

yesterday = dt.datetime.today() - dt.timedelta(days=1)
yesterday = dt.datetime.strptime(yesterday.strftime('%a, %d %b %Y'),'%a, %d %b %Y')
for i in range(len(rss_sources)):
    sources_last_date.append(yesterday)
        
speaker = tts.init()
recognizer = speech_recognition.Recognizer()

def fetch_rss() :
    '''Fetch the RSS urls and get the news.'''
    global recognizer

    for index, source in enumerate(rss_sources):
        NewsFeed = feedparser.parse(source)
        entries = NewsFeed.entries
        for entry in reversed(entries) :
            entry_date = dt.datetime.strptime(entry.published, '%a, %d %b %Y %H:%M:%S %Z')
            counter = 0

            if entry_date > yesterday:
                counter += 1
                sources_last_date[index] = entry_date
                article = Article(entry.link)
                article.download()
                article.parse()
                article.nlp()
                print("----- TITLE -----")
                print(article.title)
                print("-----SUMMARY-----")
                print(article.summary)
                speaker.say(article.title)
                speaker.runAndWait()
                speaker.say(article.summary)
                speaker.runAndWait()
                speaker.stop()
            
        if counter == 0 :
            speaker.say("No new entries were found")
            speaker.runAndWait()
                
        speaker.say("Shal I continue?")
        speaker.runAndWait()
        try :
            with speech_recognition.Microphone() as mic :
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)

                audio = recognizer.listen(mic)

                answer = recognizer.recognize_google(audio)
                if answer.lower() == "no" :
                    quit()
                else :
                    print("continuar")
        except speech_recognition.UnknownValueError :
            recognizer = speech_recognition.Recognizer()
            speaker.say("I don't understand you, please repeat")
            speaker.runAndWait()

def hello() :
    speaker.say("What can I do for you?")
    speaker.runAndWait()

def quit() :
    speaker.say("Bye")
    speaker.runAndWait()
    sys.exit(0)
    
def start_reader() :
    nltk.download('punkt')
    recognizer = speech_recognition.Recognizer()
    speaker.setProperty('rate', 200)
    speaker.setProperty('voice', 'english-us')
    
    mappings = {
        "greeting" : hello,
        "fetch_all" : fetch_rss,
        "exit" : quit
    }
    
    assistant = GenericAssistant('intents.json', intent_methods=mappings)
    assistant.train_model()
    
    while True :
        try :
            with speech_recognition.Microphone() as mic :
                recognizer.adjust_for_ambient_noise(mic, duration=0.5)
                audio = recognizer.listen(mic)
                message = recognizer.recognize_google(audio)
                message = message.lower()
                print(message)
            
            assistant.request(message)
            
        except speech_recognition.UnknownValueError :
            recognizer = speech_recognition.Recognizer()
            speaker.say("I don't understand you, please repeat")
            speaker.runAndWait()

if __name__ == "__main__":
    start_reader()