from typing import Tuple, Dict

WINDOW_WIDTH = 1200  # 1000
WINDOW_HEIGHT = 900  # 700
WINDOW_TITLE = "Lost Cities"
FPS = 60


class Colors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (80, 80, 80)
    LIGHT_GRAY = (200, 200, 200)
    LIGHT_GREEN = (150, 255, 150)
    LIGHT_RED = (220, 220, 220)

    YELLOW = (250, 200, 50)
    BLUE = (50, 100, 220)
    WHITE_CARD = (220, 220, 220)
    GREEN = (50, 180, 50)
    RED = (220, 50, 50)

    @classmethod
    def get_available_colors(cls) -> list:
        return [cls.YELLOW, cls.BLUE, cls.WHITE_CARD, cls.GREEN, cls.RED]

    @classmethod
    def get_color_names(cls) -> Dict[Tuple[int, int, int], str]:
        return {
            cls.YELLOW: "Amarela",
            cls.BLUE: "Azul",
            cls.WHITE_CARD: "Branca",
            cls.GREEN: "Verde",
            cls.RED: "Vermelha"
        }


class CardConfig:
    HAND_CARD_WIDTH = 60
    HAND_CARD_HEIGHT = 90

    SLOT_CARD_WIDTH = 55
    SLOT_CARD_HEIGHT = 85

    MIN_CARD_NUMBER = 2
    MAX_CARD_NUMBER = 10

    HAND_SIZE = 8

    INVESTMENT_CARDS_PER_COLOR = 3

    HAND_CARD_SPACING = 15


class SlotConfig:
    SLOT_WIDTH = 80
    SLOT_HEIGHT = 120

    SLOT_SPACING = 30

    SLOT_Y_POSITION = 350


class LayoutConfig:
    PLAYER1_HAND_Y = WINDOW_HEIGHT - 200  # 700
    HAND_AREA_HEIGHT = 160
    HAND_AREA_MARGIN = 30

    PLAYER2_HAND_Y = 20

    SLOTS_CONTAINER_Y = 330
    SLOTS_CONTAINER_HEIGHT = SlotConfig.SLOT_HEIGHT + 40
    SLOTS_CONTAINER_MARGIN = 20

    TITLE_Y = 30
    INSTRUCTIONS_START_Y = WINDOW_HEIGHT - 30
    HAND_TITLE_OFFSET_Y = 10

    DISCARD_AREA_X = 250
    DISCARD_AREA_Y = 550
    DISCARD_PILE_SPACING = 130


class FontConfig:
    TITLE_SIZE = 36
    CARD_NUMBER_SIZE = 24
    SMALL_TEXT_SIZE = 18
    INSTRUCTION_SIZE = 16


class VisualConfig:
    NORMAL_BORDER_WIDTH = 2
    HIGHLIGHTED_BORDER_WIDTH = 4
    DRAGGING_BORDER_WIDTH = 3

    SHADOW_OFFSET = 3
    SHADOW_COLOR = (100, 100, 100)

    HIGHLIGHT_COLOR_OFFSET = 50


class GameConfig:
    CARDS_PER_COLOR = 9
    INVESTMENT_CARDS_PER_COLOR = 3
    TOTAL_NUMBERED_CARDS = len(
        Colors.get_available_colors()) * CARDS_PER_COLOR  # 45 cartas
    TOTAL_INVESTMENT_CARDS = len(
        Colors.get_available_colors()) * INVESTMENT_CARDS_PER_COLOR  # 15 cartas
    TOTAL_DECK_SIZE = TOTAL_NUMBERED_CARDS + TOTAL_INVESTMENT_CARDS  # 60 cartas

    NUM_PLAYERS = 2
    STARTING_HAND_SIZE = 8

    # Pontuação
    INVESTMENT_MULTIPLIER = 2  # Cada carta de investimento multiplica por 2
    MINIMUM_EXPEDITION_COST = 20  # Custo base para começar expedição
    BONUS_8_OR_MORE_CARDS = 20  # Bônus por 8+ cartas na expedição

    REQUIRE_ASCENDING_ORDER = True  # Cartas devem ser jogadas em ordem crescente
    ALLOW_GAPS_IN_SEQUENCE = False  # Não pode pular números
    INVESTMENT_CARDS_FIRST = True   # Cartas de investimento devem ser jogadas primeiro


class ControlConfig:
    QUIT_KEY = "K_ESCAPE"
    NEW_CARDS_KEY = "K_r"

    LEFT_MOUSE_BUTTON = 1
    RIGHT_MOUSE_BUTTON = 3


class DebugConfig:
    SHOW_COLLISION_BOXES = False
    PRINT_CARD_MOVEMENTS = True
    SHOW_FPS = False
    LOG_GAME_EVENTS = True


def get_slot_positions() -> list:
    """
    Calcula e retorna as posições dos slots baseado nas configurações.

    Returns:
        list: Lista de tuplas (x, y) para posição de cada slot
    """
    colors = Colors.get_available_colors()
    num_slots = len(colors)

    total_width = (SlotConfig.SLOT_WIDTH * num_slots) + \
        (SlotConfig.SLOT_SPACING * (num_slots - 1))
    start_x = (WINDOW_WIDTH - total_width) // 2

    positions = []
    for i in range(num_slots):
        x = start_x + (i * (SlotConfig.SLOT_WIDTH + SlotConfig.SLOT_SPACING))
        y = SlotConfig.SLOT_Y_POSITION
        positions.append((x, y))

    return positions


def get_hand_positions(player: int = 1) -> list:
    """
    Calcula e retorna as posições das cartas na mão baseado nas configurações.

    Args:
        player: 1 para jogador 1 (embaixo), 2 para jogador 2 (em cima)

    Returns:
        list: Lista de tuplas (x, y) para posição de cada carta na mão
    """
    positions = []
    total_width = CardConfig.HAND_SIZE * \
        (CardConfig.HAND_CARD_WIDTH + CardConfig.HAND_CARD_SPACING) - \
        CardConfig.HAND_CARD_SPACING
    start_x = (WINDOW_WIDTH - total_width) // 2

    if player == 1:
        y = LayoutConfig.PLAYER1_HAND_Y + 50
    else:
        y = LayoutConfig.PLAYER2_HAND_Y + 50

    for i in range(CardConfig.HAND_SIZE):
        x = start_x + (i * (CardConfig.HAND_CARD_WIDTH +
                       CardConfig.HAND_CARD_SPACING))
        positions.append((x, y))

    return positions


def get_discard_positions() -> list:
    positions = []
    colors = Colors.get_available_colors()

    for i, _ in enumerate(colors):
        x = LayoutConfig.DISCARD_AREA_X + \
            (i * LayoutConfig.DISCARD_PILE_SPACING)
        y = LayoutConfig.DISCARD_AREA_Y
        positions.append((x, y))

    return positions
