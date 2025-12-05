#!/usr/bin/env python3
# Supervisor v4
import subprocess, time, os, sys

LED_CMD  = ["/home/sijeo/christmas_lights/bin/python3", "src/led_engine.py"]
AUDIO_CMD= ["/home/sijeo/christmas_lights/bin/python3", "src/audio_engine.py"]
SOCK="/tmp/musical_lights.sock"
LOG_DIR="logs"
os.makedirs(LOG_DIR,exist_ok=True)

def start(cmd,name):
    lf=open(os.path.join(LOG_DIR,f"{name}.log"),"a")
    p=subprocess.Popen(cmd,stdout=lf,stderr=lf)
    return p,lf

def wait_sock(timeout=10):
    for _ in range(timeout*10):
        if os.path.exists(SOCK): return True
        time.sleep(0.1)
    return False

def main():
    led,lf1=start(LED_CMD,"led_engine")
    if not wait_sock():
        led.terminate(); sys.exit(1)
    audio,lf2=start(AUDIO_CMD,"audio_engine")
    try:
        while True:
            if led.poll() is not None:
                led,lf1=start(LED_CMD,"led_engine"); wait_sock()
                audio.terminate()
                audio,lf2=start(AUDIO_CMD,"audio_engine")
            if audio.poll() is not None:
                audio,lf2=start(AUDIO_CMD,"audio_engine")
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        try: led.terminate()
        except: pass
        try: audio.terminate()
        except: pass

if __name__=="__main__":
    main()
