from typing import Tuple, Dict

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 900
WINDOW_TITLE = "Lost Cities"
FPS = 60

DEFAULT_RANDOM_SEED = 21


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

    SLOT_Y_POSITION = 340


class LayoutConfig:
    PLAYER1_HAND_Y = WINDOW_HEIGHT - 200
    HAND_AREA_HEIGHT = 160
    HAND_AREA_MARGIN = 30

    PLAYER2_HAND_Y = 20

    SLOTS_CONTAINER_Y = 330
    SLOTS_CONTAINER_HEIGHT = SlotConfig.SLOT_HEIGHT + 40
    SLOTS_CONTAINER_MARGIN = 20

    TITLE_Y = 30
    INSTRUCTIONS_START_Y = WINDOW_HEIGHT - 30
    HAND_TITLE_OFFSET_Y = 10

    DISCARD_AREA_X = 310
    DISCARD_AREA_Y = 550
    DISCARD_PILE_SPACING = 130


class FontConfig:
    TITLE_SIZE = 36
    CARD_NUMBER_SIZE = 24
    SMALL_TEXT_SIZE = 18
    INSTRUCTION_SIZE = 16


class GameConfig:
    CARDS_PER_COLOR = 9
    TOTAL_NUMBERED_CARDS = len(Colors.get_available_colors()) * CARDS_PER_COLOR
    TOTAL_INVESTMENT_CARDS = len(
        Colors.get_available_colors()) * CardConfig.INVESTMENT_CARDS_PER_COLOR
    TOTAL_DECK_SIZE = TOTAL_NUMBERED_CARDS + TOTAL_INVESTMENT_CARDS

    NUM_PLAYERS = 2
    STARTING_HAND_SIZE = 8


def get_slot_positions() -> list:
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
