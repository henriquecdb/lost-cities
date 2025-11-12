from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from config.settings import Colors, get_hand_positions
from src.game.manager import GameManager
from src.game.state import GameState
from src.models.carta import Carta


@dataclass(frozen=True)
class GameMove:
    tipo: str
    jogador: int
    carta_index: Optional[int] = None
    destino_cor: Optional[Tuple[int, int, int]] = None
    descricao: str = ""


@dataclass
class PendingMove:
    move: GameMove
    state: GameState
    mensagem: Optional[str]


@dataclass
class GameStateNode:
    state: GameState
    move: Optional[GameMove] = None
    mensagem: Optional[str] = None
    parent: Optional["GameStateNode"] = None
    depth: int = 0
    children: List["GameStateNode"] = field(default_factory=list)
    pending_moves: List[PendingMove] = field(default_factory=list)

    def describe(self) -> str:
        if self.move is None:
            return "Início"
        return self.move.descricao or self.move.tipo


class GameStateTree:
    def __init__(self, estado_inicial: GameState):
        self.root = GameStateNode(state=estado_inicial.clone())
        self.current = self.root
        self._prepare_pending_moves(self.root)

    def advance(self, move_index: int) -> GameStateNode:
        if not (0 <= move_index < len(self.current.pending_moves)):
            raise IndexError("Índice de movimento inválido")

        pending = self.current.pending_moves.pop(move_index)
        self.current.pending_moves.clear()

        novo_no = GameStateNode(
            state=pending.state,
            move=pending.move,
            mensagem=pending.mensagem,
            parent=self.current,
            depth=self.current.depth + 1
        )
        self.current.children.append(novo_no)
        self.current = novo_no
        self._prepare_pending_moves(self.current)
        return self.current

    def advance_to_child(self, child_index: int) -> GameStateNode:
        if not (0 <= child_index < len(self.current.children)):
            raise IndexError("Índice de filho inválido")

        self.current = self.current.children[child_index]
        self._prepare_pending_moves(self.current)
        return self.current

    def rewind(self) -> Optional[GameStateNode]:
        if self.current.parent is None:
            return None

        self.current = self.current.parent
        self._prepare_pending_moves(self.current)
        return self.current

    def get_pending_moves(self) -> List[GameMove]:
        return [pendente.move for pendente in self.current.pending_moves]

    def _prepare_pending_moves(self, node: GameStateNode) -> None:
        node.pending_moves.clear()

        turn_manager = node.state.turn_manager
        if turn_manager.jogo_terminado:
            return

        movimentos = self._enumerar_movimentos(node.state)
        if not movimentos:
            return

        for movimento in movimentos:
            if any(child.move == movimento for child in node.children):
                continue
            try:
                proximo_estado, mensagem = self._simular_movimento(
                    node.state, movimento)
            except ValueError:
                continue
            node.pending_moves.append(
                PendingMove(move=movimento, state=proximo_estado,
                            mensagem=mensagem)
            )

    def _enumerar_movimentos(self, state: GameState) -> List[GameMove]:
        movimentos: List[GameMove] = []
        turn_manager = state.turn_manager
        jogador = turn_manager.get_jogador_atual()

        if turn_manager.pode_jogar_carta(jogador):
            mao = state.get_player_hand(jogador)
            slots_por_cor = {
                slot.cor: slot for slot in state.get_player_slots(jogador)}
            nomes_cores = Colors.get_color_names()

            for indice, carta in enumerate(mao):
                slot_destino = slots_por_cor.get(carta.cor)
                if slot_destino and slot_destino.pode_aceitar_carta(carta, jogador):
                    descricao = (
                        f"Jogar {self._descricao_carta(carta)} em {nomes_cores.get(carta.cor, '?')}"
                    )
                    movimentos.append(
                        GameMove(
                            tipo="play",
                            jogador=jogador,
                            carta_index=indice,
                            destino_cor=carta.cor,
                            descricao=descricao
                        )
                    )

                descricao_descartar = (
                    f"Descartar {self._descricao_carta(carta)} em {nomes_cores.get(carta.cor, '?')}"
                )
                movimentos.append(
                    GameMove(
                        tipo="discard",
                        jogador=jogador,
                        carta_index=indice,
                        destino_cor=carta.cor,
                        descricao=descricao_descartar
                    )
                )

        elif turn_manager.pode_comprar_carta(jogador):
            if state.deck_manager.deck.tem_cartas():
                movimentos.append(
                    GameMove(
                        tipo="draw_deck",
                        jogador=jogador,
                        descricao="Comprar do deck"
                    )
                )

            nomes_cores = Colors.get_color_names()
            for cor, monte in state.deck_manager.montes_descarte.items():
                if not monte.esta_vazio():
                    descricao = f"Comprar do descarte {nomes_cores.get(cor, '?')}"
                    movimentos.append(
                        GameMove(
                            tipo="draw_discard",
                            jogador=jogador,
                            destino_cor=cor,
                            descricao=descricao
                        )
                    )

        return movimentos

    def _simular_movimento(self, state: GameState, movimento: GameMove) -> Tuple[GameState, Optional[str]]:
        estado_clone = state.clone()
        gerente = GameManager(estado_clone)
        mensagem = self._aplicar_movimento(gerente, movimento)
        mensagem_fim = gerente.checar_fim_de_jogo()
        if mensagem_fim:
            mensagem = f"{mensagem} {mensagem_fim}" if mensagem else mensagem_fim
        return gerente.state, mensagem

    def _aplicar_movimento(self, manager: GameManager, movimento: GameMove) -> Optional[str]:
        mensagem: Optional[str]

        if movimento.tipo == "play":
            carta = manager.get_hand(movimento.jogador)[movimento.carta_index]
            sucesso, mensagem = manager.tentar_jogar_em_expedicao(
                carta, movimento.destino_cor)
            if not sucesso:
                raise ValueError("Falha ao aplicar movimento de jogo de carta")
            self._reposicionar_mao(manager, movimento.jogador)

        elif movimento.tipo == "discard":
            carta = manager.get_hand(movimento.jogador)[movimento.carta_index]
            sucesso, mensagem = manager.tentar_descartar_carta(carta)
            if not sucesso:
                raise ValueError("Falha ao descartar carta no estado simulado")
            self._reposicionar_mao(manager, movimento.jogador)

        elif movimento.tipo == "draw_deck":
            sucesso, carta, mensagem = manager.comprar_carta_deck()
            if not sucesso:
                raise ValueError(
                    "Falha ao comprar carta do deck no estado simulado")
            self._reposicionar_mao(manager, movimento.jogador)

        elif movimento.tipo == "draw_discard":
            sucesso, carta, mensagem = manager.comprar_carta_descarte(
                movimento.destino_cor)
            if not sucesso:
                raise ValueError(
                    "Falha ao comprar do descarte no estado simulado")
            self._reposicionar_mao(manager, movimento.jogador)

        else:
            raise ValueError(
                f"Tipo de movimento desconhecido: {movimento.tipo}")

        return mensagem

    @staticmethod
    def _reposicionar_mao(manager: GameManager, jogador: int) -> None:
        posicoes = get_hand_positions(jogador)
        mao = manager.get_hand(jogador)
        for indice, carta in enumerate(mao):
            if indice < len(posicoes):
                x, y = posicoes[indice]
                carta.mover_para(x, y)

    @staticmethod
    def _descricao_carta(carta: Carta) -> str:
        if carta.tipo_carta == "investimento":
            return "INV"
        return str(carta.numero)

    def render_tree(self) -> str:
        linhas: List[str] = []
        self._render_node(self.root, linhas, prefix="", label="")
        return "\n".join(linhas)

    def _render_node(self, node: GameStateNode, linhas: List[str], prefix: str, label: str) -> None:
        marcador = "→" if node is self.current else "•"
        descricao = node.describe()
        status_turno = node.state.turn_manager.get_status_turno()
        fase = status_turno.get("fase")
        jogador = status_turno.get("jogador_atual")
        terminado = status_turno.get("jogo_terminado")
        vencedor = status_turno.get("vencedor")

        cabecalho = f"{prefix}{label}{marcador} {descricao} | J{jogador} - {fase}"
        if terminado:
            cabecalho += " (fim de jogo)"
            if vencedor is not None:
                cabecalho += f" vencedor: {vencedor}"
        linhas.append(cabecalho)

        if node.mensagem:
            linhas.append(f"{prefix}   mensagem: {node.mensagem}")

        for idx, child in enumerate(node.children):
            self._render_node(child, linhas, prefix=prefix +
                              "    ", label=f"[{idx}] ")

        if node is self.current and node.pending_moves:
            linhas.append(f"{prefix}   próximas jogadas:")
            for idx, pending in enumerate(node.pending_moves):
                linhas.append(f"{prefix}     ({idx}) {pending.move.descricao}")
