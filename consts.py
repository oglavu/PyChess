
FPS = 60
SIDE = 100
TIME = 10 * 60 * FPS #u tickovima
TIMER_WIDTH = 2 * SIDE // 3
TIMER_HEIGHT = SIDE // 4
TIMER_BUFFER = SIDE // 30
RADIUS = SIDE // 5
CHECKED_RADIUS = SIDE // 2
WIDTH = SIDE * 8
HEIGHT = SIDE * 8
LETTER_BUFFER = SIDE // 30
HEADER = 2 * SIDE // 3
MARGIN = SIDE // 4
EATEN_SIZE = SIDE // 3

TIMER_X = MARGIN + WIDTH - TIMER_WIDTH
TIMER_B_Y = HEADER - MARGIN // 2 - TIMER_HEIGHT
TIMER_W_Y = HEADER + HEIGHT + MARGIN // 2

SMALL_FONT_SIZE = 20
FONT_SIZE = 20
BIG_FONT_SIZE = 40

WHITE = (255,255,255)
BLACK = (0,0,0)
BG_COLOR = (48,48,48)
CIRCLE_COLOR = (1, 1, 1)
DARK_TILE_COLOR = (90,175,90)
LIGHT_TILE_COLOR = (235,235,235)
CHECKED_COLOR = (255,0,0)
LAST_MOVE_COLOR = (255,255,0)
GRAY = (64, 64, 64)
LIGHT_GRAY = (96,96,96)
SURRENDER_FG_COLOR = (255,0,0)
SURRENDER_BG_COLOR = (128,0,0)
DRAW_FG_COLOR = (0,0,255)
DRAW_BG_COLOR = (0,0,128)

END_GAME_MENU_SIZE = 5*SIDE
END_GAME_MENU_SHADOW_OFFSET = SIDE//5
END_GAME_MENU_X = (WIDTH - END_GAME_MENU_SIZE)//2 + MARGIN
END_GAME_MENU_Y = (HEIGHT - END_GAME_MENU_SIZE)//2 + HEADER
ENG_GAME_MENU_SHADOW_X = 0
END_GAME_MENU_SHADOW_Y = 0

BG_BTN_COLOR = GRAY
FG_BTN_COLOR = LIGHT_GRAY
BTN_BORDER = 3
BTN_WIDTH = 150
BTN_HEIGHT = 50
BTN_TEXT_SIZE = 20

TRANSMISSION_DATA_SIZE = 8
DISCONNECT_MESSAGE = "!DISCONN"
REMATCH_MESSAGE = "!REMATCH"
DRAW_MESSAGE = "!DRAWASK"
DECLINE_MESSAGE = "!DECLINE"
SURRENDER_MESSAGE = "!SURREND"
HOST = "192.168.0.19"
LOG_FILE_NAME = "serverlog.txt"
PORT = 55555