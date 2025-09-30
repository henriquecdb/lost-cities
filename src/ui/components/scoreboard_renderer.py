import pygame
from typing import List
from src.models.slot_carta import SlotCarta
from config.settings import Colors


class ScoreboardRenderer:
    def __init__(self, tela: pygame.Surface, fonte_carta: pygame.font.Font, fonte_pequena: pygame.font.Font):
        self.tela = tela
        self.fonte_carta = fonte_carta
        self.fonte_pequena = fonte_pequena

    def desenhar_estatisticas(self, slots_jogador1: List[SlotCarta], slots_jogador2: List[SlotCarta]) -> None:
        self._desenhar_placar_jogador1(slots_jogador1)
        self._desenhar_placar_jogador2(slots_jogador2)

    def _desenhar_placar_jogador1(self, slots: List[SlotCarta]) -> None:
        placar_x = 20
        placar_y = 350
        placar_width = 150
        placar_height = 200

        pygame.draw.rect(self.tela, Colors.WHITE, (placar_x,
                         placar_y, placar_width, placar_height))
        pygame.draw.rect(self.tela, Colors.BLACK, (placar_x,
                         placar_y, placar_width, placar_height), 2)

        titulo = self.fonte_carta.render("JOGADOR 1", True, Colors.BLACK)
        titulo_rect = titulo.get_rect(
            center=(placar_x + placar_width//2, placar_y + 15))
        self.tela.blit(titulo, titulo_rect)

        pygame.draw.line(self.tela, Colors.BLACK,
                         (placar_x + 5, placar_y + 30),
                         (placar_x + placar_width - 5, placar_y + 30), 2)

        self._desenhar_pontuacao_por_cor(
            slots, placar_x, placar_y, placar_width)

    def _desenhar_placar_jogador2(self, slots: List[SlotCarta]) -> None:
        placar_x = 1030
        placar_y = 350
        placar_width = 150
        placar_height = 200

        pygame.draw.rect(self.tela, Colors.WHITE, (placar_x,
                         placar_y, placar_width, placar_height))
        pygame.draw.rect(self.tela, Colors.BLACK, (placar_x,
                         placar_y, placar_width, placar_height), 2)

        titulo = self.fonte_carta.render("JOGADOR 2", True, Colors.BLACK)
        titulo_rect = titulo.get_rect(
            center=(placar_x + placar_width//2, placar_y + 15))
        self.tela.blit(titulo, titulo_rect)

        pygame.draw.line(self.tela, Colors.BLACK,
                         (placar_x + 5, placar_y + 30),
                         (placar_x + placar_width - 5, placar_y + 30), 2)

        self._desenhar_pontuacao_por_cor_jogador2(
            slots, placar_x, placar_y, placar_width)

    def _desenhar_pontuacao_por_cor(self, slots: List[SlotCarta], placar_x: int, placar_y: int, placar_width: int) -> None:
        cores_ordem = [Colors.YELLOW, Colors.BLUE,
                       Colors.WHITE_CARD, Colors.GREEN, Colors.RED]
        nomes_cores = ["AMARELA", "AZUL", "BRANCA", "VERDE", "VERMELHA"]

        total_pontos = 0
        y_offset = 45

        for _, (cor, nome) in enumerate(zip(cores_ordem, nomes_cores)):
            slot_encontrado = None
            for slot in slots:
                if slot.cor == cor:
                    slot_encontrado = slot
                    break

            pontos = slot_encontrado.calcular_pontuacao() if slot_encontrado else 0
            total_pontos += pontos

            cor_rect = pygame.Rect(placar_x + 10, placar_y + y_offset, 15, 15)
            pygame.draw.rect(self.tela, cor, cor_rect)
            pygame.draw.rect(self.tela, Colors.BLACK, cor_rect, 1)

            texto_cor = self.fonte_pequena.render(nome, True, Colors.BLACK)
            self.tela.blit(texto_cor, (placar_x + 30, placar_y + y_offset))

            texto_pontos = self.fonte_pequena.render(
                str(pontos), True, Colors.BLACK)
            pontos_rect = texto_pontos.get_rect(right=placar_x + placar_width - 10,
                                                centery=placar_y + y_offset + 7)
            self.tela.blit(texto_pontos, pontos_rect)

            y_offset += 25

        self._desenhar_total_pontos(
            total_pontos, placar_x, placar_y, placar_width, y_offset)

    def _desenhar_pontuacao_por_cor_jogador2(self, slots: List[SlotCarta], placar_x: int, placar_y: int, placar_width: int) -> None:
        cores_ordem = [Colors.YELLOW, Colors.BLUE,
                       Colors.WHITE_CARD, Colors.GREEN, Colors.RED]
        nomes_cores = ["AMARELA", "AZUL", "BRANCA", "VERDE", "VERMELHA"]

        total_pontos = 0
        y_offset = 45

        for _, (cor, nome) in enumerate(zip(cores_ordem, nomes_cores)):
            slot_encontrado = None
            for slot in slots:
                if slot.cor == cor:
                    slot_encontrado = slot
                    break

            pontos = slot_encontrado.calcular_pontuacao() if slot_encontrado else 0
            total_pontos += pontos

            cor_rect = pygame.Rect(placar_x + 10, placar_y + y_offset, 15, 15)
            pygame.draw.rect(self.tela, cor, cor_rect)
            pygame.draw.rect(self.tela, Colors.BLACK, cor_rect, 1)

            texto_cor = self.fonte_pequena.render(nome, True, Colors.BLACK)
            self.tela.blit(texto_cor, (placar_x + 30, placar_y + y_offset))

            texto_pontos = self.fonte_pequena.render(
                str(pontos), True, Colors.BLACK)
            pontos_rect = texto_pontos.get_rect(right=placar_x + placar_width - 10,
                                                centery=placar_y + y_offset + 7)
            self.tela.blit(texto_pontos, pontos_rect)

            y_offset += 20

        pygame.draw.line(self.tela, Colors.BLACK,
                         (placar_x + 10, placar_y + y_offset + 5),
                         (placar_x + placar_width - 10, placar_y + y_offset + 5), 1)

        y_offset += 15
        texto_total = self.fonte_carta.render("TOTAL:", True, Colors.BLACK)
        self.tela.blit(texto_total, (placar_x + 10, placar_y + y_offset))

        texto_total_pontos = self.fonte_carta.render(
            str(total_pontos), True, Colors.BLACK)
        total_rect = texto_total_pontos.get_rect(right=placar_x + placar_width - 10,
                                                 centery=placar_y + y_offset + 8)
        self.tela.blit(texto_total_pontos, total_rect)

    def _desenhar_total_pontos(self, total_pontos: int, placar_x: int, placar_y: int, placar_width: int, y_offset: int) -> None:
        pygame.draw.line(self.tela, Colors.BLACK,
                         (placar_x + 5, placar_y + y_offset),
                         (placar_x + placar_width - 5, placar_y + y_offset), 2)

        y_offset += 10
        texto_total = self.fonte_carta.render("TOTAL", True, Colors.BLACK)
        self.tela.blit(texto_total, (placar_x + 10, placar_y + y_offset))

        texto_total_pontos = self.fonte_carta.render(
            str(total_pontos), True, Colors.BLACK)
        total_rect = texto_total_pontos.get_rect(right=placar_x + placar_width - 10,
                                                 centery=placar_y + y_offset + 10)
        self.tela.blit(texto_total_pontos, total_rect)
