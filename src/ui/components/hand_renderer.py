import pygame
from typing import List
from src.models.carta import Carta
from config.settings import Colors, LayoutConfig, WINDOW_WIDTH


class HandRenderer:
    def __init__(self, tela: pygame.Surface, fonte_carta: pygame.font.Font):
        self.tela = tela
        self.fonte_carta = fonte_carta

    def desenhar_area_mao_jogador1(self, cartas: List[Carta], jogador_ativo: bool) -> None:
        area_y = LayoutConfig.PLAYER1_HAND_Y
        area_largura = WINDOW_WIDTH - (LayoutConfig.HAND_AREA_MARGIN * 2)
        area_altura = LayoutConfig.HAND_AREA_HEIGHT

        cor_fundo = Colors.LIGHT_GREEN if jogador_ativo else Colors.DARK_GRAY

        pygame.draw.rect(self.tela, cor_fundo,
                         (LayoutConfig.HAND_AREA_MARGIN, area_y, area_largura, area_altura))
        pygame.draw.rect(self.tela, Colors.BLACK,
                         (LayoutConfig.HAND_AREA_MARGIN,
                          area_y, area_largura, area_altura),
                         3 if jogador_ativo else 2)

        titulo = "JOGADOR 1 (SUA VEZ)" if jogador_ativo else "JOGADOR 1"
        titulo_mao = self.fonte_carta.render(titulo, True,
                                             Colors.BLACK if jogador_ativo else Colors.WHITE)
        self.tela.blit(titulo_mao, (LayoutConfig.HAND_AREA_MARGIN + 20,
                                    area_y + LayoutConfig.HAND_TITLE_OFFSET_Y))

        for carta in cartas:
            carta.desenhar(self.tela, self.fonte_carta)

    def desenhar_area_mao_jogador2(self, cartas: List[Carta], jogador_ativo: bool) -> None:
        area_y = LayoutConfig.PLAYER2_HAND_Y
        area_largura = WINDOW_WIDTH - (LayoutConfig.HAND_AREA_MARGIN * 2)
        area_altura = LayoutConfig.HAND_AREA_HEIGHT

        cor_fundo = Colors.LIGHT_GREEN if jogador_ativo else Colors.DARK_GRAY

        pygame.draw.rect(self.tela, cor_fundo,
                         (LayoutConfig.HAND_AREA_MARGIN, area_y, area_largura, area_altura))
        pygame.draw.rect(self.tela, Colors.BLACK,
                         (LayoutConfig.HAND_AREA_MARGIN,
                          area_y, area_largura, area_altura),
                         3 if jogador_ativo else 2)

        titulo = "JOGADOR 2 (SUA VEZ)" if jogador_ativo else "JOGADOR 2"
        titulo_mao = self.fonte_carta.render(titulo, True,
                                             Colors.BLACK if jogador_ativo else Colors.WHITE)
        self.tela.blit(titulo_mao, (LayoutConfig.HAND_AREA_MARGIN + 20,
                                    area_y + LayoutConfig.HAND_TITLE_OFFSET_Y))

        for carta in cartas:
            carta.desenhar(self.tela, self.fonte_carta)
