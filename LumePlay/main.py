import customtkinter as ctk
import pygame
import os
import random
from mutagen.easyid3 import EasyID3
import textwrap
from PIL import Image
from mutagen.id3 import ID3, APIC
import io

pygame.mixer.init()
# 1. Konfiguracja wyglądu 
ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("dark-blue")  

sciezka_ikon = "Ikony"
if os.path.exists(sciezka_ikon):
    try:
        ikona_shuffle = ctk.CTkImage(light_image=Image.open(os.path.join(sciezka_ikon, "shuffle.png")), size=(24, 24))
        ikona_repeat = ctk.CTkImage(light_image=Image.open(os.path.join(sciezka_ikon, "repeat.png")), size=(24, 24))
        ikona_prev = ctk.CTkImage(light_image=Image.open(os.path.join(sciezka_ikon, "prev.png")), size=(24, 24))
        ikona_play = ctk.CTkImage(light_image=Image.open(os.path.join(sciezka_ikon, "play.png")), size=(24, 24))
        ikona_next = ctk.CTkImage(light_image=Image.open(os.path.join(sciezka_ikon, "next.png")), size=(24, 24))
        print("Ikony wczytane pomyślnie.")
    except Exception as e:
        print(f"Błąd podczas wczytywania ikon: {e}")
        ikona_shuffle = ikona_repeat = ikona_prev = ikona_play = ikona_next = None
else:
    print(f"Nie znaleziono folderu: {sciezka_ikon}. Przyciski zostaną puste.")
    ikona_shuffle = ikona_repeat = ikona_prev = ikona_play = ikona_next = None


sciezka_muzyki = "Muzyka"
lista_piosenek = []
czy_zapauzowane = False
aktualny_indeks = 0
dlugosc_utworu = 0
przyciski_piosenek = []
offset_czasu = 0
pozwol_na_autoplay = False
tryb_repeat = False
tryb_shuffle = False



print("Szukam muzyki w folderze...")
if os.path.exists(sciezka_muzyki):
    for plik in os.listdir(sciezka_muzyki):
        if plik.endswith(".mp3"):
            lista_piosenek.append(plik)            
print("Znalezione piosenki:", lista_piosenek)

def formatuj_czas(sekundy):
    minuty = int(sekundy // 60)
    sekundy_reszta = int(sekundy % 60)
    return f"{minuty}:{sekundy_reszta:02d}"

def pobierz_info_o_piosence(sciezka):
    nazwa_pliku = os.path.basename(sciezka).replace(".mp3", "")
    try:
        audio = EasyID3(sciezka)
        tytul = audio.get("title", [nazwa_pliku])[0]
        artysta = audio.get("artist", ["Nieznany Artysta"])[0]
    except Exception:
        tytul = nazwa_pliku
        artysta = "Nieznany Artysta"

    if " - " in tytul and artysta == "Nieznany Artysta":
        artysta, tytul = tytul.split(" - ", 1)
    elif " - " in nazwa_pliku and tytul == nazwa_pliku:
        artysta, tytul = nazwa_pliku.split(" - ", 1)

    if tytul.startswith(artysta + " - "):
        tytul = tytul.replace(artysta + " - ", "", 1)
    
    tytul = tytul.strip()
    artysta = artysta.strip()

    dane_obrazka = None
    try:
        tagi = ID3(sciezka)
        for tag in tagi.values():
            if isinstance(tag, APIC):
                dane_obrazka = tag.data 
                break
    except Exception:
        dane_obrazka = None

    return f"{artysta}\n{tytul}", tytul, dane_obrazka

# 2. Tworzenie głównego okna aplikacji
app = ctk.CTk()
app.title("LumePlay")
app.geometry("1300x700") # Rozmiar okna 
# 3. Konfiguracja siatki (Grid)
app.grid_rowconfigure(1, weight=1)     
app.grid_columnconfigure(1, weight=1)  


def play_music(nazwa_pliku):
    global czy_zapauzowane, aktualny_indeks, dlugosc_utworu, offset_czasu, pozwol_na_autoplay
    aktualny_indeks = nazwa_pliku
    czy_zapauzowane = False
    offset_czasu = 0
    pozwol_na_autoplay = False

    print("Przycisk kliknięty! Wczytuję muzykę...")
    nazwa_pliku = lista_piosenek[nazwa_pliku]
    pelna_sciezka = os.path.join(sciezka_muzyki, nazwa_pliku)
    dlugosc_utworu = pygame.mixer.Sound(pelna_sciezka).get_length()
    print(f"Odtwarzam: {pelna_sciezka}")

    pygame.mixer.music.load(pelna_sciezka)
    pygame.mixer.music.play()
    k_czas.configure(text=formatuj_czas(dlugosc_utworu))
    pelne_info, _, obrazek_binarny = pobierz_info_o_piosence(pelna_sciezka)
    info.configure(text=pelne_info)
    if obrazek_binarny:
        try:
            obraz_pil = Image.open(io.BytesIO(obrazek_binarny))
            obraz_ctk = ctk.CTkImage(light_image=obraz_pil, size=(50, 50))
            okladka.configure(image=obraz_ctk)
        except Exception:
            okladka.configure(image=None)
    else:
        okladka.configure(image=None)



def toggle_play():
    global czy_zapauzowane
    
    if czy_zapauzowane == False:
        pygame.mixer.music.pause()
        czy_zapauzowane = True
        print("Pauza ⏸")
    else:
        pygame.mixer.music.unpause()
        czy_zapauzowane = False
        print("Wznowiono ▶️")

def nastepny_utwor():
    if tryb_shuffle:
        nowy_indeks = random.randint(0, len(lista_piosenek) - 1)
        print(f"Shuffle aktywne! Wylosowano utwór nr {nowy_indeks}")
        play_music(nowy_indeks)
        return
    
    nowy_indeks = aktualny_indeks + 1
    if nowy_indeks < len(lista_piosenek): 
        play_music(nowy_indeks)
    else:
        if tryb_repeat:
            print("Koniec listy, ale Repeat jest włączony! Wracam do pierwszej piosenki.")
            play_music(0) 
        else:
            print("Koniec listy i brak Repeat. Odtwarzacz zatrzymany.")

        
def poprzedni_utwor():
    nowy_indeks = aktualny_indeks - 1
    if nowy_indeks >= 0:
        play_music(nowy_indeks)

def aktualizuj_czas():
    global dlugosc_utworu, offset_czasu, pozwol_na_autoplay

    if pygame.mixer.music.get_busy() and not czy_zapauzowane:
        obecny_czas = offset_czasu + (pygame.mixer.music.get_pos() / 1000) 
        p_czas.configure(text=formatuj_czas(obecny_czas))
        
        pozwol_na_autoplay = True
            
        if dlugosc_utworu > 0:
            pasek.set(obecny_czas / dlugosc_utworu)

    elif not pygame.mixer.music.get_busy() and not czy_zapauzowane and pozwol_na_autoplay:
                pozwol_na_autoplay = False # Znów zabezpieczamy!
                print("Naturalny koniec piosenki. Odpalam następną!")
                nastepny_utwor()
    app.after(500, aktualizuj_czas)

def filtruj_piosenki(event):
    wpisany_tekst = pasek_szukania.get().lower() 
    aktualna_kolumna = 0
    print(f"Szukam: {wpisany_tekst}")
    
    for i, piosenka in enumerate(lista_piosenek):
        if wpisany_tekst in piosenka.lower():
            przyciski_piosenek[i].grid(row=1, column=aktualna_kolumna, padx=10, pady=10)
            aktualna_kolumna += 1
        else:
            przyciski_piosenek[i].grid_remove()

def zmien_glosnosc(wartosc):
    pygame.mixer.music.set_volume(wartosc)

def przewin_utwor(event):
    global offset_czasu, pozwol_na_autoplay
    
    if dlugosc_utworu > 0:
        wartosc = pasek.get()
        sekundy = wartosc * dlugosc_utworu
        
        offset_czasu = sekundy
        pozwol_na_autoplay = True
        pygame.mixer.music.play(start=sekundy)

def toggle_repeat():
    global tryb_repeat
    tryb_repeat = not tryb_repeat
    
    if tryb_repeat:
        btn_repeat.configure(fg_color="#14154E")
    else:
        btn_repeat.configure(fg_color="transparent")

def toggle_shuffle():
    global tryb_shuffle
    tryb_shuffle = not tryb_shuffle
    
    if tryb_shuffle:
        btn_shuffle.configure(fg_color="#14154E")
    else:
        btn_shuffle.configure(fg_color="transparent")


# 4. GÓRNY PASEK (Odtwarzacz)
top_bar = ctk.CTkFrame(app, height=80, corner_radius=0, fg_color="#1a1a24")
top_bar.grid(row=0, column=0, columnspan=2, sticky="ew") # sticky="ew" rozciąga go od lewej do prawej (East-West)

btn_shuffle = ctk.CTkButton(top_bar, text="", image=ikona_shuffle, fg_color="transparent", hover_color="#333344", command=toggle_shuffle, width=40)
btn_shuffle.grid(row=0, column=0, padx=10, pady=10)

btn_repeat = ctk.CTkButton(top_bar, text="", image=ikona_repeat, fg_color="transparent", hover_color="#333344", command=toggle_repeat, width=40)
btn_repeat.grid(row=1, column=0, padx=10, pady=10)

btn_previous = ctk.CTkButton(top_bar, text="", image=ikona_prev, fg_color="transparent", hover_color="#333344",command=poprzedni_utwor, width=40)
btn_previous.grid(row=0, column=1, padx=10, pady=10,rowspan=2)

btn_play = ctk.CTkButton(top_bar, text="", image=ikona_play, fg_color="transparent", hover_color="#333344", command=toggle_play, width=40)
btn_play.grid(row=0, column=2, padx=10, pady=10, rowspan=2)

btn_next = ctk.CTkButton(top_bar, text="", image=ikona_next, fg_color="transparent", hover_color="#333344", command=nastepny_utwor, width=40)
btn_next.grid(row=0, column=3, padx=10, pady=10,rowspan=2)

okladka = ctk.CTkLabel(top_bar, text="", fg_color="#333344", width=50, height=50)
okladka.grid(row=0, column=4, padx=20,rowspan=2) 

info = ctk.CTkLabel(top_bar, text="Imię Artysty\nTytuł Piosenki", justify="left")
info.grid(row=0, column=5, padx=10,columnspan=3,sticky="w") 

p_czas = ctk.CTkLabel(top_bar, text="0:00")
p_czas.grid(row=1, column=6, padx=10)

pasek = ctk.CTkSlider(top_bar, width=200, from_=0.0, to=1.0)
pasek.set(0.0)
pasek.grid(row=1, column=7, padx=10)
pasek.bind("<ButtonRelease-1>", przewin_utwor)

k_czas = ctk.CTkLabel(top_bar, text="3:45")
k_czas.grid(row=1 , column=8, padx=10)

pasek_szukania = ctk.CTkEntry(top_bar, placeholder_text="Szukaj utworu...", width=170)
pasek_szukania.grid(row=0, column=9, padx=8, rowspan=2,)
pasek_szukania.bind("<KeyRelease>", filtruj_piosenki)

suwak_glosnosci = ctk.CTkSlider(top_bar, from_=0.0, to=1.0, width=100, command=zmien_glosnosc)
suwak_glosnosci.grid(row=0, column=10, padx=10, rowspan=2)
suwak_glosnosci.set(0.5)
pygame.mixer.music.set_volume(0.5)


# 5. LEWY PASEK (Nawigacja)
sidebar = ctk.CTkFrame(app, width=150, corner_radius=0, fg_color="#09090e")
sidebar.grid(row=1, column=0, sticky="ns")
btn_account = ctk.CTkButton(sidebar, text="Konto", fg_color="transparent", hover_color="#333333" )
btn_account.grid(row=0, column=0, pady=10)
btn_library = ctk.CTkButton(sidebar, text="Biblioteka", fg_color="transparent", hover_color="#333333" )
btn_library.grid(row=1, column=0, pady=10) # pady to odstęp (margines) z góry i z dołu
btn_settings = ctk.CTkButton(sidebar, text="Ustawienia")
btn_settings.grid(row=2, column=0, pady=10)

# 6. GŁÓWNY WIDOK (Lista utworów / Biblioteka)
main_view = ctk.CTkFrame(app, corner_radius=0, fg_color="#12121c") # Ciemny granat
main_view.grid(row=1, column=1, sticky="nsew") # sticky="nsew" rozciąga go we wszystkie strony
naglowek = ctk.CTkLabel(main_view, text="Music", font=("Arial", 20, "bold"))
naglowek.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
# Używamy enumerate, żeby mieć i numerek kolumny (i) i nazwę pliku (piosenka)
for i, piosenka in enumerate(lista_piosenek): 
    pelna_sciezka_do_badania = os.path.join(sciezka_muzyki, piosenka)
    _, tytul_na_kafelek, _ = pobierz_info_o_piosence(pelna_sciezka_do_badania)

    zawiniety_tekst = textwrap.fill(tytul_na_kafelek, width=18)
    
    kafelek = ctk.CTkButton(
        main_view, 
        text=zawiniety_tekst, 
        width=160, 
        height=160,
       command=lambda idx=i: play_music(idx) 
    )
    kafelek.grid(row=1, column=i, padx=10, pady=10)
    przyciski_piosenek.append(kafelek)

naglowek2 = ctk.CTkLabel(main_view, text="Artist", font=("Arial", 20, "bold"))
naglowek2.grid(row=3, column=0,columnspan=2, padx=20, pady=20, sticky="w")
for i in range(8): 
    kafelek2 = ctk.CTkButton(main_view, text=f"Artysta {i+1}", width=160, height=160)
    kafelek2.grid(row=4, column=i, padx=10, pady=10)


# 7. Pętla główna
aktualizuj_czas()
app.mainloop()

