Christmas Lights – Music Reactive WS2812 System (Raspberry Pi 4)

A fully automated LED + Audio engine with supervisor + systemd integration

This project creates a real-time audio-reactive LED lighting system using a Raspberry Pi 4, WS2812 LED strips, and MP3 audio playback.
It includes:

Real-time beat detection (kick / snare / volume)

Musical pitch → color mapping (12-note LED mapping)

Multiple lighting modes:

Music Reactive

Ambient

Tree (festive)

Chase (rainbow bar)

Sparkle (white/blue glitter)

Off

Automatic playback looping through songs

OLED display support (SSD1306)

GPIO button controls (Next, Previous, Play/Pause, Mode)

Supervisor system to manage multiple engines

Systemd boot-time automation (no sudo required for code execution)

📁 Project Structure
musical_lights/
│
├── src/
│   ├── led_engine.py        # WS2812 LED animation engine
│   ├── audio_engine.py      # MP3 processing + FFT + beat detection
│   ├── buttons.py           # GPIO button input
│   ├── oled_i2c.py          # Optional OLED display helper
│   ├── protocol.py          # Message format between engines
│
├── supervisor.py            # Supervises LED & Audio engines (restarts if crashed)
│
├── lib/
│   └── libeffects.so        # Compiled C acceleration library
│
├── songs/                   # Place MP3 songs here
├── logs/                    # LED + Audio logs written here
│
├── requirements.txt         # Python dependencies
├── build.sh                 # Builds libeffects.so
└── README.md                # This file

🧠 How the System Works
🟦 1. LED Engine (led_engine.py)

This engine:

Drives WS2812 LEDs using the rpi_ws281x library

Responds to real-time commands from the audio engine

Supports six modes:

0 = MUSIC (pitch + beat reactive)
1 = AMBIENT (slow color fade)
2 = OFF
3 = TREE (festive green/red/gold twinkles)
4 = CHASE (rainbow scanning bar)
5 = SPARKLE (random white/blue glitter)


The LED engine listens on a UNIX socket:

/tmp/musical_lights.sock


The audio engine sends frames like:

STATE <mode> <note> <level> <gliss> <kick> <snare>


The LED engine updates animations at ~80 FPS.

🟩 2. Audio Engine (audio_engine.py)

The audio engine:

Plays MP3 files using ffmpeg

Extracts beat, bass, snare, lead pitch, volume, using FFT

Sends LED animation parameters via UNIX socket

Responds to GPIO buttons:

Button	Function
MODE	Cycle through modes
NEXT	Next song
PREV	Previous song
PLAY	Pause / Resume

OLED display updates with:

Playing: <song>
Mode: Music / Tree / Chase / ...

🟥 3. Supervisor (supervisor.py)

The supervisor:

Starts LED engine first

Waits for /tmp/musical_lights.sock

Starts audio engine next

Restarts LED engine if it crashes

Restarts audio engine if it crashes

Ensures both engines run in independent processes

Writes logs to:

logs/led_engine.log
logs/audio_engine.log

Supervisor Architecture
+----------------------+
|   supervisor.py      |
|----------------------|
| Starts LED Engine    |-----> led_engine.log
| Waits for socket     |
| Starts Audio Engine  |-----> audio_engine.log
| Restarts if crash    |
+----------------------+


This ensures maximum stability.

⚙️ Setup Instructions
1️⃣ Install system libraries
sudo apt update
sudo apt install python3-pip ffmpeg libatlas-base-dev python3-rpi.gpio
sudo apt install python3-rpi-ws281x

2️⃣ Create a Python virtual environment
python3 -m venv /home/sijeo/christmas_lights
source /home/sijeo/christmas_lights/bin/activate


Install project requirements:

pip install -r requirements.txt

3️⃣ Build C effects library
./build.sh

4️⃣ Place songs
cp your_mp3_files.mp3 songs/

🚀 Automating with systemd
Create:
/etc/systemd/system/christmas_lights.service


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

Enable & Start
sudo systemctl daemon-reload
sudo systemctl enable christmas_lights.service
sudo systemctl start christmas_lights.service

Check Status
systemctl status christmas_lights.service

View Live Logs

Supervisor:

journalctl -fu christmas_lights


LED engine:

tail -f logs/led_engine.log


Audio engine:

tail -f logs/audio_engine.log

🧪 Testing After Boot
sudo systemctl restart christmas_lights.service


Ensure:

Music plays

LEDs animate

Buttons work

OLED updates

🛠 Troubleshooting
❗ LEDs not updating

Check LED log:

tail -f logs/led_engine.log

❗ No sound

Check audio log:

tail -f logs/audio_engine.log

❗ Supervisor restarts instantly

Check folder permissions:

chmod 777 logs

❗ Buttons do not work

Ensure:

GPIO BCM pins: 5, 6, 13, 19
Pull-up: PUD_UP
Buttons short to GND
