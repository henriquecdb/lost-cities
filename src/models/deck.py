import random
from typing import List, Optional
from src.models.carta import Carta
from config.settings import Colors, GameConfig, CardConfig


class Deck:
    def __init__(self):
        self.cartas: List[Carta] = []
        self._criar_deck_completo()
        self.embaralhar()

    def _criar_deck_completo(self) -> None:
        self.cartas.clear()
        cores_disponiveis = Colors.get_available_colors()

        for cor in cores_disponiveis:
            for numero in range(CardConfig.MIN_CARD_NUMBER, CardConfig.MAX_CARD_NUMBER + 1):
                carta = Carta(numero=numero, cor=cor, x=0,
                              y=0, tipo_carta='numerada')
                self.cartas.append(carta)

        for cor in cores_disponiveis:
            for _ in range(CardConfig.INVESTMENT_CARDS_PER_COLOR):
                carta = Carta(numero=0, cor=cor, x=0, y=0,
                              tipo_carta='investimento')
                self.cartas.append(carta)

    def embaralhar(self) -> None:
        random.shuffle(self.cartas)

    def comprar_carta(self) -> Optional[Carta]:
        if self.cartas:
            return self.cartas.pop()
        return None

    def tem_cartas(self) -> bool:
        return len(self.cartas) > 0

    def quantidade_cartas(self) -> int:
        return len(self.cartas)

    def reset(self) -> None:
        self._criar_deck_completo()
        self.embaralhar()


class DiscardPile:
    def __init__(self, cor):
        self.cor = cor
        self.cartas: List[Carta] = []

    def adicionar_carta(self, carta: Carta) -> bool:
        if carta.cor == self.cor:
            self.cartas.append(carta)
            return True
        return False

    def comprar_carta_topo(self) -> Optional[Carta]:
        if self.cartas:
            return self.cartas.pop()
        return None

    def ver_carta_topo(self) -> Optional[Carta]:
        if self.cartas:
            return self.cartas[-1]
        return None

    def esta_vazio(self) -> bool:
        return len(self.cartas) == 0

    def quantidade_cartas(self) -> int:
        return len(self.cartas)


class DeckManager:
    def __init__(self):
        self.deck = Deck()
        self.montes_descarte = {}

        for cor in Colors.get_available_colors():
            self.montes_descarte[cor] = DiscardPile(cor)

    def distribuir_mao_inicial(self) -> List[Carta]:
        mao = []
        for _ in range(GameConfig.STARTING_HAND_SIZE):
            carta = self.deck.comprar_carta()
            if carta:
                mao.append(carta)
            else:
                break

        return mao

    def comprar_do_deck(self) -> Optional[Carta]:
        return self.deck.comprar_carta()

    def comprar_do_descarte(self, cor) -> Optional[Carta]:
        if cor in self.montes_descarte:
            return self.montes_descarte[cor].comprar_carta_topo()
        return None

    def descartar_carta(self, carta: Carta) -> bool:
        if carta.cor in self.montes_descarte:
            return self.montes_descarte[carta.cor].adicionar_carta(carta)
        return False

    def ver_topo_descarte(self, cor) -> Optional[Carta]:
        if cor in self.montes_descarte:
            return self.montes_descarte[cor].ver_carta_topo()
        return None

    def get_estatisticas_deck(self) -> dict:
        stats = {
            'cartas_deck': self.deck.quantidade_cartas(),
            'montes_descarte': {}
        }

        for cor, monte in self.montes_descarte.items():
            nome_cor = Colors.get_color_names().get(cor, "Desconhecida")
            stats['montes_descarte'][nome_cor] = {
                'quantidade': monte.quantidade_cartas(),
                'topo': monte.ver_carta_topo().numero if not monte.esta_vazio() else None
            }

        return stats

    def reset_jogo(self) -> None:
        self.deck.reset()
        for monte in self.montes_descarte.values():
            monte.cartas.clear()
