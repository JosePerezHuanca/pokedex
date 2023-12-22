import pygame

class SoundManager:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.sound_select = pygame.mixer.Sound("ui7.wav")  # Sonido al seleccionar un elemento
        self.sound_open = pygame.mixer.Sound("ui6.wav")  # Sonido al abrir el programa
        self.sound_select.set_volume(0.5)
        self.sound_open.set_volume(0.5)

    def play_select_sound(self):
        try:
            self.sound_select.play()
        except pygame.error as e:
            print(f"Error al reproducir el sonido al seleccionar un elemento: {e}")

    def play_open_sound(self):
        try:
            self.sound_open.play()
        except pygame.error as e:
            print(f"Error al reproducir el sonido al abrir el programa: {e}")
