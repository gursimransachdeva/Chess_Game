import pygame

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("Mini Chess")

WHITE = (232, 235, 239)
BLACK = (125, 135, 150)
WHITE_PIECE = (255, 255, 255)
BLACK_PIECE = (0, 0, 0)

tile = 100
font = pygame.font.SysFont(None, 48)

def create_piece(col, row, color, team, type_):
    rect = pygame.Rect(0, 0, 50, 50)
    rect.center = (col * tile + tile // 2, row * tile + tile // 2)
    return {"rect": rect, "color": color, "team": team, "type": type_, "col": col, "row": row}

pieces = [
    create_piece(4, 7, WHITE_PIECE, "white", "Ki"),
    *[create_piece(col, 6, WHITE_PIECE, "white", "P") for col in range(8)],
    create_piece(4, 0, BLACK_PIECE, "black", "Ki"),
    *[create_piece(col, 1, BLACK_PIECE, "black", "P") for col in range(8)],
    create_piece(5, 7, WHITE_PIECE, "white", "B"),
    create_piece(5, 0, BLACK_PIECE, "black", "B"),
    create_piece(2, 0, BLACK_PIECE, "black", "B"),
    create_piece(2, 7, WHITE_PIECE, "white", "B"),
    create_piece(7, 7, WHITE_PIECE, "white", "R"),
    create_piece(7, 0, BLACK_PIECE, "black", "R"),
    create_piece(0, 0, BLACK_PIECE, "black", "R"),
    create_piece(0, 7, WHITE_PIECE, "white", "R"),
    create_piece(1, 0, BLACK_PIECE, "black", "Kn"),
    create_piece(1, 7, WHITE_PIECE, "white", "Kn"),
    create_piece(6, 7, WHITE_PIECE, "white", "Kn"),
    create_piece(6, 0, BLACK_PIECE, "black", "Kn"),
    create_piece(3, 7, WHITE_PIECE, "white", "Q"),
    create_piece(3, 0, BLACK_PIECE, "black", "Q")
]

turn = "white"
dragging = None
off_x = 0
off_y = 0

def piece_in_tile(col, row):
    for p in pieces:
        if p["col"] == col and p["row"] == row:
            return True
    return False

def enemy_in_tile(col, row, team):
    for p in pieces:
        if p["col"] == col and p["row"] == row and p["team"] != team:
            return p
    return None

def is_path_clear(piece, new_col, new_row):
    dx = new_col - piece["col"]
    dy = new_row - piece["row"]
    step_x = (dx > 0) - (dx < 0)
    step_y = (dy > 0) - (dy < 0)
    x, y = piece["col"] + step_x, piece["row"] + step_y
    while (x, y) != (new_col, new_row):
        if piece_in_tile(x, y):
            return False
        x += step_x
        y += step_y
    return True

def is_valid_move(piece, new_col, new_row):
    dx = new_col - piece["col"]
    dy = new_row - piece["row"]
    if piece["type"] == "Ki":
        return abs(dx) <= 1 and abs(dy) <= 1 and (dx != 0 or dy != 0)
    if piece["type"] == "P":
        direction = -1 if piece["team"] == "white" else 1
        start_row = 6 if piece["team"] == "white" else 1
        is_first_move = piece["row"] == start_row
        if dx == 0 and dy == direction and not piece_in_tile(new_col, new_row):
            return True
        if dx == 0 and dy == 2 * direction and is_first_move and not piece_in_tile(new_col, new_row) and not piece_in_tile(piece["col"], piece["row"] + direction):
            return True
        if abs(dx) == 1 and dy == direction and enemy_in_tile(new_col, new_row, piece["team"]):
            return True
    if piece["type"] == "Q":
        return (dx == 0 or dy == 0 or abs(dx) == abs(dy)) and (dx != 0 or dy != 0) and is_path_clear(piece, new_col, new_row)
    if piece["type"] == "B":
        return abs(dx) == abs(dy) and (dx != 0 or dy != 0) and is_path_clear(piece, new_col, new_row)
    if piece["type"] == "R":
        return (dx == 0 or dy == 0) and is_path_clear(piece, new_col, new_row)
    if piece["type"] == "Kn":
        return (abs(dx), abs(dy)) in [(2, 1), (1, 2)]
    return False

def is_king_in_check(king, team):
    for p in pieces:
        if p["team"] != team and is_valid_move(p, king["col"], king["row"]):
            return True
    return False

def can_king_escape(king, team):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            new_col = king["col"] + dx
            new_row = king["row"] + dy
            if 0 <= new_col < 8 and 0 <= new_row < 8:
                if not piece_in_tile(new_col, new_row) or enemy_in_tile(new_col, new_row, team):
                    if not is_king_in_check({"col": new_col, "row": new_row, "team": team, "type": "Ki"}, team):
                        return True
    return False

def can_block_or_capture_checking_piece(king, team):
    for p in pieces:
        if p["team"] == team and p["type"] != "Ki":
            for col in range(8):
                for row in range(8):
                    if is_valid_move(p, col, row):
                        captured = enemy_in_tile(col, row, team)
                        old_col, old_row = p["col"], p["row"]
                        p["col"], p["row"] = col, row
                        if captured:
                            pieces.remove(captured)

                        if not is_king_in_check(king, team):
                            p["col"], p["row"] = old_col, old_row
                            if captured:
                                pieces.append(captured)
                            return True

                        p["col"], p["row"] = old_col, old_row
                        if captured:
                            pieces.append(captured)
    return False

def is_checkmate(team):
    king = next((p for p in pieces if p["team"] == team and p["type"] == "Ki"), None)
    if not king or not is_king_in_check(king, team):
        return False
    if not can_king_escape(king, team) and not can_block_or_capture_checking_piece(king, team):
        return True
    return False

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for p in pieces:
                if p["rect"].collidepoint(event.pos) and p["team"] == turn:
                    dragging = p
                    off_x = p["rect"].x - event.pos[0]
                    off_y = p["rect"].y - event.pos[1]
                    break
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging:
                mouse_x, mouse_y = event.pos
                new_col = (mouse_x + off_x + 25) // tile
                new_row = (mouse_y + off_y + 25) // tile
                if 0 <= new_col < 8 and 0 <= new_row < 8 and is_valid_move(dragging, new_col, new_row):
                    old_col, old_row = dragging["col"], dragging["row"]
                    captured = enemy_in_tile(new_col, new_row, dragging["team"])
                    if captured:
                        pieces.remove(captured)

                    dragging["col"], dragging["row"] = new_col, new_row
                    dragging["rect"].center = (new_col * tile + tile // 2, new_row * tile + tile // 2)

                    your_king = next(p for p in pieces if p["team"] == dragging["team"] and p["type"] == "Ki")
                    if is_king_in_check(your_king, dragging["team"]):
                        dragging["col"], dragging["row"] = old_col, old_row
                        dragging["rect"].center = (old_col * tile + tile // 2, old_row * tile + tile // 2)
                        if captured:
                            pieces.append(captured)
                    else:
                        turn = "black" if turn == "white" else "white"
                else:
                    dragging["rect"].center = (dragging["col"] * tile + tile // 2, dragging["row"] * tile + tile // 2)
                dragging = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            dragging["rect"].x = event.pos[0] + off_x
            dragging["rect"].y = event.pos[1] + off_y

    for r in range(8):
        for c in range(8):
            color = WHITE if (r + c) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (c * tile, r * tile, tile, tile))

    for p in pieces:
        pygame.draw.rect(screen, p["color"], p["rect"])
        label = font.render(p["type"], True, (0, 0, 0) if p["color"] == WHITE_PIECE else (255, 255, 255))
        text_rect = label.get_rect(center=p["rect"].center)
        screen.blit(label, text_rect)

    turn_label = font.render("Turn: " + turn, True, (0, 0, 0))
    screen.blit(turn_label, (10, 10))

    if is_checkmate("white"):
        screen.blit(font.render("Black wins! Checkmate!", True, (255, 0, 0)), (300, 350))
    elif is_checkmate("black"):
        screen.blit(font.render("White wins! Checkmate!", True, (255, 0, 0)), (300, 350))

    pygame.display.flip()

pygame.quit()
