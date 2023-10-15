"""
Chess game built in Python 3.11 using Pygame 2.1.2. and sockets.
Game is playable with either opponent on the same PC or via local Wi-Fi network.

Modules:
*button.py - contains Button class that handles button behavour
*client.py - contains Client class that handles data exchange with server
*consts.py - contains all constants used in-game
*figure.py - contains a class for each of chess pieces
*game.py - main script that runs most of GUI and state-chaning
*pieces.py - initialieses all chess pieces
*server.py - handles data exchange between clients
*images - folder containing all images for chess pieces
*Helvetica.otf - font file
"""

try:
    import pygame as pg
except:
    import os
    os.system("pip install pygame")
    import pygame as pg
    
import consts
import pieces
import client
from figure import Figure, Queen
import button

class Game:
    def __init__(self):
        """
        Initialising main surfaces, fonts, buttons and variables
        """
        pg.init()

        self.screen = pg.display.set_mode((consts.WIDTH + 2 * consts.MARGIN, consts.HEIGHT + 2*consts.HEADER))
        self.board = pg.Surface((consts.WIDTH, consts.HEIGHT))
        self.board_overlay = pg.Surface((consts.WIDTH + 2 * consts.MARGIN, consts.HEIGHT + 2*consts.HEADER))
        self.menu = pg.Surface((consts.END_GAME_MENU_SIZE, consts.END_GAME_MENU_SIZE))
        self.menu_shadow = pg.Surface((consts.END_GAME_MENU_SIZE, consts.END_GAME_MENU_SIZE))
        self.menu_shadow.set_colorkey(consts.BLACK)
        self.menu_shadow.set_alpha(100)
        self.board_overlay.set_colorkey(consts.BLACK)
        self.board_overlay.set_alpha(200)

        pg.display.set_caption("Chess")
        pg.display.set_icon(pg.image.load("images\KNIGHT_WHITE.png"))

        # importing list of initialises pieces
        self.pieces = pieces.get_pieces()
        # dict containing list of eaten pieces from both black and white player
        self.eaten = {"white": [], "black": []}
        self.timer = {"white": consts.TIME, "black": consts.TIME}
        # active_piece is the currently selected piece
        # lastPiece is the piece that played the last move
        self.active_piece: Figure = None
        self.lastPiece: Figure = None
        self.turn = "white"

        self.mouse_pos = (0,0)
        # initialisation of all the buttons
        self.QuitWaitBtn = button.Button(consts.END_GAME_MENU_SIZE // 2, 4 * consts.END_GAME_MENU_SIZE // 5, "Quit")
        self.RematchBtn = button.Button(consts.END_GAME_MENU_SIZE // 4, 6 * consts.END_GAME_MENU_SIZE // 8, "Rematch")
        self.MainMenuBtn = button.Button(3 * consts.END_GAME_MENU_SIZE // 4, 6 * consts.END_GAME_MENU_SIZE // 8, "Main Menu")
        self.SettingsBtn = button.Button(consts.END_GAME_MENU_SIZE // 2, 4 * consts.END_GAME_MENU_SIZE // 5, "Settings")
        self.OpponentBtn = button.Button(consts.END_GAME_MENU_SIZE // 2, 2 * consts.END_GAME_MENU_SIZE // 5, "Opponent")
        self.OnlineBtn = button.Button(consts.END_GAME_MENU_SIZE // 2, 3 * consts.END_GAME_MENU_SIZE // 5, "Online")
        self.AcceptBtn = button.Button(3 * consts.END_GAME_MENU_SIZE // 4, 6 * consts.END_GAME_MENU_SIZE // 8, "Accept")
        self.RefuseBtn = button.Button(consts.END_GAME_MENU_SIZE // 4, 6 * consts.END_GAME_MENU_SIZE // 8, "Refuse")
        self.SurrenderWhiteBtn = button.Button(consts.TIMER_X-3*consts.BTN_WIDTH//8 - consts.TIMER_BUFFER, consts.TIMER_W_Y + consts.TIMER_HEIGHT//2, "Surrender", 
                                            consts.SURRENDER_FG_COLOR, consts.SURRENDER_BG_COLOR, 3 * consts.BTN_WIDTH//4, consts.TIMER_HEIGHT, 
                                            consts.SMALL_FONT_SIZE, button.Board(), False)
        self.SurrenderBlackBtn = button.Button(consts.TIMER_X-3*consts.BTN_WIDTH//8 - consts.TIMER_BUFFER, consts.TIMER_B_Y + consts.TIMER_HEIGHT//2, "Surrender",
                                            consts.SURRENDER_FG_COLOR, consts.SURRENDER_BG_COLOR, 3 * consts.BTN_WIDTH//4, consts.TIMER_HEIGHT, 
                                            consts.SMALL_FONT_SIZE, button.Board(), False)
        self.DrawWhiteBtn = button.Button(consts.TIMER_X-9*consts.BTN_WIDTH//8 - 3*consts.TIMER_BUFFER, consts.TIMER_W_Y + consts.TIMER_HEIGHT//2, "Draw", 
                                            consts.DRAW_FG_COLOR, consts.DRAW_BG_COLOR, 3 * consts.BTN_WIDTH//4, consts.TIMER_HEIGHT, 
                                            consts.SMALL_FONT_SIZE, button.Board(), False)
        self.DrawBlackBtn = button.Button(consts.TIMER_X-9*consts.BTN_WIDTH//8 - 3*consts.TIMER_BUFFER, consts.TIMER_B_Y + consts.TIMER_HEIGHT//2, "Draw",
                                            consts.DRAW_FG_COLOR, consts.DRAW_BG_COLOR, 3 * consts.BTN_WIDTH//4, consts.TIMER_HEIGHT, 
                                            consts.SMALL_FONT_SIZE, button.Board(), False)

        # initalisation of fonts
        self.sfont = pg.font.Font("Helvetica.otf", consts.SMALL_FONT_SIZE)
        self.font = pg.font.Font("Helvetica.otf", consts.FONT_SIZE)
        self.FONT = pg.font.Font("Helvetica.otf", consts.BIG_FONT_SIZE)

    def reset(self):
        """
        After finished match, resets all variables to default
        """
        self.pieces = pieces.get_pieces()
        self.eaten = {"white": [], "black": []}
        self.timer = {"white": consts.TIME, "black": consts.TIME}
        self.active_piece: Figure = None
        self.lastPiece: Figure = None
        self.end: bool = False
        self.drawn: bool = False
        self.turn: str = "white"
        self.SurrenderWhiteBtn.active: int = 1
        self.SurrenderBlackBtn.active: int = 0
        self.DrawBlackBtn.active: int = 0
        self.DrawWhiteBtn.active: int = 1

    def redraw(self):
        self.screen.fill(consts.BG_COLOR)
        self.draw_clocks()
        #managing to which player will which surr/draw button appear
        if self.singleplayer or self.client.color == "white":
            self.SurrenderWhiteBtn.draw(self.screen, self.mouse_pos)
            self.DrawWhiteBtn.draw(self.screen, self.mouse_pos)
        if self.singleplayer or self.client.color == "black":    
            self.SurrenderBlackBtn.draw(self.screen, self.mouse_pos)
            self.DrawBlackBtn.draw(self.screen, self.mouse_pos)
        #drawing tiles
        for i in range(8):
            for j in range(8):
                color = consts.LIGHT_TILE_COLOR if (i + j) % 2 == 0 else consts.DARK_TILE_COLOR
                pg.draw.rect(self.board, color, (i * consts.SIDE, j * consts.SIDE, consts.SIDE, consts.SIDE))

        #indexing tiles
        for i, letter in enumerate("abcdefgh"):
            letter_image = self.font.render(letter, True, consts.DARK_TILE_COLOR if i % 2 else consts.LIGHT_TILE_COLOR)
            self.board.blit(letter_image, ((i + 1) * consts.SIDE - letter_image.get_width() - consts.LETTER_BUFFER, consts.HEIGHT - letter_image.get_height() - consts.LETTER_BUFFER))

        for i, num in enumerate("12345678"):
            num_image = self.font.render(num, True, consts.DARK_TILE_COLOR if i % 2 else consts.LIGHT_TILE_COLOR)
            self.board.blit(num_image, (consts.LETTER_BUFFER, consts.LETTER_BUFFER + consts.HEIGHT - (i + 1) * consts.SIDE))

        #drawing eaten pieces
        for color in self.eaten:
            for order, piece in enumerate(self.eaten[color]):
                piece.draw_eaten(self.screen, order)

        #shading previous move
        if self.lastPiece:
            self.lastPiece.show_previous_move(self.board)

        #drawing all pieces
        for piece in self.pieces:
            piece.draw(self.board)

        #drawing allowed tiles for active piece
        if (self.active_piece and not self.online) or (self.online and self.active_piece and self.turn == self.client.color):
            self.active_piece.draw_to_go(self.board)

        self.screen.blit(self.board, (consts.MARGIN, consts.HEADER))

        #menus and screen shadowing
        if self.end or (self.online and not self.client.ready) or self.MainMenu or self.DrawMenu:
            self.board_overlay.fill(consts.BG_COLOR)
            self.screen.blit(self.board_overlay, (0, 0))

        if self.end:
            self.draw_end_menu()

        elif self.online and not self.client.ready:
            self.draw_wait_menu()

        elif self.MainMenu:
            self.draw_main_menu()

        elif self.DrawMenu:
            self.draw_draw_menu()

    def run(self):
        # updating available moves for every piece
        self.update(setup = True)

        run = True
        clock = pg.time.Clock()

        # state flags
        self.MainMenu = True
        self.WaitMenu = False
        self.DrawMenu = False
        self.singleplayer = False
        self.online = False
        self.onlineRematch = False
        self.end = False
        self.drawn = False
        self.discSign = False
        self.rematch_requested = False
        self.draw_requested = False
        self.connError = False

        self.client = client.Client()

        while run:
            clock.tick(consts.FPS)
            self.redraw()
            pg.display.update()
            self.mouse_pos = pg.mouse.get_pos()

            # handling clock ticking and time-out
            if self.timer[self.turn] == 0:
                self.end = True
                self.singleplayer = False
                self.online = False
            elif (self.singleplayer or 
                    self.client.ready and not self.end and not self.DrawMenu):
                self.timer[self.turn] -= 1

            # [online] if data received is tuple of 2 integers,
            # it is mouse pos of click from other player
            if self.client.ready and self.client.data:
                if isinstance(self.client.data, tuple):
                    self.mouse_pos = self.client.data
                    self.client.data = None
                    self.play()

            # handling different non-tuple messages
            if self.client.data == consts.DISCONNECT_MESSAGE:
                self.MainMenu = True
                self.end = False
                self.drawn = False
                self.online = False
                self.discSign = True
                self.client.disconnect()
                self.client.data = None
            elif self.client.data == consts.DECLINE_MESSAGE:
                self.draw_requested = False
                self.online = True
                self.DrawMenu = False
                self.client.data = None
            elif self.client.data == consts.SURRENDER_MESSAGE:
                self.online = False
                self.end = True
                self.client.data = None
            elif self.client.data == consts.REMATCH_MESSAGE:
                # [online] if rematch requested and rematch message received
                # that means both players want a rematch
                if self.rematch_requested:                   
                    self.reset()
                    self.client.ready = True
                    self.online = True
                    self.client.data = None
                    self.rematch_requested = False
                # [online] if player receives a rematch request,
                # rematch sign should appear
                else:
                    self.onlineRematch = True
                    self.client.data = None
            elif self.client.data == consts.DRAW_MESSAGE:
                #[online] look at rematch request above
                if self.draw_requested:
                    self.DrawMenu = False
                    self.online = False
                    self.client.data = None
                    self.end = True
                    self.drawn = True
                else:
                    self.DrawMenu = True
                    self.online = False
                    self.client.data = None
            
            # event and state handling
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if self.singleplayer: self.play()
                    elif self.MainMenu: self.main_menu_backend()
                    elif self.online and not self.client.ready: self.wait_menu_backend()
                    elif self.online and self.turn == self.client.color: self.play()
                    elif self.end: self.end_backend()
                    elif self.DrawMenu: self.draw_menu_backend()
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        run = False

        # before closing program disconnect from server 
        if self.client.ready or self.rematch_requested:
            self.client.disconnect()
        pg.quit()
        quit()

    def get_taken_tiles(self, color):
        """
        Returns list of tiles taken by both players, 
        doesn't count king tile if king color and color argument don't match
        """
        return {piece.tile : piece.color for piece in self.pieces if (piece.symb != "K") or (piece.symb == "K" and piece.color in color)}

    def get_attacked(self, color):
        """
        Returns a list of tiles occupiable by opponent,
        based on color
        """
        attacked = set()
        for piece in self.pieces:
            if piece.color != color:
                #pawn attacking pattern
                if piece.symb == "": attacked.update(piece.attack())
                #king attacking pattern
                elif piece.symb == "K": attacked.update(piece.moving_pattern())
                #attacking pattern of other pieces
                else: attacked.update(piece.where_to_go)
        return list(attacked)
    
    def get_defended(self, color):
        """
        Returns a list of player's figures that are defended
        by player's other figures
        """
        defended = set()
        for piece in self.pieces:
            if piece.defending and piece.color != color:
                defended.update(piece.defending)

        return list(defended)

    def update(self , setup = False):
        """
        Updates walkable tiles, en passant and casteling possibilites
        as well as eaten pieces

        If setup flag is True, dict eaten won't be traversed
        """
        for piece in self.pieces:
            piece.block_tiles(self.get_taken_tiles(piece.color))
            if piece.symb == "" and self.lastPiece and not setup:
                piece.en_passant(self.lastPiece.tile, self.lastPiece.lastMove)

        for ind in self.get_kings():
            self.pieces[ind].forbidden_tiles(self.get_attacked(self.pieces[ind].color), self.get_defended(self.pieces[ind].color))
            self.tryCasteling(self.pieces[ind])

        if setup == True: return

        for piece in self.pieces:
            if piece.tile == self.active_piece.tile and piece.color != self.active_piece.color:

                self.eaten[piece.color].append(piece)
                self.pieces.remove(piece)

                self.eaten[piece.color] = sorted(self.eaten[piece.color], key = lambda piece: piece.symb)
                self.eaten[piece.color] = sorted(self.eaten[piece.color], key = lambda piece: piece.value, reverse = True )
                break

    def save_king(self, ind: int):
        if self.active_piece.color == self.pieces[ind].color:
            #deep copying current state of variables
            locked_pieces = self.pieces.copy()
            locked_eaten_white = self.eaten["white"].copy()
            locked_eaten_black = self.eaten["black"].copy()
            possible_moves = []

            #establishing local variables
            locked = self.active_piece.where_to_go
            currentTile = self.active_piece.tile
            lastTile = self.active_piece.lastMove
            moved = self.active_piece.moved

            for tile in locked:
                
                self.active_piece.move(tile)
                self.update()

                for ind in self.get_kings():
                    if self.pieces[ind].color == self.active_piece.color:
                        break

                # if particular move doesn't cause check,
                # it's added to the possible_moves list
                # that eventually becomes viable tiles list
                if not self.pieces[ind].check(self.get_attacked(self.pieces[ind].color)):
                    possible_moves.append(tile)
                
            # restarting variables to default after search
            self.active_piece.move(currentTile)
            self.pieces = locked_pieces.copy()
            self.active_piece.moved = moved
            self.active_piece.lastMove = lastTile
            self.update()

            self.eaten["white"] = locked_eaten_white.copy()
            self.eaten["black"] = locked_eaten_black.copy()
            self.active_piece.where_to_go = possible_moves.copy()

    def isChecked(self):
        for i in self.get_kings():
            self.pieces[i].checked = self.pieces[i].check(self.get_attacked(self.pieces[i].color))
            if self.active_piece:
                self.save_king(i)

    def PosToTile(self, pos: tuple[int]):
        x, y = pos
        if (consts.MARGIN <= x <= consts.MARGIN + consts.WIDTH or
                    consts.HEADER <= y <= consts.HEADER + consts.HEIGHT):
            x -= consts.MARGIN
            y -= consts.HEADER
            return chr(ord('a') + (x//consts.SIDE)) + str(8 - y//consts.SIDE)
        return None

    def isMated(self):
        kings = self.get_kings()
        # finds endangered king
        for i in kings:
            if self.pieces[i].color == self.turn:
                break
        # if king isn't checked it can't be mated
        if not self.pieces[i].checked: return False
        #checks if saving king is possible by any other piece
        for piece in self.pieces:
            if piece.color == self.pieces[i].color:
                self.active_piece = piece
                self.save_king(i)
                if self.active_piece.where_to_go:
                    return False
        self.singleplayer = True
        return True

    def find_active_piece(self, pos) -> Figure | None:
        """
        Given (x, y) coordinates pos of mouse click,
        Returns an active piece or None if click was off-board
        """
        for piece in self.pieces:
            if piece.isOverFig(pos) and piece.color == self.turn: return piece

    def get_kings(self) -> list[Figure]:
        # returns list of king indeces
        return [i for i in range(len(self.pieces)) if self.pieces[i].symb == "K"]

    def get_rooks(self, color):
        # returns list of rook indeces
        return [piece for piece in self.pieces if piece.symb == "R" and piece.color == color]

    def tryCasteling(self, king: Figure):
        # checks if casteling is viable move
        if not king.checked:
            king.ableToCastle(self.get_rooks(king.color), self.get_attacked(king.color), self.get_taken_tiles(("white", "black")))

    def set_buttons(self):
        if self.singleplayer:
            self.SurrenderBlackBtn.active = (self.SurrenderBlackBtn.active + 1) % 2
            self.SurrenderWhiteBtn.active = (self.SurrenderBlackBtn.active + 1) % 2
            self.DrawBlackBtn.active = self.SurrenderBlackBtn.active
            self.DrawWhiteBtn.active = self.SurrenderWhiteBtn.active
        elif self.online:
            if self.turn == self.client.color and self.turn == "white":
                self.SurrenderWhiteBtn.active = 1
                self.SurrenderBlackBtn.active = 0
                self.DrawBlackBtn.active = 0
                self.DrawWhiteBtn.active = 1
            elif self.turn == self.client.color and self.turn == "black":
                self.SurrenderWhiteBtn.active = 0
                self.SurrenderBlackBtn.active = 1
                self.DrawBlackBtn.active = 1
                self.DrawWhiteBtn.active = 0
            else:
                self.SurrenderWhiteBtn.active = 0
                self.SurrenderBlackBtn.active = 0
                self.DrawBlackBtn.active = 0
                self.DrawWhiteBtn.active = 0
    
    def play(self):
        if self.DrawWhiteBtn.isOver(self.mouse_pos) or self.DrawBlackBtn.isOver(self.mouse_pos):
            if self.singleplayer:
                self.singleplayer = False
                self.DrawMenu = True
            elif self.online:
                self.client.request_draw()
                self.DrawMenu = True
                self.draw_requested = True
                self.online = False
        elif self.client.ready and self.turn == self.client.color and self.online:
            self.client.send(self.mouse_pos)

        if self.SurrenderWhiteBtn.isOver(self.mouse_pos) and (self.singleplayer or self.client.color == "white"):
            if self.online:
                self.client.declare_surrender()
            self.end = True
            self.turn = "white"
        elif self.SurrenderBlackBtn.isOver(self.mouse_pos) and (self.singleplayer or self.client.color == "black"):
            if self.online:
                self.client.declare_surrender()
            self.end = True
            self.turn = "black"
        elif self.active_piece:
            tile = self.PosToTile(self.mouse_pos)
            if tile in self.active_piece.where_to_go:
                if self.active_piece.symb == "K": 
                    self.active_piece.move(tile, self.get_rooks(self.active_piece.color))
                elif self.active_piece.symb == "":
                    self.active_piece.move(tile, self.pieces, self.eaten, self.lastPiece)
                else: 
                    self.active_piece.move(tile)
                self.lastPiece = self.active_piece
                
                self.turn = "black" if self.turn == "white" else "white"
                self.set_buttons()
                self.update()

                self.isChecked()
                self.end = self.isMated()

            self.active_piece = None
        else:
            self.active_piece = self.find_active_piece(self.mouse_pos)
            if self.active_piece: 
                self.isChecked()

        if self.end:
            self.singleplayer = False
            self.online = False
            self.SurrenderBlackBtn.active = False
            self.SurrenderWhiteBtn.active = False
            self.DrawWhiteBtn.active = False
            self.DrawBlackBtn.active = False



    # Menus
    def draw_main_menu(self):
        self.menu.fill(consts.WHITE)

        sign1 = self.FONT.render("Welcome!", True, consts.GRAY)
        X = consts.END_GAME_MENU_SIZE // 2 - sign1.get_width()//2
        Y = consts.END_GAME_MENU_SIZE // 5 - sign1.get_height()//2
        self.menu.blit(sign1, (X, Y))

        if self.discSign:
            sign2 = self.font.render("Opponent has disconnected", True, consts.GRAY)
            X = consts.END_GAME_MENU_SIZE // 2 - sign2.get_width()//2
            Y = consts.END_GAME_MENU_SIZE - 3*sign2.get_height()//2
            self.menu.blit(sign2, (X, Y))
        elif self.connError:
            sign2 = self.font.render("Couldn't establish connection with the server", True, consts.GRAY)
            X = consts.END_GAME_MENU_SIZE // 2 - sign2.get_width()//2
            Y = consts.END_GAME_MENU_SIZE - 3*sign2.get_height()//2
            self.menu.blit(sign2, (X, Y))

        self.OpponentBtn.draw(self.menu, self.mouse_pos)
        self.OnlineBtn.draw(self.menu, self.mouse_pos)
        self.SettingsBtn.draw(self.menu, self.mouse_pos)

        self.screen.blit(self.menu, (consts.END_GAME_MENU_X, consts.END_GAME_MENU_Y))

    def main_menu_backend(self):
        if self.OpponentBtn.isOver(self.mouse_pos):
            self.reset()
            self.singleplayer = True
            self.MainMenu = False
            self.online = False
            self.setup = True
            self.discSign = False
            self.connError = False
        elif self.OnlineBtn.isOver(self.mouse_pos):
            self.client.connect()
            self.discSign = False
            if self.client.signal:
                self.reset()
                self.MainMenu = False
                self.setup = True
                self.online = True
            else:
                self.connError = True
        elif self.SettingsBtn.isOver(self.mouse_pos):
            pass

    def draw_end_menu(self):
        self.menu_shadow.fill(consts.CIRCLE_COLOR)
        self.menu.fill(consts.WHITE)

        self.RematchBtn.draw(self.menu, self.mouse_pos)
        self.MainMenuBtn.draw(self.menu, self.mouse_pos)

        if self.drawn:
            sign = self.FONT.render("It's a draw!", True, consts.GRAY)
            X = consts.END_GAME_MENU_SIZE // 2 - sign.get_width() // 2
            Y = consts.END_GAME_MENU_SIZE // 5 - sign.get_height() // 2
            self.menu.blit(sign, (X, Y))
        else:
            loser = self.FONT.render(f"{self.turn[0].upper() + self.turn[1:]} has lost!", True, consts.GRAY)
            self.menu.blit(loser, ((consts.END_GAME_MENU_SIZE - loser.get_width()) // 2, 3 * consts.END_GAME_MENU_SIZE // 10 - loser.get_height() //2))
            
            color = "Black" if self.turn == "white" else "White"
            winner = self.FONT.render(f"{color} has won!", True, consts.GRAY)
            self.menu.blit(winner, ((consts.END_GAME_MENU_SIZE - winner.get_width()) // 2, consts.END_GAME_MENU_SIZE // 10 - winner.get_height() //2))
        
        if self.onlineRematch:
            sign = self.font.render("Opponent requests rematch", True, consts.GRAY)
            X = (consts.END_GAME_MENU_SIZE - sign.get_width())//2
            Y = (consts.END_GAME_MENU_SIZE - 3 * sign.get_height()//2)
            self.menu.blit(sign, (X, Y))

        self.screen.blit(self.menu_shadow, (consts.END_GAME_MENU_X - consts.END_GAME_MENU_SHADOW_OFFSET, consts.END_GAME_MENU_Y + consts.END_GAME_MENU_SHADOW_OFFSET))
        self.screen.blit(self.menu, (consts.END_GAME_MENU_X, consts.END_GAME_MENU_Y))

    def end_backend(self):
        if self.RematchBtn.isOver(self.mouse_pos) and not self.rematch_requested:
            if self.onlineRematch:
                self.reset()
                self.client.request_rematch()
                self.end = False
                self.online = True
                self.client.data = None
                self.onlineRematch = False
            elif self.client.ready and not self.rematch_requested:
                self.client.ready = False
                self.client.data = None
                self.client.request_rematch()
                self.rematch_requested = True
            else:
                self.reset()
                self.singleplayer = True
                self.end = False
                self.setup = True
        elif self.MainMenuBtn.isOver(self.mouse_pos):
            self.client.disconnect()
            self.MainMenu = True
            self.singleplayer = False
            self.end = False
            self.setup = True
            self.online = False

    def draw_wait_menu(self):
        self.menu.fill(consts.WHITE)

        sign = self.FONT.render("Waiting for opponent", True, consts.GRAY)
        X = consts.END_GAME_MENU_SIZE // 2 - sign.get_width()//2
        Y = consts.END_GAME_MENU_SIZE // 5 - sign.get_height()//2
        self.menu.blit(sign, (X, Y))

        self.QuitWaitBtn.draw(self.menu, self.mouse_pos)
        self.screen.blit(self.menu, (consts.END_GAME_MENU_X, consts.END_GAME_MENU_Y))

    def wait_menu_backend(self):
        if self.QuitWaitBtn.isOver(self.mouse_pos):
            self.MainMenu = True
            self.online = False
            self.client.disconnect()

    def get_clock(self, color):
        if (minutes := self.timer[color] // (60 * consts.FPS)) > 0:
            return str(minutes) + ":" + str((self.timer[color] % (60 * consts.FPS)) // consts.FPS).zfill(2)
        else:
            return str((self.timer[color] % (60 * consts.FPS)) // consts.FPS) + "." + str((self.timer[color] % consts.FPS) // 10)

    def draw_clocks(self):
        pg.draw.rect(self.screen, consts.LIGHT_TILE_COLOR, (consts.TIMER_X, consts.TIMER_B_Y, consts.TIMER_WIDTH, consts.TIMER_HEIGHT))
        pg.draw.rect(self.screen, consts.LIGHT_TILE_COLOR, (consts.TIMER_X, consts.TIMER_W_Y, consts.TIMER_WIDTH, consts.TIMER_HEIGHT))

        tw = self.sfont.render(self.get_clock("white"), 1, consts.GRAY)
        tb = self.sfont.render(self.get_clock("black"), 1, consts.GRAY)

        self.screen.blit(tw, (consts.TIMER_X + consts.TIMER_WIDTH - tw.get_width() - consts.TIMER_BUFFER, consts.TIMER_W_Y))
        self.screen.blit(tb, (consts.TIMER_X + consts.TIMER_WIDTH - tb.get_width() - consts.TIMER_BUFFER, consts.TIMER_B_Y))

    def draw_draw_menu(self):
        self.menu.fill(consts.WHITE)

        if self.draw_requested:
            sign1 = self.FONT.render("You have", True, consts.GRAY)
            X1 = consts.END_GAME_MENU_SIZE // 2 - sign1.get_width()//2
            Y1 = consts.END_GAME_MENU_SIZE // 5 - sign1.get_height()//2
            self.menu.blit(sign1, (X1, Y1))

            sign2 = self.FONT.render("offered a draw", True, consts.GRAY)
            X2 = consts.END_GAME_MENU_SIZE // 2 - sign2.get_width()//2
            Y2 = consts.END_GAME_MENU_SIZE // 5 + sign1.get_height()//2 + sign2.get_height()//2
            self.menu.blit(sign2, (X2, Y2))

            sign3 = self.font.render("Waiting for opponent", True, consts.GRAY)
            X3 = consts.END_GAME_MENU_SIZE // 2 - sign3.get_width() // 2
            Y3 = consts.END_GAME_MENU_SIZE - 3 * sign3.get_height() // 2
            self.menu.blit(sign3, (X3, Y3))

        else:
            sign1 = self.FONT.render("Opponent", True, consts.GRAY)
            X1 = consts.END_GAME_MENU_SIZE // 2 - sign1.get_width()//2
            Y1 = consts.END_GAME_MENU_SIZE // 5 - sign1.get_height()//2
            self.menu.blit(sign1, (X1, Y1))

            sign2 = self.FONT.render("has offered a draw", True, consts.GRAY)
            X2 = consts.END_GAME_MENU_SIZE // 2 - sign2.get_width()//2
            Y2 = consts.END_GAME_MENU_SIZE // 5 + sign1.get_height()//2 + sign2.get_height()//2
            self.menu.blit(sign2, (X2, Y2))

            self.RefuseBtn.draw(self.menu, self.mouse_pos)
            self.AcceptBtn.draw(self.menu, self.mouse_pos)

        

        
        self.screen.blit(self.menu, (consts.END_GAME_MENU_X, consts.END_GAME_MENU_Y))

    def draw_menu_backend(self):
        if self.AcceptBtn.isOver(self.mouse_pos) and not self.draw_requested:
            if self.client.ready:
                self.client.request_draw()
                self.DrawMenu = False
                self.end = True
                self.drawn = True
            else:
                self.end = True
                self.drawn = True
                self.DrawMenu = False
        elif self.RefuseBtn.isOver(self.mouse_pos) and not self.draw_requested:
            if self.client.ready:
                self.client.decline_draw()
                self.online = True
                self.DrawMenu = False
            else:
                self.singleplayer = True
                self.DrawMenu = False

if __name__ == "__main__":
    game = Game()
    game.run() 
        