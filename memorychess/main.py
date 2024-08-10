import pygame
import sys
import random
import time
import math
import os

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
WOOD_COLOR = (193, 154, 107)  # 木色背景
LIGHT_WOOD_COLOR = (218, 185, 145)  # 浅木色，用于棋盘格子

# 游戏设置
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GRID_SIZE = 6
PIECE_SIZE = 120
GRID_PADDING = 100
FONT_SIZE = 32

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("记忆棋游戏 - 6x6版本")


# 创建字体
def get_font():
    try:
        return pygame.font.Font("/Library/Fonts/Arial Unicode.ttf", FONT_SIZE)
    except:
        return pygame.font.Font(None, FONT_SIZE)


font = get_font()

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 加载音效
dice_sound = pygame.mixer.Sound(os.path.join(script_dir, "dice_roll.mp3"))
click_sound = pygame.mixer.Sound(os.path.join(script_dir, "click.mp3"))
remove_sound = pygame.mixer.Sound(os.path.join(script_dir, "remove.mp3"))


class ChessPiece:
    def __init__(self, color, x, y):
        self.color = color
        self.rect = pygame.Rect(x, y, PIECE_SIZE, PIECE_SIZE)
        self.visible = False
        self.reveal_time = 0
        self.removed = False

    def draw(self):
        # 绘制格子
        pygame.draw.rect(screen, LIGHT_WOOD_COLOR, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        if not self.removed:
            if self.visible:
                pygame.draw.rect(screen, self.color, self.rect.inflate(-4, -4))
            else:
                pygame.draw.rect(screen, GRAY, self.rect.inflate(-4, -4))

    def reveal(self):
        self.visible = True
        self.reveal_time = time.time()

    def hide(self):
        self.visible = False

    def remove(self):
        self.removed = True


class DiceButton:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = LIGHT_WOOD_COLOR
        self.rolling = False
        self.roll_start_time = 0
        self.roll_duration = 1  # 1 second roll animation
        self.result_color = None

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        if self.rolling:
            t = (time.time() - self.roll_start_time) / self.roll_duration
            angle = t * 2 * math.pi * 2  # Two full rotations
            x = self.rect.centerx + math.cos(angle) * 20
            y = self.rect.centery + math.sin(angle) * 20
            pygame.draw.circle(screen, BLACK, (int(x), int(y)), 10)
        elif self.result_color:
            pygame.draw.circle(
                screen, self.result_color, self.rect.center, self.rect.width // 2 - 10
            )

    def start_roll(self):
        self.rolling = True
        self.roll_start_time = time.time()
        self.result_color = None
        dice_sound.play()

    def stop_roll(self, color):
        self.rolling = False
        self.result_color = color


class MemoryChessGame:
    def __init__(self):
        self.colors = [
            RED,
            YELLOW,
            BLUE,
            GREEN,
            BLACK,
            (128, 0, 128),
        ]  # 将WHITE改为紫色
        self.color_names = {
            RED: "红",
            YELLOW: "黄",
            BLUE: "蓝",
            GREEN: "绿",
            BLACK: "黑",
            (128, 0, 128): "紫",
        }
        self.board = []
        self.initialize_board()
        self.player_score = 0
        self.computer_score = 0
        self.current_player = "player"
        self.dice_color = None
        self.selected_piece = None
        self.game_over = False
        self.dice_button = DiceButton(WINDOW_WIDTH - 600, WINDOW_HEIGHT // 2 - 100, 200)
        self.waiting_for_roll = True
        self.computer_memory = {}

    def initialize_board(self):
        colors = self.colors * 6
        random.shuffle(colors)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                x = GRID_PADDING + j * (PIECE_SIZE + 10)
                y = GRID_PADDING + i * (PIECE_SIZE + 10)
                self.board.append(ChessPiece(colors.pop(), x, y))

    def roll_dice(self):
        self.dice_color = random.choice(self.colors)
        self.dice_button.stop_roll(self.dice_color)

    def draw(self):
        screen.fill(WOOD_COLOR)
        for piece in self.board:
            piece.draw()

        # 显示分数
        player_text = font.render(f"玩家: {self.player_score}", True, BLACK)
        computer_text = font.render(f"电脑: {self.computer_score}", True, BLACK)
        screen.blit(player_text, (20, 20))
        screen.blit(computer_text, (WINDOW_WIDTH - 200, 20))

        # 显示当前玩家
        current_player_text = font.render(
            f"当前玩家: {'玩家' if self.current_player == 'player' else '电脑'}",
            True,
            BLACK,
        )
        screen.blit(current_player_text, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 60))

        if self.game_over:
            game_over_text = font.render("游戏结束!", True, BLACK)
            screen.blit(
                game_over_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20)
            )

        self.dice_button.draw()

        pygame.display.flip()

    def handle_click(self, pos):
        if self.game_over:
            return

        if self.current_player == "player":
            if self.waiting_for_roll and self.dice_button.rect.collidepoint(pos):
                self.dice_button.start_roll()
                self.waiting_for_roll = False
                return

            if not self.waiting_for_roll:
                for piece in self.board:
                    if piece.rect.collidepoint(pos) and not piece.removed:
                        click_sound.play()
                        self.selected_piece = piece
                        piece.reveal()
                        self.draw()
                        pygame.time.wait(500)  # 显示颜色0.5秒

                        if piece.color == self.dice_color:
                            remove_sound.play()
                            piece.remove()
                            self.player_score += 1
                            if self.player_score + self.computer_score == 36:
                                self.game_over = True
                            self.waiting_for_roll = True
                        else:
                            piece.hide()
                            self.current_player = "computer"
                            self.waiting_for_roll = True
                        break

    def computer_turn(self):
        if self.waiting_for_roll:
            self.dice_button.start_roll()
            self.waiting_for_roll = False
            return

        matching_pieces = [
            p
            for p in self.board
            if self.computer_memory.get(p) == self.dice_color and not p.removed
        ]
        if matching_pieces:
            piece = random.choice(matching_pieces)
        else:
            unknown_pieces = [
                p for p in self.board if p not in self.computer_memory and not p.removed
            ]
            if unknown_pieces:
                piece = random.choice(unknown_pieces)
            else:
                piece = random.choice([p for p in self.board if not p.removed])

        click_sound.play()
        piece.reveal()
        self.computer_memory[piece] = piece.color  # 记住这个棋子的颜色
        self.draw()
        pygame.time.wait(500)  # 显示颜色0.5秒

        if piece.color == self.dice_color:
            remove_sound.play()
            piece.remove()
            self.computer_score += 1
            if self.player_score + self.computer_score == 36:
                self.game_over = True
            self.waiting_for_roll = True
        else:
            piece.hide()
            self.current_player = "player"
            self.waiting_for_roll = True

    def play(self):
        clock = pygame.time.Clock()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    self.handle_click(event.pos)

            if self.dice_button.rolling:
                if (
                    time.time() - self.dice_button.roll_start_time
                    >= self.dice_button.roll_duration
                ):
                    self.roll_dice()
                    pygame.time.wait(500)  # 显示结果0.5秒

            if self.current_player == "computer" and not self.game_over:
                if self.waiting_for_roll:
                    self.computer_turn()
                elif not self.dice_button.rolling:
                    self.computer_turn()

            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    game = MemoryChessGame()
    game.play()
