"""
campaign.py

Place for CampaignView class.
"""

import arcade
import assets
import data
import pause
import math
import random
from developer import log
from player import Player

# --- Constants ---
param = data.load_parameters()
RADIANS_PER_FRAME = float(param['CAMPAIGN']['RADIANS_PER_FRAME'])


class CampaignView(arcade.View):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.choose_level = self.window.levels_unlocked
        self.sweep_length = self.window.height * 0.4
        self.mouse_position = (0, 0)
        # Add stars
        self.star_sprite_list = arcade.SpriteList()
        # Setup levels coordinates:
        self.level_5 = (self.window.width // 2 * 0.4, self.window.height // 2 * 1.2)
        self.level_4 = (self.window.width // 2 * 1.1, self.window.height // 2 * 1.5)
        self.level_3 = (self.window.width // 2 * 1.2, self.window.height // 2 * 1.3)
        self.level_2 = (self.window.width // 2 * 0.8, self.window.height // 2 * 0.4)
        self.level_1 = (self.window.width // 2 * 0.8, self.window.height // 2 * 1.1)
        for i in range(100):
            sprite = arcade.SpriteSolidColor(2, 2, arcade.color.WHITE)
            sprite.center_x = random.randrange(self.window.width)
            sprite.center_y = random.randrange(self.window.height)
            self.star_sprite_list.append(sprite)
        if self.window.pause_view is None:
            self.window.pause_view = pause.PauseView(self)

        # Variables that will hold sprite lists
        self.player_list = arcade.SpriteList()
        # Set up the player
        self.player_sprite = Player(level_width=self.window.width, level_height=self.window.height)
        self.player_sprite.center_x = 400
        self.player_sprite.center_y = 400
        self.player_list.append(self.player_sprite)

    def on_draw(self):
        """ Use this function to draw everything to the screen. """

        # Move the angle of the sweep.
        self.angle += RADIANS_PER_FRAME

        # Calculate the end point of our radar sweep. Using math.
        x = self.sweep_length * math.sin(self.angle) + (self.window.width // 2)
        y = self.sweep_length * math.cos(self.angle) + (self.window.height // 2)

        # Start the render. This must happen before any drawing
        # commands. We do NOT need an stop render command.
        self.window.developer_tool.on_draw_start()

        arcade.start_render()

        # Draw the background texture
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            self.window.width, self.window.height,
                                            assets.bg_campaign)
        self.star_sprite_list.draw()
        # Representation of levels:
        # Level 5:
        if self.window.levels_unlocked >= 5:
            if self.choose_level >= 4:
                arcade.draw_line(self.level_5[0], self.level_5[1],
                                 self.level_4[0], self.level_4[1], arcade.color.ROMAN_SILVER,
                                 1)
            arcade.draw_circle_filled(self.level_5[0], self.level_5[1], 10,
                                      arcade.color.BROWN, 3)
        if self.window.levels_unlocked >= 4:
            # Level 4:
            if self.choose_level in range(2, 5):
                arcade.draw_line(self.level_4[0], self.level_4[1],
                                 self.level_3[0], self.level_3[1], arcade.color.ROMAN_SILVER,
                                 1)
            arcade.draw_circle_filled(self.level_4[0], self.level_4[1], 5,
                                      arcade.color.DARK_BYZANTIUM, 3)
            arcade.draw_circle_filled(self.level_4[0], self.level_4[1], 3,
                                      arcade.color.GREEN_YELLOW, 3)
        if self.window.levels_unlocked >= 3:
            # Level 3: Kingdom End
            if self.choose_level in range(1, 4):
                arcade.draw_line(self.level_3[0], self.level_3[1],
                                 self.level_2[0], self.level_2[1], arcade.color.ROMAN_SILVER,
                                 1)
            arcade.draw_circle_filled(self.level_3[0], self.level_3[1], 14,
                                      arcade.color.DARK_BYZANTIUM, 3)
            arcade.draw_circle_filled(self.level_3[0], self.level_3[1], 12,
                                      arcade.color.RED_DEVIL, 3)
        if self.window.levels_unlocked >= 2:
            # Level 2: Tartolyyn
            if self.choose_level in range(0, 3):
                arcade.draw_line(self.level_2[0], self.level_2[1],
                                 self.level_1[0], self.level_1[1], arcade.color.ROMAN_SILVER,
                                 1)
            arcade.draw_circle_filled(self.level_2[0], self.level_2[1], 8,
                                      arcade.color.DARK_BYZANTIUM, 3)
            arcade.draw_circle_filled(self.level_2[0], self.level_2[1], 5,
                                      arcade.color.BROWN_NOSE, 3)
        # Level 1: Imperial City (tutorial)
        arcade.draw_circle_filled(self.level_1[0], self.level_1[1], 20,
                                  arcade.color.SILVER_LAKE_BLUE, 3)

        # Draw the radar line
        arcade.draw_line(self.window.width // 2, self.window.height // 2, x, y, arcade.color.ROMAN_SILVER, 4)

        # Draw the outline of the radar
        arcade.draw_circle_outline(self.window.width // 2, self.window.height // 2, self.sweep_length,
                                   arcade.color.OLD_SILVER, 8)

        self.window.developer_tool.on_draw_finish()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.ESCAPE:
            log('Scene switched to ' + str(self.window.pause_view))
            self.window.scenes.append(self.window.pause_view)
            self.window.show_view(self.window.pause_view)

