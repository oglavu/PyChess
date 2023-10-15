import figure

def get_pieces() -> list[figure.Figure]:
    Rook1 = figure.Rook("a8", "black")
    Rook2 = figure.Rook("h8", "black")
    Knight1 = figure.Knight("b8", "black")
    Knight2 = figure.Knight("g8", "black")
    Bishop1 = figure.Bishop("c8", "black")
    Bishop2 = figure.Bishop("f8", "black")
    King = figure.King("e8", "black")
    Queen = figure.Queen("d8", "black")

    pieces = [Rook1, Rook2, Bishop1, Bishop2, Knight1, Knight2, King, Queen]

    for i in "abcdefgh":
        Pawn = figure.Pawn(f"{i}7", "black")
        pieces.append(Pawn)

    Rook1 = figure.Rook("a1", "white")
    Rook2 = figure.Rook("h1", "white")
    Knight1 = figure.Knight("b1", "white")
    Knight2 = figure.Knight("g1", "white")
    Bishop1 = figure.Bishop("c1", "white")
    Bishop2 = figure.Bishop("f1", "white")
    King = figure.King("e1", "white")
    Queen = figure.Queen("d1", "white")

    pieces += [Rook1, Rook2, Bishop1, Bishop2, Knight1, Knight2, King, Queen]

    for i in "abcdefgh":
        Pawn = figure.Pawn(f"{i}2", "white")
        pieces.append(Pawn)

    return pieces