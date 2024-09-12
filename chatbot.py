import speech_recognition as sr
import pyttsx3
from datetime import date, datetime
import requests
import wikipedia
from gtts import gTTS
import os
import time
import pygame
import uuid

# Các thư viện mới
from scholarly import scholarly
import feedparser

# Khởi tạo Recognizer và Speech Engine
robot_ear = sr.Recognizer()
robot_mouth = pyttsx3.init()
robot_brain = ""
is_speaking = False

def get_weather(city):
    api_key = "1df7d279e27869dccb309c39f5973269"
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=vi"
    response = requests.get(base_url)
    weather_data = response.json()
    if weather_data["cod"] == 200:
        main = weather_data["main"]
        weather_desc = weather_data["weather"][0]["description"]
        temperature = main["temp"]
        weather_response = f"Thời tiết ở {city} là {weather_desc} với nhiệt độ là {temperature} độ C."
    else:
        weather_response = "Không thể tìm thấy thông tin thời tiết cho thành phố này."
    return weather_response

def speak(text):
    global is_speaking
    is_speaking = True
    filename = f"response_{uuid.uuid4().hex}.mp3"
    try:
        tts = gTTS(text=text, lang='vi')
        tts.save(filename)
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print(f"Đã xảy ra lỗi khi phát âm thanh: {e}")
    finally:
        pygame.mixer.music.stop()  # Dừng âm thanh nếu còn đang phát
        pygame.mixer.music.unload()  # Giải phóng tài nguyên âm thanh
        if os.path.exists(filename):
            try:
                os.remove(filename)  # Xóa file âm thanh
            except Exception as e:
                print(f"Đã xảy ra lỗi khi xóa file âm thanh: {e}")
        is_speaking = False

def search_scholarly(query):
    search_query = scholarly.search_pubs(query)
    results = []
    for article in search_query:
        results.append(article.bib['title'])
    return results

def search_loc(query):
    url = "https://www.loc.gov/search/"
    params = {
        'q': query,
        'fo': 'json'
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    for item in data['results']:
        results.append(item['title'])
    return results

def search_arxiv(query):
    url = f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5'
    feed = feedparser.parse(url)
    results = []
    for entry in feed.entries:
        results.append(entry.title)
    return results

# Đảm bảo mã hóa UTF-8 cho console
import sys
sys.stdout.reconfigure(encoding='utf-8')

while True:
    if not is_speaking:
        you = ""
        with sr.Microphone() as mic:
            print("Robot: Tôi đang lắng nghe...")
            try:
                audio = robot_ear.listen(mic, timeout=5, phrase_time_limit=10)
                print("Robot: ...")
                you = robot_ear.recognize_google(audio, language="vi-VN")
                print("Bạn nói:", you)
            except sr.WaitTimeoutError:
                print("Không nhận được âm thanh trong thời gian chờ.")
            except sr.UnknownValueError:
                print("Không thể nhận dạng được giọng nói.")
            except Exception as e:
                print("Đã xảy ra lỗi:", str(e))

        # Xử lý kết quả nhận dạng
        if you == "":
            robot_brain = "Tôi không hiểu bạn nói gì."
        elif "xin chào" in you.lower():
            robot_brain = "Xin chào bạn! tôi là trợ lý ảo Taka"
        elif "hôm nay" in you.lower():
            today = date.today()
            robot_brain = today.strftime("%d tháng %m, %Y")
        elif "giờ" in you.lower():
            now = datetime.now()
            robot_brain = f"{now.hour} giờ {now.minute} phút {now.second} giây"
        elif "thời tiết" in you.lower():
            robot_brain = get_weather("Thái Nguyên")  # Thay "Thái Nguyên" bằng thành phố mong muốn
        elif "scholarly" in you.lower():
            results = search_scholarly("Quantum computing")
            robot_brain = ", ".join(results)
        elif "loc" in you.lower():
            results = search_loc("Civil War")
            robot_brain = ", ".join(results)
        elif "arxiv" in you.lower():
            results = search_arxiv("quantum computing")
            robot_brain = ", ".join(results)
        elif "tạm biệt" in you.lower():
            robot_brain = "Tạm biệt bạn!"
            print("Robot: " + robot_brain)
            speak(robot_brain)
            break
        else:
            try:
                wikipedia.set_lang("vi")
                robot_brain = wikipedia.summary(you, sentences=1)
            except wikipedia.exceptions.DisambiguationError as e:
                robot_brain = "Có nhiều kết quả cho từ khóa này, hãy cụ thể hơn."
            except wikipedia.exceptions.PageError:
                robot_brain = "Không tìm thấy thông tin trên Wikipedia."
            except Exception as e:
                robot_brain = f"Đã xảy ra lỗi: {str(e)}"

        print(robot_brain)
        speak(robot_brain)
