from src.game.manager import GameFactory
import sys
import os


def main():
    try:
        jogo = GameFactory.criar_jogo_padrao()
        jogo.executar()
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Jogo finalizado.")


if __name__ == "__main__":
    main()
