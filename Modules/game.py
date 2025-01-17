from Modules.Menu import *
from Modules.Objects import *
import datetime

SCREEN_WIDTH, SCREEN_HEIGHT = config.SCREEN_SIZE


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, 16, 2, 4096)
        pg.init()
        pg.display.set_caption("00 Racing")
        icon = pg.image.load("Resources/Images/icon.png")
        pg.display.set_icon(icon)
        self.running, self.playing = True, False
        self.window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert_alpha()
        self.FPS = 60
        self.font_name = "Resources/Fonts/pxl_tactical.ttf"
        self.frame_per_second = pg.time.Clock()
        pg.mouse.set_cursor(pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND))

        # HANDLE_EVENTS

        self.clicked = False
        self.menu_state = "MENU"
        self.game_state = "GAME"
        self.keys = {"MOUSE DOWN": False, "BACK": False, "ENTER": False,
                     "MOVE UP": False, "MOVE DOWN": False, "MOUSEWHEEL": 0,
                     "MOVE RIGHT": False, "MOVE LEFT": False, "MOUSEWHEEL_X": 0
                     }

        # MENU

        self.main_menu = MainMenu(self)
        self.levels_menu = LevelsMenu(self)
        self.sets_menu = SetsMenu(self)
        self.garage_menu = GarageMenu(self)
        self.music_menu = MusicMenu(self)
        self.authors_menu = Authors(self)

        # BUTTONS GAME

        self.close_button_game = Button("Resources/Images/Buttons/close_button_off.png",
                                        "Resources/Images/Buttons/close_button_on.png",
                                        button_sound,
                                        0.25)
        self.back_button = Button("Resources/Images/Buttons/back_button_off.png",
                                  "Resources/Images/Buttons/back_button_on.png",
                                  button_sound,
                                  0.25)

        # BACKGROUND

        self.curr_level = 0
        self.game_over_bg = Picture("Resources/Images/Backgrounds/window_vert.png", 0.5)
        self.pause_bg = Picture("Resources/Images/Backgrounds/window_vert.png", 0.5)

        # HINTS

        self.hints_bg = Picture("Resources/Images/Backgrounds/hints_bg.png", 1.6)
        self.forward_hint = GIF("Resources/Images/Hud/controls/forward/", scale=0.15)
        self.left_hint = GIF("Resources/Images/Hud/controls/left/", scale=0.15)
        self.right_hint = GIF("Resources/Images/Hud/controls/right/", scale=0.15)

        # CARS

        self.opp1 = GIF("Resources/Images/cars/opps/opp1/", scale=0.5).gif
        self.opp2 = GIF("Resources/Images/cars/opps/opp2/", scale=0.45).gif
        self.opp3 = GIF("Resources/Images/cars/opps/opp3/", scale=0.55).gif
        self.opp4 = GIF("Resources/Images/cars/opps/opp4/", scale=0.45).gif

        self.first_enemy = None
        self.second_enemy = None
        self.third_enemy = None

        gold_coin_image = pg.image.load("Resources/Images/Hud/coins/MonedaD.png").convert_alpha()
        self.gold_coin_images = get_sheet(gold_coin_image, 5, 3)

        rubin_coin_image = pg.image.load("Resources/Images/Hud/coins/spr_coin_roj.png").convert_alpha()
        self.rubin_coin_images = get_sheet(rubin_coin_image, 4, 3)

        self.oil_stain_image = Picture("Resources/Images/Hud/oil_stain.png", 0.65)

        self.speedometer_base = Picture("Resources/Images/Hud/speedometer/base.png", 1.35)

        # MUSIC

        self.music_player = MusicPlayer()
        self.music_player.set_volume()
        self.music_player.play()

        # TRANSITION

        self.transition = False
        self.last_update = pg.time.get_ticks()

        # GAME ATTRIBUTES

        self.map_number = None
        self.lives = None
        self.blinks_counter = None
        self.coins = None
        self.score = None
        self.main_speed = None
        self.enemy_speed = None
        self.angle_of_main = None
        self.player_group = None
        self.coins_group = None
        self.ruby_group = None
        self.explosion_group = None
        self.P1 = None
        self.E1 = None
        self.E2 = None
        self.E3 = None
        self.E4 = None
        self.enemies = None
        self.Gold_Co = None
        self.Ruby_Co = None
        self.Oil = None
        self.first_bg = None
        self.time = None
        self.time2 = None

    def set_default_attributes(self):
        def add_sprites(images, sprite_group, state=None):
            obj = None
            for frame in range(len(images)):
                if state == "Vehicle":
                    obj = OppVehicle(0, 0, images[frame].image)
                if state == "PlayerVehicle":
                    obj = PlayerVehicle(790, 590, images[frame].image)
                if state == "Elements":
                    obj = Elements(0, 0, images[frame])

                sprite_group.add(obj)

        def choose_car():  # CHECk IF LIST IS EMPTY
            for car in settings.cars:
                if car["chosen"]:
                    return car

        # choosing map
        self.map_number = int(settings.levels[self.curr_level]["number"])

        # set game variables
        self.lives = 3
        self.blinks_counter = 0
        self.coins = 0
        self.score = 0
        self.main_speed = 1
        self.enemy_speed = 5
        self.angle_of_main = 0
        max_player_speed = choose_car()["specs"]["speed"]["val"]
        player_acceleration = choose_car()["specs"]["braking"]["val"]
        change_moving_lr_vel = choose_car()["specs"]["driveability"]["val"]

        # creating sprite groups
        self.player_group = pg.sprite.Group()
        enemy1_group = pg.sprite.Group()
        enemy2_group = pg.sprite.Group()
        enemy3_group = pg.sprite.Group()
        enemy4_group = pg.sprite.Group()
        oil_group = pg.sprite.Group()
        self.coins_group = pg.sprite.Group()
        self.ruby_group = pg.sprite.Group()
        self.explosion_group = pg.sprite.Group()

        add_sprites(GIF(f'Resources/Images/cars/{choose_car()["name"]} topdown/',
                    scale=choose_car()["topdown_size"]).gif,
                    self.player_group,
                    "PlayerVehicle")
        add_sprites(self.opp1, enemy1_group, "Vehicle")
        add_sprites(self.opp2, enemy2_group, "Vehicle")
        add_sprites(self.opp3, enemy3_group, "Vehicle")
        add_sprites(self.opp4, enemy4_group, "Vehicle")

        add_sprites(self.gold_coin_images, self.coins_group, "Elements")
        add_sprites(self.rubin_coin_images, self.ruby_group, "Elements")
        add_sprites([self.oil_stain_image.image], oil_group, "Elements")

        # creating instances of the class for subsequent manipulations
        self.P1 = Player(self.player_group.sprites(), max_player_speed, player_acceleration, change_moving_lr_vel)

        self.E1 = Enemy(enemy1_group.sprites(), self.enemy_speed, self.main_speed)
        self.E2 = Enemy(enemy2_group.sprites(), self.enemy_speed, self.main_speed)
        self.E3 = Enemy(enemy3_group.sprites(), self.enemy_speed, self.main_speed)
        self.E4 = Enemy(enemy4_group.sprites(), self.enemy_speed, self.main_speed)
        self.enemies = [self.E1, self.E2, self.E3, self.E4]
        self.first_enemy = 0
        self.second_enemy = 1
        self.third_enemy = 2

        self.Gold_Co = CoinsMechanics(self.coins_group.sprites(), self.main_speed, "gold")
        self.Ruby_Co = CoinsMechanics(self.ruby_group.sprites(), self.main_speed, "ruby")
        self.Oil = OilMechanics(oil_group.sprites(), self.main_speed)

        # set background
        self.first_bg = None
        bgs = []
        for file in sorted(os.listdir(f'Resources/Images/Backgrounds/Levels/level{str(self.map_number)}/')):
            if ".png" in file:
                bg = Background(f'Resources/Images/Backgrounds/Levels/level{str(self.map_number)}/' + file, (1280, 720))
                if self.first_bg:
                    bgs.append(bg)
                else:
                    self.first_bg = bg

        self.first_bg.set_bgs(bgs, (60, 5, 20, 30, 5), 10)

        self.time = pg.time.get_ticks()
        self.time2 = pg.time.get_ticks()

    def game_loop(self):
        # setting attributes for start game
        self.set_default_attributes()
        # game loop
        while self.playing:
            self.check_events()

            if self.game_state == "GAME OVER":
                self.game_over()
            elif self.game_state == "PAUSED":
                self.paused()
            elif self.game_state == "COLLISION":
                self.collision()
            elif self.game_state == "GAME":
                self.game()

            self.hud()
            self.blit_screen()

        self.garage_menu.player_stats.coins += self.coins
        self.garage_menu.player_stats.increase_score(self.score)
        pg.time.delay(500)
        pg.mixer.fadeout(500)

    def collisions_with_objects(self):
        # actions when hitting oil
        if self.Oil.get_const(mask=True) is not None:
            if self.P1.get_const(mask=True).overlap(self.Oil.get_const(mask=True),
                                                    (self.Oil.get_const(x=True) - self.P1.get_const(x=True),
                                                     self.Oil.get_const(y=True) - self.P1.get_const(y=True))):
                if self.P1.get_const(vel_of_forward=True) != -1:
                    self.P1.collision(True)
                else:
                    self.P1.collision(False)

                if self.main_speed > 5:
                    self.main_speed /= 1.05
                    self.main_speed = max(self.main_speed, 1)

                self.P1.set_const(speed=self.main_speed, angle=self.angle_of_main, update_rate=100)
                self.actions_with_enemies("set_speed")

        # actions when hitting a gold coin
        if self.P1.get_const(mask=True).overlap(self.Gold_Co.get_const(mask=True),
                                                (self.Gold_Co.get_const(x=True) - self.P1.get_const(x=True),
                                                 self.Gold_Co.get_const(y=True) - self.P1.get_const(y=True))):
            self.Gold_Co = CoinsMechanics(self.coins_group.sprites(), self.main_speed, "gold")
            self.coins += 1

        # actions when hitting a ruby coin
        if self.Ruby_Co.get_const(mask=True) is not None:
            if self.P1.get_const(mask=True).overlap(self.Ruby_Co.get_const(mask=True),
                                                    (self.Ruby_Co.get_const(x=True) - self.P1.get_const(x=True),
                                                    self.Ruby_Co.get_const(y=True) - self.P1.get_const(y=True))):
                self.Ruby_Co = CoinsMechanics(self.ruby_group.sprites(), self.main_speed, "ruby")
                self.coins += 10

    def actions_with_enemies(self, type_of_actions):
        # moving enemy cars
        if type_of_actions == "move":
            current_time = pg.time.get_ticks()

            # if map_number is 1 then show 1 an enemy car
            if self.map_number == 1:
                self.enemies[self.first_enemy].move(self.screen)
                if self.enemies[self.first_enemy].get_const(y=True) == -300:
                    self.score += 15
                    self.first_enemy = (self.first_enemy + 1) % 4

            # if map_number is 2 then show 2 an enemy car
            if self.map_number == 2:
                for i in range(4):
                    if i != self.first_enemy:
                        self.enemies[self.first_enemy].set_speed(
                            another_x=self.enemies[i].get_const(x=True))

                for i in range(4):
                    if i != self.second_enemy:
                        self.enemies[self.second_enemy].set_speed(
                            another_x=self.enemies[i].get_const(x=True))

                self.enemies[self.first_enemy].set_speed(rendering_frequency=-1)
                self.enemies[self.first_enemy].move(self.screen)

                self.enemies[self.second_enemy].set_speed(rendering_frequency=1000)
                self.enemies[self.second_enemy].move(self.screen)

                if self.enemies[self.first_enemy].get_const(y=True) == -300:
                    self.score += 20
                    self.first_enemy = (self.first_enemy + 2) % 4

                if self.enemies[self.second_enemy].get_const(y=True) == -300:
                    if current_time - self.time2 > 1200:
                        self.score += 20
                    self.second_enemy = (self.second_enemy + 2) % 4

            # if map_number is 3 then show 3 an enemy car
            if self.map_number > 2:
                for i in range(4):
                    if i != self.first_enemy:
                        self.enemies[self.first_enemy].set_speed(
                            another_x=self.enemies[i].get_const(x=True))

                for i in range(4):
                    if i != self.second_enemy:
                        self.enemies[self.second_enemy].set_speed(
                            another_x=self.enemies[i].get_const(x=True))

                for i in range(4):
                    if i != self.third_enemy:
                        self.enemies[self.third_enemy].set_speed(
                            another_x=self.enemies[i].get_const(x=True))

                self.enemies[self.first_enemy].set_speed(rendering_frequency=-1)
                self.enemies[self.first_enemy].move(self.screen)

                self.enemies[self.second_enemy].set_speed(rendering_frequency=1000)
                self.enemies[self.second_enemy].move(self.screen)

                self.enemies[self.third_enemy].set_speed(rendering_frequency=2000)
                self.enemies[self.third_enemy].move(self.screen)

                if self.enemies[self.first_enemy].get_const(y=True) == -300:
                    self.score += 30
                    for i in range(self.first_enemy + 1, 4 + self.first_enemy):
                        if self.enemies[i % 4].get_const(y=True) == -300:
                            self.first_enemy = i % 4
                            break

                if self.enemies[self.second_enemy].get_const(y=True) == -300:
                    if current_time - self.time2 > 1200:
                        self.score += 30
                    for i in range(self.second_enemy + 1, 4 + self.second_enemy):
                        if self.enemies[i % 4].get_const(y=True) == -300:
                            self.second_enemy = i % 4
                            break

                if self.enemies[self.third_enemy].get_const(y=True) == -300:
                    if current_time - self.time2 > 2200:
                        self.score += 30
                    for i in range(self.third_enemy + 1, 4 + self.third_enemy):
                        if self.enemies[i % 4].get_const(y=True) == -300:
                            self.third_enemy = i % 4
                            break

        # stopping an enemy cars
        if type_of_actions == "stop":
            for obj in self.enemies:
                obj.set_speed(enemy_speed=0, main_speed=0)

        # setting the speed of enemy cars
        if type_of_actions == "set_speed":
            for obj in self.enemies:
                obj.set_speed(enemy_speed=self.enemy_speed, main_speed=self.main_speed)

    def game(self):

        if not car_sound.num_channels:
            car_sound.play(loops=-1, fade_ms=500)

        # setting the values of variables
        if self.P1.get_const(speed=True) == 0:
            self.P1.set_const(speed=self.main_speed, angle=self.angle_of_main, update_rate=100)
        self.main_speed = max(self.P1.get_const(speed=True), 1)
        self.actions_with_enemies("set_speed")
        self.Gold_Co.set_const(speed=self.main_speed)
        self.Ruby_Co.set_const(speed=self.main_speed)
        self.Oil.set_const(speed=self.main_speed)

        # showing background
        self.first_bg.random_scroll(self.screen, self.main_speed + 15)

        # moving objects and cars
        self.P1.move(self.screen)
        self.Oil.move(self.screen)
        self.Gold_Co.move(self.screen)
        self.Ruby_Co.move(self.screen)

        # updating global variables in the game.py
        self.main_speed = max(self.P1.get_const(speed=True), 1)
        self.angle_of_main = self.P1.get_const(angle=True)

        # output other things to the screen
        Player.blit_rotate_center(self.P1, self.screen)
        self.actions_with_enemies("move")

        # checking for collisions with objects and enemy vehicles
        self.collisions_with_objects()
        self.collision_with_enemies(self.E1)
        self.collision_with_enemies(self.E2)
        self.collision_with_enemies(self.E3)
        self.collision_with_enemies(self.E4)

        # show hints
        if all(not i for i in pg.key.get_pressed()):
            if pg.time.get_ticks() - self.time > 5000:
                self.show_hints()
        else:
            self.time = pg.time.get_ticks()

    def blinks(self, state=None):
        a = datetime.datetime.now()
        b = datetime.datetime.now()

        while (b - a).microseconds < 250000:
            b = datetime.datetime.now()

            # output to the screen
            self.blit_screen()
            self.first_bg.random_scroll(self.screen, self.main_speed + 15)
            self.hud()
            if state == "ON":
                Player.blit_rotate_center(self.P1, self.screen)

            # setting the values of variables
            self.main_speed = max(self.P1.get_const(speed=True), 1)
            self.actions_with_enemies("set_speed")

            # moving objects and cars
            self.P1.move(self.screen)
            self.actions_with_enemies("move")

            # checking for collisions with objects self.collisions_with_objects()

    def collision(self):
        # setting the values of variables to start a collision
        if self.blinks_counter == 0:
            self.P1.collision(True)
            self.E1.render(False)
            self.Gold_Co.render(False)
            self.Ruby_Co.render(False)
            self.Oil.render(False)

        # updating global variables
        self.blinks_counter += 1
        self.P1.set_const(speed=self.main_speed)

        # blinking of objects and cars on the screen
        self.blinks("OFF")
        self.blinks("ON")

        # setting the values of variables to finish a collision
        if self.blinks_counter == 3:
            self.blinks_counter = 0
            self.game_state = "GAME"

            self.P1.collision(False)
            self.E1.render(True)
            self.Gold_Co.render(True)
            self.Ruby_Co.render(True)
            self.Oil.render(True)
            self.angle_of_main = 0

            self.P1.move(self.screen)
            self.actions_with_enemies("move")

            Player.blit_rotate_center(self.P1, self.screen)

    def game_over(self):
        # show background
        self.first_bg.random_scroll(self.screen, 0)

        # setting the values of variables
        self.lives = 3
        self.P1.set_const(speed=0, angle=self.angle_of_main, update_rate=0)
        self.actions_with_enemies("stop")
        self.actions_with_enemies("move")
        self.Gold_Co.set_const(speed=0)
        self.Gold_Co.move(self.screen)
        self.Ruby_Co.set_const(speed=0)
        self.Ruby_Co.move(self.screen)
        self.Oil.set_const(speed=0)
        self.Oil.move(self.screen)

        # showing car, game over window and explosion on screen
        Player.blit_rotate_center(self.P1, self.screen)
        self.explosion_group.draw(self.screen)
        self.explosion_group.update()
        self.hud("GAME_OVER")

    def hud(self, state=None):
        # set text color
        if self.map_number == 3 or self.map_number == 4:
            color = (255, 255, 255)
        else:
            color = (0, 0, 0)

        # showing game over and pause info
        if state == "GAME_OVER":
            self.game_over_bg.draw(self.screen, (640, 360))
            game_over_text = Text("GAME OVER", 50)
            game_over_text.draw(self.screen, (640, 150))

            coins_gain = Text(f"+ {self.coins} coins", scale=35)
            coins_gain.draw(self.screen, (640, 450))

            score_gain = Text(f"+ {self.score} score", scale=35)
            score_gain.draw(self.screen, (640, 400))

        if state == "PAUSED":
            self.pause_bg.draw(self.screen, (640, 360))
            paused_text = Text("PAUSED", 50)
            paused_text.draw(self.screen, (640, 150))

            coins_gain = Text(f"+ {self.coins} coins", scale=35)
            coins_gain.draw(self.screen, (640, 350))

            score_gain = Text(f"+ {self.score} score", scale=35)
            score_gain.draw(self.screen, (640, 400))

        # creating and showing text on screen
        coins_text = Text("COINS:" + str(self.coins), scale=35, color=color)
        score_text = Text("SCORE:" + str(self.score), scale=35, color=color)
        coins_text.draw(self.screen, (20, 20), position="topleft")
        score_text.draw(self.screen, (20, 50), position="topleft")

        # showing hearts on screen
        for i in range(self.lives):
            heart_pic = Picture("Resources/Images/Hud/heart.png", scale=2.25)
            heart_pic.draw(self.screen, (1125 + i * 50, 55))

        # showing speedometer on screen
        self.speedometer_base.draw(self.screen, (1091, 720), position="bottomleft")
        self.P1.rotate_arrow_of_speedometer(self.screen, "Resources/Images/Hud/speedometer/arrow.png",
                                            self.speedometer_base.rect.center, 1.35)

        # showing name of current_song on screen
        self.music_player.draw_current_song(self.screen, (10, 710), position="bottomleft")

        # if state is game_over then showing game close button
        if state == "GAME_OVER":
            if self.close_button_game.draw(self.screen, (510, 530)) and self.clicked:
                self.playing = False
                self.game_state = "GAME"

    def paused(self):
        # show background
        self.first_bg.random_scroll(self.screen, 0)

        car_sound.stop()

        # setting the values of variables
        self.time = pg.time.get_ticks()
        self.P1.set_const(speed=0, angle=self.angle_of_main, update_rate=0)
        self.actions_with_enemies("stop")
        self.actions_with_enemies("move")
        self.Gold_Co.set_const(speed=0)
        self.Gold_Co.move(self.screen)
        self.Ruby_Co.set_const(speed=0)
        self.Ruby_Co.move(self.screen)
        self.Oil.set_const(speed=0)
        self.Oil.move(self.screen)
        Player.blit_rotate_center(self.P1, self.screen)

        # showing hud
        self.hud("PAUSED")

        # closing game
        if self.close_button_game.draw(self.screen, (510, 530)) and self.clicked:
            self.playing = False
            if self.blinks_counter != 0:
                self.game_state = "COLLISION"
            else:
                self.game_state = "GAME"

        # resuming game
        if self.back_button.draw(self.screen, (770, 530)) and self.clicked:
            if self.blinks_counter != 0:
                self.game_state = "COLLISION"
            else:
                self.game_state = "GAME"

    def collision_with_enemies(self, enemy):
        player_mask = self.P1.get_const(mask=True)
        player_rect_x = self.P1.get_const(x=True)
        player_rect_y = self.P1.get_const(y=True)

        enemy_mask = enemy.get_const(mask=True)
        enemy_rect_x = enemy.get_const(x=True)
        enemy_rect_y = enemy.get_const(y=True)

        if enemy_mask is not None:
            if player_mask.overlap(enemy_mask, (enemy_rect_x - player_rect_x, enemy_rect_y - player_rect_y)):
                self.lives -= 1
                settings.player_stats["crashed"] += 1
                if self.lives == 0:
                    self.game_state = "GAME OVER"
                    settings.player_stats["defeats"] += 1

                    pos = [self.player_group.sprites()[0].rect.center[0], self.player_group.sprites()[0].rect.top]
                    explosion = Explosion(pos[0], pos[1])
                    self.explosion_group.add(explosion)

                else:
                    self.game_state = "COLLISION"

    def show_hints(self):
        self.hints_bg.draw(self.screen, (640, 360))

        bar = pg.surface.Surface((270, 100), pg.SRCALPHA).convert_alpha()
        bar_rect = bar.get_rect()
        bar_rect.center = (640, 360)

        bar.fill((0, 0, 0, 255))

        self.forward_hint.draw(bar, coordinates=(bar.get_width() / 2, bar.get_height() / 2 - 10))
        move_up = Text(pg.key.name(settings.KEYS["MOVE UP"]), scale=15)
        move_up.draw(bar, (bar.get_width() / 2, bar.get_height() / 2 + 30), position="center")

        self.left_hint.draw(bar, coordinates=(bar.get_width() / 2 - 100, bar.get_height() / 2 - 10))
        move_left = Text(pg.key.name(settings.KEYS["MOVE LEFT"]), scale=15)
        move_left.draw(bar, (bar.get_width() / 2 - 100, bar.get_height() / 2 + 30), position="center")

        self.right_hint.draw(bar, coordinates=(bar.get_width() / 2 + 100, bar.get_height() / 2 - 10))
        move_right = Text(pg.key.name(settings.KEYS["MOVE RIGHT"]), scale=15)
        move_right.draw(bar, (bar.get_width() / 2 + 100, bar.get_height() / 2 + 30), position="center")

        self.screen.blit(bar, bar_rect)

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running, self.playing = False, False
                pg.mixer.fadeout(500)
                pg.quit()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.clicked = True
            else:
                self.clicked = False
            if event.type == pg.KEYDOWN:
                if event.key == settings.KEYS["BACK"] and self.game_state != "GAME OVER":
                    self.keys["BACK"] = True
                    if self.game_state == "PAUSED":
                        self.game_state = "GAME"
                    else:
                        self.game_state = "PAUSED"
                if event.key == settings.KEYS["ENTER"]:
                    self.keys["ENTER"] = True
                if event.key == settings.KEYS["PLAY MUSIC"]:
                    self.music_player.play()
                if event.key == settings.KEYS["CHANGE MUSIC"]:
                    self.music_player.next()
            if event.type == self.music_player.MUSIC_END:
                self.music_player.playing = False
                if self.music_player.loop:
                    self.music_player.play()
                else:
                    self.music_player.next()

    def blit_screen(self, transition_time=500):
        for button in self.keys.keys():
            self.keys[button] = 0
        self.window.blit(self.screen, (0, 0))

        if self.transition:
            current_time = pg.time.get_ticks()
            bar = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA).convert_alpha()
            if current_time - self.last_update < transition_time / 2:
                bar.fill((0, 0, 0, ((current_time - self.last_update) / (transition_time / 2)) * 255))
            elif current_time - self.last_update < transition_time:
                bar.fill((0, 0, 0,
                          ((transition_time - (current_time - self.last_update)) / (transition_time / 2)) * 255))
                if ((transition_time - (current_time - self.last_update)) / (transition_time / 2)) * 255:
                    self.transition = False
            else:
                self.last_update = pg.time.get_ticks()
            self.window.blit(bar, (0, 0))

        pg.display.update()
        self.frame_per_second.tick(self.FPS)
