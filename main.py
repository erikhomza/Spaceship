import pygame as pg
import random
import os
import pickle


pg.init()

clock = pg.time.Clock()
fps = 20
score = 0
if os.path.exists('./highscore.dat'):
    highscore = pickle.load(open("highscore.dat", "rb"))
else:
    highscore = 0
player_ammo = 1
screen_width = 1000
screen_height = 800
shot_cooldown = 20
score_cooldown = 100
screen = pg.display.set_mode((screen_width, screen_height))
bg = pg.image.load("background-black.png").convert_alpha()
bg = pg.transform.scale(bg, (screen_width, screen_height))
purple = (255, 0, 255)
font = pg.font.Font("Turok.ttf", 60)

pg.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0))


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def reset_game():
    ammo_group.empty()
    obstacle_group.empty()
    projectile_group.empty()
    score = 0
    player_ammo = 1
    end = True
    spaceship = Spaceship(500, 400)
    while end:
        pg.display.update()
        draw_text("YOU LOST! press r to restart", font, purple, 110, 300)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    end = False
    return score, player_ammo, spaceship


def pause(run):
    game_paused = True
    draw_text("GAME PAUSED", font, purple, 330, 300)
    pg.display.update()
    while game_paused:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                game_paused = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    game_paused = False
    return run


class Spaceship:
    def __init__(self, x, y):
        self.img = pg.image.load("pixel_ship_yellow.png").convert_alpha()
        self.image = pg.transform.scale(self.img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.speed = 10

    def update(self):
        pos = pg.mouse.get_pos()

        if pg.mouse.get_pressed()[0] == 1:
            self.speed = 20
        else:
            self.speed = 10
        if pos[0] > self.rect.centerx:
            self.rect.centerx += self.speed
        if pos[0] < self.rect.centerx:
            self.rect.centerx -= self.speed
        if pos[1] > self.rect.centery:
            self.rect.centery += self.speed
        if pos[1] < self.rect.centery:
            self.rect.centery -= self.speed
        screen.blit(self.image, self.rect)


class Obstacle(pg.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pg.image.load("castleCenter.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.speed = random.randint(3, 7)

    def update(self):
        self.rect.y += self.speed
        screen.blit(self.image, self.rect)


class Ammo(pg.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pg.image.load("laserYellowBurst.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = 0
        self.speed = random.randint(3, 5)

    def update(self):
        self.rect.y += self.speed
        screen.blit(self.image, self.rect)


class Projectile(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load("laserYellowVertical.png").convert_alpha()
        self.image = pg.transform.scale(self.image, (30, 30))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.y -= 10
        screen.blit(self.image, self.rect)


obstacle_group = pg.sprite.Group()
ammo_group = pg.sprite.Group()
projectile_group = pg.sprite.Group()
spaceship = Spaceship(500, 400)

run = True
while run:
    clock.tick(fps)
    screen.blit(bg, (0, 0))
    spaceship.update()

    if score > highscore:
        highscore = score

    draw_text(f"score: {score}", font, purple, 30, 20)
    draw_text(f"highscore: {highscore}", font, purple, 30, 60)
    draw_text(f"ammo:{player_ammo}", font, purple, 780, 20)

    for event in pg.event.get():
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_p:
                run = pause(run)

    if shot_cooldown > 0:
        shot_cooldown -= 1
    if score_cooldown > 0:
        score_cooldown -= 1

    for i in range(0, 20):
        n = random.randint(1, 200)
        if n == 9:
            obstacle = Obstacle(i * 50)
            obstacle_group.add(obstacle)
    obstacle_group.update()

    for obstacle in obstacle_group:
        if pg.sprite.collide_rect(obstacle, spaceship):
            if score == highscore:
                pickle.dump(highscore, open("highscore.dat", "wb"))
            score, player_ammo, spaceship = reset_game()

    for i in range(0, 20):
        n = random.randint(1, 1000)
        if n == 9:
            ammo = Ammo(i * 50)
            ammo_group.add(ammo)
    ammo_group.update()

    for ammo in ammo_group:
        if pg.sprite.collide_rect(ammo, spaceship):
            player_ammo += 1
            ammo.kill()

    key = pg.key.get_pressed()
    if shot_cooldown == 0:
        if key[pg.K_SPACE]:
            if player_ammo > 0:
                projectile = Projectile(spaceship.rect.centerx - 15, spaceship.rect.centery - 25)
                projectile_group.add(projectile)
                player_ammo -= 1
                shot_cooldown = 20
    for projectile in projectile_group:
        if pg.sprite.spritecollide(projectile, obstacle_group, True):
            projectile.kill()
    projectile_group.update()
    if score_cooldown == 0:
        score += 1
        score_cooldown = 100

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    pg.display.update()

pg.quit()