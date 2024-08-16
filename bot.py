import os
import playsound
import speech_recognition as sr
import time
import sys
import ctypes
import wikipedia
import datetime
import json
import re
import webbrowser
import smtplib
import requests
import urllib.request as urllib2
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from time import strftime
from gtts import gTTS
from youtubesearchpython import VideosSearch
import pygame
import uuid
from datetime import date  # Thêm import date
import yfinance as yf
import openai  # Thư viện OpenAI để sử dụng GPT-3/4

# Đặt ngôn ngữ Wikipedia và ngôn ngữ sử dụng
wikipedia.set_lang('vi')
language = 'vi'

# Cài đặt driver Chrome
path = ChromeDriverManager().install()

# Cài đặt OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Thay thế bằng khóa API của bạn

# Hàm phát âm thanh
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

# Hàm nhận diện giọng nói
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Tôi: ", end='')
        audio = r.listen(source, phrase_time_limit=5)
        try:
            text = r.recognize_google(audio, language="vi-VN")
            print(text)
            return text
        except:
            print("...")
            return None

# Hàm dừng trợ lý ảo
def stop():
    speak("Hẹn gặp lại bạn sau!")

# Hàm nhận và xử lý văn bản từ giọng nói
def get_text():
    for i in range(3):
        text = get_audio()
        if text:
            return text.lower()
        elif i < 2:
            speak("Bot không nghe rõ. Bạn nói lại được không!")
    time.sleep(2)
    stop()
    return None

# Hàm chào hỏi
def hello(name):
    day_time = int(strftime('%H'))
    if day_time < 12:
        speak(f"Chào buổi sáng bạn {name}. Chúc bạn một ngày tốt lành.")
    elif 12 <= day_time < 18:
        speak(f"Chào buổi chiều bạn {name}. Bạn đã dự định gì cho chiều nay chưa.")
    else:
        speak(f"Chào buổi tối bạn {name}. Bạn đã ăn tối chưa nhỉ.")

# Hàm lấy thời gian hiện tại
def get_time(text):
    now = datetime.datetime.now()
    if "giờ" in text:
        speak(f'Bây giờ là {now.hour} giờ {now.minute} phút')
    elif "ngày" in text:
        speak(f"Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}")
    else:
        speak("Bot chưa hiểu ý của bạn. Bạn nói lại được không?")

# Hàm mở ứng dụng
def open_application(text):
    if "google" in text:
        speak("Mở Google Chrome")
        os.startfile(
            'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Google Chrome.lnk')
    elif "word" in text:
        speak("Mở Microsoft Word")
        os.startfile(
            'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Word.lnk')
    elif "excel" in text:
        speak("Mở Microsoft Excel")
        os.startfile(
            'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Excel.lnk')
    else:
        speak("Ứng dụng chưa được cài đặt. Bạn hãy thử lại!")

# Hàm mở website
def open_website(text):
    reg_ex = re.search('mở (.+)', text)
    if reg_ex:
        domain = reg_ex.group(1)
        url = 'https://www.' + domain
        webbrowser.open(url)
        speak("Trang web bạn yêu cầu đã được mở.")
        return True
    else:
        return False

# Hàm mở Google và tìm kiếm
def open_google_and_search(text):
    search_for = text.split("tìm kiếm", 1)[1]
    speak('Okay!')
    driver = webdriver.Chrome(path)
    driver.get("https://www.google.com")
    que = driver.find_element("xpath", "//input[@name='q']")
    que.send_keys(str(search_for))
    que.send_keys(Keys.RETURN)

# Hàm gửi email
def send_email(text):
    speak('Bạn gửi email cho ai nhỉ')
    recipient = get_text()
    if 'yến' in recipient:
        speak('Nội dung bạn muốn gửi là gì')
        content = get_text()
        mail = smtplib.SMTP('smtp.gmail.com', 587)
        mail.ehlo()
        mail.starttls()
        mail.login('luongngochungcntt@gmail.com', 'hung23081997')
        mail.sendmail('luongngochungcntt@gmail.com',
                      'hungdhv97@gmail.com', content.encode('utf-8'))
        mail.close()
        speak('Email của bạn vừa được gửi. Bạn check lại email nhé hihi.')
    else:
        speak('Bot không hiểu bạn muốn gửi email cho ai. Bạn nói lại được không?')

# Hàm lấy thông tin thời tiết hiện tại
def current_weather():
    speak("Bạn muốn xem thời tiết ở đâu ạ.")
    ow_url = "http://api.openweathermap.org/data/2.5/weather?"
    city = get_text()
    if not city:
        return
    api_key = "1df7d279e27869dccb309c39f5973269"
    call_url = ow_url + "appid=" + api_key + "&q=" + city + "&units=metric"
    response = requests.get(call_url)
    data = response.json()
    if data["cod"] != "404":
        city_res = data["main"]
        current_temperature = city_res["temp"]
        current_pressure = city_res["pressure"]
        current_humidity = city_res["humidity"]
        suntime = data["sys"]
        sunrise = datetime.datetime.fromtimestamp(suntime["sunrise"])
        sunset = datetime.datetime.fromtimestamp(suntime["sunset"])
        wthr = data["weather"]
        weather_description = wthr[0]["description"]
        now = datetime.datetime.now()
        content = f"""
        Hôm nay là ngày {now.day} tháng {now.month} năm {now.year}
        Mặt trời mọc vào {sunrise.hour} giờ {sunrise.minute} phút
        Mặt trời lặn vào {sunset.hour} giờ {sunset.minute} phút
        Nhiệt độ trung bình là {current_temperature} độ C
        Áp suất không khí là {current_pressure} héc tơ Pascal
        Độ ẩm là {current_humidity}%
        Trời hôm nay {weather_description}. Dự báo mưa rải rác ở một số nơi."""
        speak(content)
        time.sleep(20)
    else:
        speak("Không tìm thấy địa chỉ của bạn")

# Hàm phát bài hát từ YouTube
def play_song():
    speak('Xin mời bạn chọn tên bài hát')
    mysong = get_text()
    while True:
        result = VideosSearch(mysong, limit=1).result()
        if result['result']:
            break
    url = result['result'][0]['link']
    webbrowser.open(url)
    speak("Bài hát bạn yêu cầu đã được mở.")

# Hàm thay đổi hình nền máy tính
def change_wallpaper():
    api_key = 'RF3LyUUIyogjCpQwlf-zjzCf1JdvRwb--SLV6iCzOxw'
    url = 'https://api.unsplash.com/photos/random?client_id=' + api_key
    f = urllib2.urlopen(url)
    json_string = f.read()
    f.close()
    parsed_json = json.loads(json_string)
    photo = parsed_json['urls']['full']
    urllib2.urlretrieve(photo, "C:/Users/Night Fury/Downloads/a.png")
    image = os.path.join("C:/Users/Night Fury/Downloads/a.png")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image, 3)
    speak('Hình nền máy tính vừa được thay đổi')

# Hàm đọc tin tức
def read_news():
    speak("Bạn muốn đọc báo về gì")
    queue = get_text()
    params = {
        'apiKey': '30d02d187f7140faacf9ccd27a1441ad',
        "q": queue,
    }
    api_result = requests.get('http://newsapi.org/v2/top-headlines?', params=params)
    api_response = api_result.json()
    if api_response['status'] == "ok":
        for number, result in enumerate(api_response['articles'], start=1):
            print(
                f"""Tin {number}:\nTiêu đề: {result['title']}\nTrích dẫn: {result['description']}\nLink: {result['url']}""")
            if number <= 3:
                webbrowser.open(result['url'])
    else:
        speak("Không tìm thấy thông tin về chủ đề bạn quan tâm.")

# Hàm lấy giá cổ phiếu
def get_stock_price(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return f"Giá cổ phiếu {ticker} hiện tại là {info['last_price']}"

# Hàm tương tác với GPT-3/4 của OpenAI
def get_gpt3_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Hoặc phiên bản khác như "gpt-3.5-turbo" hoặc "gpt-4"
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Hàm trợ lý chính
import wikipedia
import openai

# Hàm trợ lý chính
def virtual_assistant():
    name = "Anh"
    speak("Xin chào bạn.Mình là Taka. Bạn tên là gì nhỉ?")
    user_name = get_text()
    if user_name:
        name = user_name.capitalize()
    hello(name)

    while True:
        text = get_text()
        if not text:
            break
        elif "dừng" in text or "tạm biệt" in text or "hẹn gặp lại" in text:
            stop()
            break
        elif "thời gian" in text:
            get_time(text)
        elif "hôm nay" in text:
            today = date.today()
            robot_brain = today.strftime("%d tháng %m, %Y")
            speak(f"Hôm nay là {robot_brain}")
        elif "wikipedia" in text:
            search_query = text.replace("wikipedia", "").strip()
            try:
                robot_brain = wikipedia.summary(search_query, sentences=1)
            except wikipedia.exceptions.DisambiguationError:
                robot_brain = "Có nhiều kết quả cho từ khóa này, hãy cụ thể hơn."
            except wikipedia.exceptions.PageError:
                robot_brain = "Không tìm thấy thông tin trên Wikipedia."
            except Exception as e:
                robot_brain = f"Đã xảy ra lỗi: {str(e)}"
            speak(robot_brain)
        elif "tìm kiếm" in text:
            search_for = text.split("tìm kiếm", 1)[1]
            open_google_and_search(search_for)
        elif "email" in text:
            send_email(text)
        elif "thời tiết" in text:
            current_weather()
        elif "nghe nhạc" in text or "phát bài hát" in text:
            play_song()
        elif "thay đổi hình nền" in text:
            change_wallpaper()
        elif "giá cổ phiếu" in text:
            ticker = text.replace("giá cổ phiếu", "").strip()
            price_info = get_stock_price(ticker)
            speak(price_info)
        elif "trợ lý" in text:  # Tùy chọn sử dụng GPT-3/4 để trả lời câu hỏi
            prompt = text.replace("trợ lý", "").strip()
            try:
                robot_brain = get_gpt3_response(prompt)
            except Exception as e:
                robot_brain = f"Đã xảy ra lỗi: {str(e)}"
            speak(robot_brain)
        else:
            # Xử lý trường hợp không có sẵn thông tin trong bot
            search_query = text
            try:
                # Truy vấn Wikipedia
                robot_brain = wikipedia.summary(search_query, sentences=1)
                speak(robot_brain)
            except wikipedia.exceptions.DisambiguationError:
                robot_brain = "Có nhiều kết quả cho từ khóa này, hãy cụ thể hơn."
                speak(robot_brain)
            except wikipedia.exceptions.PageError:
                robot_brain = "Không tìm thấy thông tin trên Wikipedia. Tôi sẽ thử tìm thông tin khác."
                speak(robot_brain)
                # Sử dụng GPT-3/4 nếu Wikipedia không có thông tin
                try:
                    robot_brain = get_gpt3_response(search_query)
                    speak(robot_brain)
                except Exception as e:
                    robot_brain = f"Đã xảy ra lỗi khi truy vấn GPT-3: {str(e)}"
                    speak(robot_brain)
            except Exception as e:
                robot_brain = f"Đã xảy ra lỗi: {str(e)}"
                speak(robot_brain)

if __name__ == "__main__":
    virtual_assistant()

