from src.models.carta import Carta
import pygame
from typing import List, Tuple, Optional


class SlotCarta:
    def __init__(self, x: int, y: int, cor: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.cor = cor
        self.largura = 80
        self.altura = 120
        self.cartas: List[Carta] = []
        self._destacado = False

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def pode_aceitar_carta(self, carta: Carta) -> bool:
        if carta.cor != self.cor:
            return False

        if self.esta_vazio():
            return True

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

    def adicionar_carta(self, carta: Carta) -> bool:
        if self.pode_aceitar_carta(carta):
            self.cartas.append(carta)
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
        # Cor do fundo (mais escura se destacado)
        cor_fundo = self.cor
        if self._destacado:
            # Tornar a cor mais brilhante
            cor_fundo = tuple(min(255, c + 50) for c in self.cor)

        # Desenhar fundo do slot
        pygame.draw.rect(tela, cor_fundo, (self.x, self.y,
                         self.largura, self.altura))

        # Desenhar borda
        cor_borda = (0, 0, 0)
        espessura_borda = 4 if self._destacado else 2
        pygame.draw.rect(tela, cor_borda, (self.x, self.y,
                         self.largura, self.altura), espessura_borda)

        # Desenhar conteúdo baseado no estado
        if self.esta_vazio():
            texto = fonte_pequena.render("Vazio", True, (255, 255, 255))
            texto_rect = texto.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura//2))
            tela.blit(texto, texto_rect)
        else:
            # Slot com cartas - mostrar informações
            quantidade = self.get_quantidade_cartas()

            # Texto da quantidade
            texto_qtd = fonte_pequena.render(f"{quantidade} carta{'s' if quantidade > 1 else ''}",
                                             True, (255, 255, 255))
            texto_rect = texto_qtd.get_rect(
                center=(self.x + self.largura//2, self.y + 20))
            tela.blit(texto_qtd, texto_rect)

            # Mostrar a última carta (se houver)
            ultima_carta = self.get_ultima_carta()
            if ultima_carta:
                if ultima_carta.tipo_carta == 'investimento':
                    texto_numero = fonte_pequena.render(
                        "Topo: INV", True, (255, 255, 255))
                else:
                    texto_numero = fonte_pequena.render(f"Topo: {ultima_carta.numero}",
                                                        True, (255, 255, 255))
                texto_rect = texto_numero.get_rect(
                    center=(self.x + self.largura//2, self.y + 45))
                tela.blit(texto_numero, texto_rect)

            # Pontuação
            pontuacao = self.calcular_pontuacao()
            texto_pontos = fonte_pequena.render(
                f"Pts: {pontuacao}", True, (255, 255, 255))
            texto_rect = texto_pontos.get_rect(
                center=(self.x + self.largura//2, self.y + self.altura - 20))
            tela.blit(texto_pontos, texto_rect)

    def __str__(self) -> str:
        return f"SlotCarta({self.cor}, {len(self.cartas)} cartas)"

    def __repr__(self) -> str:
        return self.__str__()
