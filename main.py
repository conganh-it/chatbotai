import asyncio
import ctypes
import os
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
from datetime import date
import yfinance as yf
import openai
from youtubesearchpython import VideosSearch

# Đặt ngôn ngữ Wikipedia và ngôn ngữ sử dụng
wikipedia.set_lang('vi')

# Cài đặt driver Chrome
path = ChromeDriverManager().install()

# Cài đặt OpenAI API
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Thay thế bằng khóa API của bạn


# Hàm nhận văn bản từ người dùng
def get_text():
    return input("Bạn: ")


# Hàm in ra văn bản trả lời
def speak(text):
    print(f"Bot: {text}")


# Hàm chào hỏi
def hello(name):
    day_time = int(datetime.datetime.now().strftime('%H'))
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


# Hàm cảm ơn
def thank(text):
    if "cảm ơn" in text or "thanks" in text:
        speak('Không có gì, bạn cần mình giúp thêm gì không?')


# Hàm mở ứng dụng
def open_application(text):
    if "google" in text:
        speak("Mở Google Chrome")
        os.startfile('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Google Chrome.lnk')
    elif "word" in text:
        speak("Mở Microsoft Word")
        os.startfile('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Word.lnk')
    elif "excel" in text:
        speak("Mở Microsoft Excel")
        os.startfile('C:\\ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\Excel.lnk')
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
        mail.sendmail('luongngochungcntt@gmail.com', 'hungdhv97@gmail.com', content.encode('utf-8'))
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
    return f"Giá cổ phiếu {ticker} hiện tại là {info.get('last_price', 'Không có thông tin')}"


# Hàm tương tác với GPT-3/4 của OpenAI
async def get_gpt3_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Hoặc phiên bản khác như "gpt-3.5-turbo" hoặc "gpt-4"
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()


# Hàm tra cứu thông tin từ Wikipedia
def search_wikipedia(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError as e:
        summary = wikipedia.summary(e.options[0], sentences=2)
    except wikipedia.exceptions.PageError:
        summary = "Không tìm thấy trang phù hợp trên Wikipedia."
    return summary


# Hàm xử lý câu lệnh
async def process_command(command):
    command = command.lower()

    if "chào" in command:
        speak("Chào bạn! Tôi có thể giúp gì cho bạn?")
    elif "giờ" in command or "ngày" in command:
        get_time(command)
    elif "cảm ơn" in command or "thanks" in command:
        thank(command)
    elif "mở" in command:
        if "google" in command or "chrome" in command or "firefox" in command:
            open_application(command)
        elif "website" in command:
            open_website(command)
        elif "tìm kiếm" in command:
            open_google_and_search(command)
    elif "email" in command:
        send_email(command)
    elif "thời tiết" in command:
        current_weather()
    elif "bài hát" in command:
        play_song()
    elif "hình nền" in command:
        change_wallpaper()
    elif "tin tức" in command:
        read_news()
    elif "giá cổ phiếu" in command:
        ticker = re.search(r'giá cổ phiếu (\w+)', command)
        if ticker:
            price = get_stock_price(ticker.group(1))
            speak(price)
    else:
        # Xử lý các câu hỏi với Wikipedia
        response = search_wikipedia(command)
        speak(response)


# Chương trình chính
async def main():
    while True:
        user_input = get_text()
        if user_input.lower() in ["dừng", "tạm dừng", "quit", "exit"]:
            speak("Tạm biệt!")
            break
        await process_command(user_input)


if __name__ == "__main__":
    asyncio.run(main())
