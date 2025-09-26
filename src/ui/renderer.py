from config.settings import (
    Colors, FontConfig, LayoutConfig, WINDOW_WIDTH, WINDOW_HEIGHT
)
from src.models.slot_carta import SlotCarta
from src.models.carta import Carta
from .components import HandRenderer, ScoreboardRenderer, GameInfoRenderer, UIEffectsRenderer
import pygame
from typing import List


class GameRenderer:
    def __init__(self, tela: pygame.Surface):
        self.tela = tela
        self._inicializar_fontes()
        self._inicializar_componentes()

    def _inicializar_fontes(self) -> None:
        self.fonte_titulo = pygame.font.Font(None, FontConfig.TITLE_SIZE)
        self.fonte_carta = pygame.font.Font(None, FontConfig.CARD_NUMBER_SIZE)
        self.fonte_pequena = pygame.font.Font(None, FontConfig.SMALL_TEXT_SIZE)
        self.fonte_instrucoes = pygame.font.Font(
            None, FontConfig.INSTRUCTION_SIZE)

    def _inicializar_componentes(self) -> None:
        self.hand_renderer = HandRenderer(self.tela, self.fonte_carta)
        self.scoreboard_renderer = ScoreboardRenderer(
            self.tela, self.fonte_carta, self.fonte_pequena)
        self.game_info_renderer = GameInfoRenderer(
            self.tela, self.fonte_carta, self.fonte_pequena)
        self.ui_effects_renderer = UIEffectsRenderer(
            self.tela, self.fonte_carta)

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
        self.hand_renderer.desenhar_area_mao_jogador1(cartas, jogador_ativo)

    def desenhar_area_mao_jogador2(self, cartas: List[Carta], jogador_ativo: bool) -> None:
        self.hand_renderer.desenhar_area_mao_jogador2(cartas, jogador_ativo)

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
        self.game_info_renderer.desenhar_info_turno(turn_manager)

    def desenhar_info_deck(self, deck_manager) -> None:
        self.game_info_renderer.desenhar_info_deck(deck_manager)

    def desenhar_feedback_arraste(self, carta_arrastada: Carta, slots: List[SlotCarta],
                                  pos_mouse: tuple) -> None:
        self.ui_effects_renderer.desenhar_feedback_arraste(
            carta_arrastada, slots, pos_mouse)

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
        self.scoreboard_renderer.desenhar_estatisticas(
            slots_jogador1, slots_jogador2)

    def desenhar_mensagem_temporaria(self, mensagem: str, x: int, y: int,
                                     cor: tuple = None) -> None:
        self.ui_effects_renderer.desenhar_mensagem_temporaria(
            mensagem, x, y, cor)

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
