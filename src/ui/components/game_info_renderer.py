import pygame
from config.settings import Colors, WINDOW_WIDTH


class GameInfoRenderer:
    def __init__(self, tela: pygame.Surface, fonte_carta: pygame.font.Font, fonte_pequena: pygame.font.Font):
        self.tela = tela
        self.fonte_carta = fonte_carta
        self.fonte_pequena = fonte_pequena
        self.fonte_titulo = pygame.font.Font(
            None, 48)

    def desenhar_info_turno(self, turn_manager) -> None:
        status = turn_manager.get_status_turno()
        info_y = 250

        jogador_texto = f"Vez do Jogador {status['jogador_atual']}"
        jogador_surface = self.fonte_carta.render(
            jogador_texto, True, Colors.BLACK)
        jogador_rect = jogador_surface.get_rect(
            center=(WINDOW_WIDTH // 2, info_y))
        self.tela.blit(jogador_surface, jogador_rect)

        fase_texto = "Jogar carta" if status['fase'] == 'jogar_carta' else "Comprar carta"
        fase_surface = self.fonte_pequena.render(
            f"Fase: {fase_texto}", True, Colors.BLACK)
        fase_rect = fase_surface.get_rect(
            center=(WINDOW_WIDTH // 2, info_y + 25))
        self.tela.blit(fase_surface, fase_rect)

        if status['jogo_terminado']:
            if status['vencedor'] == 0:
                fim_texto = "EMPATE!"
            else:
                fim_texto = f"JOGADOR {status['vencedor']} VENCEU!"
            fim_surface = self.fonte_titulo.render(fim_texto, True, Colors.RED)
            fim_rect = fim_surface.get_rect(
                center=(WINDOW_WIDTH // 2, info_y + 60))
            self.tela.blit(fim_surface, fim_rect)

    def desenhar_info_deck(self, deck_manager) -> None:
        stats = deck_manager.get_estatisticas_deck()

        x = WINDOW_WIDTH - 160
        y = 200

        pygame.draw.rect(self.tela, Colors.WHITE, (x, y, 140, 80))
        pygame.draw.rect(self.tela, Colors.BLACK, (x, y, 140, 80), 2)

        titulo = self.fonte_pequena.render("DECK", True, Colors.BLACK)
        self.tela.blit(titulo, (x + 5, y + 5))

        cartas_texto = f"Cartas: {stats['cartas_deck']}"
        cartas_surface = self.fonte_pequena.render(
            cartas_texto, True, Colors.BLACK)
        self.tela.blit(cartas_surface, (x + 5, y + 25))

        descarte_texto = "Descartes:"
        descarte_surface = self.fonte_pequena.render(
            descarte_texto, True, Colors.BLACK)
        self.tela.blit(descarte_surface, (x + 5, y + 45))

        total_descartes = sum(info['quantidade']
                              for info in stats['montes_descarte'].values())
        total_texto = f"Total: {total_descartes}"
        total_surface = self.fonte_pequena.render(
            total_texto, True, Colors.BLACK)
        self.tela.blit(total_surface, (x + 5, y + 60))
