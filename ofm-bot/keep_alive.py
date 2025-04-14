from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    print("✅ Ping reçu de UptimeRobot – Le bot reste en ligne !")
    return "Le bot OFM est en ligne !", 200

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
