import displayio
import math
import time
import random
from arambadge import badge
from adafruit_display_shapes.rect import Rect

class PongApp:    
    def __init__(self):
        # Initilize objects bounding box
        self.bot = (15, 15, 10, badge.display.height-15-15)
        self.player = (badge.display.width-15-10, 15, 10, badge.display.height-15-15)
        self.pong = (badge.display.width/2-4, badge.display.height/2-4, 8, 8)
        self.direction = None
        self.bot_turn = True
        self.speed = 8
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
        self.direction = random.randint(0, 90) * random.choice(quarters)
    
    def move_ball(self):
        if 0 <= self.direction <= 90:
            print("q:", 1)
            dy = -1 * self.speed * math.sin(math.radians(self.direction))
            dx = self.speed * math.cos(math.radians(self.direction))
        elif 90 < self.direction <= 180:
            print("q:", 2)
            direction = 180 - self.direction
            dy = -1 * self.speed * math.sin(math.radians(direction))
            dx = -1 * self.speed * math.cos(math.radians(direction))
        elif 180 < self.direction <= 270:
            print("q:", 3)
            direction = self.direction - 180
            dy = self.speed * math.sin(math.radians(direction))
            dx = -1 * self.speed * math.cos(math.radians(direction))
        else:
            print("q:", 4)
            direction = 360 - self.direction
            dy = self.speed * math.sin(math.radians(direction))
            dx = self.speed * math.cos(math.radians(direction))
        self.pong = (self.pong[0] + dx, self.pong[1] + dy, self.pong[2], self.pong[3])
    
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
        if x_end_ball < x_player and x_ball > x_player and y_end_ball > y_player and y_ball < y_end_player:
            print("Player Collision")
            collision = True
        
        # Bot collision
        if x_ball < x_end_bot and x_end_ball > x_end_bot and y_end_ball > y_bot and y_ball < y_end_bot:
            print("Bot Collision")
            collision = True
        
        if collision:
            quarter = (self.direction // 90) + 1
            print("Collision!", quarter, self.direction)
            if quarter == 1 and not self.bot_turn:
                quarter = 2
                self.bot_turn = True
            elif quarter == 2 and self.bot_turn:
                quarter = 1
                self.bot_turn = False
            elif quarter == 3 and self.bot_turn:
                quarter = 4
                self.bot_turn = False
            elif quarter == 4 and not self.bot_turn:
                quarter = 3
                self.bot_turn = True
            self.random_direction(quarters=[quarter])
        
        # Wall collisions
        if y_ball <= 0:
            quarter = (self.direction // 90) + 1
            print("Up!", quarter, self.direction)
            if quarter == 1:
                self.direction = (-self.direction) % 360
            elif quarter == 2:
                self.direction += (180 - self.direction) * 2
        
        if y_end_ball >= badge.display.height:
            quarter = (self.direction // 90) + 1
            print("Down!", quarter, self.direction)
            if quarter == 3:
                self.direction -= (self.direction - 180) * 2
            elif quarter == 4:
                self.direction = 360 - self.direction
        


    def process_input(self):
        buttons = badge.gamepad.get_pressed() 
        if buttons & badge.BTN_LEFT:
            #self.selected_digit = (self.selected_digit + 5 - 1) % 5
            return True
        if buttons & badge.BTN_RIGHT:
            #self.selected_digit = (self.selected_digit + 1) % 5
            return True
        if (buttons & badge.BTN_UP) or (buttons & badge.BTN_DOWN):
            return True
        if buttons & badge.BTN_ACTION:
            self.running = False
            return True
        return False

    def run(self):
        display = badge.display
        self.running = True

        while self.running:
            group = self.render()
            self.move_ball()
            self.handle_collision()
            display.show(group)
            while display.time_to_refresh > 0:
                pass
            if not self.process_input():
                display.refresh()

def main():
    return PongApp()
