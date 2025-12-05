Christmas Lights – Music Reactive WS2812 LED System (Raspberry Pi 4)

Real-time audio-reactive LED lighting using WS2812 LED strips, MP3 playback, FFT analysis, beat detection, OLED display, GPIO buttons, and a Python supervisor to manage the LED and audio engines.

⭐ Features
🔊 Audio Reactive Effects

Real-time FFT analysis

Kick / Snare / Volume detection

Lead melody → LED color mapping

Smooth glissando transitions

Per-frame LED animations (80 FPS)

💡 Lighting Modes
Mode	Description
Music	Full reactive mode (pitch + beats)
Ambient	Slow breathing colors
Off	LEDs off
Tree	Festive twinkling lights
Chase	Rainbow bar running across strip
Sparkle	Random white-blue glitter
🧰 Supervisor Architecture

Starts LED engine

Waits for socket to initialize

Starts Audio engine

Restarts either if crashed

Logs stored independently in logs/

🔘 Button Controls
Button	Action
MODE	Cycle through modes
NEXT	Next song
PREV	Previous song
PLAY	Pause / Resume
🖥️ OLED Display (SSD1306)

Shows:

Playing: <song>
Mode: Music / Tree / Chase / Sparkle

📁 Project Structure
musical_lights/
│
├── src/
│   ├── led_engine.py
│   ├── audio_engine.py
│   ├── buttons.py
│   ├── oled_i2c.py
│   ├── protocol.py
│
├── supervisor.py
├── lib/
│   └── libeffects.so
│
├── songs/
├── logs/
├── build.sh
├── requirements.txt
└── README.md


🧠 System Architecture
+----------------------+
|   supervisor.py      |
|----------------------|
| Starts LED Engine    |
| Waits for socket     |
| Starts Audio Engine  |
| Restarts on failure  |
+----------+-----------+
           |
    +------v-------+
    | LED Engine   |
    | WS2812 FX    |
    +--------------+
           ^
           |
    +------v-------+
    | Audio Engine |
    | FFT + Beats  |
    +--------------+

⚙️ Installation
1️⃣ Install system dependencies
sudo apt update
sudo apt install ffmpeg python3-pip python3-rpi.gpio python3-rpi-ws281x libatlas-base-dev

2️⃣ Create and activate virtual environment
python3 -m venv /home/sijeo/christmas_lights
source /home/sijeo/christmas_lights/bin/activate


Install Python requirements:

pip install -r requirements.txt

3️⃣ Build the C effects library
./build.sh

4️⃣ Add MP3 files
cp *.mp3 songs/

🚀 Running Manually
source /home/sijeo/christmas_lights/bin/activate
python3 supervisor.py

🔁 Automate with systemd

Create the service file:

sudo nano /etc/systemd/system/christmas_lights.service


Paste:

[Unit]
Description=Christmas Lights (Supervisor)
After=network.target sound.target

[Service]
Type=simple
User=sijeo
WorkingDirectory=/home/sijeo/musical_lights

Environment="VIRTUAL_ENV=/home/sijeo/christmas_lights"
Environment="PATH=/home/sijeo/christmas_lights/bin:/usr/bin:/bin"

ExecStart=/home/sijeo/christmas_lights/bin/python3 supervisor.py

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target


Reload and enable:

sudo systemctl daemon-reload
sudo systemctl enable christmas_lights.service
sudo systemctl start christmas_lights.service

🧪 Monitoring & Debugging
Supervisor logs:
journalctl -fu christmas_lights

LED engine log:
tail -f logs/led_engine.log

Audio engine log:
tail -f logs/audio_engine.log

🛠 Troubleshooting
LEDs not turning on

Check power supply (5V 10A recommended)

Verify ground is shared with Raspberry Pi

No sound

Ensure correct ALSA device in audio_engine.py

Buttons not working

Verify wiring to BCM pins:

MODE = 5
NEXT = 6
PREV = 13
PLAY = 19

OLED not responding

Check I²C bus:

sudo i2cdetect -y 1

📜 License

MIT License

🙌 Acknowledgements

Raspberry Pi Foundation

rpi_ws281x Library

FFmpeg Team

Adafruit SSD1306 Library
