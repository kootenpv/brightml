import numpy as np

with open("/sys/class/backlight/gmux_backlight/max_brightness") as f:
    MAX_BRIGHTNESS = int(f.read())


def write_brightness(brightness, clip_min=1, clip_max=MAX_BRIGHTNESS):
    brightness = np.clip(int(brightness), clip_min, clip_max)
    with open("/sys/class/backlight/gmux_backlight/brightness", "w") as f:
        f.write(str(brightness))
