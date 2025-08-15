import os
import sys
import time
import datetime as dt
import random
import operator
import subprocess
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests

# --- Third-party libs ---
try:
    import tkinter as tk
    from tkinter import messagebox, font
    from PIL import ImageTk
except Exception as e:
    print("GUI imports failed:", e)
    raise

try:
    import pyttsx3
except Exception:
    pyttsx3 = None

try:
    import speech_recognition as sr
except Exception:
    sr = None

try:
    import pyaudio
except Exception:
    pyaudio = None

try:
    import wikipedia
except Exception:
    wikipedia = None

try:
    import webbrowser
except Exception:
    webbrowser = None

try:
    import cv2
except Exception:
    cv2 = None

try:
    import psutil
except Exception:
    psutil = None

try:
    import pywhatkit as kit
except Exception:
    kit = None

try:
    import pyjokes
except Exception:
    pyjokes = None

try:
    from pywikihow import search_wikihow
except Exception:
    search_wikihow = None

try:
    import wolframalpha
except Exception:
    wolframalpha = None

try:
    import pyautogui
except Exception:
    pyautogui = None

# --- Your local database module ---
try:
    from database import initialize_connection, login, register
except Exception:
    # Provide safe fallbacks if database.py not present
    def initialize_connection():
        return None, None
    def login(cur, data):
        return data.get("email") == "demo@gmail.com" and data.get("password") == "Demo@1234"
    def register(cur, conn, data):
        pass

# =========================
# Global engine for TTS
# =========================
engine = None
if pyttsx3:
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 180)
    except Exception:
        engine = None

def speak(text: str):
    try:
        if engine:
            engine.say(text)
            engine.runAndWait()
    except Exception:
        pass  # fail silently for TTS

# =========================
# Utility helpers
# =========================
APP_NAME = "OGI"

ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'runhello')
WELCOME_IMG = os.path.join(ASSETS_DIR, 'C:\\Users\\Welcome\\Desktop\\OGI\\RunHello\\welcome.png')
LOGIN_IMG = os.path.join(ASSETS_DIR, 'C:\\Users\\Welcome\\Desktop\\OGI\\RunHello\\login.jpg')
REGISTER_IMG = os.path.join(ASSETS_DIR, 'C:\\Users\\Welcome\\Desktop\\OGI\\RunHello\\register.png')
SEARCH_BG_IMG = os.path.join(ASSETS_DIR, 'C:\\Users\\Welcome\\Desktop\\OGI\\RunHello\\ss.jpg')

NEWS_API_KEY = os.environ.get('NEWSAPI_KEY', '46786c72fac44c23a036335cac3bd86c')  # optional, currently unused
WOLFRAM_APP_ID = os.environ.get('WOLFRAM_APP_ID', 'YG5T4TP5W3')

DOWNLOADS_DIR = os.path.join(os.path.expanduser('~'), 'Downloads')

# -------------------------
# NEWS (FIXED)
# -------------------------
# Multiple reliable Indian + global RSS feeds
RSS_URLS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://www.indiatoday.in/rss/1206578",          # India Today Top News
    "https://indianexpress.com/section/india/feed/",
    "https://feeds.reuters.com/reuters/INtopNews",
    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "https://feeds.ndtv.com/ndtvnews-top-stories"
]

def fetch_rss():
    """Fetch and merge entries from multiple RSS feeds."""
    all_entries = []
    for url in RSS_URLS:
        try:
            feed = feedparser.parse(url)
            if feed and feed.entries:
                all_entries.extend(feed.entries)
        except Exception as ex:
            print(f"RSS error for {url}: {ex}")
    return all_entries

def _parse_pubdate(entry):
    """Get a datetime (UTC) for the feed entry."""
    # Prefer published_parsed, then updated_parsed, then now()
    t = None
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        t = entry.published_parsed
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        t = entry.updated_parsed
    if t:
        return datetime(*t[:6])
    return datetime.utcnow()

def process_rss(entries):
    """Filter last 24h, fetch small summary from page, sort, return top 10."""
    cutoff = datetime.utcnow() - timedelta(hours=24)
    processed = []
    for e in entries:
        try:
            pub_dt = _parse_pubdate(e)
            if pub_dt < cutoff:
                continue
            link = getattr(e, "link", "")
            title = getattr(e, "title", "(no title)")

            summary_text = ""
            # Light summary fetch (best-effort, safe timeouts)
            if link:
                try:
                    resp = requests.get(link, timeout=6, headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
                    })
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    # Pick the first decent paragraph
                    p = soup.find('p')
                    if p:
                        summary_text = p.get_text(strip=True)
                except Exception as ex:
                    print(f"Summary fetch error {link}: {ex}")

            processed.append({
                'title': title,
                'published_at': pub_dt,
                'url': link,
                'summary': (summary_text or getattr(e, "summary", "")).strip()[:220]
            })
        except Exception as ex:
            print(f"Entry error: {ex}")

    processed.sort(key=lambda x: x['published_at'], reverse=True)
    return processed[:10]

def fetch_news():
    """Return list of dicts: [{'title','published_at','summary','url'}, ...]"""
    entries = fetch_rss()
    return process_rss(entries)

# =========================
# Voice capture
# =========================
def takeCommand(record_seconds=5, rate=16000, chunk=1024):
    """Capture audio via PyAudio (if available) and return recognized text using Google SR.
       Falls back to sr.Microphone if PyAudio stream creation fails."""
    if not sr:
        messagebox.showinfo("listen", "SpeechRecognition not installed")
        return "None"

    recognizer = sr.Recognizer()

    # --- Primary path: custom PyAudio stream ---
    if pyaudio:
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=rate, input=True, frames_per_buffer=chunk)
            messagebox.showinfo("listen", "Tell something")
            frames = []
            for _ in range(0, int(rate / chunk * record_seconds)):
                frames.append(stream.read(chunk))
            stream.stop_stream(); stream.close(); p.terminate()
            audio_data = sr.AudioData(b''.join(frames), rate, 2)
            try:
                query = recognizer.recognize_google(audio_data, language='en-IN')
                messagebox.showinfo("You said", query)
                return query
            except sr.UnknownValueError:
                messagebox.showinfo("listen", "Sorry, I did not understand that.")
                return "None"
            except sr.RequestError as e:
                messagebox.showinfo("listen", f"Could not request results; {e}")
                return "None"
        except Exception:
            pass  # fall back

    # --- Fallback: Microphone ---
    try:
        with sr.Microphone() as source:
            messagebox.showinfo("listen", "Listening…")
            recognizer.adjust_for_ambient_noise(source, duration=0.6)
            audio = recognizer.listen(source, phrase_time_limit=record_seconds)
        try:
            query = recognizer.recognize_google(audio, language='en-IN')
            messagebox.showinfo("You said", query)
            return query
        except sr.UnknownValueError:
            messagebox.showinfo("listen", "Sorry, I did not understand that.")
            return "None"
        except sr.RequestError as e:
            messagebox.showinfo("listen", f"Could not request results; {e}")
            return "None"
    except Exception as e:
        messagebox.showinfo("listen", f"Microphone error: {e}")
        return "None"

# =========================
# Features (helpers)
# =========================
def wishMe():
    hour = int(dt.datetime.now().hour)
    if 0 <= hour < 12:
        greet = "Good Morning!"
    elif 12 <= hour < 18:
        greet = "Good Afternoon!"
    else:
        greet = "Good Evening!"
    speak(greet)
    speak(f"I am {APP_NAME}. Please tell me how may I help you")

def clickpicture():
    if not cv2:
        messagebox.showinfo("result", "OpenCV not installed")
        return
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)
    now = dt.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    filename = os.path.join(DOWNLOADS_DIR, f"{now}.png")

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        messagebox.showinfo("result", "Camera not available")
        return
    # warm up
    for _ in range(3):
        cam.read()
    ret, frame = cam.read()
    cam.release()
    if ret:
        cv2.imwrite(filename, frame)
        speak("Photo taken!")
        messagebox.showinfo("result", f"Photo saved at: {filename}")
    else:
        messagebox.showinfo("result", "Failed to capture image")

def google_search(query: str):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Try multiple selectors as Google frequently changes markup
        candidates = [
            ("div", {"class": "BNeawe s3v9rd AP7Wnd"}),
            ("div", {"class": "BNeawe vvjwJb AP7Wnd"}),
        ]
        for tag, attrs in candidates:
            el = soup.find(tag, attrs=attrs)
            if el and el.get_text(strip=True):
                return el.get_text(strip=True)
        return "No results found"
    except Exception:
        return "No results found"

def system_info():
    if not psutil:
        messagebox.showinfo("result", "psutil not installed")
        return
    usage = f"{psutil.cpu_percent()}%"
    speak(f"CPU usage is at {usage}")
    vm = psutil.virtual_memory()
    available_gb = round(vm.available / (1024.0 ** 3), 2)
    total_gb = round(vm.total / (1024.0 ** 3), 2)
    speak(f"Available RAM is {available_gb} gigabytes out of {total_gb} gigabytes.")
    messagebox.showinfo("result", f"Available RAM: {available_gb} GB / {total_gb} GB")

def lockScreen():
    try:
        import ctypes
        ctypes.windll.user32.LockWorkStation()
        speak("Screen locked.")
    except Exception:
        messagebox.showinfo("result", "Lock screen is only supported on Windows desktop.")

def openControlPanel():
    try:
        os.system("control")
        speak("Control Panel opened.")
    except Exception:
        messagebox.showinfo("result", "Unable to open Control Panel")

def openTaskManager():
    try:
        os.system("taskmgr")
        speak("Task Manager opened.")
    except Exception:
        messagebox.showinfo("result", "Unable to open Task Manager")

def open_chatgpt():
    if webbrowser:
        webbrowser.open("https://chat.openai.com/")

# WolframAlpha
wa_client = None
if wolframalpha and WOLFRAM_APP_ID and WOLFRAM_APP_ID != 'YG5T4TP5W3':
    try:
        wa_client = wolframalpha.Client(WOLFRAM_APP_ID)
    except Exception:
        wa_client = None

def get_wolframalpha_response(query):
    if not wa_client:
        return ""
    try:
        res = wa_client.query(query)
        return next(res.results).text
    except Exception:
        return ""

def find_all_video_files(drives, extensions):
    video_files = []
    for drive in drives:
        for root, dirs, files in os.walk(drive, topdown=True, followlinks=False):
            for file in files:
                if file.lower().endswith(extensions):
                    video_files.append(os.path.join(root, file))
    return video_files

def whatsappmess():
    if not kit:
        messagebox.showinfo("Information", "pywhatkit not installed")
        return
    speak("Which number do you want to send message? Include country code like 91XXXXXXXXXX")
    messagebox.showinfo("Information", "Say the number with country code, e.g., 918228XXXXX")
    number = takeCommand()
    if not number or number.lower() == 'none':
        messagebox.showinfo("Information", "No number captured")
        return
    number = '+' + ''.join(ch for ch in number if ch.isdigit())

    speak("What is your message?")
    messagebox.showinfo("Information", "Say your message")
    text = takeCommand()
    while not text or text.lower() == 'none':
        speak("Please speak the message again")
        text = takeCommand()

    # Ask for time (ensure >= current minute + 2 as pywhatkit requires)
    now = dt.datetime.now()
    min_send = (now + dt.timedelta(minutes=2))

    speak("Which hour to send (24-hour format)?")
    hour_s = takeCommand().replace(' ', '')
    hour = int(hour_s) if hour_s.isdigit() else min_send.hour

    speak("Which minute to send?")
    minute_s = takeCommand().replace(' ', '')
    minute = int(minute_s) if minute_s.isdigit() else min_send.minute

    # Ensure scheduled time is at least 2 minutes in the future
    scheduled = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if scheduled < min_send:
        scheduled = min_send
        hour, minute = scheduled.hour, scheduled.minute

    try:
        kit.sendwhatmsg(number, text, hour, minute, 20, True, True)
        messagebox.showinfo("result", f"Message scheduled at {hour:02d}:{minute:02d}")
    except Exception as e:
        messagebox.showinfo("result", f"Failed to schedule: {e}")

def find_all_files_by_ext(drives, extensions):
    files_list = []
    for drive in drives:
        for root, dirs, files in os.walk(drive, topdown=True, followlinks=False):
            for file in files:
                if file.lower().endswith(extensions):
                    files_list.append(os.path.join(root, file))
    return files_list
# =========================
# Tkinter Windows
# =========================
conn, cursor = initialize_connection()

def center_window(root, width, height):
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

class WelcomeWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Welcome")
        center_window(self.master, 1200, 700)
        self.master.resizable(True, True)
        self.master.configure(bg='black')

        # Background image if present
        if os.path.exists(WELCOME_IMG):
            self.bg = ImageTk.PhotoImage(file=WELCOME_IMG)
            tk.Label(self.master, image=self.bg).place(relwidth=1, relheight=1)

        f1 = tk.Frame(self.master, bg='black', borderwidth=6)
        f1.place(relx=0.75, rely=0.85, width=220, height=80)

        btn_font = font.Font(family="Helvetica", size=16, weight="bold")
        tk.Button(
            f1,
            text="Next",
            width=12,
            height=2,
            font=btn_font,
            fg='#00ff00',
            bg='#1c1c1c',
            activebackground='#00ff00',
            activeforeground='black',
            relief='flat',
            command=self.open_register_window
        ).pack(pady=10)

        self.pack(fill='both', expand=True)
        wishMe()

    def open_register_window(self):
        self.destroy()
        if os.path.exists(REGISTER_IMG):
            self.master.bg = ImageTk.PhotoImage(file=REGISTER_IMG)
            tk.Label(self.master, image=self.master.bg).place(relwidth=1, relheight=1)
        RegisterWindow(self.master)

class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Login")
        center_window(self.master, 1200, 700)

        if os.path.exists(LOGIN_IMG):
            self.bg = ImageTk.PhotoImage(file=LOGIN_IMG)
            tk.Label(self.master, image=self.bg).place(relwidth=1, relheight=1)

        f1 = tk.Frame(self.master, bg='#011226', borderwidth=6, relief=tk.GROOVE)
        f1.place(x=700, y=250, width=360, height=210)

        f3 = tk.Frame(self.master, bg='#011226', borderwidth=6)
        f3.place(x=700, y=150, width=360, height=80)
        tk.Label(f3, text="Login Now", bg='#011226', fg='#ADD8E6', font=('arial', 28, 'bold')).grid(row=0, column=0)

        tk.Label(f1, text="Email:", bg='#011226', fg='#ADD8E6').grid(row=0, column=0)
        self.username_entry = tk.Entry(f1)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(f1, text="Password:", bg='#011226', fg='#ADD8E6').grid(row=1, column=0)
        self.password_entry = tk.Entry(f1, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Button(f1, text="Submit", bg='#011226', fg='#ADD8E6', width=8, command=self.submit).grid(row=2, column=1, sticky="e", padx=10, pady=(10, 0))
        tk.Button(f1, text="Refresh", bg='#011226', fg='#ADD8E6', width=8, command=self.refresh_window).grid(row=3, column=0, padx=10, pady=(10, 0))
        tk.Button(f1, text="Back", bg='#011226', fg='#ADD8E6', width=8, command=self.back).grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))

        self.pack(fill='both', expand=True)

    def refresh_window(self):
        self.username_entry.delete(0, 'end')
        self.password_entry.delete(0, 'end')
        messagebox.showinfo("Window", "Refresh Successfully")

    def submit(self):
        data = {"email": self.username_entry.get().strip(), "password": self.password_entry.get()}
        if not data["email"] or not data["password"]:
            messagebox.showinfo("check input", "Enter email and password")
            return
        try:
            ok = login(cursor, data)
        except Exception as e:
            ok = False
        if ok:
            messagebox.showinfo("Login Status", "Login Successfully")
            self.destroy()
            if os.path.exists(SEARCH_BG_IMG):
                self.master.bg = ImageTk.PhotoImage(file=SEARCH_BG_IMG)
                tk.Label(self.master, image=self.master.bg).place(relwidth=1, relheight=1)
            SearchWindow(self.master)
        else:
            messagebox.showinfo("Login Status", "Login failed")

    def back(self):
        self.destroy()
        if os.path.exists(WELCOME_IMG):
            self.master.bg = ImageTk.PhotoImage(file=WELCOME_IMG)
            tk.Label(self.master, image=self.master.bg).place(relwidth=1, relheight=1)
        WelcomeWindow(self.master)

class RegisterWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Register")
        center_window(self.master, 1200, 700)
        self.master.configure(bg='black')

        if os.path.exists(REGISTER_IMG):
            self.bg = ImageTk.PhotoImage(file=REGISTER_IMG)
            tk.Label(self.master, image=self.bg).place(relwidth=1, relheight=1)

        self.label_font = font.Font(family="Helvetica", size=16, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=14, weight="bold")

        f2 = tk.Frame(self.master, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f2.place(x=800, y=200, width=380, height=420)

        f3 = tk.Frame(self.master, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f3.place(x=800, y=120, width=380, height=70)

        f4 = tk.Frame(self.master, bg='#1C1C1C', borderwidth=6, relief=tk.GROOVE)
        f4.place(x=800, y=630, width=380, height=40)

        tk.Label(f3, text="Register Now", bg='#1C1C1C', fg='#FF4500', font=('Helvetica', 24, 'bold')).grid(row=0, column=0)
        tk.Label(f4, text="If you already have an account:", bg='#1C1C1C', fg='white', font=('Helvetica', 12, 'bold')).grid(row=0, column=0)

        entries = {}
        def add_row(r, label, width=26):
            tk.Label(f2, text=f"{label}", bg='#1C1C1C', fg='white').grid(row=r, column=0, sticky="w")
            e = tk.Entry(f2, width=width, bg='#333333', fg='white')
            e.grid(row=r, column=1, padx=10, pady=8, sticky="e")
            entries[label] = e

        add_row(0, "First Name:")
        add_row(1, "Last Name:")
        tk.Label(f2, text="Password:", bg='#1C1C1C', fg='white').grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(f2, show="*", width=26, bg='#333333', fg='white')
        self.password_entry.grid(row=2, column=1, padx=10, pady=8, sticky="e")
        add_row(3, "Email:")
        add_row(4, "Gender (M/F):", width=10)
        add_row(5, "Age:", width=10)
        add_row(6, "State:", width=20)

        self.first_name_entry = entries["First Name:"]
        self.last_name_entry = entries["Last Name:"]
        self.email_entry = entries["Email:"]
        self.gender_entry = entries["Gender (M/F):"]
        self.age_entry = entries["Age:"]
        self.state_entry = entries["State:"]

        tk.Button(f2, text="Register", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=10, command=self.submit).grid(row=7, column=1, padx=10, pady=10, sticky="e")
        tk.Button(f2, text="Refresh", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=10, command=self.refresh_window).grid(row=8, column=0, padx=10, pady=8)
        tk.Button(f2, text="Back", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=10, command=self.back).grid(row=7, column=0, sticky="w", padx=10, pady=10)

        tk.Button(self.master, text="Login", bg='#1C1C1C', fg='#FF4500', font=self.button_font, width=10, command=self.open_login_window).place(x=1040, y=630)

        self.pack(fill='both', expand=True)

    def open_login_window(self):
        self.destroy()
        if os.path.exists(LOGIN_IMG):
            self.master.bg = ImageTk.PhotoImage(file=LOGIN_IMG)
            tk.Label(self.master, image=self.master.bg).place(relwidth=1, relheight=1)
        LoginWindow(self.master)

    def refresh_window(self):
        for e in [self.first_name_entry, self.last_name_entry, self.password_entry, self.email_entry, self.gender_entry, self.age_entry, self.state_entry]:
            e.delete(0, 'end')
        messagebox.showinfo("Window", "Refresh Successfully")

    def submit(self):
        data = {
            "firstName": self.first_name_entry.get().strip(),
            "lastName": self.last_name_entry.get().strip(),
            "password": self.password_entry.get(),
            "email": self.email_entry.get().strip(),
            "gender": self.gender_entry.get().strip().upper(),
            "age": self.age_entry.get().strip(),
            "state": self.state_entry.get().strip(),
        }
        special_char = {'@', '#', '$', '%', '&'}

        if not all([data["firstName"], data["lastName"], data["password"], data["email"], data["gender"], data["age"], data["state"]]):
            messagebox.showinfo("Register Status", "Register Failed. Please fill all details")
            return
        if data["gender"] not in {"M", "F"}:
            messagebox.showinfo("Check input", "Please enter 'M' or 'F' for gender")
            return
        try:
            age_int = int(data["age"])
        except ValueError:
            messagebox.showinfo("Check input", "Age must be a number")
            return
        if age_int <= 2:
            messagebox.showinfo("Check input", "You are not eligible to use this application (age < 3)")
            return
        if '@gmail.com' not in data["email"]:
            messagebox.showinfo("Check input", "Enter valid email like *****@gmail.com")
            return
        if len(data["password"]) < 8 or not any(c in special_char for c in data["password"]):
            messagebox.showinfo("Check input", "Password must be ≥ 8 chars and include at least one of @ # $ % &")
            return

        try:
            register(cursor, conn, data)
            messagebox.showinfo("Register Status", "Register Successfully. Now you can login")
        except Exception as e:
            messagebox.showinfo("Register Status", f"Register failed: {e}")

    def back(self):
        self.destroy()
        if os.path.exists(WELCOME_IMG):
            self.master.bg = ImageTk.PhotoImage(file=WELCOME_IMG)
            tk.Label(self.master, image=self.master.bg).place(relwidth=1, relheight=1)
        WelcomeWindow(self.master)

class SearchWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Search")
        center_window(self.master, 1200, 700)

        self.create_widgets()
        self.pack(fill='both', expand=True)

    def create_widgets(self):
        f1 = tk.Frame(self.master, bg='black', borderwidth=6)
        f1.place(x=300, y=40, width=600, height=140)

        tk.Label(f1, text="⋆ ˚｡⋆୨୧˚✎", bg='black', fg='#ADD8E6').grid(row=0, column=0)
        self.query_entry = tk.Entry(f1, width=40)
        self.query_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Button(f1, text="🔎", bg='black', fg='#ADD8E6', width=8, command=self.search).grid(row=1, column=2, sticky="e", padx=10, pady=(10, 0))
        tk.Button(f1, text="🎙️", bg='black', fg='#ADD8E6', command=self.listen).grid(row=0, column=2, sticky="w", padx=10, pady=(10, 0))
        tk.Button(f1, text="Exit", bg='black', fg='#ADD8E6', width=8, command=self.back).grid(row=1, column=0, columnspan=1, pady=(10, 0))

        # Result area with scrollbar
        self.result_frame = tk.Frame(self.master, bg='black', borderwidth=6, relief=tk.RIDGE)
        self.result_frame.place(x=60, y=220, width=1080, height=430)

        self.result_text = tk.Text(self.result_frame, wrap=tk.WORD, bg='black', fg='white', font=("Arial", 12))
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.result_frame, command=self.result_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.result_text.config(yscrollcommand=self.scrollbar.set)

    def listen(self):
        q = takeCommand()
        self.query_entry.delete(0, tk.END)
        if q and q.lower() != 'none':
            self.query_entry.insert(0, q)

    def search(self):
        q = self.query_entry.get().strip()
        if not q:
            messagebox.showinfo("Error", "Please enter a search query")
            return
        self.search_querys(q)

    def back(self):
        messagebox.showinfo("alert", "You exited")
        self.master.destroy()

    # =========================
    # Core command router
    # =========================
    def search_querys(self, query):
        query_low = query.lower()
        self.result_text.delete(1.0, tk.END)

        # Wikipedia
        if 'wikipedia' in query_low:
            if not wikipedia:
                self.result_text.insert(tk.END, "wikipedia module not installed")
                return
            try:
                speak('Searching Wikipedia...')
                topic = query_low.replace("wikipedia", "").strip()
                results = wikipedia.summary(topic, sentences=2)
                speak("According to Wikipedia")
                self.result_text.insert(tk.END, results)
            except wikipedia.exceptions.PageError:
                speak(f"{topic} not found on Wikipedia")
                self.result_text.insert(tk.END, "Not found on Wikipedia")
            except wikipedia.exceptions.DisambiguationError:
                speak("This may refer to multiple things. Please be more specific.")
                self.result_text.insert(tk.END, "Multiple matches. Be more specific.")
            except Exception as e:
                self.result_text.insert(tk.END, f"Wikipedia error: {e}")

        # Small talk
        elif any(k in query_low for k in ['hello', 'hii', 'hi']):
            speak("Hello, how can I assist you?")
            self.result_text.insert(tk.END, "Hello, how can I assist you?")
        elif 'how are you' in query_low:
            speak("I'm fine. What about you?")
            self.result_text.insert(tk.END, "I'm fine. What about you?")

        # Open websites/apps
        elif 'open youtube' in query_low:
            webbrowser.open("https://youtube.com")
        elif 'open google' in query_low:
            webbrowser.open("https://google.com")
        elif 'send whatsapp message' in query_low or 'send whatsApp message' in query:
            whatsappmess()
        elif 'open stack overflow' in query_low:
            webbrowser.open("https://stackoverflow.com")
        elif 'instagram' in query_low:
            webbrowser.open("https://instagram.com")
        elif 'whatsapp' in query_low:
            webbrowser.open("https://web.whatsapp.com/")

        # Power
        elif 'shutdown' in query_low or 'shut down' in query_low or 'close device' in query_low:
            os.system("shutdown /s /t 0")
            messagebox.showinfo("result", "Shutting down…")
        elif 'restart device' in query_low or 're start device' in query_low:
            os.system("shutdown /r /t 0")
            messagebox.showinfo("result", "Restarting…")

        # System tools
        elif 'command prompt' in query_low or 'command' in query_low:
            os.system('start cmd')
        elif 'open camera' in query_low:
            if not cv2:
                self.result_text.insert(tk.END, "OpenCV not installed")
            else:
                messagebox.showinfo("Advise", "Press ESC to close camera")
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    self.result_text.insert(tk.END, "Camera not available")
                else:
                    while True:
                        ret, img = cap.read()
                        if not ret:
                            break
                        cv2.imshow("webcam", img)
                        if cv2.waitKey(1) & 0xFF == 27:
                            break
                    cap.release(); cv2.destroyAllWindows()
        elif 'take picture' in query_low:
            clickpicture()
        elif 'file' in query_low:
            file_path = r"D:\Sudhanshu\cirtificate"
            if os.path.isdir(file_path):
                os.startfile(file_path)
            else:
                self.result_text.insert(tk.END, f"Path not found: {file_path}")
        elif 'system info' in query_low:
            system_info()
        elif 'lock screen' in query_low or 'screen lock' in query_low:
            lockScreen()
        elif 'open control panel' in query_low:
            openControlPanel()
        elif 'open task manager' in query_low:
            openTaskManager()

        # Google search
        elif query_low.startswith('search'):
            n_query = query_low.replace('search', '').strip()
            speak(f'Searching for {n_query} on Google…')
            webbrowser.open(f'https://www.google.com/search?q={n_query}')

        # Play YouTube song
        elif 'play song on youtube' in query_low:
            speak("Which song do you want to play?")
            name = takeCommand()
            if kit and name and name.lower() != 'none':
                try:
                    kit.playonyt(name)
                except Exception as e:
                    self.result_text.insert(tk.END, f"Failed to play: {e}")
            else:
                self.result_text.insert(tk.END, "pywhatkit not installed or no song name")

        # Jokes
        elif 'joke' in query_low:
            if pyjokes:
                j = pyjokes.get_joke()
                self.result_text.insert(tk.END, j)
                speak(j)
            else:
                self.result_text.insert(tk.END, "pyjokes not installed")

        # -------- NEWS (FIXED) --------
        elif 'news' in query_low:
            speak("Please wait, fetching the latest news")
            try:
                items = fetch_news()
            except Exception as e:
                items = []
                print("fetch_news error:", e)

            if items:
                self.result_text.insert(tk.END, "\nTop 10 Latest News (Last 24 Hours):\n\n")
                for i, n in enumerate(items, 1):
                    pub_str = n['published_at'].strftime("%Y-%m-%d %H:%M")
                    block = f"{i}. {n['title']}\n   Published: {pub_str}\n   Summary: {n['summary']}\n   Link: {n['url']}\n\n"
                    self.result_text.insert(tk.END, block)
                    try:
                        speak(n['title'])
                    except Exception:
                        pass
            else:
                self.result_text.insert(tk.END, "Sorry, I couldn't fetch the news at the moment.")

        # Screenshot
        elif 'screenshot' in query_low:
            if not pyautogui:
                self.result_text.insert(tk.END, "pyautogui not installed")
            else:
                speak("Please tell me the name for this screenshot file")
                name = takeCommand().lower()
                if not name or name == 'none':
                    name = dt.datetime.now().strftime("screenshot-%Y%m%d-%H%M%S")
                speak("Hold the screen for a few seconds, I am taking screenshot")
                time.sleep(2)
                img = pyautogui.screenshot()
                path = os.path.join(DOWNLOADS_DIR, f"{name}.png")
                img.save(path)
                speak("Done. Screenshot saved in Downloads")
                self.result_text.insert(tk.END, f"Saved: {path}")

        # Calculator (voice)
        elif 'do some calculation' in query_low or 'can you calculate' in query_low:
            if not sr:
                self.result_text.insert(tk.END, "SpeechRecognition not installed")
                return
            r = sr.Recognizer()
            try:
                with sr.Microphone() as source:
                    speak("Say what you want to calculate, for example: 3 plus 3")
                    r.adjust_for_ambient_noise(source, duration=0.6)
                    audio = r.listen(source)
                phrase = r.recognize_google(audio)
            except Exception as e:
                self.result_text.insert(tk.END, f"Mic error: {e}")
                return

            # Flexible parse: extract numbers and operator words
            tokens = phrase.lower().replace('by', ' ').split()
            ops = {
                '+': operator.add, 'plus': operator.add, 'add': operator.add,
                '-': operator.sub, 'minus': operator.sub, 'subtract': operator.sub,
                'x': operator.mul, '*': operator.mul, 'multiply': operator.mul, 'into': operator.mul,
                '/': operator.truediv, 'divided': operator.truediv, 'divide': operator.truediv
            }
            nums = []
            op_fn = None
            for t in tokens:
                if t in ops and not op_fn:
                    op_fn = ops[t]
                else:
                    try:
                        nums.append(float(t))
                    except ValueError:
                        pass
            if op_fn and len(nums) >= 2:
                result = op_fn(nums[0], nums[1])
                speak(f"Your result is {result}")
                self.result_text.insert(tk.END, f"Your result is {result}")
            else:
                self.result_text.insert(tk.END, f"Couldn't parse expression: {phrase}")

        # How-to via wikiHow
        elif 'can you give some information' in query_low or 'can u give some information' in query_low:
            if not search_wikihow:
                self.result_text.insert(tk.END, "pywikihow not installed")
                return
            speak("Yes, how can I help you")
            while True:
                speak("Please tell me what you want to know. Say exit to stop.")
                how = takeCommand()
                if not how or how.lower() == 'none':
                    continue
                low = how.lower()
                if any(x in low for x in ['exit', 'close', 'back']):
                    speak("Okay, exiting how-to mode")
                    break
                try:
                    how_to = search_wikihow(how, max_results=1)
                    if how_to:
                        self.result_text.insert(tk.END, str(how_to[0].summary) + "\n\n")
                    else:
                        self.result_text.insert(tk.END, "No result found\n")
                except Exception:
                    self.result_text.insert(tk.END, "Sorry, I couldn't find this\n")
        elif 'play music' in query_low:
            music_ext = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma')
            drives = [f"{chr(i)}:\\" for i in range(65, 91) if os.path.exists(f"{chr(i)}:\\")]
        
            self.result_text.insert(tk.END, "Searching for music files...\n")
            all_music = find_all_files_by_ext(drives, music_ext)
        
            if all_music:
                rd = random.choice(all_music)
                os.startfile(rd)
                self.result_text.insert(tk.END, f"Playing music: {rd}\n")
            else:
                self.result_text.insert(tk.END, "No music files found.\n")
        elif 'play video' in query_low:
            video_ext = ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv')
            drives = [f"{chr(i)}:\\" for i in range(65, 91) if os.path.exists(f"{chr(i)}:\\")]
        
            self.result_text.insert(tk.END, "Searching for video files...\n")
        
            all_videos = find_all_video_files(drives, video_ext)
        
            if all_videos:
                rd = random.choice(all_videos)
                os.startfile(rd)
                self.result_text.insert(tk.END, f"Playing: {rd}\n")
            else:
                self.result_text.insert(tk.END, "No video files found on the system.\n")

        # Time & battery
        elif 'the time' in query_low:
            now = dt.datetime.now().strftime("%H:%M:%S")
            self.result_text.insert(tk.END, now)
            speak(f"The time is {now}")
        elif 'battery' in query_low or 'how much power left' in query_low or 'how much power we have' in query_low:
            if not psutil:
                self.result_text.insert(tk.END, "psutil not installed")
            else:
                b = psutil.sensors_battery()
                if not b:
                    self.result_text.insert(tk.END, "Battery info not available")
                else:
                    p = b.percent
                    speak(f"Our system has {p} percent battery")
                    self.result_text.insert(tk.END, f"Battery: {p}%\n")
                    if p >= 70:
                        tip = "We have enough power to continue our work"
                    elif 40 <= p <= 69:
                        tip = "Consider connecting to charger"
                    elif 15 <= p <= 39:
                        tip = "Low power, please connect to charger"
                    else:
                        tip = "Very low power, system may shutdown soon"
                    speak(tip)
                    self.result_text.insert(tk.END, tip)

        # Volume
        elif 'volume up' in query_low or 'increase volume' in query_low:
            if pyautogui: pyautogui.press("volumeup")
        elif 'volume down' in query_low:
            if pyautogui: pyautogui.press("volumedown")
        elif 'mute' in query_low or 'volume mute' in query_low:
            if pyautogui: pyautogui.press("volumemute")
        elif 'unmute' in query_low:
            if pyautogui: pyautogui.press("volumemute")  # toggle

        # About & ChatGPT
        elif any(k in query_low for k in [' who are you', 'who r u', 'what is your name', 'hu are you', 'hu r u']):
            about_path = os.path.join(os.path.dirname(__file__), 'about.html')
            if os.path.exists(about_path):
                open_webpage(about_path)
            else:
                self.result_text.insert(tk.END, f"about.html not found at {about_path}")
        elif 'open chat' in query_low or 'open chatgpt' in query_low:
            open_chatgpt()

        # Q/A via WolframAlpha
        elif any(w in query_low for w in ['what is', 'where is', 'how', 'when', 'why', 'who']):
            cleaned = query
            for w in ['what is', 'where is', 'how', 'when', 'why', 'who']:
                cleaned = cleaned.replace(w, '')
            result = get_wolframalpha_response(cleaned.strip())
            if result:
                speak("Result is " + result)
                self.result_text.insert(tk.END, "Your result is " + result)
            else:
                speak('Sorry, I could not find an answer for that.')
                self.result_text.insert(tk.END, "Sorry, I couldn't find an answer for that")

        elif 'thank' in query_low:
            speak("You're welcome. Have a great day!")
            thanks_page = os.path.join(os.path.dirname(__file__), 'secure', 'thankyou.html')
            if os.path.exists(thanks_page):
                webbrowser.open(thanks_page)
            self.master.destroy()

        elif query_low in {'none', 'null', ''}:
            speak("Please ask me about something")
        else:
            speak('Searching…')
            results = google_search(query)
            speak("Your result is ")
            self.result_text.insert(tk.END, results)
            speak(results)

# =========================
# App bootstrap
# =========================
def main():
    root = tk.Tk()
    root.title(APP_NAME)
    try:
        root.eval('tk::PlaceWindow . center')
    except Exception:
        pass

    # Background for first screen
    if os.path.exists(WELCOME_IMG):
        bg = ImageTk.PhotoImage(file=WELCOME_IMG)
        tk.Label(root, image=bg).place(relwidth=1, relheight=1)
        # keep reference
        root._bg = bg

    WelcomeWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
