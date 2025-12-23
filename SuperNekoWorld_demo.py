import pygame
import os
import pygame as pg

os.chdir(os.path.dirname(os.path.abspath(__file__)))

os.chdir(os.path.dirname(os.path.abspath(__file__)))
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
TILE_SIZE = 32
GRAVITY = 1
JUMP_POWER = -16
PLAYER_SPEED = 5
GHOST_SPEED = 1
DOG_SPEED = -2
FISH_SIZE = 24
MAP_WIDTH = 40
MAP_HEIGHT = 15
ASSET_DIR = "images"  # アセットディレクトリのパス
INVINCIBLE_TIME = 200 # 無敵時間（フレーム数：60fpsで約5秒）（無敵）

def load_img(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size if size else (TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((100, 200, 255) if "fish" in name else (200, 200, 200, 255))
        pygame.draw.rect(surf, (0, 0, 255), surf.get_rect(), 2)
        return surf

def get_map():
    MAP = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    for x in range(MAP_WIDTH):
        MAP[-1][x] = 1
    for x in range(MAP_WIDTH):
        if x >= 12 and x <= 13:
            MAP[-1][x] = 0
        if x >= 15 and x <= 17:
            MAP[-1][x] = 0
        if x >= 27 and x <= 36:
            MAP[-1][x] = 0
    for x in range(2, 6):
        MAP[-7][x] = 1
    for x in range(8, 13):
        MAP[-4][x] = 1
    for x in range(8, 12):
        MAP[-13][x] = 1
    for x in range(19, 23):
        MAP[-12][x] = 1
    for x in range(19, 33):
        MAP[-9][x] = 1
    for x in range(22, 24):
        MAP[-10][x] = 1
    for x in range(22, 25):
        MAP[-11][x] = 1
    for x in range(MAP_WIDTH):
        if x == 2: 
            MAP[-8][x] = 1
        elif x == 7:
            MAP[-10][x] = 1
        elif x == 12:
            MAP[-5][x] = 1
        elif x == 19:
            MAP[-10][x] = 1
            MAP[-11][x] = 1
            MAP[-13][x] = 1
        elif x == 32:
            MAP[-10][x] = 1
        elif x == 35:
            MAP[-9][x] = 1
        elif x == 37:
            MAP[-7][x] = 1
        elif x == 38:
            MAP[-11][x] = 1
        elif x == 39:
            MAP[-4][x] = 1
            MAP[-14][x] = 1
        elif x == 14 or x == 18 or x == 24: 
            MAP[-2][x] = 1
        elif x == 30 or x == 33:
            MAP[-3][x] = 1
    for x in range(MAP_WIDTH):
        if x == 10:
            MAP[-7][x] = 2
        elif x == 12:
            MAP[-15][x] = 2
        elif x == 13:
            MAP[-7][x] = 2
        elif x == 21:
            MAP[-10][x] = 2
        elif x == 24:
            MAP[-5][x] = 2
        elif x == 28:
            MAP[-13][x] = 2
        elif x == 33:
            MAP[-13][x] = 2
        elif x == 30:
            MAP[-13][x] = 3
        elif x == 5:
            MAP[-3][x] = 7
        elif x == 20:
            MAP[-5][x] = 7  # スター配置（無敵）
        elif x == 35:
            MAP[-14][31] = 7  # スター配置（無敵）
    for x in range(MAP_WIDTH):
        if x == 0:
            MAP[-2][x] = 5
        if x == 1:
            MAP[-4][x] = 6
    for x in range(MAP_WIDTH):
        if x == 2:
            MAP[-13][x] = 4
        elif x == 10:
            MAP[-2][x] = 4      
        elif x == 11:
            MAP[-14][x] = 4
        elif x == 12:
            MAP[-7][x] = 4
        elif x == 17:
            MAP[-10][x] = 4
        elif x == 24:
            MAP[-10][x] = 4
        elif x == 30:
            MAP[-4][x] = 4
        elif x == 33:
            MAP[-4][x] = 4
        elif x == 39:
            MAP[-2][x] = 4
            MAP[-15][x] = 4
    return MAP

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_img = load_img("あるく.png", (TILE_SIZE, TILE_SIZE))
        self.jump_img = load_img("ジャンプ.png", (TILE_SIZE, TILE_SIZE))
        self.invincible_img = load_img("最強こうかとん.png", (TILE_SIZE, TILE_SIZE))  # 無敵画像の読み込み（無敵）
        self.image = self.original_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dx = 0
        self.dy = 0
        self.on_ground = False
        self.fish = 0
        self.facing_right = True
        self.jump_count = 0  # ジャンプ回数
        self.max_jump = 1  # 最大ジャンプ回数
        self.invincibility_timer = 0  # 無敵時間

    def update(self, keys, map_rects):
        self.dx = 0
        if keys[pygame.K_LEFT]:
            self.dx = -PLAYER_SPEED
            if self.facing_right:
                self.facing_right = False
                self.image = pygame.transform.flip(self.original_img, True, False)
        if keys[pygame.K_RIGHT]:
            self.dx = PLAYER_SPEED
            if not self.facing_right:
                self.facing_right = True
                self.image = self.original_img
        # if keys[pygame.K_SPACE] and self.jump_count < self.max_jump:
        #     self.dy = JUMP_POWER
        #     self.jump_count += 1  # ジャンプ回数を1増やす
        #     self.on_ground = False
        self.dy += GRAVITY
        self.rect.x += self.dx
        for block in map_rects:
            if self.rect.colliderect(block):
                if self.dx > 0:
                    self.rect.right = block.left
                if self.dx < 0:
                    self.rect.left = block.right
        self.rect.y += self.dy
        self.on_ground = False
        for block in map_rects:
            if self.rect.colliderect(block):
                if self.dy > 0:
                    self.rect.bottom = block.top
                    self.dy = 0
                    self.on_ground = True
                    self.jump_count = 0  # 地面についたときジャンプ回数をリセット
                elif self.dy < 0:
                    self.rect.top = block.bottom
                    self.dy = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAP_WIDTH * TILE_SIZE:
            self.rect.right = MAP_WIDTH * TILE_SIZE
        if self.invincibility_timer > 0:  # 無敵タイマーのカウントダウン（無敵）
            self.invincibility_timer -= 1  # 無敵タイマーをデクリメント(無敵)
        if self.invincibility_timer > 0:  # 無敵中の画像切り替え（無敵）
            self.image = self.invincible_img if self.facing_right else pygame.transform.flip(self.invincible_img, True, False)  # 無敵画像に切り替え（無敵）
        else:
            # ジャンプ中の画像切り替え
            if self.dy < 0:
                self.image = self.jump_img if self.facing_right else pygame.transform.flip(self.jump_img, True, False)
            else:
                self.image = self.original_img if self.facing_right else pygame.transform.flip(self.original_img, True, False)

class Dog(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.original_img = load_img("inu.png", (TILE_SIZE, TILE_SIZE))
        self.image = self.original_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = DOG_SPEED
        self.dy = 0
        self.facing_right = True

    def update(self, map_rects, player=None):
        self.rect.x += self.vx
        hit = False
        for block in map_rects:
            if self.rect.colliderect(block):
                hit = True
                if self.vx > 0:
                    self.rect.right = block.left
                else:
                    self.rect.left = block.right
        if hit:
            self.vx *= -1
        if self.vx < 0 and not self.facing_right:
            self.facing_right = True
            self.image = self.original_img
        elif self.vx > 0 and self.facing_right:
            self.facing_right = False
            self.image = pygame.transform.flip(self.original_img, True, False)
        self.dy += GRAVITY
        self.rect.y += self.dy
        on_ground = False
        for block in map_rects:
            if self.rect.colliderect(block):
                if self.dy > 0:
                    self.rect.bottom = block.top
                    self.dy = 0
                    on_ground = True
                elif self.dy < 0:
                    self.rect.top = block.bottom
                    self.dy = 0
        if on_ground:
            self.dy = 0

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image_normal = load_img("yuurei.png", (TILE_SIZE, TILE_SIZE))
        self.image_stop = load_img("yuurei2.png", (TILE_SIZE, TILE_SIZE))
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.facing_right = True
    def update(self, player):
        px, py = player.rect.center
        gx, gy = self.rect.center
        dx = 1 if px > gx else -1 if px < gx else 0
        dy = 1 if py > gy else -1 if py < gy else 0
        if dx > 0:
            self.facing_right = True
        elif dx < 0:
            self.facing_right = False
        ghost_side = 'right' if gx > px else 'left'
        look_at_ghost = (ghost_side == 'right' and player.facing_right) or (ghost_side == 'left' and not player.facing_right)
        if look_at_ghost:
            if self.facing_right:
                self.image = pygame.transform.flip(self.image_stop, True, False)
            else:
                self.image = self.image_stop
            return
        if self.facing_right:
            self.image = pygame.transform.flip(self.image_normal, True, False)
        else:
            self.image = self.image_normal
        self.rect.x += dx * GHOST_SPEED
        self.rect.y += dy * GHOST_SPEED

class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img("fish.png", (FISH_SIZE, FISH_SIZE))
        self.rect = self.image.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))

class Star(pygame.sprite.Sprite):  # スタークラス（無敵）
    """
    Star の Docstring
    スターアイテムを表すクラスです。プレイヤーがこのアイテムに触れると一定時間無敵になります。
    Attributes:
        image (pygame.Surface): スターの画像。
        rect (pygame.Rect): スターの位置とサイズを表す矩形。
    Methods:
        __init__(self, x, y): スターオブジェクトを初期化します。
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img("スター.png", (TILE_SIZE, TILE_SIZE))  # スター画像の読み込み（無敵）
        self.rect = self.image.get_rect(topleft=(x, y))  # スターの位置設定（無敵）

class Goal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = load_img("goal_neko.png", (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

class Image(pygame.sprite.Sprite):
    def __init__(self, x, y, img_name):
        super().__init__()
        self.image = load_img(img_name)
        self.rect = self.image.get_rect(topleft=(x, y))

    @classmethod
    def serihu(cls, x, y):
        return cls(x, y, "serihu.png")

pygame.init()
pg.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Neko World")
clock = pygame.time.Clock()
font = pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", 32)
pg.mixer.music.load("sound/BGM.mp3")  # BGMロード

game_state: str = "title"

def reset_game():
    global all_sprites, enemies, fish_group, star_group, player, fish_total, map_rects, goal_rect, MAP, MAP_WIDTH, MAP_HEIGHT

    MAP = get_map()
    MAP_WIDTH = len(MAP[0])
    MAP_HEIGHT = len(MAP)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    fish_group = pygame.sprite.Group()
    star_group = pygame.sprite.Group()  # スターグループの初期化（無敵）
    map_rects = []
    goal_rect = None

    for y, row in enumerate(MAP):
        for x, v in enumerate(row):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            if v == 1:
                map_rects.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))
            elif v == 2:
                dog = Dog(px, py)
                all_sprites.add(dog)
                enemies.add(dog)
            elif v == 3:
                ghost = Ghost(px, py)
                all_sprites.add(ghost)
                enemies.add(ghost)
            elif v == 4:
                fish = Fish(px, py)
                all_sprites.add(fish)
                fish_group.add(fish)
            elif v == 5:
                goal = Goal(px, py)
                all_sprites.add(goal)
                goal_rect = goal.rect
            elif v == 6:
                image = Image.serihu(px, py)
                all_sprites.add(image)
            elif v == 7:  # スターの配置（無敵）
                star = Star(px, py)
                all_sprites.add(star)
                star_group.add(star)

    player_start_y = (MAP_HEIGHT - 3) * TILE_SIZE
    player = Player(32, player_start_y)
    all_sprites.add(player)

    fish_total = len(fish_group)

reset_game()

# --- メインループ ---
while True:
    keys = pygame.key.get_pressed()
    if game_state == "playing" and not pg.mixer.music.get_busy():
        pg.mixer.music.play(loops=-1)  # ゲーム中BGMをループ再生
    elif game_state in ("gameover", "title", "clear") and pg.mixer.music.get_busy():
        pg.mixer.music.stop()  # ゲーム中以外の時BGMを停止
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # ESCで一時停止／再開（吉留)（一時停止）
            if game_state == "playing":
                game_state = "pause"
            elif game_state == "pause":
                game_state = "playing"

        if game_state == "title":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                reset_game()
                game_state = "playing"
        elif game_state in ("gameover", "clear"):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_state = "title"
        if event.type == pygame.KEYDOWN:  
            if event.key == pygame.K_SPACE:
                if player.fish >= 5:
                    player.max_jump = 2  # 魚5個以上の時、2段ジャンプ
                else:
                    player.max_jump = 1
                if player.jump_count < player.max_jump:
                    snd = pg.mixer.Sound("sound/jump.mp3")
                    snd.play()  # ジャンプ時jump.mp3
                    player.dy = JUMP_POWER
                    player.jump_count += 1
                    player.on_ground = False


    if game_state == "playing":
        player.update(keys, map_rects)
        for enemy in enemies:
            if isinstance(enemy, Dog):
                enemy.update(map_rects, player)
            elif isinstance(enemy, Ghost):
                enemy.update(player)

        for enemy in enemies.copy():
            if player.rect.colliderect(enemy.rect):
                if player.invincibility_timer > 0:  # 0の場合敵を削除、そうでない場合は消せない（無敵）
                    enemies.remove(enemy)  # 無敵中なら敵を消す(無敵)
                    all_sprites.remove(enemy)
                else:
                    if isinstance(enemy, Dog):
                        if player.dy > 0 and player.rect.bottom - enemy.rect.top < TILE_SIZE // 2:
                            enemies.remove(enemy)
                            all_sprites.remove(enemy)
                            player.dy = JUMP_POWER // 2
                        else:
                            game_state = "gameover"
                    else:
                        game_state = "gameover"

        got_fish = pygame.sprite.spritecollide(player, fish_group, True)
        player.fish += len(got_fish)

        got_star = pygame.sprite.spritecollide(player, star_group, True)  # スタートの接触（タイマーの起動）「メインループ内の衝突判定でプレイヤーがスターに触れるタイマーがセット）（無敵）
        if got_star:
            player.invincibility_timer = INVINCIBLE_TIME

        if 'goal_rect' in locals() and player.rect.colliderect(goal_rect):
            if player.fish >= fish_total:
                game_state = "clear"

        if player.rect.top > SCREEN_HEIGHT:
            game_state = "gameover"
    

    camera_x = 0
    if 'player' in locals():
        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, (MAP_WIDTH * TILE_SIZE) - SCREEN_WIDTH))

    if game_state == "title":
        screen.fill((110, 190, 255))
        txt1 = font.render("Super Neko World", True, (50, 50, 50))
        txt2 = font.render("スペースキーでスタート", True, (0,0,0))
        screen.blit(txt1, (SCREEN_WIDTH//2 - txt1.get_width()//2, 150))
        screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 260))
    else:
        screen.fill((110, 190, 255))
        for r in map_rects:
            rx = r.x - camera_x
            if -TILE_SIZE < rx < SCREEN_WIDTH:
                pygame.draw.rect(screen, (130, 100, 70), (rx, r.y, TILE_SIZE, TILE_SIZE))
        if 'goal_rect' in locals() and goal_rect:
            rx = goal_rect.x - camera_x

        for sprite in all_sprites:
            rx = sprite.rect.x - camera_x
            if -TILE_SIZE < rx < SCREEN_WIDTH:
                screen.blit(sprite.image, (rx, sprite.rect.y))

        fish_txt = font.render(f"魚: {player.fish}/{fish_total}", True, (0,0,0))
        screen.blit(fish_txt, (10, 10))

        if game_state == "gameover":
            txt = font.render("GAME OVER", True, (255,0,0))
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 220))
            txt2 = font.render("スペースキーでタイトルへ", True, (255,255,255))
            screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 260))
        if game_state == "clear":
            txt = font.render("STAGE CLEAR!", True, (0,0,255))
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 220))
            txt2 = font.render("スペースキーでタイトルへ", True, (0,0,0))
            screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 260))
        if game_state == "pause":  # 一時停止画面表示(吉留)（一時停止）
            pause_txt = font.render("PAUSE", True, (0, 0, 0))
            info_txt = font.render("ESCで再開", True, (0, 0, 0))

            screen.blit(
                pause_txt,
                (SCREEN_WIDTH // 2 - pause_txt.get_width() // 2, 200)
            )
            screen.blit(
                info_txt,
                (SCREEN_WIDTH // 2 - info_txt.get_width() // 2, 250)
            )


    pygame.display.update()
    clock.tick(60)
