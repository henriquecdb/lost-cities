from src.models.carta import Carta
from src.models.slot_carta import SlotCarta


class TurnManager:
    def __init__(self):
        self.jogador_atual = 1  # Jogador 1 sempre vai começar
        self.fase_turno = 'jogar_carta'  # 'jogar_carta' ou 'comprar_carta'
        self.carta_jogada_neste_turno = False
        self.carta_comprada_neste_turno = False
        self.jogo_terminado = False
        self.vencedor = None

    def get_jogador_atual(self) -> int:
        return self.jogador_atual

    def get_fase_turno(self) -> str:
        return self.fase_turno

    def pode_jogar_carta(self, jogador: int) -> bool:
        return (jogador == self.jogador_atual and
                self.fase_turno == 'jogar_carta' and
                not self.carta_jogada_neste_turno and
                not self.jogo_terminado)

    def pode_comprar_carta(self, jogador: int) -> bool:
        return (jogador == self.jogador_atual and
                self.fase_turno == 'comprar_carta' and
                self.carta_jogada_neste_turno and
                not self.carta_comprada_neste_turno and
                not self.jogo_terminado)

    def pode_mover_carta(self, jogador: int) -> bool:
        return (jogador == self.jogador_atual and
                not self.jogo_terminado)

    def validar_jogada_em_expedicao(self, carta: Carta, slot: SlotCarta) -> bool:
        return slot.pode_aceitar_carta(carta, self.jogador_atual)

    def registrar_carta_jogada(self, carta: Carta, tipo_jogada: str) -> bool:
        if not self.pode_jogar_carta(self.jogador_atual):
            return False

        self.carta_jogada_neste_turno = True
        self.fase_turno = 'comprar_carta'
        return True

    def registrar_carta_comprada(self, origem: str) -> bool:
        if not self.pode_comprar_carta(self.jogador_atual):
            return False

        self.carta_comprada_neste_turno = True
        self._finalizar_turno()
        return True

    def _finalizar_turno(self) -> None:
        self.carta_jogada_neste_turno = False
        self.carta_comprada_neste_turno = False
        self.fase_turno = 'jogar_carta'

        self.jogador_atual = 2 if self.jogador_atual == 1 else 1

    def verificar_fim_de_jogo(self, deck_vazio: bool, maos_vazias: bool) -> bool:
        if deck_vazio or maos_vazias:
            self.jogo_terminado = True
            return True
        return False

    def definir_vencedor(self, pontuacao_jogador1: int, pontuacao_jogador2: int) -> None:
        if pontuacao_jogador1 > pontuacao_jogador2:
            self.vencedor = 1
        elif pontuacao_jogador2 > pontuacao_jogador1:
            self.vencedor = 2
        else:
            self.vencedor = 0  # Empate

    def get_status_turno(self) -> dict:
        return {
            'jogador_atual': self.jogador_atual,
            'fase': self.fase_turno,
            'carta_jogada': self.carta_jogada_neste_turno,
            'carta_comprada': self.carta_comprada_neste_turno,
            'jogo_terminado': self.jogo_terminado,
            'vencedor': self.vencedor
        }

    def reset_jogo(self) -> None:
        self.jogador_atual = 1
        self.fase_turno = 'jogar_carta'
        self.carta_jogada_neste_turno = False
        self.carta_comprada_neste_turno = False
        self.jogo_terminado = False
        self.vencedor = None

    def forcar_proxima_fase(self) -> None:
        if self.fase_turno == 'jogar_carta' and not self.carta_jogada_neste_turno:
            self.carta_jogada_neste_turno = True
            self.fase_turno = 'comprar_carta'
        elif self.fase_turno == 'comprar_carta' and not self.carta_comprada_neste_turno:
            self.carta_comprada_neste_turno = True
            self._finalizar_turno()

    def pular_turno(self) -> None:
        self._finalizar_turno()
