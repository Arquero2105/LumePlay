import pygame
import time

# 1. Uruchamiamy "silnik" dźwiękowy
pygame.mixer.init()

print("Wczytywanie utworu...")
# 2. Wczytujemy Twój plik (upewnij się, że nazywa się test.mp3)
pygame.mixer.music.load("test.mp3")

# 3. Puszczamy muzykę!
print("Odtwarzam muzykę! 🎵")
pygame.mixer.music.play()

# 4. Ponieważ Python wykonuje kod błyskawicznie, musimy go "uśpić", 
# inaczej program skończyłby się w ułamku sekundy, zanim usłyszałbyś dźwięk.
# Ten kod pozwala muzyce grać przez 10 sekund.
time.sleep(100)

print("Koniec testu!")