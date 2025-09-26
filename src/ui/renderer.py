from config.settings import (
    Colors, FontConfig, LayoutConfig, WINDOW_WIDTH, WINDOW_HEIGHT
)
from src.models.slot_carta import SlotCarta
from src.models.carta import Carta
import pygame
from typing import List


class GameRenderer:
    def __init__(self, tela: pygame.Surface):
        self.tela = tela
        self._inicializar_fontes()

    def _inicializar_fontes(self) -> None:
        self.fonte_titulo = pygame.font.Font(None, FontConfig.TITLE_SIZE)
        self.fonte_carta = pygame.font.Font(None, FontConfig.CARD_NUMBER_SIZE)
        self.fonte_pequena = pygame.font.Font(None, FontConfig.SMALL_TEXT_SIZE)
        self.fonte_instrucoes = pygame.font.Font(
            None, FontConfig.INSTRUCTION_SIZE)

    def limpar_tela(self) -> None:
        self.tela.fill(Colors.LIGHT_GRAY)

    def desenhar_titulo(self, texto: str = None) -> None:
        if texto is None:
            texto = "Lost Cities - Arraste as cartas para os slots da mesma cor"

        titulo_surface = self.fonte_titulo.render(texto, True, Colors.BLACK)
        titulo_rect = titulo_surface.get_rect(
            center=(WINDOW_WIDTH // 2, LayoutConfig.TITLE_Y))
        self.tela.blit(titulo_surface, titulo_rect)

    def desenhar_container_slots(self, slots: List[SlotCarta]) -> None:
        if not slots:
            return

        primeiro_slot = slots[0]
        ultimo_slot = slots[-1]

        container_x = primeiro_slot.x - LayoutConfig.SLOTS_CONTAINER_MARGIN
        container_y = LayoutConfig.SLOTS_CONTAINER_Y
        container_largura = (ultimo_slot.x + ultimo_slot.largura) - \
            primeiro_slot.x + (LayoutConfig.SLOTS_CONTAINER_MARGIN * 2)
        container_altura = LayoutConfig.SLOTS_CONTAINER_HEIGHT

        pygame.draw.rect(self.tela, Colors.DARK_GRAY,
                         (container_x, container_y, container_largura, container_altura))
        pygame.draw.rect(self.tela, Colors.BLACK,
                         (container_x, container_y, container_largura, container_altura), 3)

    def desenhar_slots(self, slots: List[SlotCarta]) -> None:
        for slot in slots:
            slot.desenhar(self.tela, self.fonte_pequena)

    def desenhar_area_mao_jogador1(self, cartas: List[Carta], jogador_ativo: bool) -> None:
        area_y = LayoutConfig.PLAYER1_HAND_Y
        area_largura = WINDOW_WIDTH - (LayoutConfig.HAND_AREA_MARGIN * 2)
        area_altura = LayoutConfig.HAND_AREA_HEIGHT

        cor_fundo = Colors.LIGHT_GREEN if jogador_ativo else Colors.DARK_GRAY

        pygame.draw.rect(self.tela, cor_fundo,
                         (LayoutConfig.HAND_AREA_MARGIN, area_y, area_largura, area_altura))
        pygame.draw.rect(self.tela, Colors.BLACK,
                         (LayoutConfig.HAND_AREA_MARGIN, area_y, area_largura, area_altura), 3 if jogador_ativo else 2)

        titulo = "JOGADOR 1 (SUA VEZ)" if jogador_ativo else "JOGADOR 1"
        titulo_mao = self.fonte_carta.render(
            titulo, True, Colors.BLACK if jogador_ativo else Colors.WHITE)
        self.tela.blit(titulo_mao, (LayoutConfig.HAND_AREA_MARGIN +
                       20, area_y + LayoutConfig.HAND_TITLE_OFFSET_Y))

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
                         (LayoutConfig.HAND_AREA_MARGIN, area_y, area_largura, area_altura), 3 if jogador_ativo else 2)

        titulo = "JOGADOR 2 (SUA VEZ)" if jogador_ativo else "JOGADOR 2"
        titulo_mao = self.fonte_carta.render(
            titulo, True, Colors.BLACK if jogador_ativo else Colors.WHITE)
        self.tela.blit(titulo_mao, (LayoutConfig.HAND_AREA_MARGIN +
                       20, area_y + LayoutConfig.HAND_TITLE_OFFSET_Y))

        for carta in cartas:
            carta.desenhar(self.tela, self.fonte_carta)

    def desenhar_areas_descarte(self, deck_manager, areas_descarte) -> None:
        cores_disponiveis = Colors.get_available_colors()
        nomes_cores = Colors.get_color_names()

        for i, cor in enumerate(cores_disponiveis):
            area = areas_descarte[cor]

            pygame.draw.rect(self.tela, cor, area)
            pygame.draw.rect(self.tela, Colors.BLACK, area, 2)

            carta_topo = deck_manager.ver_topo_descarte(cor)
            if carta_topo:
                carta_topo.x = area.x
                carta_topo.y = area.y
                carta_topo.desenhar(self.tela, self.fonte_pequena)
            else:
                nome_cor = nomes_cores.get(cor, "?")
                texto = self.fonte_pequena.render(
                    nome_cor[:3], True, Colors.WHITE)
                texto_rect = texto.get_rect(center=area.center)
                self.tela.blit(texto, texto_rect)

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

        x = WINDOW_WIDTH - 160  # 150
        y = 200  # 20

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

    def desenhar_feedback_arraste(self, carta_arrastada: Carta, slots: List[SlotCarta],
                                  pos_mouse: tuple) -> None:
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

    def desenhar_instrucoes(self, instrucoes_customizadas: List[str] = None) -> None:
        if instrucoes_customizadas is None:
            instrucoes = [
                "R - Gerar novas cartas",
                "S - Alternar placares",
                "ESC - Sair",
                "Arraste cartas para slots da mesma cor"
            ]
        else:
            instrucoes = instrucoes_customizadas

        for i, instrucao in enumerate(instrucoes):
            texto_surface = self.fonte_instrucoes.render(
                instrucao, True, Colors.BLACK)
            y_pos = LayoutConfig.INSTRUCTIONS_START_Y + (i * 20)
            self.tela.blit(texto_surface, (20, y_pos))

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

    def desenhar_mensagem_temporaria(self, mensagem: str, x: int, y: int,
                                     cor: tuple = None) -> None:
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

    def atualizar_tela(self) -> None:
        pygame.display.flip()


class UIManager:
    def __init__(self, renderer: GameRenderer):
        self.renderer = renderer
        self.mensagens_temporarias = []
        self.mostrar_estatisticas = True

    def adicionar_mensagem_temporaria(self, mensagem: str, duracao: int = 180) -> None:
        mensagem_y = 300

        self.mensagens_temporarias.append({
            'texto': mensagem,
            'frames_restantes': duracao,
            'x': WINDOW_WIDTH // 2,
            'y': mensagem_y
        })

    def atualizar_mensagens(self) -> None:
        self.mensagens_temporarias = [
            msg for msg in self.mensagens_temporarias
            if msg['frames_restantes'] > 0
        ]

        for msg in self.mensagens_temporarias:
            msg['frames_restantes'] -= 1

    def renderizar_completo(self, cartas_mao_jogador1: List[Carta] = None, cartas_mao_jogador2: List[Carta] = None,
                            slots: List[SlotCarta] = None, carta_arrastada: Carta = None, pos_mouse: tuple = None,
                            turn_manager=None, deck_manager=None, areas_descarte=None,
                            slots_jogador1: List[SlotCarta] = None, slots_jogador2: List[SlotCarta] = None,
                            cartas_mao: List[Carta] = None) -> None:

        if cartas_mao is not None and cartas_mao_jogador1 is None:
            cartas_mao_jogador1 = cartas_mao
            cartas_mao_jogador2 = []

        if cartas_mao_jogador1 is None:
            cartas_mao_jogador1 = []
        if cartas_mao_jogador2 is None:
            cartas_mao_jogador2 = []
        if slots is None:
            slots = []

        if slots_jogador1 is None:
            slots_jogador1 = slots
        if slots_jogador2 is None:
            slots_jogador2 = slots

        self.renderer.limpar_tela()

        jogador_atual = turn_manager.get_jogador_atual() if turn_manager else 1

        self.renderer.desenhar_titulo("Lost Cities - Dois Jogadores")

        self.renderer.desenhar_area_mao_jogador1(
            cartas_mao_jogador1, jogador_atual == 1)
        self.renderer.desenhar_area_mao_jogador2(
            cartas_mao_jogador2, jogador_atual == 2)

        self.renderer.desenhar_container_slots(slots)
        self.renderer.desenhar_slots(slots)

        if deck_manager and areas_descarte:
            self.renderer.desenhar_areas_descarte(deck_manager, areas_descarte)

        if turn_manager:
            self.renderer.desenhar_info_turno(turn_manager)

        if deck_manager:
            self.renderer.desenhar_info_deck(deck_manager)

        if carta_arrastada and pos_mouse and turn_manager:
            self.renderer.desenhar_feedback_arraste(
                carta_arrastada, slots, pos_mouse)

        if self.mostrar_estatisticas:
            self.renderer.desenhar_estatisticas(slots_jogador1, slots_jogador2)

        instrucoes = [
            "ESC: Sair | R: Novo Jogo | S: Estatísticas | D: Comprar do Deck | ESPAÇO: Avançar Fase"
        ]
        self.renderer.desenhar_instrucoes(instrucoes)

        for msg in self.mensagens_temporarias:
            self.renderer.desenhar_mensagem_temporaria(
                msg['texto'], msg['x'], msg['y']
            )

        self.atualizar_mensagens()

        self.renderer.atualizar_tela()
