# noqa: D401 - documentação reduzida e clara o suficiente
from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx

from src.game.state_tree import GameStateNode, GameStateTree


def render_state_tree(tree: GameStateTree, output_path: Path | str) -> Path:
    """Renderiza a GameStateTree com NetworkX + Matplotlib e salva em arquivo."""

    if tree.root is None:
        raise ValueError("Árvore de estados vazia")

    graph = nx.DiGraph()
    node_ids: Dict[int, str] = {}

    queue = deque([(tree.root, None, 0)])
    counter = 0
    max_layer = 0

    while queue:
        node, parent_id, layer = queue.popleft()
        max_layer = max(max_layer, layer)

        key = id(node)
        node_id = node_ids.get(key)
        if node_id is None:
            node_id = f"n{counter}"
            counter += 1
            node_ids[key] = node_id

            graph.add_node(
                node_id,
                label=_build_node_label(node),
                layer=layer,
                status=_node_status(tree, node),
            )

        if parent_id is not None:
            graph.add_edge(parent_id, node_id, pending=False)

        for child in node.children:
            queue.append((child, node_id, layer + 1))

    current_id = node_ids.get(id(tree.current))
    if current_id is not None and tree.current.pending_moves:
        for idx, pending in enumerate(tree.current.pending_moves):
            node_id = f"p{idx}"
            graph.add_node(
                node_id,
                label=f"{pending.move.descricao}\n(próxima)",
                layer=tree.current.depth + 1,
                status="pending",
            )
            graph.add_edge(current_id, node_id, pending=True)
            max_layer = max(max_layer, tree.current.depth + 1)

    pos = _compute_layout(graph)
    figura = plt.figure(figsize=_suggest_figsize(len(graph.nodes), max_layer))

    _draw_nodes(graph, pos)
    _draw_edges(graph, pos)
    _draw_labels(graph, pos)

    plt.axis('off')
    plt.tight_layout()

    destino = Path(output_path)
    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=220, bbox_inches='tight')
    plt.close(figura)
    return destino


def _build_node_label(node: GameStateNode) -> str:
    descricao = node.describe()
    status_turno = node.state.turn_manager.get_status_turno()
    fase = status_turno.get("fase")
    jogador = status_turno.get("jogador_atual")

    linhas = [f"{descricao}", f"J{jogador} - {fase}"]
    if node.mensagem:
        linhas.append(node.mensagem)
    if node.state.turn_manager.jogo_terminado:
        vencedor = status_turno.get("vencedor")
        complemento = "Empate" if vencedor == 0 else f"Venceu J{vencedor}"
        linhas.append(f"Fim de jogo: {complemento}")

    return "\n".join(linhas)


def _node_status(tree: GameStateTree, node: GameStateNode) -> str:
    if node is tree.current:
        return "current"
    if node.state.turn_manager.jogo_terminado:
        return "finished"
    return "visited"


def _compute_layout(graph: nx.DiGraph) -> Dict[str, tuple[float, float]]:
    try:
        from networkx.drawing.nx_pydot import graphviz_layout  # type: ignore

        return graphviz_layout(graph, prog="dot")
    except Exception:
        return nx.multipartite_layout(graph, subset_key="layer", align="vertical")


def _draw_nodes(graph: nx.DiGraph, pos: Dict[str, tuple[float, float]]) -> None:
    palettes = {
        "visited": {"color": "#90caf9", "size": 1600, "shape": "o"},
        "current": {"color": "#ffcc80", "size": 1800, "shape": "o"},
        "finished": {"color": "#f48fb1", "size": 1700, "shape": "o"},
        "pending": {"color": "#c5e1a5", "size": 1500, "shape": "s"},
    }

    for status, style in palettes.items():
        nodes = [n for n, data in graph.nodes(
            data=True) if data.get("status") == status]
        if nodes:
            nx.draw_networkx_nodes(
                graph,
                pos,
                nodelist=nodes,
                node_color=style["color"],
                node_size=style["size"],
                node_shape=style["shape"],
                linewidths=1.2,
                edgecolors="#37474f",
            )


def _draw_edges(graph: nx.DiGraph, pos: Dict[str, tuple[float, float]]) -> None:
    real_edges = [(u, v) for u, v, data in graph.edges(
        data=True) if not data.get("pending")]
    pending_edges = [(u, v) for u, v, data in graph.edges(
        data=True) if data.get("pending")]

    if real_edges:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=real_edges,
            arrows=True,
            width=1.6,
            arrowstyle='-|>',
            arrowsize=14,
            edge_color="#455a64",
        )

    if pending_edges:
        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=pending_edges,
            arrows=True,
            width=1.3,
            style='dashed',
            arrowstyle='-|>',
            arrowsize=12,
            edge_color="#66bb6a",
        )


def _draw_labels(graph: nx.DiGraph, pos: Dict[str, tuple[float, float]]) -> None:
    labels = {node: data.get("label", "")
              for node, data in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, pos, labels=labels,
                            font_size=8, font_weight='bold')


def _suggest_figsize(num_nodes: int, depth: int) -> tuple[float, float]:
    largura = max(8.0, min(20.0, num_nodes * 1.2))
    altura = max(6.0, min(16.0, (depth + 2) * 2.0))
    return largura, altura
