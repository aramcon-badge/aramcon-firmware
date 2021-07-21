import displayio
import math
import time
import random
from arambadge import badge
from adafruit_display_shapes.rect import Rect

PLAYER_SPEED = 10
BOT_SPEED = 7
REDUCE_FACTOR = 5
CLOSE_FACTOR = 7

class PongApp:    
    def __init__(self):
        # Initilize objects bounding box
        self.bot = (10, 40, 20, badge.display.height-2*40)
        self.player = (badge.display.width-10-20, 40, 20, badge.display.height-2*40)
        self.pong = (badge.display.width/2-4, badge.display.height/2-4, 8, 8)
        self.direction = None
        self.bot_turn = True
        self.speed = 15
        self.random_direction([2,3])
    
    @staticmethod
    def get_rectangle(x, y, width, height):
        return Rect(int(x), int(y), int(width), int(height), fill=0xff)

    def render(self):
        group = displayio.Group()
        background = Rect(0, 0, badge.display.width, badge.display.height, fill=0xffffff)
        player_rect = PongApp.get_rectangle(*self.player)
        bot_rect = PongApp.get_rectangle(*self.bot)
        pong_rect = PongApp.get_rectangle(*self.pong)
        group.append(background)
        group.append(player_rect)
        group.append(bot_rect)
        group.append(pong_rect)
        return group
    
    def random_direction(self, quarters):
        direction = random.randint(0, 45)
        quarter = random.choice(quarters)
        if quarter == 1:
            self.direction = direction
        elif quarter == 2:
            self.direction = 180 - direction
        elif quarter == 3:
            self.direction = 180 + direction
        else:
            self.direction = 360 - direction
    
    def move_ball(self):
        if 0 <= self.direction <= 90:
            dy = -1 * self.speed * math.sin(math.radians(self.direction))
            dx = self.speed * math.cos(math.radians(self.direction))
        elif 90 < self.direction <= 180:
            direction = 180 - self.direction
            dy = -1 * self.speed * math.sin(math.radians(direction))
            dx = -1 * self.speed * math.cos(math.radians(direction))
        elif 180 < self.direction <= 270:
            direction = self.direction - 180
            dy = self.speed * math.sin(math.radians(direction))
            dx = -1 * self.speed * math.cos(math.radians(direction))
        else:
            direction = 360 - self.direction
            dy = self.speed * math.sin(math.radians(direction))
            dx = self.speed * math.cos(math.radians(direction))
        self.pong = (self.pong[0] + dx, self.pong[1] + dy, self.pong[2], self.pong[3])

    def move_bot(self):
        mid_ball = self.pong[1] + self.pong[3] / 2
        mid_bot = self.bot[1] + self.bot[3] / 2
        if mid_ball > mid_bot and self.bot[1] + self.bot[3] < badge.display.height:
            self.bot = (self.bot[0], self.bot[1] + BOT_SPEED, self.bot[2], self.bot[3])
        elif mid_ball < mid_bot and self.bot[1] > 0:
            self.bot = (self.bot[0], self.bot[1] - BOT_SPEED, self.bot[2], self.bot[3])

    def make_harder(self):
        # Reduce height
        if self.bot[3] > REDUCE_FACTOR:
            self.bot = (self.bot[0], self.bot[1] + REDUCE_FACTOR/2, self.bot[2], self.bot[3] - REDUCE_FACTOR)
            self.player = (self.player[0], self.player[1] + REDUCE_FACTOR/2, self.player[2], self.player[3] - REDUCE_FACTOR)

        # Move closer
        self.bot = (self.bot[0] + CLOSE_FACTOR, self.bot[1], self.bot[2], self.bot[3])
        self.player = (self.player[0] - CLOSE_FACTOR, self.player[1], self.player[2], self.player[3])

    
    def handle_collision(self):
        x_ball, y_ball, width_ball, height_ball = self.pong
        x_player, y_player, width_player, height_player = self.player
        x_bot, y_bot, width_bot, height_bot = self.bot

        x_end_ball = x_ball + width_ball
        y_end_ball = y_ball + height_ball
        x_end_player = x_player + width_player
        y_end_player = y_player + height_player
        x_end_bot = x_bot + width_bot
        y_end_bot = y_bot + height_bot

        collision = False

        # Player collision
        if not self.bot_turn:
            if y_end_ball > y_player and y_ball < y_end_player:
                if x_ball < x_player and x_end_ball > x_player:
                    collision = True
                    self.make_harder()
                elif x_ball > x_player and x_end_ball < x_end_player:
                    collision = True
                    self.make_harder()
                elif x_ball < x_end_ball and x_end_ball > x_end_player:
                    collision = True
                    self.make_harder()
        
        # Bot collision
        if self.bot_turn:
            if y_end_ball > y_bot and y_ball < y_end_bot:
                if x_ball < x_end_bot and x_end_ball > x_end_bot:
                    collision = True
                elif x_ball > x_bot and x_end_ball < x_end_bot:
                    collision = True
                elif x_ball < x_bot and x_end_ball > x_bot:
                    collision = True
        
        if collision:
            quarter = (self.direction // 90) + 1
            if quarter == 1 and not self.bot_turn:
                quarter = 2
            elif quarter == 2 and self.bot_turn:
                quarter = 1
            elif quarter == 3 and self.bot_turn:
                quarter = 4
            elif quarter == 4 and not self.bot_turn:
                quarter = 3
            self.random_direction(quarters=[quarter])
            self.bot_turn = not self.bot_turn
        
        # Wall collisions
        if y_ball <= 0:
            quarter = (self.direction // 90) + 1
            if quarter == 1:
                self.direction = (-self.direction) % 360
            elif quarter == 2:
                self.direction += (180 - self.direction) * 2
        
        if y_end_ball >= badge.display.height:
            quarter = (self.direction // 90) + 1
            if quarter == 3:
                self.direction -= (self.direction - 180) * 2
            elif quarter == 4:
                self.direction = 360 - self.direction
    
    def check_end_game(self):
        if self.pong[0] + self.pong[2] < 0:
            # Player win
            self.running = False
            for _ in range(3):
                for i in range(4):
                    badge.pixels[i] = (0, 255, 0)
                time.sleep(0.3)
                for i in range(4):
                    badge.pixels[i] = (0, 0, 0)
                time.sleep(0.1)
        if self.pong[0] > badge.display.width:
            # Bot win
            self.running = False
            for _ in range(3):
                badge.vibration = True
                time.sleep(0.3)
                badge.vibration = False
                time.sleep(0.1)


    def process_input(self):
        buttons = badge.gamepad.get_pressed()
        if buttons & badge.BTN_UP:
            if self.player[1] > 0:
                self.player = (self.player[0], self.player[1] - PLAYER_SPEED, self.player[2], self.player[3])
        if buttons & badge.BTN_DOWN:
            if self.player[1] + self.player[3] < badge.display.height:
                self.player = (self.player[0], self.player[1] + PLAYER_SPEED, self.player[2], self.player[3])
        if buttons & badge.BTN_ACTION:
            self.running = False

    def run(self):
        display = badge.display
        display.push_mode(display.MODE_QUICKER)
        self.running = True

        while self.running:
            self.move_ball()
            self.move_bot()
            self.handle_collision()
            while display.time_to_refresh > 0:
                pass
            self.process_input()
            group = self.render()
            display.show(group)
            display.refresh()
            self.check_end_game()
        display.pop_mode()

def main():
    return PongApp()
