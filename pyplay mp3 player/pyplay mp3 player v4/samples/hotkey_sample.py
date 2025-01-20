import pynput

def run():
    print('f7') # your code

def press(key):
    if key == pynput.keyboard.Key.f7:
        run()

pynput.keyboard.Listener(on_press=press).run()