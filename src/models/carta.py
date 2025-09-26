import pygame
from typing import Tuple


class Carta:
    def __init__(self, numero: int, cor: Tuple[int, int, int], x: int, y: int, tipo_carta: str = 'numerada'):
        self.numero = numero
        self.cor = cor
        self.x = x
        self.y = y
        self.tipo_carta = tipo_carta
        self.largura = 60
        self.altura = 90
        self.sendo_arrastada = False
        self.offset_x = 0
        self.offset_y = 0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def contem_ponto(self, pos: Tuple[int, int]) -> bool:
        return self.get_rect().collidepoint(pos)

    def iniciar_arraste(self, pos_mouse: Tuple[int, int]) -> None:
        self.sendo_arrastada = True
        self.offset_x = pos_mouse[0] - self.x
        self.offset_y = pos_mouse[1] - self.y

    def parar_arraste(self) -> None:
        self.sendo_arrastada = False
        self.offset_x = 0
        self.offset_y = 0

    def atualizar_posicao(self, pos_mouse: Tuple[int, int]) -> None:
        if self.sendo_arrastada:
            self.x = pos_mouse[0] - self.offset_x
            self.y = pos_mouse[1] - self.offset_y

    def mover_para(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def desenhar(self, tela: pygame.Surface, fonte_pequena: pygame.font.Font,
                 slots_jogador1=None, slots_jogador2=None) -> None:
        pygame.draw.rect(tela, self.cor, (self.x, self.y,
                         self.largura, self.altura))

        cor_borda = (0, 0, 0)
        espessura_borda = 3 if self.sendo_arrastada else 2
        pygame.draw.rect(tela, cor_borda, (self.x, self.y,
                         self.largura, self.altura), espessura_borda)

        if self.tipo_carta == 'investimento':
            cor_texto = (255, 255, 255)
            texto = fonte_pequena.render("$", True, cor_texto)
            texto_rect = texto.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura//2))
            tela.blit(texto, texto_rect)

            fonte_pequena = pygame.font.Font(None, 16)
            inv_texto = fonte_pequena.render("INV", True, cor_texto)
            inv_rect = inv_texto.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura - 15))
            tela.blit(inv_texto, inv_rect)
        else:
            cor_texto = (255, 255, 255)
            texto = fonte_pequena.render(str(self.numero), True, cor_texto)
            texto_rect = texto.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura//2))
            tela.blit(texto, texto_rect)

        if self.sendo_arrastada:
            sombra_offset = 3
            pygame.draw.rect(tela, (100, 100, 100),
                             (self.x + sombra_offset, self.y + sombra_offset,
                              self.largura, self.altura))

    def __str__(self) -> str:
        if self.tipo_carta == 'investimento':
            return f"Carta(Investimento, {self.cor})"
        else:
            return f"Carta({self.numero}, {self.cor})"

    def __repr__(self) -> str:
        return self.__str__()
