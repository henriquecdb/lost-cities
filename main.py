import sys
import time
from src.game.manager import GameFactory
from config.settings import AIConfig
from src.game.ai.q_learning_trainer import train_q_table
from src.game.ai.q_learning import DEFAULT_Q_TABLE_PATH


def get_input(prompt, validator, error_msg):
    while True:
        try:
            value = input(prompt).strip()
            if validator(value):
                return value
        except (ValueError, EOFError):
            pass
        print(error_msg)


def get_player_config(player_num):
    print(f"\n--- Configuração do Jogador {player_num} ---")
    tipos = ["human", "minimax", "alphabeta", "qlearning"]
    print("Tipos disponíveis: " + ", ".join(tipos))

    p_type = get_input(
        f"Digite o tipo do Jogador {player_num}: ",
        lambda x: x.lower() in tipos,
        "Tipo inválido. Escolha entre: " + ", ".join(tipos)
    ).lower()

    depth = 1
    if p_type != "human" and p_type != "qlearning":
        depth = int(get_input(
            "Digite a profundidade da IA (1-5): ",
            lambda x: x.isdigit() and 1 <= int(x) <= 5,
            "Profundidade inválida. Digite um número entre 1 e 5."
        ))

    return p_type, depth


def prompt_int(prompt: str, default: int, min_value: int = 1, max_value: int | None = None) -> int:
    while True:
        raw = input(f"{prompt} (padrão={default}): ").strip()
        if not raw:
            return default
        if raw.lstrip("-").isdigit():
            value = int(raw)
            if value < min_value:
                print(f"Valor precisa ser >= {min_value}")
                continue
            if max_value is not None and value > max_value:
                print(f"Valor precisa ser <= {max_value}")
                continue
            return value
        print("Digite um número inteiro válido.")


def maybe_run_training():
    resposta = get_input(
        "Deseja treinar o Q-Learning agora? (s/n): ",
        lambda x: x.lower() in {"s", "n"},
        "Responda com 's' ou 'n'."
    ).lower()

    if resposta != "s":
        return

    episodes = prompt_int("Quantidade de episódios", 50, 1)
    opponent = get_input(
        "Oponente de treino (minimax/alphabeta): ",
        lambda x: x.lower() in {"minimax", "alphabeta"},
        "Escolha entre minimax ou alphabeta"
    ).lower()
    opponent_depth = prompt_int("Profundidade do oponente", 1, 1, 5)

    seed_input = input("Seed inicial (Enter para padrão=1): ").strip()
    seed = int(seed_input) if seed_input.isdigit() else 1

    lock_seed = get_input(
        "Manter a mesma seed em todos os episódios? (s/n): ",
        lambda x: x.lower() in {"s", "n"},
        "Responda com 's' ou 'n'."
    ).lower() == "s"

    print("\nIniciando treino Q-Learning...\n")
    start = time.time()
    train_q_table(
        episodes=episodes,
        opponent=opponent,
        opponent_depth=opponent_depth,
        seed=seed,
        lock_seed=lock_seed,
    )
    duration = time.time() - start
    print(
        f"Treino concluído em {duration:.2f}s. Tabela salva em {DEFAULT_Q_TABLE_PATH}.\n"
    )


def main():
    print("=== Lost Cities - Configuração Interativa ===")

    try:
        maybe_run_training()

        p1_type, p1_depth = get_player_config(1)
        p2_type, p2_depth = get_player_config(2)

        print("\n--- Configurações Globais ---")
        delay = float(get_input(
            "Digite o delay da IA em segundos (ex: 0.5): ",
            lambda x: x.replace('.', '', 1).isdigit() and float(x) >= 0,
            "Valor inválido. Digite um número positivo."
        ))

        seed_input = input(
            "Digite a semente aleatória (pressione Enter para padrão=1): ").strip()
        seed = int(seed_input) if seed_input.isdigit() else 1

        AIConfig.DEFAULT_DELAY = delay

        print("\nIniciando o jogo...")
        print(f"P1: {p1_type} (Depth: {p1_depth})")
        print(f"P2: {p2_type} (Depth: {p2_depth})")
        print(f"Delay: {delay}s, Seed: {seed}")
        print("===========================================\n")

        jogo = GameFactory.criar_jogo_customizado(
            seed=seed,
            p1_type=p1_type,
            p1_depth=p1_depth,
            p2_type=p2_type,
            p2_depth=p2_depth
        )
        jogo.executar()

    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Jogo finalizado.")


if __name__ == "__main__":
    main()
