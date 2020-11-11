
import random
import arcade
import os
# http://kenney.nl/assets/casino-audio Kenney.nl
good_sound = arcade.load_sound("chipLay1.ogg")
# I got this sound from your example in the online book. Kenney.nl
bad_sound = arcade.load_sound("laser.ogg")
# https://opengameart.org/content/caketown-cuteplayful OpenGameArt.org
background_sound = arcade.load_sound("Caketown.ogg")

# These numbers represent "states" that the game can be in.
INSTRUCTIONS_PAGE = 0
GAME_RUNNING = 1
GAME_OVER = 2

# Sizes and speed of Sprites and Screen
ENEMY_SCALING = .4
BANANA_SCALING = .25
SPRITE_SCALING = 0.5
SPRITE_NATIVE_SIZE = 128
SPRITE_SIZE = int(SPRITE_NATIVE_SIZE * SPRITE_SCALING)
POO_SPEED = 5
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
LASER_COUNT = 1

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 70
RIGHT_MARGIN = 150

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 9
GRAVITY = 0.5


class Poo(arcade.Sprite):
    def update(self):
        self.center_x += POO_SPEED



def get_map(filename):
    """
    This function loads an array based on a map stored as a list of
    numbers separated by commas.
    """
    map_file = open(filename)
    map_array = []
    for line in map_file:
        line = line.strip()
        map_row = line.split(",")
        for index, item in enumerate(map_row):
            map_row[index] = int(item)
        map_array.append(map_row)
    return map_array


class Laser(arcade.Sprite):
    def reset_laser(self):

        self.center_y = 1280
        self.center_x = random.randrange(300, 3520)

    def update(self):

        self.center_y -= 3

        if self.top < 0:
            self.reset_laser()


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """
        Initializer
        """
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        self.score = 0
        # Sprite lists
        self.enemy_list = None
        self.player_list = None
        self.banana_list = None
        self.poo_list = None
        self.laser_list = None
        self.wall_list = None
        self.player_sprite = None
        self.physics_engine = None
        self.view_left = 0
        self.view_bottom = 0
        self.game_over = False
        self.background = None
        self.current_state = INSTRUCTIONS_PAGE
        self.instructions = []
        texture = arcade.load_texture("Real_instructions.png")
        self.instructions.append(texture)

    def setup(self):
        """ Set up the game and initialize the variables. """
        # Background Image
        # https://andigr.deviantart.com/art/Jungle-350444175 Deviant Art.com
        self.background = arcade.load_texture("jungle_background.jpg")
        self.score = 5
        # Sprite lists
        self.wall_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.banana_list = arcade.SpriteList()
        self.poo_list = arcade.SpriteList()
        self.laser_list = arcade.SpriteList()
        # Set up the player
        # OpenGameArt.org https://opengameart.org/content/monkey-platform-game
        self.player_sprite = arcade.Sprite("monkey.png",
                                           SPRITE_SCALING)

        for i in range(LASER_COUNT):
            # https://opengameart.org/content/aircrafts OpenGameArt.org
            laser = Laser("bullet_2_blue.png", SPRITE_SCALING + 2)
            laser.center_x = random.randrange(SCREEN_WIDTH)
            laser.center_y = random.randrange(SCREEN_HEIGHT)

            self.laser_list.append(laser)
        coordinate_list = [[150, 100],
                           [700, 500],
                           [500, 250],
                           [380, 650],
                           [1800, 100]]

        for coordinate in coordinate_list:
            # OpenGameArt.org https://opengameart.org/content/monkey-platform-game
            banana = arcade.Sprite("Banana.png", BANANA_SCALING)
            banana.center_x = coordinate[0]
            banana.center_y = coordinate[1]
            self.banana_list.append(banana)
        # Starting position of the player
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # Get a 2D array made of numbers based on the map
        map_array = get_map("real_game_map..csv")

        for row_index, row in enumerate(map_array):
            for column_index, item in enumerate(row):

                # For this map, the numbers represent:
                # -1 = empty
                # 0  = box
                if item == -1:
                    continue
                elif item == 0:
                    # OpenGameArt.org https://opengameart.org/content/platformer-tiles
                    wall = arcade.Sprite("block.png", SPRITE_SCALING)

                wall.right = column_index * 36
                wall.top = (20 - row_index) * 36
                self.wall_list.append(wall)
            # Create platform moving up and down
            # OpenGameArt.org https://opengameart.org/content/platformer-tiles
            wall = arcade.Sprite("block.png", SPRITE_SCALING)
            wall.center_y = 100
            wall.center_x = 340
            wall.boundary_top = 700
            wall.boundary_bottom = 150
            wall.change_y = 3 * SPRITE_SCALING
            self.wall_list.append(wall)

            # Top platform
            coordinate_list = [[375, 600], [410, 600], [445, 600], [480, 600],
                               [515, 600], [550, 600]]

            for coordinate in coordinate_list:
                # OpenGameArt.org https://opengameart.org/content/platformer-tiles

                wall = arcade.Sprite("block.png",
                                         SPRITE_SCALING)
                wall.center_x = coordinate[0]
                wall.center_y = coordinate[1]
                self.wall_list.append(wall)

        self.physics_engine = \
            arcade.PhysicsEnginePlatformer(self.player_sprite,
                                           self.wall_list,
                                           gravity_constant=GRAVITY)
        # Set the background color
        arcade.set_background_color(arcade.color.KELLY_GREEN)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

        # -- Draw a enemy on the platform
        # https: // opengameart.org / content / platformer - tiles OpenGameArt.org
        enemy = arcade.Sprite("walk0001.png", ENEMY_SCALING)

        enemy.bottom = SPRITE_SCALING * 940
        enemy.left = SPRITE_SCALING * 4 + 700

        # Set boundaries on the left/right the enemy can't cross
        enemy.boundary_right = SPRITE_SCALING * 8 + 830
        enemy.boundary_left = SPRITE_SCALING * 3 + 650
        self.enemy_list.append(enemy)
        enemy.change_x = 2
        # https: // opengameart.org / content / platformer - tiles OpenGameArt.org
        enemy = arcade.Sprite("walk0001.png", ENEMY_SCALING)

        enemy.bottom = SPRITE_SIZE * .60
        enemy.left = SPRITE_SIZE * 16

        enemy.boundary_right = SPRITE_SCALING * 16 + 1500
        enemy.boundary_left = SPRITE_SCALING * 16 + 900
        # Set enemy initial speed
        enemy.change_x = 2
        self.enemy_list.append(enemy)

    # STEP 2: Add this function.
    def draw_instructions_page(self, page_number):
        """
        Draw an instruction page. Load the page as an image.
        """
        page_texture = self.instructions[page_number]
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      page_texture.width,
                                      page_texture.height, page_texture, 0)

    def draw_game(self):
        # Background Image
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      SCREEN_WIDTH * 4.5, SCREEN_HEIGHT * 2.5, self.background)
        # Draw all the sprites.
        self.wall_list.draw()
        self.player_list.draw()
        self.enemy_list.draw()
        self.banana_list.draw()
        self.poo_list.draw()
        self.laser_list.draw()

        # How many bananas are remaining
        if len(self.banana_list) != 0:
            output = f"Bananas remaining: {self.score}"
            arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20,
                             arcade.color.WHITE, 14)
        if self.game_over:
            arcade.draw_text("Restart!", self.view_left + 350, self.view_bottom + 300, arcade.color.RED, 28)
        if len(self.banana_list) == 0:
            arcade.draw_text("YOU WIN!", self.view_left + 250, self.view_bottom + 400, arcade.color.RED, 64)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        if self.current_state == INSTRUCTIONS_PAGE:
            self.draw_instructions_page(0)

        elif self.current_state == GAME_RUNNING:
            self.draw_game()

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called when the user presses a mouse button.
        """

        # Change states as needed.
        if self.current_state == INSTRUCTIONS_PAGE:
            self.setup()
            self.current_state = GAME_RUNNING
            arcade.play_sound(background_sound)

        elif self.current_state == GAME_OVER:
            # Restart the game.
            self.setup()
            self.current_state = GAME_RUNNING

    def on_key_press(self, key, modifiers):
        """
        Called whenever the mouse moves.
        """
        if key == arcade.key.W:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.A:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.D:
            self.player_sprite.change_x = MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            poo = Poo("creamChoco.png", SPRITE_SCALING)
            poo.center_x = self.player_sprite.center_x
            poo.center_y = self.player_sprite.center_y
            self.poo_list.append(poo)

    def on_key_release(self, key, modifiers):
        """
        Called when the user presses a mouse button.
        """
        if key == arcade.key.A or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """
        if not self.game_over:
            self.physics_engine.update()

            # --- Manage Scrolling ---

            # Track if we need to change the view port

            changed = False

            # Scroll left
            left_bndry = self.view_left + VIEWPORT_MARGIN
            if self.player_sprite.left < left_bndry:
                self.view_left -= left_bndry - self.player_sprite.left
                changed = True

            # Scroll right
            right_bndry = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
            if self.player_sprite.right > right_bndry:
                self.view_left += self.player_sprite.right - right_bndry
                changed = True

            # Scroll up
            top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
            if self.player_sprite.top > top_bndry:
                self.view_bottom += self.player_sprite.top - top_bndry
                changed = True

            # Scroll down
            bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
            if self.player_sprite.bottom < bottom_bndry:
                self.view_bottom -= bottom_bndry - self.player_sprite.bottom
                changed = True

            # If we need to scroll, go ahead and do it.
            if changed:
                arcade.set_viewport(self.view_left,
                                    SCREEN_WIDTH + self.view_left,
                                    self.view_bottom,
                                    SCREEN_HEIGHT + self.view_bottom)
            # If monkey collects a banana
            banana_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                self.banana_list)
            for banana in banana_hit_list:
                banana.kill()
                arcade.play_sound(good_sound)
                self.score -= 1
            # If monkey runs into alien
            enemy_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                                 self.enemy_list)
            for enemy in enemy_hit_list:
                enemy.kill()
                arcade.play_sound(bad_sound)
            if len(enemy_hit_list) > 0:
                self.game_over = True
            self.laser_list.update()
            laser_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.laser_list)
            for laser in laser_hit_list:
                laser.kill()
                arcade.play_sound(bad_sound)
            if len(laser_hit_list) > 0:
                self.player_sprite.kill()
                self.game_over = True
            self.poo_list.update()

            # Loop through each poo
            for poo in self.poo_list:

                # Check this poo to see if it hit a enemy
                poo_hit_list = arcade.check_for_collision_with_list(poo,
                                                                self.enemy_list)

                # If it did, get rid of the poo
                if len(poo_hit_list) > 0:
                    poo.kill()

                for enemy in poo_hit_list:
                    enemy.kill()

                wall_hit_list = arcade.check_for_collision_with_list(poo, self.wall_list)

                if len(wall_hit_list) > 0:
                    poo.kill()

            self.enemy_list.update()
            for enemy in self.enemy_list:
                # If the enemy hit a wall, reverse
                if len(arcade.check_for_collision_with_list(enemy,
                                                            self.wall_list)) > 0:
                    enemy.change_x *= -1
                # If the enemy hit the left boundary, reverse
                elif enemy.boundary_left is not None and enemy.left < enemy.boundary_left:
                    enemy.change_x *= -1
                # If the enemy hit the right boundary, reverse
                elif enemy.boundary_right is not None and enemy.right > enemy.boundary_right:
                    enemy.change_x *= -1
        if len(self.banana_list) == 0:
            self.game_over = True



def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()