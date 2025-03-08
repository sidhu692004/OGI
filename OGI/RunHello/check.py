import pyttsx3 #pip install pyttsx3     for give sound
import speech_recognition as sr #pip install speechRecognition  for take sound
import datetime  #time detect for greeting
import wikipedia #pip install wikipedia
import webbrowser #for search on webbrowser
import os  # for work in system like open camera, take picture, open task manager..
import cv2   #pip install opencv-python    for camera and take screenshot
import random    #for take random like music, jokes
import psutil # for getting current running details like battery status,cpu usage
import pywhatkit as kit  # for send whatsapp message   
import ctypes # used in translation and lockscreen
import pyjokes  # for a joke
import requests  # for URL request
import time  #for sleep screen some second to take screenshots
import pyautogui  # for screenshots
import operator  #for calculator
from bs4 import BeautifulSoup   #for wikipedia and google search on terminal
from pywikihow import search_wikihow #used for searching (beautiful soup)
import urllib.request # for url
import wolframalpha  # for mathematical problem
import subprocess  #for open play video to give path
from PIL import ImageTk
import requests
import tkinter as tk
from PIL import ImageTk
from tkinter import messagebox
from tkinter import font
from database import *



engine = pyttsx3.init('sapi5')  #The SAPI application programming interface (API) 
#dramatically reduces the code overhead required for an application to use speech 
#recognition and text-to-speech, making speech technology more accessible and robust
# for a wide range of applications.
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


    # DEFINING WISH ME FUNCTION 
def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak("I  am  OGI. Please tell me how may I help you")       


def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("listen","tell something")
        speak("speak something")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        query = r.recognize_google(audio, language='en-in')
        messagebox.showinfo(" ","you said: "+query)
        speak("you said: "+query)
    except Exception as e:  
        messagebox.showinfo("listen","please stop making noise ")
        speak("please stop making noise")
        return "None"
    return query

    # DEFINING CLICK PICTURE CASE IT WILL CLICK THE PICTURE USING CV2 LIBRAAY
def clickpicture():
    # Set directory for saving screenshot
    directory = r"C:\Users\sudha\Downloads\\"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Get current date and time for naming the file
    now = datetime.datetime.now()
    filename = directory + now.strftime("%Y-%m-%d %H-%M-%S") + ".png"

    # Take screenshot using cv2 library
    img = cv2.VideoCapture(0)
    ret, frame = img.read()
    cv2.imwrite(filename, frame)
    img.release()

    # Speak confirmation message and show file location
    speak("Photo taken!")
    messagebox.showinfo("result","Photo taken!")
    speak("The photo has been saved at "+filename)
    messagebox.showinfo("result","The photo has been saved at "+filename)
    # DEFINING SYSTEM INFO CASE

def google_search(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    query = query.replace(' ', '+')
    url = f"https://www.google.com/search?q={query}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    snippets = soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd')
    if snippets:
        return snippets[0].get_text()
    else:
        return "No results found"
    


def system_info():
    usage = str(psutil.cpu_percent())+'%'
    speak('CPU usage is at '+usage)
    
    available_ram =  round(psutil.virtual_memory().available / (1024.0 ** 3), 2)
    total_ram = round(psutil.virtual_memory().total / (1024.0 ** 3), 2)
    speak('Available RAM is ' + str(available_ram) + " gigabytes out of " + str(total_ram) + " gigabytes.")
    messagebox.showinfo("result","Available RAM is "+str(available_ram)+" gigabytes out of "+str(total_ram)+" gigabytes. ")
    # DEFINING LOCK SCREEN CASE
def lockScreen():
    """Lock the screen"""
    ctypes.windll.user32.LockWorkStation()
    speak("Screen locked.")
    # DEFINING CONTROL PANNEL CASE
def openControlPanel():
    os.system("control panel")
    speak("Control Panel opened.")
    #DEFININF TASK MANAGER CASE
    
def openTaskManager():
    os.system("taskmgr")
    speak("Task Manager opened.")
    
    #DEFINING SEARCH ON GOOGLE 
def searchOnGoogle(query):
    query = query.strip()
    speak('Searching for '+query+' on Google...')
    url = 'https://www.google.com/search?q='+query
    webbrowser.open(url)
    # DEFINING NEWS FUNCTION

def open_chatgpt():
    url = "https://chat.openai.com/"
    webbrowser.open(url)

def news():
    main_url= "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=d257604ecd2b4164a1eb4fd10431a68e"
    main_page = requests.get(main_url).json()
    articles = main_page["articles"]
    head=[]
    day=["first","second","third","fourth","fifth","sixth","seventh","eighth","ninth","tenth","eleventh"] 
    for ar in articles:
        head.append(ar["title"])
    return day,head

def open_webpage(url):
    try:
        webbrowser.get().open(url)
        speak('Opening webpage in web browser')
    except Exception as e:
        print(e)
        speak('Sorry, unable to open webpage')


 # Replace YOUR_APP_ID with your actual app ID
ss1 = '55A4Y5-Y2YWQWQ355'
client = wolframalpha.Client(ss1)

def get_wolframalpha_response(query):
    
    try:
        res = client.query(query)
        return next(res.results).text
    except:
        return ""

def whatsappmess():
    speak("which number do you want to send message with country code without + like form 918228*****")
    messagebox.showinfo("Information","Say which number do you want to send message with country code without + like form 918228*****")
    number = takeCommand()  
    number='+'+number
    speak("what is your message")
    messagebox.showinfo("Information","Say what is your message")
    message = takeCommand()
    while message=='None' or message=='none':
        speak("Please speak a message")
        messagebox.showinfo("Information","Say again what is your message")
        message=takeCommand()
    speak("which hour send message using 24 hour")
    messagebox.showinfo("information","which hour send message using 24 hour: ")
    
    hour = takeCommand()  # 24-hour format
    hour = hour.replace(' ', '')
    while  not hour.isdigit() or int(hour) < 0 or int(hour) > 24:
        speak("Please tell the hour of sending times")
        messagebox.showinfo("Information","Please tell the hour of sending times")
        hour = takeCommand().replace(' ', '')
    
    hour = int(hour)  # 24-hour format
    speak("Which minute to send message")
    messagebox.showinfo("Information","Which minute to send message")
    minute = takeCommand()  # minute
    minute = minute.replace(' ', '')
    # Clean up and validate the minute input
    while not minute.isdigit() or int(minute) < 0 or int(minute) > 59:
        speak("Please tell the minute of sending times")
        messagebox.showinfo("Information","Please tell the minute of sending times")
        minute = takeCommand().replace(' ', '')
    
    minute = int(minute)  # minute
    
    # Assuming ss.sendwhatmsg is defined and number, message variables are set
    messagebox.showinfo("result","Message scheduled successfully!")


conn, cursor = initialize_connection()

def center_window(width, height):
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

class WelcomeWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Welcome")
        center_window(1950, 1100)
        root.resizable(True, True)  #window resize

        self.root = root
        self.root.configure(bg='black')  # Background for better neon contrast
        
        f1 = tk.Frame(root, bg='black', borderwidth=6)
        f1.place(x=1500, y=900, width=330, height=100)
        
        # Custom button styling
        self.neon_button_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.neon_button = tk.Button(
            f1, 
            text="Next", 
            width=20, 
            height=3, 
            font=self.neon_button_font, 
            fg='#00ff00',  # Neon green for futuristic glow effect
            bg='#1c1c1c',  # Dark background for contrast
            activebackground='#00ff00',  # Button turns neon green when clicked
            activeforeground='black',  # Text color changes on click
            relief='flat',  # Flat button for modern look
            command=self.open_register_window
        )
        
        self.neon_button.pack(pady=10)

    def open_register_window(self):
        # Logic to open another window
        messagebox.showinfo("buttob status","Next button clicked")
        
    def open_register_window(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        #========================Back_ground_image==============================
        self.bg=ImageTk.PhotoImage(file="register.png")
        self.bg_lbl=tk.Label(root, image=self.bg).place(relwidth=1,relheight=1)
        RegisterWindow(self.master)

 
class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Login")
        self.master.resizable(False, False)
        center_window(1950, 1100)
        
        
        f1=tk.Frame(root,bg='#011226',borderwidth=6,relief=tk.GROOVE)
        f1.place(x=1100,y=350,width=315,height=200)

        f3=tk.Frame(root,bg='#011226',borderwidth=6)
        f3.place(x=1100,y=200,width=360,height=100)
      
        tk.Label(f3, text="Login Now",bg='#011226',fg='#ADD8E6',font=('arial',40,'bold')).grid(row=0, column=0)

        tk.Label(f1, text="Email:",bg='#011226',fg='#ADD8E6').grid(row=0, column=0)
        self.username_entry = tk.Entry(f1)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
         
        tk.Label(f1, text="Password:",bg='#011226',fg='#ADD8E6').grid(row=1, column=0)
        self.password_entry = tk.Entry(f1, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
         
        submit_button = tk.Button(f1, text="Submit",bg='#011226',fg='#ADD8E6', width=8, command=self.submit)
        submit_button.grid(row=2, column=1, sticky="e", padx=10, pady=(10, 0))

        submit_button = tk.Button(f1, text="Refresh",bg='#011226',fg='#ADD8E6', width=8, command=self.refresh_window)
        submit_button.grid(row=3, column=0, padx=10, pady=(10, 0))
 
        submit_button = tk.Button(f1, text="Back",bg='#011226',fg='#ADD8E6', width=8, command=self.back)
        submit_button.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        self.pack()

    def refresh_window(self):
           self.username_entry.delete(0,'end')
           self.password_entry.delete(0,"end")
           messagebox.showinfo("Window","Refresh Successfully")
           
    def submit(self):
        data = {}
        data["email"] = self.username_entry.get()
        data["password"] = self.password_entry.get()
          
        if login(cursor, data) == True:
            messagebox.showinfo("Login Status","Login Successfully")
            for widget in self.winfo_children(): 
                widget.destroy()
                self.destroy()
    #===       =====================Back_ground_image==============================
            self.bg=ImageTk.PhotoImage(file="ss.jpg")
            self.bg_lbl=tk.Label(root, image=self.bg).place(relwidth=1,relheight=1)
            SearchWindow(self.master)
           
        else:
            if data["email"]=="" or data["password"]=="":
                messagebox.showinfo("check input","Enter email and password")

            else:
                messagebox.showinfo("Login Status","Login failed")
 
    def back(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        # ========================Back_ground_image============================
        self.bg=ImageTk.PhotoImage(file="welcome.png")
        self.bg_lbl=tk.Label(root, image=self.bg).place(relwidth=1,relheight=1)
        WelcomeWindow(self.master)
        
 
 
class RegisterWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Register")
        self.master.resizable(False, False)
        center_window(1950, 1100)
         
        self.root = root
        self.root.configure(bg='black')  # Set background to match futuristic look

        # Define custom font for labels and buttons
        self.label_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=18, weight="bold")

        # Frame Styling (Futuristic Borders and Colors)
        f2 = tk.Frame(root, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f2.place(x=1450, y=260, width=420, height=470)

        f3 = tk.Frame(root, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f3.place(x=1450, y=130, width=420, height=100)

        f4 = tk.Frame(root, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f4.place(x=1450, y=720, width=420, height=40)

        f5 = tk.Frame(root, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f5.place(x=1450, y=220, width=420, height=40)

        f6 = tk.Frame(root, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f6.place(x=1450, y=760, width=420, height=90)

        # Label and Button Styling (Glowing Effect, Sci-fi Font)
        tk.Label(f3, text="Register Now", bg='#1C1C1C', fg='#FF4500', font=('Helvetica', 30, 'bold')).grid(row=0, column=0)

        tk.Label(f5, text="Only for new user", bg='#1C1C1C', fg='white', font=('Helvetica', 10,)).grid(row=0, column=0)

        tk.Label(f2, text="First Name:", bg='#1C1C1C', fg='white').grid(row=0, column=0, sticky="w")
        self.first_name_entry = tk.Entry(f2, width=26, bg='#333333', fg='white')
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="Last Name:", bg='#1C1C1C', fg='white').grid(row=1, column=0, sticky="w")
        self.last_name_entry = tk.Entry(f2, width=26, bg='#333333', fg='white')
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="Password:", bg='#1C1C1C', fg='white').grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(f2, show="*", width=26, bg='#333333', fg='white')
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="Email:", bg='#1C1C1C', fg='white').grid(row=3, column=0, sticky="w")
        self.email_entry = tk.Entry(f2, width=26, bg='#333333', fg='white')
        self.email_entry.grid(row=3, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="Gender:", bg='#1C1C1C', fg='white').grid(row=4, column=0, sticky="w")
        self.gender_entry = tk.Entry(f2, width=10, bg='#333333', fg='white')
        self.gender_entry.grid(row=4, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="Age:", bg='#1C1C1C', fg='white').grid(row=5, column=0, sticky="w")
        self.age_entry = tk.Entry(f2, width=10, bg='#333333', fg='white')
        self.age_entry.grid(row=5, column=1, padx=10, pady=10, sticky="e")

        tk.Label(f2, text="State:", bg='#1C1C1C', fg='white').grid(row=6, column=0, sticky="w")
        self.state_entry = tk.Entry(f2, width=20, bg='#333333', fg='white')
        self.state_entry.grid(row=6, column=1, padx=10, pady=10, sticky="e")

        # Buttons with neon-like glow
        submit_button = tk.Button(f2, text="Register", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=8, command=self.submit)
        submit_button.grid(row=7, column=1, padx=10, pady=10, sticky="e")

        refresh_button = tk.Button(f2, text="Refresh", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=8, command=self.refresh_window)
        refresh_button.grid(row=8, column=0, padx=10, pady=10)

        back_button = tk.Button(f2, text="Back", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=8, command=self.back)
        back_button.grid(row=7, column=0, sticky="w", padx=10, pady=(10, 10))

        tk.Label(f4, text="If you already created an account!", bg='#1C1C1C', fg='white', font=('Helvetica', 12, 'bold')).grid(row=0, column=0)

        login_button = tk.Button(f6, text="Login", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=8, command=self.open_login_window)
        login_button.grid(row=8, column=1, sticky="e", padx=10, pady=(10, 10))
    
    def open_login_window(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
    #========================Back_ground_image==============================
        self.bg=ImageTk.PhotoImage(file="login.jpg")
        self.bg_lbl=tk.Label(root, image=self.bg).place(relwidth=1,relheight=1)
        LoginWindow(self.master)


    def refresh_window(self):
       self.first_name_entry.delete(0, 'end')
       self.last_name_entry.delete(0, 'end')
       self.password_entry.delete(0,'end')
       self.email_entry.delete(0,'end')
       self.gender_entry.delete(0,'end')
       self.age_entry.delete(0,'end')
       self.state_entry.delete(0,'end')
       messagebox.showinfo("Window","Refresh Successfully")

    def submit(self):
        data = {}
        data["firstName"] = self.first_name_entry.get()
        data["lastName"] = self.last_name_entry.get()
        data["password"] = self.password_entry.get()
        data["email"] = self.email_entry.get()
        data["gender"] = self.gender_entry.get()
        data["age"] = self.age_entry.get()
        #data["state"] = self.state_entry.get(1.0, tk.END)
        data["state"] = self.state_entry.get()
        special_char=['@','#','$','%','&']
        if self.first_name_entry.get()=="" or self.last_name_entry.get()=="" or self.password_entry.get=="" or self.email_entry.get()=="" or self.gender_entry.get()=="" or self.age_entry.get()=="" or self.state_entry.get()=="":
            messagebox.showinfo("Register Status","Register Failed,Please fill all detail")
        elif self.gender_entry.get()!="M" and self.gender_entry.get()!="F":
            messagebox.showinfo("Check input","Please enter male for 'M' and female for 'F' only in gender")
        elif int(self.age_entry.get())<=2:
            messagebox.showinfo("Check input","You are not elligible for use this application beacause your age is less than 3")
        elif '@gmail.com' not in self.email_entry.get():
            messagebox.showinfo("Check input","Enter valid email like *****@gmail.com")

        elif len(self.password_entry.get()) < 8 or not any(char in special_char for char in self.password_entry.get()):
            messagebox.showinfo("Check input", "Length of password must be at least 8 characters and should include at least one special character like @, #, $, %, &")
        else:
            register(cursor, conn, data)
            messagebox.showinfo("Register Status","Register Successfully,Now you can login for use this")
        
 
    def back(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        #   ========================Back_ground_image============================
        self.bg=ImageTk.PhotoImage(file="welcome.png")
        self.bg_lbl=tk.Label(root, image=self.bg).place(relwidth=1,relheight=1)
        WelcomeWindow(self.master)

class SearchWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Search")
        self.master.resizable(False, False)
        self.center_window(1950, 1100)
        self.create_widgets()
        self.pack()
        

    def center_window(self, width, height):
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')
    
    def search_querys(self,query):
# SEACRCHING WIKIPEDIA   
        # Frame for displaying results with scrollbar
        self.result_frame = tk.Frame(self.master, bg='black', borderwidth=6, relief=tk.RIDGE)
        self.result_frame.place(x=100, y=300, width=1700, height=700)

        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, bg='black', fg='white', font=("Arial", 12))
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_text.config(yscrollcommand=self.scrollbar.set)

        query=query.lower()    
        self.result_text.delete(1.0, tk.END)
        if 'wikipedia' in query:
            try:
                messagebox.showinfo("wikipedia",query)
                speak('Searching Wikipedia...')
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                # print(results)
                # self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, results)
            except wikipedia.exceptions.PageError as e:
                # print(query," not found on Wikipedia")
                speak(query+" not found on Wikipedia")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "not found data on Wikipedia")
            except wikipedia.exceptions.DisambiguationError as e:
                print(query," may refer to multiple things. Please be more specific.")
                speak(query+" may refer to multiple things. Please be more specific.")
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "may refer to multiple things. Please be more specific.")
            except Exception as e:
                # print("Error: ",e)
                messagebox.showinfo("information","Error: "+e)
                speak("Sorry, there was an error searching on Wikipedia")
# TA    LKIG WITTH AI VOICE DETECTOR
        elif 'hello' in query or 'hii' in query:
            speak("hello , how can i assist you  ")
            messagebox.showinfo("result","hello, how can i assist you")
            # print("hello , how can i assist you  ")
        elif 'how are you' in query:
            speak("i m fine , what about you ")
            messagebox.showinfo("result","i am fine, what about you")
            # print("i m fine , what about you")
# OP    ENIG YOU TUBE
        elif 'open youtube' in query:
            messagebox.showinfo("result","opening on browser")
            webbrowser.open("youtube.com")
# OP    ENIG GOOGLE
        elif 'open google' in query:
            messagebox.showinfo("result","opening on browser")
            webbrowser.open("google.com")
        
        elif 'send whatsapp message' in query or 'send whatsapp messege' in query or 'send whatsApp message' in query:
            messagebox.showinfo("result","opening on browser")
            whatsappmess()
# OP    ENIG STACK OVERFLOW
        elif 'open stack overflow' in query:
            messagebox.showinfo("result","opening on browser")
            webbrowser.open("stackoverflow.com")
        #OPENING INSTAGRAM
        elif 'instagram' in query:
            messagebox.showinfo("result","opening on browser")
            webbrowser.open("instagram.com")
        #    OPENING WHATSAPP
        elif 'whatsapp' in query or 'Whatsapp' in query or 'WhatsApp' in query or 'whatsApp' in query:
            messagebox.showinfo("result","opening on browser")
            webbrowser.open("https://web.whatsapp.com/")
# SH    UTDWN THE SYSTEM 
        elif 'shutdown' in query or 'shut down' in query or 'close device' in query:
            os.system("shutdown /s") 
            messagebox.showinfo("result","Your system will be shutdown in few second")
    
        #restart system
        elif 'restart device' in query or 're start device' in query:
            os.system("shutdown /r")
            messagebox.showinfo("result","Your system will be restart in few second")
    
# OP    ENIG CMD
        elif 'command prompt' in query or 'command' in query:
            os.system('start cmd') # open command prompt
# OP    EN AMERA
        elif 'open camera' in query:
            messagebox.showinfo("Advise","press ESC for close camera")
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow("webcam", img)
                k = cv2.waitKey(1)
                if k == 27:  # press ESC for off or close camera
                    break
            
            cap.release()
            cv2.destroyAllWindows()  # Close all OpenCV windows
# IT     WIL CLICK THE PICTURES
        elif 'take picture' in query:
            clickpicture()
            messagebox.showinfo("result","Your pic. has been taken")
        
# IT     WIL OPEN THE FILES 
        elif 'file' in query:
            file_path = r"D:\Sudhanshu\cirtificate" # We Have To change the path of file if we are using any other laptop
            os.startfile(file_path)
# IT     WIL PROVIDE THE SYSTEM INFORMATION
        elif 'system info' in query:
            system_info()
        # IT WILL LOCK THE PC SCREEN         
        elif 'lock screen' in query or 'screen lock' in query:
            lockScreen()  
# OPENIG CONTROL PANEL
        elif 'open control panel' in query:
            openControlPanel()
# OPEN ASK MANAGER
        elif 'open task manager' in query:
            openTaskManager()
# SEARCING ON GOOGLE
        elif 'search' in query:
            n_query=query.replace('search','')
            searchOnGoogle(n_query)
# PLAY USIC FROM YOU TUBE 
        elif 'play song on youtube' in query:
            # print("Which song you want to play or listen")
            speak("Which song you want to play or listen")
            messagebox.showinfo("advise","say song name")
            song=takeCommand()
            kit.playonyt(song)
# ENGLISH JOKES
        elif 'joke' in query:
            joke =  pyjokes.get_joke()
            self.result_text.insert(tk.END, joke)
            speak(joke)
            
# LATEST INDIA NEWS  
        elif 'news' in query:
            speak("please wait bro, fetching the latest news")
            day,head=news()
            for i in range(len(head)):
                self.result_text.insert(tk.END, "Today's " + day[i] + " news is: " + head[i] + "\n")
# SCREENSHOT 
        elif 'screenshot' in query:
            speak("bro , please tell  me the name for this screenshot file")
            messagebox.showinfo("alert","please tell me the name for this screenshot file")
            name = takeCommand().lower()
            speak("please sir hold the screen for few seconds, i am taking screenshot")
            time.sleep(3)
            img=pyautogui.screenshot()
            img.save(name+".png")
            speak("im done , the screenshot is saved in our main folder ")
            
# CA    LCUATION USING J.A.R.V.I.S 
        elif 'do some calculation' in query or 'can you calculate' in query:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("say what you want to calculate, for example: 3 plus 3 ")
                messagebox.showinfo("alert","say what you want to calculate, for example: 3 plus 3")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            my_string = r.recognize_google(audio)
            print(my_string)
            def get_operator_fn(op):
                return {
                    '+': operator.add,#plus
                    '-': operator.sub,#minus
                    'multiply': operator.mul,#multiple by
                    'into': operator.mul,#multiple by
                    'x': operator.mul,#multiple by
                    '*': operator.mul,
                    'divided': operator.truediv,#divided
                    'divide': operator.truediv,#divided
                    'by': operator.truediv,#divided
                    'bi': operator.truediv,#divided
                    'bye': operator.truediv,#divided
                    '/': operator.truediv
                }[op]
            def eval_binary_expr(op1, oper, op2):
                op1, op2 = int(op1), int(op2)
                return get_operator_fn(oper)(op1, op2)
            result = eval_binary_expr(*(my_string.split()))
            self.result_text.insert(tk.END, "your result is "+str(result))
            speak("your result is ")
            speak(result)
            
# AC    TIVTE HOW TO DO ANYTHING MODE 
        elif 'can you give some information' in query or 'can u give some information' in query or 'Can you give some information' in query:
            speak("Yes, How can i help yoy")
            messagebox.showinfo("result","Yes, how can i help you")

            while True:
                speak("please tell me what you want to know")
                messagebox.showinfo("result","please tell me what you want to know")
                how = takeCommand()
                try:
                    if 'exit' in how or 'close' in how or 'back' in how:
                        speak("okay sir,you are existed")
                        break
                    else:
                        max_results = 1
                        how_to = search_wikihow(how, max_results)
                        assert len(how_to) == 1
                        self.result_text.insert(tk.END, str(how_to[0].summary))
                except Exception as e:
                    speak("sorry sir, im not able to find this")
                    messagebox.showinfo("result","sorry sir, i am not able to find this")  
# PL    AYIG MUSIC FROM C DRIVE USING C DRIVE PATH           
        elif 'play music' in query:
            music_dir = r'C:\music'
            songs = os.listdir(music_dir)
            messagebox.showinfo("play song","songs")
            rd=random.choice(songs)
            os.startfile(os.path.join(music_dir, rd))
 # P    LAYNG VIDEO FROM C DRIVE USING C DRIVE PATH           
        elif 'play video' in query:
            subprocess.Popen(['explorer', '/select,', "C:\\video\\mr_kanchan_44-20230303-0001.mp4"])        
# As    kin The Time
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")   
            self.result_text.insert(tk.END, strTime)
            speak("Sir, the time is "+strTime)
            # THIS CASE CHECK THE BATTERY PERCENTAGE 
        elif 'how much power left' in query or 'how much power we have' in query or 'battery' in query:
            battery = psutil.sensors_battery()
            percentage = battery.percent
            speak(" our system have")
            speak(percentage)
            speak(" percent battery")
            messagebox.showinfo("result","our system have "+str(percentage)+"% battery")
            if percentage>=70:
                speak("we have enough power to continue our work")
                messagebox.showinfo("alert","we have enough power to continue our work")
            elif percentage>=40 and percentage<=69:
                speak("we should connect our system to charging point to charge our battery")
                messagebox.showinfo("alert","we should connect our system to charging point to charge our battery")
            elif percentage>=15 and percentage<=39:
                speak("we don't have enough power to work ,please connect to charger")
                messagebox.showinfo("alert","we don't have enough power to work, please connect to charger")
            elif percentage<=14:
                speak("we have very low power , please connect to charging, the system will shutdown soon")
                messagebox.showinfo("alert","we have very low power , please connect to charging, the system will shutdown soon")
            # THIS CASE WILL INCREASE THE VOLUME AND DECRREASE & MUTE THE VOLLLLLUME 
        elif 'volume up' in query or 'increase volume' in query:
            pyautogui.press("volumeup")
        elif 'volume down' in query:
            pyautogui.press("volumedown")
        elif 'mute' in query or 'volume mute' in query:
            pyautogui.press("volumemute")
        elif 'unmute' in query:
            pyautogui.press("volumeunmute")
        
        elif ' who are you' in query or 'who r u' in query or 'what is your name' in query or 'hu are you' in query or 'hu r u' in query:
            open_webpage('about.html')
        elif 'open chat' in query or 'open chatgpt' in query:
            open_chatgpt()
            print("Opening ChatGPT...")
        elif any(word in query for word in ['what is', 'where is', 'how', 'when', 'why' , 'who']):
            for word in ['what is', 'where is', 'how', 'when', 'why' ,'who']:
                if word in query:
                    query = query.replace(word, "")
                    break
            result = get_wolframalpha_response(query)
            if result:
                speak("result is "+result)
                self.result_text.insert(tk.END, "you result is "+result)
           
            else:
                speak('Sorry, I could not find an answer for that.')
                messagebox.showinfo("result","sorry, I couldn't find an answer for that")
        elif 'thank' in query:
            speak("You're welcome. Have a great day!")
            webbrowser.open(r'C:\Users\sudha\OneDrive\Desktop\secure\thankyou.html')
            root.destroy()
        
        elif query=='none' or query=='None':
            speak("please ask me about something")
        else:
            speak('Searching........')
            results = google_search(query)
            speak("your result is ")
            self.result_text.insert(tk.END, results)
            speak(results)

    def create_widgets(self):
        f1 = tk.Frame(self.master, bg='black', borderwidth=6)
        f1.place(x=700, y=90, width=700, height=200)
                
        tk.Label(f1, text="⋆ ˚｡⋆୨୧˚✎", bg='black', fg='#ADD8E6').grid(row=0, column=0)
        self.query_entry = tk.Entry(f1,width=40)
        self.query_entry.grid(row=0, column=1, padx=10, pady=10)
        
        submit_button = tk.Button(f1, text="🔎", bg='black', fg='#ADD8E6', width=8, command=self.search)
        submit_button.grid(row=1, column=2, sticky="e", padx=10, pady=(10, 0))
        
        microphone_button = tk.Button(f1, text="🎙️", bg='black', fg='#ADD8E6', command=self.listen)
        microphone_button.grid(row=0, column=2, sticky="w", padx=10, pady=(10, 0))

        back_button = tk.Button(f1, text="Exit", bg='black', fg='#ADD8E6', width=8, command=self.back)
        back_button.grid(row=1, column=0, columnspan=1, pady=(10, 0))

    def listen(self):
        query=takeCommand()
        self.query_entry.delete(0,tk.END)
        if query!='None':
            self.query_entry.insert(0,query)
       

    def search(self):
        query = self.query_entry.get()
        if query:
            self.search_querys(query)
        else:
            messagebox.showinfo("Error", "Please enter a search query")

    def back(self):
        messagebox.showinfo("alert","You exited")
        root.destroy()
root = tk.Tk()
root.eval('tk::PlaceWindow . center')
#   ========================Back_ground_image============================
bg=ImageTk.PhotoImage(file="welcome.png")
bg_lbl=tk.Label(root, image=bg).place(relwidth=1,relheight=1)
WelcomeWindow(root)
root.mainloop()
