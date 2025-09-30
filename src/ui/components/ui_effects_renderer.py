import pygame
from typing import List
from src.models.carta import Carta
from src.models.slot_carta import SlotCarta
from config.settings import Colors


class UIEffectsRenderer:
    def __init__(self, tela: pygame.Surface, fonte_carta: pygame.font.Font):
        self.tela = tela
        self.fonte_carta = fonte_carta

    def desenhar_feedback_arraste(self, carta_arrastada: Carta, slots: List[SlotCarta], pos_mouse: tuple) -> None:
        if not carta_arrastada:
            return

        slot_valido = None
        slot_invalido = None

        for slot in slots:
            if slot.get_rect().collidepoint(pos_mouse):
                if slot.pode_aceitar_carta(carta_arrastada):
                    slot_valido = slot
                else:
                    slot_invalido = slot
                break

        if slot_valido:
            pygame.draw.rect(self.tela, Colors.LIGHT_GREEN,
                             slot_valido.get_rect(), 5)
        elif slot_invalido:
            pygame.draw.rect(self.tela, Colors.LIGHT_RED,
                             slot_invalido.get_rect(), 5)

    def desenhar_mensagem_temporaria(self, mensagem: str, x: int, y: int, cor: tuple = None) -> None:
        if cor is None:
            cor = Colors.BLACK

        texto_surface = self.fonte_carta.render(mensagem, True, cor)

        texto_width = texto_surface.get_width()
        texto_height = texto_surface.get_height()

        fundo_width = texto_width + 20
        fundo_height = texto_height + 10

        fundo_x = x - fundo_width // 2
        fundo_y = y - fundo_height // 2
        texto_x = x - texto_width // 2
        texto_y = y - texto_height // 2

        fundo = pygame.Surface((fundo_width, fundo_height))
        fundo.fill(Colors.WHITE)
        fundo.set_alpha(200)

        self.tela.blit(fundo, (fundo_x, fundo_y))
        self.tela.blit(texto_surface, (texto_x, texto_y))
