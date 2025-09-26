from src.models.carta import Carta
import pygame
from typing import List, Tuple, Optional


class SlotCarta:
    def __init__(self, x: int, y: int, cor: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.cor = cor
        self.largura = 80
        self.altura = 140
        self.cartas: List[Carta] = []
        self.cartas_jogador1: List[Carta] = []
        self.cartas_jogador2: List[Carta] = []
        self._destacado = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def pode_aceitar_carta(self, carta: Carta, jogador: int = None) -> bool:
        if carta.cor != self.cor:
            return False

        if self.esta_vazio():
            return True

        if jogador is None:
            ultima_carta = self.get_ultima_carta()
            if not ultima_carta:
                return True

            if carta.tipo_carta == 'numerada' and ultima_carta.tipo_carta == 'investimento':
                return True
            elif carta.tipo_carta == 'investimento' and ultima_carta.tipo_carta == 'numerada':
                return False
            elif carta.tipo_carta == 'investimento' and ultima_carta.tipo_carta == 'investimento':
                return True
            else:
                return carta.numero >= ultima_carta.numero

        if jogador == 1:
            cartas_jogador_atual = self.cartas_jogador1
        elif jogador == 2:
            cartas_jogador_atual = self.cartas_jogador2
        else:
            return False

        if not cartas_jogador_atual:
            return True

        ultima_carta_jogador = cartas_jogador_atual[-1]

        if carta.tipo_carta == 'investimento':
            for carta_existente in cartas_jogador_atual:
                if carta_existente.tipo_carta == 'numerada':
                    return False
            return True
        elif carta.tipo_carta == 'numerada':
            for carta_existente in reversed(cartas_jogador_atual):
                if carta_existente.tipo_carta == 'numerada':
                    return carta.numero >= carta_existente.numero
            return True

        return False

    def adicionar_carta(self, carta: Carta, jogador: int = None) -> bool:
        if self.pode_aceitar_carta(carta, jogador):
            self.cartas.append(carta)

            if jogador == 1:
                self.cartas_jogador1.append(carta)
            elif jogador == 2:
                self.cartas_jogador2.append(carta)

            carta.mover_para(
                self.x + (self.largura - carta.largura) // 2,
                self.y + (self.altura - carta.altura) // 2
            )
            carta.parar_arraste()
            return True
        return False

    def remover_carta(self, carta: Carta) -> bool:
        if carta in self.cartas:
            self.cartas.remove(carta)
            return True
        return False

    def get_ultima_carta(self) -> Optional[Carta]:
        return self.cartas[-1] if self.cartas else None

    def get_ultima_carta_jogador1(self) -> Optional[Carta]:
        return self.cartas_jogador1[-1] if self.cartas_jogador1 else None

    def get_ultima_carta_jogador2(self) -> Optional[Carta]:
        return self.cartas_jogador2[-1] if self.cartas_jogador2 else None

    def esta_vazio(self) -> bool:
        return len(self.cartas) == 0

    def get_quantidade_cartas(self) -> int:
        return len(self.cartas)

    def destacar(self, destacado: bool = True) -> None:
        self._destacado = destacado

    def calcular_pontuacao(self) -> int:
        if not self.cartas:
            return 0

        cartas_investimento = sum(
            1 for carta in self.cartas if carta.tipo_carta == 'investimento')

        soma_cartas = sum(
            carta.numero for carta in self.cartas if carta.tipo_carta == 'numerada')

        pontuacao = soma_cartas - 20

        for _ in range(cartas_investimento):
            pontuacao *= 2

        if len(self.cartas) >= 8:
            pontuacao += 20

        return pontuacao

    def desenhar(self, tela: pygame.Surface, fonte_pequena: pygame.font.Font) -> None:
        cor_fundo = self.cor
        if self._destacado:
            cor_fundo = tuple(min(255, c + 50) for c in self.cor)

        pygame.draw.rect(tela, cor_fundo, (self.x, self.y,
                         self.largura, self.altura))

        cor_borda = (0, 0, 0)
        espessura_borda = 4 if self._destacado else 2
        pygame.draw.rect(tela, cor_borda, (self.x, self.y,
                         self.largura, self.altura), espessura_borda)

        if self.esta_vazio():
            texto = fonte_pequena.render("Vazio", True, (255, 255, 255))
            texto_rect = texto.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura//2))
            tela.blit(texto, texto_rect)
        else:
            quantidade = self.get_quantidade_cartas()

            texto_qtd = fonte_pequena.render(f"{quantidade} carta{'s' if quantidade > 1 else ''}",
                                             True, (255, 255, 255))
            texto_rect = texto_qtd.get_rect(
                center=(self.x + self.largura//2, self.y + 20))
            tela.blit(texto_qtd, texto_rect)

            y_offset = 35

            ultima_carta_j1 = self.get_ultima_carta_jogador1()
            if ultima_carta_j1:
                if ultima_carta_j1.tipo_carta == 'investimento':
                    texto_j1 = fonte_pequena.render(
                        "J1: INV", True, (255, 255, 255))
                else:
                    texto_j1 = fonte_pequena.render(
                        f"J1: {ultima_carta_j1.numero}", True, (255, 255, 255))
            else:
                texto_j1 = fonte_pequena.render(
                    "J1: --", True, (255, 255, 255))

            texto_rect = texto_j1.get_rect(
                center=(self.x + self.largura//2, self.y + y_offset))
            tela.blit(texto_j1, texto_rect)

            y_offset += 15
            ultima_carta_j2 = self.get_ultima_carta_jogador2()
            if ultima_carta_j2:
                if ultima_carta_j2.tipo_carta == 'investimento':
                    texto_j2 = fonte_pequena.render(
                        "J2: INV", True, (255, 255, 255))
                else:
                    texto_j2 = fonte_pequena.render(
                        f"J2: {ultima_carta_j2.numero}", True, (255, 255, 255))
            else:
                texto_j2 = fonte_pequena.render(
                    "J2: --", True, (255, 255, 255))

            texto_rect = texto_j2.get_rect(
                center=(self.x + self.largura//2, self.y + y_offset))
            tela.blit(texto_j2, texto_rect)

            y_offset += 20

            if self.cartas_jogador1:
                cartas_j1_str = ",".join([
                    "I" if c.tipo_carta == 'investimento' else str(c.numero)
                    for c in self.cartas_jogador1
                ])
                texto_lista_j1 = fonte_pequena.render(
                    f"J1:[{cartas_j1_str}]", True, (200, 200, 200))
                texto_rect = texto_lista_j1.get_rect(
                    center=(self.x + self.largura//2, self.y + y_offset))
                tela.blit(texto_lista_j1, texto_rect)

            y_offset += 12

            if self.cartas_jogador2:
                cartas_j2_str = ",".join([
                    "I" if c.tipo_carta == 'investimento' else str(c.numero)
                    for c in self.cartas_jogador2
                ])
                texto_lista_j2 = fonte_pequena.render(
                    f"J2:[{cartas_j2_str}]", True, (200, 200, 200))
                texto_rect = texto_lista_j2.get_rect(
                    center=(self.x + self.largura//2, self.y + y_offset))
                tela.blit(texto_lista_j2, texto_rect)

            pontuacao = self.calcular_pontuacao()
            texto_pontos = fonte_pequena.render(
                f"Pts: {pontuacao}", True, (255, 255, 255))
            texto_rect = texto_pontos.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura - 15))
            tela.blit(texto_pontos, texto_rect)

    def __str__(self) -> str:
        return f"SlotCarta({self.cor}, {len(self.cartas)} cartas)"

    def __repr__(self) -> str:
        return self.__str__()
