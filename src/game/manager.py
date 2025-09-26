from config.settings import (
    Colors, WINDOW_WIDTH, WINDOW_HEIGHT,
    WINDOW_TITLE, FPS, get_slot_positions, get_hand_positions, get_discard_positions
)
from src.ui.renderer import GameRenderer, UIManager
from src.models.slot_carta import SlotCarta
from src.models.carta import Carta
from src.models.deck import DeckManager
from src.game.turn_manager import TurnManager
import pygame
from typing import List, Optional, Tuple


class GameManager:
    def __init__(self):
        pygame.init()

        self.tela = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)

        self.clock = pygame.time.Clock()

        self.renderer = GameRenderer(self.tela)
        self.ui_manager = UIManager(self.renderer)
        self.deck_manager = DeckManager()
        self.turn_manager = TurnManager()

        # Estado do jogo
        self.rodando = True
        self.slots_jogador1: List[SlotCarta] = []
        self.slots_jogador2: List[SlotCarta] = []

        # Slots compartilhados
        self.slots: List[SlotCarta] = []

        # Mãos dos jogadores
        self.cartas_mao_jogador1: List[Carta] = []
        self.cartas_mao_jogador2: List[Carta] = []

        # Estado de arraste
        self.carta_sendo_arrastada: Optional[Carta] = None
        self.posicao_original: Optional[Tuple[int, int]] = None
        self.jogador_carta_arrastada: Optional[int] = None

        self.areas_descarte = {}

        self._inicializar_jogo()

    def _inicializar_jogo(self) -> None:
        self._inicializar_slots()
        self._inicializar_areas_descarte()
        self._distribuir_cartas_iniciais()

    def _inicializar_slots(self) -> None:
        self.slots.clear()
        self.slots_jogador1.clear()
        self.slots_jogador2.clear()

        cores_disponiveis = Colors.get_available_colors()
        posicoes_slots = get_slot_positions()

        for i, cor in enumerate(cores_disponiveis):
            x, y = posicoes_slots[i]

            # Slot principal (jogador 1 - compartilhado para compatibilidade)
            slot = SlotCarta(x, y, cor)
            self.slots.append(slot)

            # Slot do jogador 1 (mesmo que o principal por enquanto)
            slot_j1 = SlotCarta(x, y, cor)
            self.slots_jogador1.append(slot_j1)

            # Slot do jogador 2 (separado para pontuação independente)
            slot_j2 = SlotCarta(x, y, cor)
            self.slots_jogador2.append(slot_j2)

    def _inicializar_areas_descarte(self) -> None:
        self.areas_descarte.clear()
        cores_disponiveis = Colors.get_available_colors()
        posicoes_descarte = get_discard_positions()

        for i, cor in enumerate(cores_disponiveis):
            x, y = posicoes_descarte[i]
            self.areas_descarte[cor] = pygame.Rect(x, y, 60, 90)

    def _distribuir_cartas_iniciais(self) -> None:
        self.cartas_mao_jogador1 = self.deck_manager.distribuir_mao_inicial()
        self._posicionar_cartas_mao(self.cartas_mao_jogador1, 1)

        self.cartas_mao_jogador2 = self.deck_manager.distribuir_mao_inicial()
        self._posicionar_cartas_mao(self.cartas_mao_jogador2, 2)

    def _posicionar_cartas_mao(self, cartas: List[Carta], jogador: int) -> None:
        posicoes = get_hand_positions(jogador)

        for i, carta in enumerate(cartas):
            if i < len(posicoes):
                x, y = posicoes[i]
                carta.mover_para(x, y)

    def _get_mao_jogador_atual(self) -> List[Carta]:
        if self.turn_manager.get_jogador_atual() == 1:  # testar com ternario dps
            return self.cartas_mao_jogador1
        else:
            return self.cartas_mao_jogador2

    def _processar_evento_mouse_down(self, evento: pygame.event.Event) -> None:
        if evento.button == 1:
            pos_mouse = pygame.mouse.get_pos()
            jogador_atual = self.turn_manager.get_jogador_atual()

            if self.turn_manager.pode_comprar_carta(jogador_atual):
                for cor, area in self.areas_descarte.items():
                    if area.collidepoint(pos_mouse):
                        self._comprar_carta_descarte(cor)
                        return

            if not self.turn_manager.pode_mover_carta(jogador_atual):
                self.ui_manager.adicionar_mensagem_temporaria(
                    # f"Aguarde sua vez, Jogador {jogador_atual}!")
                    f"Aguarde sua vez!")
                return

            mao_atual = self._get_mao_jogador_atual()

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
        if evento.button == 1 and self.carta_sendo_arrastada:
            pos_mouse = pygame.mouse.get_pos()
            carta_colocada = False
            # jogador_atual = self.turn_manager.get_jogador_atual()

            slots_visuais = self.slots
            for slot in slots_visuais:
                if slot.get_rect().collidepoint(pos_mouse):
                    if self._tentar_jogar_em_expedicao(slot):
                        carta_colocada = True
                        break

            if not carta_colocada:
                for cor, area in self.areas_descarte.items():
                    if area.collidepoint(pos_mouse):
                        if self._tentar_descartar_carta(cor):
                            carta_colocada = True
                            break

            if not carta_colocada and self.posicao_original:
                self.carta_sendo_arrastada.mover_para(*self.posicao_original)

            if self.carta_sendo_arrastada:
                self.carta_sendo_arrastada.parar_arraste()
            self.carta_sendo_arrastada = None
            self.posicao_original = None
            self.jogador_carta_arrastada = None

    def _tentar_jogar_em_expedicao(self, slot: SlotCarta) -> bool:
        if not self.carta_sendo_arrastada:
            return False

        if not self.turn_manager.pode_jogar_carta(self.turn_manager.get_jogador_atual()):
            self.ui_manager.adicionar_mensagem_temporaria(
                "Complete a fase atual primeiro!")
            return False

        jogador_atual = self.turn_manager.get_jogador_atual()
        slots_jogador = self.slots_jogador1 if jogador_atual == 1 else self.slots_jogador2

        slot_jogador = None
        for s in slots_jogador:
            if s.cor == slot.cor:
                slot_jogador = s
                break

        if not slot_jogador:
            return False

        if self.turn_manager.validar_jogada_em_expedicao(self.carta_sendo_arrastada, slot_jogador):
            if slot_jogador.adicionar_carta(self.carta_sendo_arrastada):
                slot.adicionar_carta(self.carta_sendo_arrastada)

                mao_atual = self._get_mao_jogador_atual()
                if self.carta_sendo_arrastada in mao_atual:
                    mao_atual.remove(self.carta_sendo_arrastada)

                self.turn_manager.registrar_carta_jogada(
                    self.carta_sendo_arrastada, 'expedicao')

                nomes_cores = Colors.get_color_names()
                cor_nome = nomes_cores.get(
                    self.carta_sendo_arrastada.cor, "Desconhecida")
                if self.carta_sendo_arrastada.tipo_carta == 'investimento':
                    mensagem = f"Investimento {cor_nome} jogado!"
                else:
                    mensagem = f"Carta {self.carta_sendo_arrastada.numero} {cor_nome} jogada!"
                self.ui_manager.adicionar_mensagem_temporaria(mensagem)

                return True
        else:
            self.ui_manager.adicionar_mensagem_temporaria(
                "Jogada inválida! Verifique cor e ordem.")

        return False

    def _tentar_descartar_carta(self, cor) -> bool:
        if not self.carta_sendo_arrastada:
            return False

        if not self.turn_manager.pode_jogar_carta(self.turn_manager.get_jogador_atual()):
            self.ui_manager.adicionar_mensagem_temporaria(
                "Complete a fase atual primeiro!")
            return False

        if self.deck_manager.descartar_carta(self.carta_sendo_arrastada):
            mao_atual = self._get_mao_jogador_atual()
            if self.carta_sendo_arrastada in mao_atual:
                mao_atual.remove(self.carta_sendo_arrastada)

            self.turn_manager.registrar_carta_jogada(
                self.carta_sendo_arrastada, 'descarte')

            nomes_cores = Colors.get_color_names()
            cor_nome = nomes_cores.get(cor, "Desconhecida")
            self.ui_manager.adicionar_mensagem_temporaria(
                f"Carta descartada em {cor_nome}!")

            return True

        return False

    def _processar_evento_mouse_motion(self, evento: pygame.event.Event) -> None:
        if self.carta_sendo_arrastada:
            pos_mouse = pygame.mouse.get_pos()
            self.carta_sendo_arrastada.atualizar_posicao(pos_mouse)

    def _processar_evento_teclado(self, evento: pygame.event.Event) -> None:
        if evento.key == pygame.K_ESCAPE:
            self.rodando = False
        elif evento.key == pygame.K_r:
            self._novo_jogo()
            self.ui_manager.adicionar_mensagem_temporaria(
                "Novo jogo iniciado!")
        elif evento.key == pygame.K_s:
            self.ui_manager.mostrar_estatisticas = not self.ui_manager.mostrar_estatisticas
            status = "ativadas" if self.ui_manager.mostrar_estatisticas else "desativadas"
            self.ui_manager.adicionar_mensagem_temporaria(
                f"Estatísticas {status}!")
        elif evento.key == pygame.K_d:
            self._comprar_carta_deck()
        elif evento.key == pygame.K_SPACE:
            self.turn_manager.forcar_proxima_fase()
            self.ui_manager.adicionar_mensagem_temporaria("Fase avançada!")

    def _comprar_carta_descarte(self, cor) -> None:
        if not self.turn_manager.pode_comprar_carta(self.turn_manager.get_jogador_atual()):
            self.ui_manager.adicionar_mensagem_temporaria(
                "Não é possível comprar carta agora!")
            return

        carta = self.deck_manager.comprar_do_descarte(cor)
        if carta:
            mao_atual = self._get_mao_jogador_atual()
            jogador_atual = self.turn_manager.get_jogador_atual()

            posicoes = get_hand_positions(jogador_atual)

            if len(mao_atual) < len(posicoes):
                for i, carta_existente in enumerate(mao_atual):
                    x, y = posicoes[i]
                    carta_existente.mover_para(x, y)

                x, y = posicoes[len(mao_atual)]
                carta.mover_para(x, y)
                mao_atual.append(carta)

                self.turn_manager.registrar_carta_comprada('descarte')

                nomes_cores = Colors.get_color_names()
                cor_nome = nomes_cores.get(cor, "Desconhecida")
                self.ui_manager.adicionar_mensagem_temporaria(
                    f"Carta comprada do descarte {cor_nome}!")
            else:
                self.ui_manager.adicionar_mensagem_temporaria("Mão cheia!")
        else:
            nomes_cores = Colors.get_color_names()
            cor_nome = nomes_cores.get(cor, "Desconhecida")
            self.ui_manager.adicionar_mensagem_temporaria(
                f"Descarte {cor_nome} vazio!")

    def _comprar_carta_deck(self) -> None:
        jogador_atual = self.turn_manager.get_jogador_atual()

        if not self.turn_manager.pode_comprar_carta(jogador_atual):
            self.ui_manager.adicionar_mensagem_temporaria(
                "Não é possível comprar carta agora!")
            return

        carta = self.deck_manager.comprar_do_deck()
        if carta:
            mao_atual = self._get_mao_jogador_atual()
            posicoes = get_hand_positions(jogador_atual)

            if len(mao_atual) < len(posicoes):
                for i, carta_existente in enumerate(mao_atual):
                    x, y = posicoes[i]
                    carta_existente.mover_para(x, y)

                x, y = posicoes[len(mao_atual)]
                carta.mover_para(x, y)
                mao_atual.append(carta)

                self.turn_manager.registrar_carta_comprada('deck')
                self.ui_manager.adicionar_mensagem_temporaria(
                    "Carta comprada do deck!")
            else:
                self.ui_manager.adicionar_mensagem_temporaria("Mão cheia!")
        else:
            self.ui_manager.adicionar_mensagem_temporaria("Deck vazio!")

    def _novo_jogo(self) -> None:
        self.deck_manager.reset_jogo()
        self.turn_manager.reset_jogo()

        for slot in self.slots:
            slot.cartas.clear()

        self._distribuir_cartas_iniciais()

        self.ui_manager.adicionar_mensagem_temporaria("Novo jogo iniciado!")

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
                    if self.turn_manager.validar_jogada_em_expedicao(self.carta_sendo_arrastada, slot):
                        slot.destacar(True)
                    break

        deck_vazio = not self.deck_manager.deck.tem_cartas()
        mao1_vazia = len(self.cartas_mao_jogador1) == 0
        mao2_vazia = len(self.cartas_mao_jogador2) == 0

        if self.turn_manager.verificar_fim_de_jogo(deck_vazio, mao1_vazia or mao2_vazia):
            if not hasattr(self, '_fim_jogo_processado'):
                self._processar_fim_de_jogo()
                self._fim_jogo_processado = True

    def _processar_fim_de_jogo(self) -> None:
        pontuacao1 = sum(slot.calcular_pontuacao() for slot in self.slots)
        pontuacao2 = 0

        self.turn_manager.definir_vencedor(pontuacao1, pontuacao2)

        vencedor = self.turn_manager.vencedor
        if vencedor == 0:
            self.ui_manager.adicionar_mensagem_temporaria("Empate!")
        else:
            self.ui_manager.adicionar_mensagem_temporaria(
                f"Jogador {vencedor} venceu!")

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
            turn_manager=self.turn_manager,
            deck_manager=self.deck_manager,
            areas_descarte=self.areas_descarte
        )

    def get_estatisticas(self) -> dict:
        pontuacao_total = sum(slot.calcular_pontuacao() for slot in self.slots)
        cartas_jogadas = sum(slot.get_quantidade_cartas()
                             for slot in self.slots)

        estatisticas_por_cor = {}
        nomes_cores = Colors.get_color_names()

        for slot in self.slots:
            cor_nome = nomes_cores.get(slot.cor, "Desconhecida")
            estatisticas_por_cor[cor_nome] = {
                'cartas': slot.get_quantidade_cartas(),
                'pontuacao': slot.calcular_pontuacao()
            }

        status_turno = self.turn_manager.get_status_turno()
        stats_deck = self.deck_manager.get_estatisticas_deck()

        return {
            'pontuacao_total': pontuacao_total,
            'cartas_jogadas': cartas_jogadas,
            'cartas_mao_j1': len(self.cartas_mao_jogador1),
            'cartas_mao_j2': len(self.cartas_mao_jogador2),
            'por_cor': estatisticas_por_cor,
            'turno': status_turno,
            'deck': stats_deck
        }

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
    def criar_jogo_padrao() -> GameManager:
        return GameManager()

    def executar(self) -> None:
        while self.rodando:
            self._processar_eventos()
            self._atualizar_logica()
            self._renderizar()
            self.clock.tick(FPS)

        self._finalizar()

    def _finalizar(self) -> None:
        pygame.quit()
