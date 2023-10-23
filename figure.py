"""
File containing class for each chess pieces.
Every particular piece class inherits from Figure.
"""

import pygame as pg
import consts

class Figure:
    def __init__(self, tile, color):
        self.letter_ord, self.num = self.tile_to_pos(tile)
        self.letter = tile[0]
        self.tile = tile
        self.color = color
        self.image = None
        self.where_to_go = []
        self.symb = None
        self.defending = []
        self.moved = False
        self.lastMove = self.tile
        self.value = 0

    # overloading == operator
    def __eq__(self, other):
        return self.tile == other.tile and self.color == other.color
    
    def __repr__(self):
        return f"PieceType: {self.symb}\nPieceColor: {self.color}\nPieceTile: {self.tile}\nPieceLast: {self.lastMove}\nPieceMoved: {self.moved}\n----"
        
    def tile_to_pos(self, tile):
        return (ord(tile[0]), int(tile[1]))

    def draw(self, screen : pg.Surface):
        screen.blit(self.image, self.get_image_pos())

    # return pos to blit image onto
    def get_image_pos(self):
        x, y= self.get_pos()
        return x + (consts.SIDE - self.image.get_width()) // 2, y + (consts.SIDE - self.image.get_width()) // 2

    # based on tile, return (x, y) of a piece
    def get_pos(self, tile = ""):
        if tile:
            return ((ord(tile[0]) - ord("a")) * consts.SIDE, (8 - int(tile[1])) * consts.SIDE)
        return ((self.letter_ord - ord("a")) * consts.SIDE, (8 - self.num) * consts.SIDE)

    # returns rect dot cords (A, B, C, D) of tile
    def get_rect(self, tile = ""):
        if tile:
            return (x := (ord(tile[0]) - ord("a")) * consts.SIDE), (y := (8 - int(tile[1])) * consts.SIDE), x + consts.SIDE, y + consts.SIDE
        return (x := (self.letter_ord - ord("a")) * consts.SIDE), (y := (8 - self.num) * consts.SIDE), x + consts.SIDE, y + consts.SIDE

    # draws transparent circle on a walkable tile
    def draw_circle(self, screen: pg.Surface, tile):
        x, y = self.get_pos(tile)
        plate = pg.Surface((consts.SIDE, consts.SIDE))
        plate.set_colorkey(consts.BLACK)
        plate.set_alpha(100)
        rel_x, rel_y = consts.SIDE // 2, consts.SIDE // 2
        pg.draw.circle(plate, consts.CIRCLE_COLOR, (rel_x, rel_y), consts.RADIUS)
        screen.blit(plate, (x, y))

    # draws transparent circles on all walkable tiles
    def draw_to_go(self, screen: pg.Surface):
        for tile in self.where_to_go:
            self.draw_circle(screen, tile)

    # if the piece is eaten, draw it scaled on a proper position
    def draw_eaten(self, screen: pg.Surface, order: int):
        img = pg.transform.scale(self.image, (consts.EATEN_SIZE, consts.EATEN_SIZE))
        x = consts.MARGIN + order * img.get_width() 
        if self.color == "white":
            y = consts.HEADER//2 - img.get_height() // 2
        else:
            y = consts.HEIGHT + 3 * consts.HEADER // 2 - img.get_height() // 2
        screen.blit(img, (x, y))

    # yellow highlight for previous move 
    def show_previous_move(self, screen: pg.Surface):
        plate = pg.Surface((consts.SIDE, consts.SIDE))
        plate.set_colorkey(consts.BLACK)
        plate.set_alpha(100)
        plate.fill(consts.LAST_MOVE_COLOR)
        screen.blit(plate, self.get_pos())
        screen.blit(plate, self.get_pos(self.lastMove))

    # checks if mouse over figure's tile   
    def isOverFig(self, pos) -> bool:
        x, y = pos
        x -= consts.MARGIN
        y -= consts.HEADER
        selfX, selfY, selfX_, selfY_ = self.get_rect()
        if selfX <= x <= selfX_ and selfY <= y <= selfY_:
            return True

    # checks if mouse is over walkable tile
    def isOverCircle(self, tile, pos) -> bool:
        x, y = pos
        x -= consts.MARGIN
        y -= consts.HEADER
        tileX, tileY, tileX_, tileY_ = self.get_rect(tile)
        if tileX <= x <=tileX_ and tileY <= y <= tileY_:
            return True

    # moving piece
    def move(self, tile, figures = None):
        lastTile = self.tile
        self.__init__(tile, self.color)
        self.moved = True
        self.lastMove = lastTile
            

class King(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/KING_{self.color.upper()}.png").convert_alpha())
        self.where_to_go = self.moving_pattern()
        self.symb = "K"
        self.checked = False
        self.mated = False

    def draw(self, screen: pg.Surface):
        # if king is checked draw red background behind him 
        if self.checked:
            x, y, _, _ = self.get_rect()
            plate = pg.Surface((consts.SIDE, consts.SIDE))
            plate.set_colorkey(consts.BLACK)
            plate.set_alpha(150)
            plate.fill(consts.CHECKED_COLOR)
            screen.blit(plate, (x, y))
        screen.blit(self.image, self.get_image_pos())

    # king's moving pattern
    def moving_pattern(self):
        # neighbouring colums
        letters = [chr(letter) for letter in range(self.letter_ord - 1, self.letter_ord + 2) if ord("a") <= letter <= ord("h")]
        # neighbouring rows
        nums = [num for num in range(self.num - 1, self.num + 2) if 1 <= num <= 8]
        return [tile for letter in letters for num in nums if (tile := f"{letter}{num}") != self.tile]
    
    # removes taken tiles from king's moving pattern
    def block_tiles(self, taken_tiles):
        self.where_to_go = self.moving_pattern()
        new = self.where_to_go.copy()
        for tile in self.where_to_go:
            if tile in taken_tiles.keys() and taken_tiles[tile] == self.color:
                self.defending.append(tile)
                new.remove(tile)
        self.where_to_go = new.copy()

    # adds tiles where castelling is possible
    def ableToCastle(self, rooks, attacked, taken_tiles):
        for rook in rooks:
            if not(rook.moved or self.moved):
                if not "c1" in attacked and rook.tile == "a1" and not "b1" in taken_tiles.keys() and not "c1" in taken_tiles.keys() and not "d1" in taken_tiles.keys(): self.where_to_go.append("c1")
                if not "g1" in attacked and rook.tile == "h1" and not "f1" in taken_tiles.keys() and not "g1" in taken_tiles.keys(): self.where_to_go.append("g1")
                if not "c8" in attacked and rook.tile == "a8" and not "b8" in taken_tiles.keys() and not "c8" in taken_tiles.keys() and not "d8" in taken_tiles.keys(): self.where_to_go.append("c8")
                if not "g8" in attacked and rook.tile == "h8" and not "f8" in taken_tiles.keys() and not "g8" in taken_tiles.keys(): self.where_to_go.append("g8")
    
    # remove attacked tiles from king's moving pattern
    def forbidden_tiles(self, attacked, defended):
        new = self.where_to_go.copy()
        for tile in self.where_to_go:
            if tile in attacked or tile in defended:
                new.remove(tile)
        self.where_to_go = new.copy()

    def check(self, attacked):
        return self.tile in attacked
    
    def move(self, tile, figures = []):
        lastTile = self.tile
        checked = self.checked
        self.__init__(tile, self.color)
        for rook in figures:
            if not (self.moved or rook.moved):
                if tile == "c1" and rook.tile == "a1": rook.move("d1")
                elif tile == "g1" and rook.tile == "h1": rook.move("f1")
                elif tile == "c8" and rook.tile == "a8": rook.move("d8")
                elif tile == "g8" and rook.tile == "h8": rook.move("f8")
        self.moved = True
        self.lastMove = lastTile
        self.checked = checked


class Bishop(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/Bishop_{self.color.upper()}.png").convert_alpha())
        self.where_to_go = self.moving_pattern()
        self.symb = "B"
        self.value = 3
    def moving_pattern(self):
        tiles = [f"{chr(letter)}{num}" for i in range(-7, 8) if ord("a") <= (letter := self.letter_ord + i) <= ord("h") and 1 <= (num := self.num + i) <= 8]
        tiles += [f"{chr(letter)}{num}" for i in range(-7, 8) if ord("a") <= (letter := self.letter_ord - i) <= ord("h") and 1 <= (num := self.num + i) <= 8]
        for _ in range(2):
            tiles.remove(f"{self.letter}{self.num}")
        return tiles

    def rate(self, tile):
        # / up 
        # \ down
        if self.num > int(tile[1]) and self.letter_ord > ord(tile[0]):
            return "up"
        elif self.num < int(tile[1]) and self.letter_ord < ord(tile[0]):
            return "up"

        return "down"

    def bishop_boa(self, anchor, tile, rate):
        if rate == "up":
            if int(anchor[1]) < int(tile[1]):
                return "after"
            elif int(anchor[1]) == int(tile[1]):
                return self.bishop_boa(anchor, self.tile, rate)
            return "before"
        else:
            if int(anchor[1]) < int(tile[1]):
                return "before"
            elif int(anchor[1]) == int(tile[1]):
                return self.bishop_boa(anchor, self.tile, rate)
            return "after"

    # checks if piece is defended by this bishop
    def clean_defending(self):
        new = self.defending.copy()
        for tile in self.defending:
            rate = self.rate(tile)
            bishop_boa = self.bishop_boa(tile, self.tile, rate)

            new = [tile_ for tile_ in new if (rate != self.rate(tile_)) or (bishop_boa == self.bishop_boa(tile, tile_, rate))]

        self.defending = new.copy()

    # removes tiles blocked by ally pieces from walkable tiles    
    def block_tiles(self, taken_tiles):
        self.defending = []
        self.where_to_go = self.moving_pattern()
        new = self.where_to_go.copy()

        for tile in self.where_to_go:
            if tile in taken_tiles.keys():
                rate = self.rate(tile)
                bishop_boa = self.bishop_boa(tile, self.tile, rate)

                new = [tile_ for tile_ in new if (rate != self.rate(tile_)) or (bishop_boa == self.bishop_boa(tile, tile_, rate))]

                if taken_tiles[tile] == self.color and tile in new:
                    self.defending.append(tile)
                    new.remove(tile)
        
        self.clean_defending()
        self.where_to_go = new.copy()


class Rook(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/Rook_{self.color.upper()}.png").convert_alpha())
        self.where_to_go = self.moving_pattern()
        self.symb = "R"
        self.moved = False
        self.value = 5
    def moving_pattern(self):
        tiles = [f"{letter}{self.num}" for letter in "abcdefgh"]
        tiles += [f"{self.letter}{num}" for num in range(1, 9)]
        for _ in range(2):
            tiles.remove(f"{self.letter}{self.num}")
        return tiles
    def rook_boa(self, tile):
        if self.num == int(tile[1]):
            if self.letter_ord > ord(tile[0]):
                return "before"
        else:
            if self.num > int(tile[1]):
                return "before"
        
        return "after"

    def boa_tile(self, tile, common, other):
        if common.isdigit():
            if ord(tile[0]) < ord(other):
                return "before"
        else:
            if int(tile[1]) < int(other):
                return "before"
        
        return "after"

    def clean_defending(self):
        new = self.defending.copy()
        for tile in self.defending:
            common = tile[0] if self.letter == tile[0] else tile[1]
            other = tile.replace(common, '')
            
            new = [tile_ for tile_ in new if (other in tile_) or self.boa_tile(tile_, common, other) != self.rook_boa(tile)]

        self.defending = new.copy()


    def block_tiles(self, taken_tiles):
        self.defending = []
        self.where_to_go = self.moving_pattern()
        new = self.where_to_go.copy()

        for tile in self.where_to_go:
            if tile in taken_tiles.keys():
                
                common = tile[0] if self.letter == tile[0] else tile[1]
                other = tile.replace(common, '')
                
                new = [tile_ for tile_ in new if (other in tile_) or self.boa_tile(tile_, common, other) != self.rook_boa(tile)]

                if taken_tiles[tile] == self.color and tile in new:
                    self.defending.append(tile)
                    new.remove(tile)

        self.clean_defending()
        self.where_to_go = new.copy()


class Knight(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/Knight_{self.color.upper()}.png").convert_alpha())
        self.where_to_go = self.moving_pattern()
        self.symb = "N"
        self.value = 3
    def moving_pattern(self):
        tiles = [f"{chr(letter_ord)}{num}" for letter_ord in range(self.letter_ord - 2, self.letter_ord + 3) for num in range(self.num - 2, self.num + 3) if chr(letter_ord) in "abcdefgh" and num in range(1,9) and self.distanced(letter_ord, num)]
        return tiles

    def distanced(self, letter_ord, num):
        if abs(letter_ord - self.letter_ord) == 2 and abs(num - self.num) == 1:
            return True
        if abs(letter_ord - self.letter_ord) == 1 and abs(num - self.num) == 2:
            return True

    def block_tiles(self, taken_tiles):
        self.where_to_go = self.moving_pattern()
        new = self.where_to_go.copy()
        for tile in self.where_to_go:
            if tile in taken_tiles.keys():
                if self.color == taken_tiles[tile]:
                    self.defending.append(tile)
                    new.remove(tile)
        self.where_to_go = new.copy()


class Pawn(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/Pawn_{self.color.upper()}.png").convert_alpha())
        self.where_to_go = self.moving_pattern()
        self.symb = ""
        self.value = 1
        self.lastMove = tile
    def moving_pattern(self):
        if self.color.lower() == "black":
            if self.num == 7:
                return [f"{self.letter}{i}" for i in range(6, 4, -1)]
            else:
                return [f"{self.letter}{self.num - 1}"]
        elif self.color.lower() == "white":
            if self.num == 2:
                return [f"{self.letter}{i}" for i in range(3,5)]
            else:
                return [f"{self.letter}{self.num + 1}"]

    def attack(self):
        step = -1 if self.color == "black" else 1
        tiles = []
        if self.letter != "a" and 1 <= self.num - 1 <= 8: 
            tiles.append(f"{chr(ord(self.letter) - 1)}{self.num + step}")
        if self.letter != "h" and 1 <= self.num - 1 <= 8: 
            tiles.append(f"{chr(ord(self.letter) + 1)}{self.num + step}")
        return tiles

    def en_passant(self, opponentMove, lastMove):
        if self.color == "white":
            if self.num == 5 and opponentMove[1] == "5" and (self.letter_ord == ord(opponentMove[0]) - 1 or self.letter_ord == ord(opponentMove[0]) + 1) and lastMove[1] == "7":
                self.where_to_go.append(f"{opponentMove[0]}{int(opponentMove[1]) + 1}")
                return f"{opponentMove[0]}{int(opponentMove[1]) + 1}"
        else:
            if self.num == 4 and opponentMove[1] == "4" and (self.letter_ord == ord(opponentMove[0]) - 1 or self.letter_ord == ord(opponentMove[0]) + 1) and lastMove[1] == "2":
                self.where_to_go.append(f"{opponentMove[0]}{int(opponentMove[1]) - 1}")
                return f"{opponentMove[0]}{int(opponentMove[1]) - 1}"
        return ""

    def block_tiles(self, taken_tiles):
        self.where_to_go = self.moving_pattern()
        new = [tile for tile in self.where_to_go if not tile in taken_tiles.keys()]

        step = -1 if self.color == "black" else 1

        if f"{self.letter}{self.num + step}" in taken_tiles.keys():
            new = []
        if (tile := f"{chr(ord(self.letter) - 1)}{self.num + step}") in taken_tiles.keys():
            if self.color != taken_tiles[tile]:
                new.append(tile)
        if (tile := f"{chr(ord(self.letter) + 1)}{self.num + step}") in taken_tiles.keys():
            if self.color != taken_tiles[tile]:
                new.append(tile)

        self.where_to_go = new.copy()

    def move(self, tile, figures = [], eaten = [], lastPiece = None):
        if lastPiece:
            if tile == self.en_passant(lastPiece.tile, lastPiece.lastMove):
                figures.remove(lastPiece)
                eaten[lastPiece.color].append(lastPiece)
                
        super().move(tile)
        if (self.num == 1 or self.num == 8) and figures:
            figures.remove(self)
            figures.append(Queen(self.tile, self.color))
        


class Queen(Figure):
    def __init__(self, tile, color):
        super().__init__(tile, color)
        self.image = pg.transform.scale2x(pg.image.load(f"images/Queen_{self.color.upper()}.png").convert_alpha())
        self.Rook = Rook(tile, color)
        self.Bishop = Bishop(tile, color)
        self.where_to_go = self.moving_pattern()
        self.symb = "Q"
        self.value = 9
    def moving_pattern(self):
        tiles = self.Bishop.moving_pattern()
        tiles += self.Rook.moving_pattern()
        return tiles
    def block_tiles(self, taken_tiles):
        self.Bishop.block_tiles(taken_tiles)
        self.Rook.block_tiles(taken_tiles)
        self.where_to_go = self.Bishop.where_to_go + self.Rook.where_to_go
        self.defending = self.Bishop.defending + self.Rook.defending
