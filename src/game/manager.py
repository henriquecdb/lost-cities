import pygame
from typing import Dict, List, Optional, Tuple

from config.settings import (
    Colors,
    DEFAULT_RANDOM_SEED,
    FPS,
    GameConfig,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    get_discard_positions,
    get_hand_positions,
    get_slot_positions,
)
from src.game.state import GameState
from src.game.turn_manager import TurnManager
from src.models.carta import Carta
from src.models.deck import DeckManager
from src.models.slot_carta import SlotCarta
from src.ui.renderer import GameRenderer, UIManager


class GameManager:
    def __init__(self, state: GameState):
        self.state = state

    @classmethod
    def create_default(cls, seed: Optional[int] = DEFAULT_RANDOM_SEED) -> 'GameManager':
        deck_manager = DeckManager(seed=seed)
        turn_manager = TurnManager()
        state = GameState(deck_manager=deck_manager, turn_manager=turn_manager)
        manager = cls(state)
        manager.start_new_game()  # manager.start_new_game(seed=41)
        return manager

    def start_new_game(self, seed: Optional[int] = None) -> None:
        if seed is not None:
            self.state.deck_manager.set_seed(seed)
        else:
            self.state.deck_manager.reset_jogo()
        self.state.turn_manager.reset_jogo()
        self.state.reset()
        colors = Colors.get_available_colors()
        slot_positions = get_slot_positions()
        self.state.configure_slots(colors, slot_positions)
        self._distribuir_cartas_iniciais()
        self.state.fim_jogo_processado = False

    def _distribuir_cartas_iniciais(self) -> None:
        for jogador in (1, 2):
            mao = self.state.deck_manager.distribuir_mao_inicial()
            self.state.players[jogador].hand = mao

    def get_shared_slots(self) -> List[SlotCarta]:
        return self.state.shared_slots

    def get_player_slots(self, jogador: int) -> List[SlotCarta]:
        return self.state.get_player_slots(jogador)

    def get_hand(self, jogador: int) -> List[Carta]:
        return self.state.get_player_hand(jogador)

    def get_turn_manager(self) -> TurnManager:
        return self.state.turn_manager

    def get_deck_manager(self) -> DeckManager:
        return self.state.deck_manager

    def get_jogador_atual(self) -> int:
        return self.state.turn_manager.get_jogador_atual()

    def pode_mover_carta(self, jogador: int) -> bool:
        return self.state.turn_manager.pode_mover_carta(jogador)

    def pode_jogar_carta(self, jogador: int) -> bool:
        return self.state.turn_manager.pode_jogar_carta(jogador)

    def pode_comprar_carta(self, jogador: int) -> bool:
        return self.state.turn_manager.pode_comprar_carta(jogador)

    def validar_jogada_em_slot(self, carta: Carta, slot: SlotCarta) -> bool:
        jogador = self.get_jogador_atual()
        slot_jogador = self.state.find_player_slot(jogador, slot.cor)
        if not slot_jogador:
            return False
        return self.state.turn_manager.validar_jogada_em_expedicao(carta, slot_jogador)

    def forcar_proxima_fase(self) -> None:
        self.state.turn_manager.forcar_proxima_fase()

    def pular_turno(self) -> None:
        self.state.turn_manager.pular_turno()

    def tentar_jogar_em_expedicao(self, carta: Carta, cor) -> Tuple[bool, str]:
        jogador = self.get_jogador_atual()
        if not self.pode_jogar_carta(jogador):
            return False, 'Complete a fase atual primeiro!'

        slot_jogador = self.state.find_player_slot(jogador, cor)
        slot_compartilhado = self.state.find_shared_slot(cor)
        if not slot_jogador or not slot_compartilhado:
            return False, 'Slot inválido!'

        if not self.state.turn_manager.validar_jogada_em_expedicao(carta, slot_jogador):
            return False, 'Jogada inválida! Verifique cor e ordem.'

        if slot_jogador.adicionar_carta(carta):
            slot_compartilhado.adicionar_carta(carta, jogador)
            mao = self.state.get_player_hand(jogador)
            if carta in mao:
                mao.remove(carta)
            self.state.turn_manager.registrar_carta_jogada(carta, 'expedicao')
            return True, self._mensagem_carta_jogada(carta)

        return False, 'Não foi possível jogar a carta.'

    def tentar_descartar_carta(self, carta: Carta) -> Tuple[bool, str]:
        jogador = self.get_jogador_atual()
        if not self.pode_jogar_carta(jogador):
            return False, 'Complete a fase atual primeiro!'

        if self.state.deck_manager.descartar_carta(carta):
            mao = self.state.get_player_hand(jogador)
            if carta in mao:
                mao.remove(carta)
            self.state.turn_manager.registrar_carta_jogada(carta, 'descarte')
            carta.parar_arraste()
            nomes_cores = Colors.get_color_names()
            cor_nome = nomes_cores.get(carta.cor, 'Desconhecida')
            return True, f'Carta descartada em {cor_nome}!'

        return False, 'Não é possível descartar a carta!'

    def comprar_carta_deck(self) -> Tuple[bool, Optional[Carta], str]:
        jogador = self.get_jogador_atual()
        if not self.pode_comprar_carta(jogador):
            return False, None, 'Não é possível comprar carta agora!'

        mao = self.state.get_player_hand(jogador)
        if len(mao) >= GameConfig.STARTING_HAND_SIZE:
            return False, None, 'Mão cheia!'

        carta = self.state.deck_manager.comprar_do_deck()
        if not carta:
            return False, None, 'Deck vazio!'

        mao.append(carta)
        self.state.turn_manager.registrar_carta_comprada('deck')
        return True, carta, 'Carta comprada do deck!'

    def comprar_carta_descarte(self, cor) -> Tuple[bool, Optional[Carta], str]:
        jogador = self.get_jogador_atual()
        if not self.pode_comprar_carta(jogador):
            return False, None, 'Não é possível comprar carta agora!'

        mao = self.state.get_player_hand(jogador)
        if len(mao) >= GameConfig.STARTING_HAND_SIZE:
            return False, None, 'Mão cheia!'

        carta = self.state.deck_manager.comprar_do_descarte(cor)
        nomes_cores = Colors.get_color_names()
        if not carta:
            cor_nome = nomes_cores.get(cor, 'Desconhecida')
            return False, None, f'Descarte {cor_nome} vazio!'

        mao.append(carta)
        self.state.turn_manager.registrar_carta_comprada('descarte')
        cor_nome = nomes_cores.get(cor, 'Desconhecida')
        return True, carta, f'Carta comprada do descarte {cor_nome}!'

    def checar_fim_de_jogo(self) -> Optional[str]:
        deck_vazio = not self.state.deck_manager.deck.tem_cartas()
        mao1_vazia = len(self.state.get_player_hand(1)) == 0
        mao2_vazia = len(self.state.get_player_hand(2)) == 0

        if self.state.turn_manager.verificar_fim_de_jogo(deck_vazio, mao1_vazia or mao2_vazia):
            if not self.state.fim_jogo_processado:
                return self._processar_fim_de_jogo()
        return None

    def _processar_fim_de_jogo(self) -> str:
        pontuacao1 = sum(slot.calcular_pontuacao()
                         for slot in self.state.get_player_slots(1))
        pontuacao2 = sum(slot.calcular_pontuacao()
                         for slot in self.state.get_player_slots(2))

        self.state.turn_manager.definir_vencedor(pontuacao1, pontuacao2)
        self.state.fim_jogo_processado = True

        vencedor = self.state.turn_manager.vencedor
        if vencedor == 0:
            return 'Empate!'
        return f'Jogador {vencedor} venceu!'

    def get_estatisticas(self) -> dict:
        slots = self.state.shared_slots
        pontuacao_total = sum(slot.calcular_pontuacao() for slot in slots)
        cartas_jogadas = sum(slot.get_quantidade_cartas() for slot in slots)

        estatisticas_por_cor: Dict[str, dict] = {}
        nomes_cores = Colors.get_color_names()
        for slot in slots:
            cor_nome = nomes_cores.get(slot.cor, 'Desconhecida')
            estatisticas_por_cor[cor_nome] = {
                'cartas': slot.get_quantidade_cartas(),
                'pontuacao': slot.calcular_pontuacao(),
            }

        pontuacao_j1 = sum(slot.calcular_pontuacao()
                           for slot in self.state.get_player_slots(1))
        pontuacao_j2 = sum(slot.calcular_pontuacao()
                           for slot in self.state.get_player_slots(2))

        return {
            'pontuacao_total': pontuacao_total,
            'pontuacao_j1': pontuacao_j1,
            'pontuacao_j2': pontuacao_j2,
            'cartas_jogadas': cartas_jogadas,
            'cartas_mao_j1': len(self.state.get_player_hand(1)),
            'cartas_mao_j2': len(self.state.get_player_hand(2)),
            'por_cor': estatisticas_por_cor,
            'turno': self.state.turn_manager.get_status_turno(),
            'deck': self.state.deck_manager.get_estatisticas_deck(),
        }

    @staticmethod
    def _mensagem_carta_jogada(carta: Carta) -> str:
        nomes_cores = Colors.get_color_names()
        cor_nome = nomes_cores.get(carta.cor, 'Desconhecida')
        if carta.tipo_carta == 'investimento':
            return f'Investimento {cor_nome} jogado!'
        return f'Carta {carta.numero} {cor_nome} jogada!'


class GameApp:
    '''Responsável por lidar com a interface e delegar ações ao GameManager.'''

    def __init__(self, game_manager: GameManager):
        pygame.init()

        self.game_manager = game_manager
        self.tela = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()
        self.renderer = GameRenderer(self.tela)
        self.ui_manager = UIManager(self.renderer)

        self.rodando = True
        self.carta_sendo_arrastada: Optional[Carta] = None
        self.posicao_original: Optional[Tuple[int, int]] = None
        self.jogador_carta_arrastada: Optional[int] = None
        self.areas_descarte: Dict[Tuple[int, int, int], pygame.Rect] = {}

        self.slots: List[SlotCarta] = []
        self.slots_jogador1: List[SlotCarta] = []
        self.slots_jogador2: List[SlotCarta] = []
        self.cartas_mao_jogador1: List[Carta] = []
        self.cartas_mao_jogador2: List[Carta] = []

        self._sync_state_references()
        self._inicializar_areas_descarte()
        self._reposicionar_mao(1)
        self._reposicionar_mao(2)

    def _sync_state_references(self) -> None:
        self.slots = self.game_manager.get_shared_slots()
        self.slots_jogador1 = self.game_manager.get_player_slots(1)
        self.slots_jogador2 = self.game_manager.get_player_slots(2)
        self.cartas_mao_jogador1 = self.game_manager.get_hand(1)
        self.cartas_mao_jogador2 = self.game_manager.get_hand(2)

    def _inicializar_areas_descarte(self) -> None:
        self.areas_descarte.clear()
        cores_disponiveis = Colors.get_available_colors()
        posicoes_descarte = get_discard_positions()

        for indice, cor in enumerate(cores_disponiveis):
            x, y = posicoes_descarte[indice]
            self.areas_descarte[cor] = pygame.Rect(x, y, 60, 90)

    def _reposicionar_mao(self, jogador: int) -> None:
        mao = self.game_manager.get_hand(jogador)
        posicoes = get_hand_positions(jogador)

        for indice, carta in enumerate(mao):
            if indice < len(posicoes):
                x, y = posicoes[indice]
                carta.mover_para(x, y)

    def _novo_jogo(self, seed: Optional[int] = None) -> None:
        self.game_manager.start_new_game(seed=seed)
        self._sync_state_references()
        self._reposicionar_mao(1)
        self._reposicionar_mao(2)
        self.carta_sendo_arrastada = None
        self.posicao_original = None
        self.jogador_carta_arrastada = None
        self.ui_manager.adicionar_mensagem_temporaria('Novo jogo iniciado!')

    def _processar_evento_mouse_down(self, evento: pygame.event.Event) -> None:
        if evento.button != 1:
            return

        pos_mouse = pygame.mouse.get_pos()
        jogador_atual = self.game_manager.get_jogador_atual()

        if self.game_manager.pode_comprar_carta(jogador_atual):
            for cor, area in self.areas_descarte.items():
                if area.collidepoint(pos_mouse):
                    self._comprar_carta_descarte(cor)
                    return

        if not self.game_manager.pode_mover_carta(jogador_atual):
            self.ui_manager.adicionar_mensagem_temporaria('Aguarde sua vez!')
            return

        mao_atual = self.game_manager.get_hand(jogador_atual)

        for carta in reversed(mao_atual):
            if carta.contem_ponto(pos_mouse):
                self.carta_sendo_arrastada = carta
                self.posicao_original = (carta.x, carta.y)
                self.jogador_carta_arrastada = jogador_atual
                carta.iniciar_arraste(pos_mouse)

                mao_atual.remove(carta)
                mao_atual.append(carta)
                break

    def _processar_evento_mouse_up(self, evento: pygame.event.Event) -> None:
        if evento.button != 1 or not self.carta_sendo_arrastada:
            return

        pos_mouse = pygame.mouse.get_pos()
        carta_colocada = False
        jogador = self.jogador_carta_arrastada

        for slot in self.slots:
            if slot.get_rect().collidepoint(pos_mouse):
                sucesso, mensagem = self.game_manager.tentar_jogar_em_expedicao(
                    self.carta_sendo_arrastada, slot.cor
                )
                if mensagem:
                    self.ui_manager.adicionar_mensagem_temporaria(mensagem)
                if sucesso:
                    carta_colocada = True
                    if jogador:
                        self._reposicionar_mao(jogador)
                break

        if not carta_colocada:
            for cor, area in self.areas_descarte.items():
                if area.collidepoint(pos_mouse):
                    sucesso, mensagem = self.game_manager.tentar_descartar_carta(
                        self.carta_sendo_arrastada
                    )
                    if mensagem:
                        self.ui_manager.adicionar_mensagem_temporaria(mensagem)
                    if sucesso:
                        self.carta_sendo_arrastada.mover_para(area.x, area.y)
                        carta_colocada = True
                        if jogador:
                            self._reposicionar_mao(jogador)
                    break

        if not carta_colocada and self.posicao_original:
            self.carta_sendo_arrastada.mover_para(*self.posicao_original)

        if self.carta_sendo_arrastada:
            self.carta_sendo_arrastada.parar_arraste()

        self.carta_sendo_arrastada = None
        self.posicao_original = None
        self.jogador_carta_arrastada = None

    def _processar_evento_mouse_motion(self, evento: pygame.event.Event) -> None:
        if self.carta_sendo_arrastada:
            pos_mouse = pygame.mouse.get_pos()
            self.carta_sendo_arrastada.atualizar_posicao(pos_mouse)

    def _processar_evento_teclado(self, evento: pygame.event.Event) -> None:
        if evento.key == pygame.K_ESCAPE:
            self.rodando = False
        elif evento.key == pygame.K_r:
            self._novo_jogo()
        elif evento.key == pygame.K_s:
            self.ui_manager.mostrar_estatisticas = not self.ui_manager.mostrar_estatisticas
            status = 'ativadas' if self.ui_manager.mostrar_estatisticas else 'desativadas'
            self.ui_manager.adicionar_mensagem_temporaria(
                f'Estatísticas {status}!')
        elif evento.key == pygame.K_d:
            self._comprar_carta_deck()
        elif evento.key == pygame.K_SPACE:
            self.game_manager.forcar_proxima_fase()
            self.ui_manager.adicionar_mensagem_temporaria('Fase avançada!')

    def _comprar_carta_descarte(self, cor) -> None:
        jogador = self.game_manager.get_jogador_atual()
        sucesso, carta, mensagem = self.game_manager.comprar_carta_descarte(
            cor)
        if mensagem:
            self.ui_manager.adicionar_mensagem_temporaria(mensagem)
        if sucesso and carta:
            self._reposicionar_mao(jogador)

    def _comprar_carta_deck(self) -> None:
        jogador = self.game_manager.get_jogador_atual()
        sucesso, carta, mensagem = self.game_manager.comprar_carta_deck()
        if mensagem:
            self.ui_manager.adicionar_mensagem_temporaria(mensagem)
        if sucesso and carta:
            self._reposicionar_mao(jogador)

    def _processar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                self._processar_evento_mouse_down(evento)
            elif evento.type == pygame.MOUSEBUTTONUP:
                self._processar_evento_mouse_up(evento)
            elif evento.type == pygame.MOUSEMOTION:
                self._processar_evento_mouse_motion(evento)
            elif evento.type == pygame.KEYDOWN:
                self._processar_evento_teclado(evento)

    def _atualizar_logica(self) -> None:
        for slot in self.slots:
            slot.destacar(False)

        if self.carta_sendo_arrastada:
            pos_mouse = pygame.mouse.get_pos()
            for slot in self.slots:
                if slot.get_rect().collidepoint(pos_mouse):
                    if self.game_manager.validar_jogada_em_slot(self.carta_sendo_arrastada, slot):
                        slot.destacar(True)
                    break

        mensagem_fim = self.game_manager.checar_fim_de_jogo()
        if mensagem_fim:
            self.ui_manager.adicionar_mensagem_temporaria(mensagem_fim)

    def _renderizar(self) -> None:
        pos_mouse = pygame.mouse.get_pos() if self.carta_sendo_arrastada else None

        self.ui_manager.renderizar_completo(
            cartas_mao_jogador1=self.cartas_mao_jogador1,
            cartas_mao_jogador2=self.cartas_mao_jogador2,
            slots=self.slots,
            slots_jogador1=self.slots_jogador1,
            slots_jogador2=self.slots_jogador2,
            carta_arrastada=self.carta_sendo_arrastada,
            pos_mouse=pos_mouse,
            turn_manager=self.game_manager.get_turn_manager(),
            deck_manager=self.game_manager.get_deck_manager(),
            areas_descarte=self.areas_descarte,
        )

    def get_estatisticas(self) -> dict:
        return self.game_manager.get_estatisticas()

    def executar(self) -> None:
        while self.rodando:
            self._processar_eventos()
            self._atualizar_logica()
            self._renderizar()
            self.clock.tick(FPS)

        self._finalizar()

    def _finalizar(self) -> None:
        pygame.quit()


class GameFactory:
    @staticmethod
    def criar_jogo_padrao(seed: Optional[int] = DEFAULT_RANDOM_SEED) -> 'GameApp':
        manager = GameManager.create_default(seed=seed)
        return GameApp(manager)
