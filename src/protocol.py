import socket

SOCKET_PATH = "/tmp/musical_lights.sock"

MODE_MUSIC = 0
MODE_AMBIENT = 1
MODE_OFF = 2
MODE_TREE = 3
MODE_CHASE = 4
MODE_SPARKLE = 5

MODE_NAMES = {
    MODE_MUSIC: "Music",
    MODE_AMBIENT: "Ambient",
    MODE_OFF: "Off",
    MODE_TREE: "Tree",
    MODE_CHASE: "Chase",
    MODE_SPARKLE: "Sparkle",
}

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]


def create_client_socket():
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        s.connect(SOCKET_PATH)
        return s
    except (FileNotFoundError, ConnectionRefusedError):
        return None
