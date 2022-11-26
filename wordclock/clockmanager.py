import datetime
import math
import time
import pytz

from rpi_ws281x import Color, PixelStrip, ws


def get_rgb_from_int(int):
    red = int & 255
    green = (int >> 8) & 255
    blue = (int >> 16) & 255
    white = (int >> 24) & 255
    return red, green, blue, white


class ClockManager:
    WORDS = {
        "oneminute": [0],
        "twominutes": [12],
        "threeminutes": [113],
        "fourminutes": [101],
        "es": [1, 2],
        "ist": [4, 5, 6],
        "fuenf1": [8, 9, 10, 11],
        "zehn1": [23, 22, 21, 20],
        "viertel": [28, 29, 30, 31, 32, 33, 34],
        "zwanzig": [19, 18, 17, 16, 15, 14, 13],
        "nach": [43, 42, 41, 40],
        "vor": [38, 37, 36],
        "halb": [46, 47, 48, 49],
        "ein": [63, 64, 65],
        "eins": [62, 63, 64, 65],
        "zwei": [64, 65, 66, 67],
        "drei": [69, 70, 71, 72],
        "vier": [79, 80, 81, 82],
        "fuenf2": [75, 76, 77, 78],
        "sechs": [107, 108, 109, 110, 111],
        "sieben": [57, 58, 59, 60, 61, 62],
        "acht": [91, 92, 93, 94],
        "neun": [83, 84, 85, 86],
        "zehn2": [95, 96, 97, 98],
        "elf": [87, 88, 89],
        "zwoelf": [51, 52, 53, 54, 55],
        "uhr": [102, 103, 104]
    }

    TIMES = {
        "01:00": ["ein", "uhr"],
        "01:05": ["fuenf1", "nach", "eins"],
        "01:10": ["zehn1", "nach", "eins"],
        "01:15": ["viertel", "nach", "eins"],
        "01:20": ["zwanzig", "nach", "eins"],
        "01:25": ["fuenf1", "vor", "halb", "zwei"],
        "01:30": ["halb", "zwei"],
        "01:35": ["fuenf1", "nach", "halb", "zwei"],
        "01:40": ["zwanzig", "vor", "zwei"],
        "01:45": ["viertel", "vor", "zwei"],
        "01:50": ["zehn1", "vor", "zwei"],
        "01:55": ["fuenf1", "vor", "zwei"],
        "02:00": ["zwei", "uhr"],
        "02:05": ["fuenf1", "nach", "zwei"],
        "02:10": ["zehn1", "nach", "zwei"],
        "02:15": ["viertel", "nach", "zwei"],
        "02:20": ["zwanzig", "nach", "zwei"],
        "02:25": ["fuenf1", "vor", "halb", "drei"],
        "02:30": ["halb", "drei"],
        "02:35": ["fuenf1", "nach", "halb", "drei"],
        "02:40": ["zwanzig", "vor", "drei"],
        "02:45": ["viertel", "vor", "drei"],
        "02:50": ["zehn1", "vor", "drei"],
        "02:55": ["fuenf1", "vor", "drei"],
        "03:00": ["drei", "uhr"],
        "03:05": ["fuenf1", "nach", "drei"],
        "03:10": ["zehn1", "nach", "drei"],
        "03:15": ["viertel", "nach", "drei"],
        "03:20": ["zwanzig", "nach", "drei"],
        "03:25": ["fuenf1", "vor", "halb", "vier"],
        "03:30": ["halb", "vier"],
        "03:35": ["fuenf1", "nach", "halb", "vier"],
        "03:40": ["zwanzig", "vor", "vier"],
        "03:45": ["viertel", "vor", "vier"],
        "03:50": ["zehn1", "vor", "vier"],
        "03:55": ["fuenf1", "vor", "vier"],
        "04:00": ["vier", "uhr"],
        "04:05": ["fuenf1", "nach", "vier"],
        "04:10": ["zehn1", "nach", "vier"],
        "04:15": ["viertel", "nach", "vier"],
        "04:20": ["zwanzig", "nach", "vier"],
        "04:25": ["fuenf1", "vor", "halb", "fuenf2"],
        "04:30": ["halb", "fuenf2"],
        "04:35": ["fuenf1", "nach", "halb", "fuenf2"],
        "04:40": ["zwanzig", "vor", "fuenf2"],
        "04:45": ["viertel", "vor", "fuenf2"],
        "04:50": ["zehn1", "vor", "fuenf2"],
        "04:55": ["fuenf1", "vor", "fuenf2"],
        "05:00": ["fuenf2", "uhr"],
        "05:05": ["fuenf1", "nach", "fuenf2"],
        "05:10": ["zehn1", "nach", "fuenf2"],
        "05:15": ["viertel", "nach", "fuenf2"],
        "05:20": ["zwanzig", "nach", "fuenf2"],
        "05:25": ["fuenf1", "vor", "halb", "sechs"],
        "05:30": ["halb", "sechs"],
        "05:35": ["fuenf1", "nach", "halb", "sechs"],
        "05:40": ["zwanzig", "vor", "sechs"],
        "05:45": ["viertel", "vor", "sechs"],
        "05:50": ["zehn1", "vor", "sechs"],
        "05:55": ["fuenf1", "vor", "sechs"],
        "06:00": ["sechs", "uhr"],
        "06:05": ["fuenf1", "nach", "sechs"],
        "06:10": ["zehn1", "nach", "sechs"],
        "06:15": ["viertel", "nach", "sechs"],
        "06:20": ["zwanzig", "nach", "sechs"],
        "06:25": ["fuenf1", "vor", "halb", "sieben"],
        "06:30": ["halb", "sieben"],
        "06:35": ["fuenf1", "nach", "halb", "sieben"],
        "06:40": ["zwanzig", "vor", "sieben"],
        "06:45": ["viertel", "vor", "sieben"],
        "06:50": ["zehn1", "vor", "sieben"],
        "06:55": ["fuenf1", "vor", "sieben"],
        "07:00": ["sieben", "uhr"],
        "07:05": ["fuenf1", "nach", "sieben"],
        "07:10": ["zehn1", "nach", "sieben"],
        "07:15": ["viertel", "nach", "sieben"],
        "07:20": ["zwanzig", "nach", "sieben"],
        "07:25": ["fuenf1", "vor", "halb", "acht"],
        "07:30": ["halb", "acht"],
        "07:35": ["fuenf1", "nach", "halb", "acht"],
        "07:40": ["zwanzig", "vor", "acht"],
        "07:45": ["viertel", "vor", "acht"],
        "07:50": ["zehn1", "vor", "acht"],
        "07:55": ["fuenf1", "vor", "acht"],
        "08:00": ["acht", "uhr"],
        "08:05": ["fuenf1", "nach", "acht"],
        "08:10": ["zehn1", "nach", "acht"],
        "08:15": ["viertel", "nach", "acht"],
        "08:20": ["zwanzig", "nach", "acht"],
        "08:25": ["fuenf1", "vor", "halb", "neun"],
        "08:30": ["halb", "neun"],
        "08:35": ["fuenf1", "nach", "halb", "neun"],
        "08:40": ["zwanzig", "vor", "neun"],
        "08:45": ["viertel", "vor", "neun"],
        "08:50": ["zehn1", "vor", "neun"],
        "08:55": ["fuenf1", "vor", "neun"],
        "09:00": ["neun", "uhr"],
        "09:05": ["fuenf1", "nach", "neun"],
        "09:10": ["zehn1", "nach", "neun"],
        "09:15": ["viertel", "nach", "neun"],
        "09:20": ["zwanzig", "nach", "neun"],
        "09:25": ["fuenf1", "vor", "halb", "zehn2"],
        "09:30": ["halb", "zehn2"],
        "09:35": ["fuenf1", "nach", "halb", "zehn2"],
        "09:40": ["zwanzig", "vor", "zehn2"],
        "09:45": ["viertel", "vor", "zehn2"],
        "09:50": ["zehn1", "vor", "zehn2"],
        "09:55": ["fuenf1", "vor", "zehn2"],
        "10:00": ["zehn2", "uhr"],
        "10:05": ["fuenf1", "nach", "zehn2"],
        "10:10": ["zehn1", "nach", "zehn2"],
        "10:15": ["viertel", "nach", "zehn2"],
        "10:20": ["zwanzig", "nach", "zehn2"],
        "10:25": ["fuenf1", "vor", "halb", "elf"],
        "10:30": ["halb", "elf"],
        "10:35": ["fuenf1", "nach", "halb", "elf"],
        "10:40": ["zwanzig", "vor", "elf"],
        "10:45": ["viertel", "vor", "elf"],
        "10:50": ["zehn1", "vor", "elf"],
        "10:55": ["fuenf1", "vor", "elf"],
        "11:00": ["elf", "uhr"],
        "11:05": ["fuenf1", "nach", "elf"],
        "11:10": ["zehn1", "nach", "elf"],
        "11:15": ["viertel", "nach", "elf"],
        "11:20": ["zwanzig", "nach", "elf"],
        "11:25": ["fuenf1", "vor", "halb", "zwoelf"],
        "11:30": ["halb", "zwoelf"],
        "11:35": ["fuenf1", "nach", "halb", "zwoelf"],
        "11:40": ["zwanzig", "vor", "zwoelf"],
        "11:45": ["viertel", "vor", "zwoelf"],
        "11:50": ["zehn1", "vor", "zwoelf"],
        "11:55": ["fuenf1", "vor", "zwoelf"],
        "12:00": ["zwoelf", "uhr"],
        "12:05": ["fuenf1", "nach", "zwoelf"],
        "12:10": ["zehn1", "nach", "zwoelf"],
        "12:15": ["viertel", "nach", "zwoelf"],
        "12:20": ["zwanzig", "nach", "zwoelf"],
        "12:25": ["fuenf1", "vor", "halb", "eins"],
        "12:30": ["halb", "eins"],
        "12:35": ["fuenf1", "nach", "halb", "eins"],
        "12:40": ["zwanzig", "vor", "eins"],
        "12:45": ["viertel", "vor", "eins"],
        "12:50": ["zehn1", "vor", "eins"],
        "12:55": ["fuenf1", "vor", "eins"],
    }

    def __init__(self):
        self.strip = PixelStrip(114, 18, 800000, 10, False, 255, 0, ws.SK6812_STRIP_RGBW)
        self.strip.begin()
        self.set_all(Color(0, 0, 0, 0))

    def set_all(self, color):
        for i in range(0, 114):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def set_all_without_show(self, color):
        for i in range(0, 114):
            self.strip.setPixelColor(i, color)

    def set_word(self, word_key, color):
        word = self.WORDS[word_key]
        for i in word:
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def set_words(self, word_keys, color):
        for word_key in word_keys:
            word = self.WORDS[word_key]
            for i in word:
                self.strip.setPixelColor(i, color)
        self.strip.show()

    def clear_difference(self, old: list, new: list):
        for word in new:
            old.remove(word)
        self.set_words(old, Color(0, 0, 0, 0))

    def tick(self):
        while True:
            now = datetime.datetime.now(pytz.timezone('Europe/Zurich'))
            hours = now.strftime("%I")
            minutes = now.minute

            partminutes = minutes % 5
            fullminutes = math.floor(minutes / 5) * 5
            fullminutes = f'{fullminutes:02d}'

            timestring = hours + ":" + fullminutes

            col = Color(0, 0, 0, 10)

            if partminutes == 1:
                minutepoints = ["oneminute"]
            elif partminutes == 2:
                minutepoints = ["oneminute", "twominutes"]
            elif partminutes == 3:
                minutepoints = ["oneminute", "twominutes", "threeminutes"]
            elif partminutes == 4:
                minutepoints = ["oneminute", "twominutes", "threeminutes", "fourminutes"]
            else:
                minutepoints = []

            words = []
            words.extend(self.TIMES[timestring])
            words.extend(["es", "ist"])

            print(words)

            words.extend(minutepoints)
            self.set_all_without_show(Color(0, 0, 0, 0))
            self.set_words(words, col)

            time.sleep(1)
