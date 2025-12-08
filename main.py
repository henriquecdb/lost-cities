import sys
from src.game.manager import GameFactory
from config.settings import AIConfig


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
    print("Tipos disponíveis: human, minimax, alphabeta")

    p_type = get_input(
        f"Digite o tipo do Jogador {player_num}: ",
        lambda x: x.lower() in ["human", "minimax", "alphabeta"],
        "Tipo inválido. Escolha entre: human, minimax, alphabeta"
    ).lower()

    depth = 1
    if p_type != "human":
        depth = int(get_input(
            f"Digite a profundidade da IA (1-5): ",
            lambda x: x.isdigit() and 1 <= int(x) <= 5,
            "Profundidade inválida. Digite um número entre 1 e 5."
        ))

    return p_type, depth


def main():
    print("=== Lost Cities - Configuração Interativa ===")

    try:
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
