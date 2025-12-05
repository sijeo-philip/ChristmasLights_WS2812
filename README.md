# 🎄 Christmas Lights – Music Reactive WS2812 LED System (Raspberry Pi 4)

Real-time audio-reactive LED lighting using WS2812 strips, MP3 playback, FFT analysis, beat detection, OLED display, GPIO buttons, and a Python supervisor that manages the LED and audio engines.

---

## ⭐ Features

### 🔊 Audio Reactive Effects
```
- Real-time FFT analysis  
- Kick / Snare / Volume detection  
- Lead melody → LED color mapping  
- Glissando smoothing  
- High-performance C-accelerated effects  
```

### 💡 Lighting Modes
```
0  MUSIC     - Full reactive mode (pitch + beat)
1  AMBIENT   - Slow breathing colors
2  OFF       - LEDs off
3  TREE      - Festive green/red/gold twinkles
4  CHASE     - Rainbow bar scanning
5  SPARKLE   - Random white/blue glitter
```

### 🔘 Button Controls
```
MODE → Cycle modes
NEXT → Next track
PREV → Previous track
PLAY → Pause / Resume
```

### 🖥️ OLED SSD1306 Display
```
Playing: <song>
Mode: Music / Tree / Sparkle ...
```

---

## 📁 Project Structure

```
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
```

---

## 🧠 System Architecture

```
+----------------------+
|   supervisor.py      |
|----------------------|
| Starts LED Engine    |
| Waits for socket     |
| Starts Audio Engine  |
| Restarts on crash    |
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
```

---

## ⚙️ Installation

### 1️⃣ System Packages

```bash
sudo apt update
sudo apt install ffmpeg python3-pip python3-rpi.gpio python3-rpi-ws281x libatlas-base-dev
```

### 2️⃣ Create Python Virtual Environment

```bash
python3 -m venv /home/sijeo/christmas_lights
source /home/sijeo/christmas_lights/bin/activate
pip install -r requirements.txt
```

### 3️⃣ Build C Library

```bash
./build.sh
```

### 4️⃣ Add MP3 Songs

```bash
cp *.mp3 songs/
```

---

## 🚀 Running Manually

```bash
source /home/sijeo/christmas_lights/bin/activate
python3 supervisor.py
```

---

# 🔁 Automating with systemd

Create:

```
/etc/systemd/system/christmas_lights.service
```

Paste:

```ini
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
```

Enable + start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable christmas_lights.service
sudo systemctl start christmas_lights.service
```

---

## 🧪 Monitoring & Debugging

Supervisor:
```bash
journalctl -fu christmas_lights
```

LED Engine:
```bash
tail -f logs/led_engine.log
```

Audio Engine:
```bash
tail -f logs/audio_engine.log
```

---

## 🛠 Troubleshooting

### LEDs not turning on
```
Check 5V power supply (10A recommended)
Ensure GND is shared with Raspberry Pi
```

### Buttons not responding
```
BCM pin mapping:
MODE = 5
NEXT = 6
PREV = 13
PLAY = 19
```

### OLED not working
```bash
sudo i2cdetect -y 1
```

### Audio issues
```
Verify ALSA device in audio_engine.py
```

---

## 📜 License
MIT License

---

## 🙌 Acknowledgements

```
Raspberry Pi Foundation
rpi_ws281x Developers
FFmpeg Project
Adafruit SSD1306 Contributors
```

---

## 🚀 Want More Enhancements?

```
• LED visualizer presets
• BLE remote control
• Web dashboard UI
• Multi-strip animations
• GIF previews in README
```

Just ask!
