import tkinter as tk
import speech_recognition as sr
import pyttsx3
from datetime import date, datetime
import requests
from gtts import gTTS
import os
import time

# Khởi tạo Recognizer và Speech Engine
robot_ear = sr.Recognizer()
robot_mouth = pyttsx3.init()
robot_brain = ""

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
    tts = gTTS(text=text, lang='vi')
    tts.save("response.mp3")
    os.system("start response.mp3")  # Windows
    time.sleep(5)  # Thêm thời gian chờ để đảm bảo rằng âm thanh đã được phát hết

def change_expression(expression):
    if expression == 'neutral':
        draw_robot(face='neutral')
    elif expression == 'happy':
        draw_robot(face='happy')
    elif expression == 'sad':
        draw_robot(face='sad')
    elif expression == 'angry':
        draw_robot(face='angry')
    elif expression == 'excited':
        draw_robot(face='excited')

def draw_robot(face='neutral'):
    canvas.delete("all")

    # Body
    canvas.create_oval(150, 50, 350, 250, fill='lightgrey', outline='grey')

    # Eyes and Mouth based on expression
    if face == 'neutral':
        canvas.create_oval(210, 110, 230, 130, fill='black')
        canvas.create_oval(270, 110, 290, 130, fill='black')
        canvas.create_line(230, 160, 270, 160, width=2)
    elif face == 'happy':
        canvas.create_oval(210, 110, 230, 130, fill='black')
        canvas.create_oval(270, 110, 290, 130, fill='black')
        canvas.create_arc(220, 140, 280, 180, start=0, extent=-180, style=tk.ARC)
    elif face == 'sad':
        canvas.create_oval(210, 110, 230, 130, fill='black')
        canvas.create_oval(270, 110, 290, 130, fill='black')
        canvas.create_arc(220, 160, 280, 200, start=0, extent=180, style=tk.ARC)
    elif face == 'angry':
        canvas.create_line(210, 110, 230, 130, width=2)
        canvas.create_line(230, 110, 210, 130, width=2)
        canvas.create_line(270, 110, 290, 130, width=2)
        canvas.create_line(290, 110, 270, 130, width=2)
        canvas.create_line(230, 160, 270, 160, width=2)
    elif face == 'excited':
        canvas.create_oval(205, 105, 235, 135, fill='black')
        canvas.create_oval(265, 105, 295, 135, fill='black')
        canvas.create_oval(230, 150, 270, 190, outline='black', width=2)

    # Draw limbs
    canvas.create_line(150, 150, 100, 180, width=8)
    canvas.create_line(350, 150, 400, 180, width=8)
    canvas.create_line(200, 250, 180, 300, width=8)
    canvas.create_line(300, 250, 320, 300, width=8)
    canvas.create_line(250, 50, 250, 20, width=5)
    canvas.create_oval(240, 10, 260, 30, fill='green')

def handle_voice_command():
    global robot_brain
    you = ""
    with sr.Microphone() as mic:
        print("Robot: Tôi đang lắng nghe...")
        try:
            audio = robot_ear.listen(mic, timeout=5, phrase_time_limit=10)
            print("Robot: ...")
            you = robot_ear.recognize_google(audio, language="vi-VN")
            print("Bạn nói:", you)
        except sr.WaitTimeoutError:
            robot_brain = "Không nhận được âm thanh trong thời gian chờ."
        except sr.UnknownValueError:
            robot_brain = "Không thể nhận dạng được giọng nói."
        except Exception as e:
            robot_brain = f"Đã xảy ra lỗi: {str(e)}"

    if you:
        if "xin chào" in you.lower():
            robot_brain = "Xin chào bạn!"
            change_expression('happy')
        elif "hôm nay" in you.lower():
            today = date.today()
            robot_brain = today.strftime("%d tháng %m, %Y")
            change_expression('neutral')
        elif "giờ" in you.lower():
            now = datetime.now()
            robot_brain = f"{now.hour} giờ {now.minute} phút {now.second} giây"
            change_expression('neutral')
        elif "thời tiết" in you.lower():
            robot_brain = get_weather("Hà Nội")  # Thay "Hà Nội" bằng thành phố mong muốn
            change_expression('excited')
        elif "tạm biệt" in you.lower():
            robot_brain = "Tạm biệt bạn!"
            change_expression('sad')
            speak(robot_brain)
            root.quit()
        else:
            robot_brain = "Tôi không hiểu bạn nói gì."
            change_expression('neutral')

        print(robot_brain)
        speak(robot_brain)

    # Schedule the next listening
    root.after(1000, handle_voice_command)  # Lắng nghe lại sau 1 giây

# Create the main window
root = tk.Tk()
root.title("Trợ Lý Ảo")
root.geometry("500x500")
root.configure(bg='lightblue')

# Create a canvas to draw the robot
canvas = tk.Canvas(root, width=500, height=400, bg='lightblue')
canvas.pack()

# Initial drawing of the robot
draw_robot()

# Start handling voice commands
handle_voice_command()

# Run the main loop
root.mainloop()
