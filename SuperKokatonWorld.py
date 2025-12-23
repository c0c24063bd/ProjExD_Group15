import pygame
import os
import pygame as pg
import sys
from typing import List, Tuple, Optional  # 型ヒント用のインポート

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# --- 定数設定 ---
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
PLATFORM_RANGE = TILE_SIZE * 3
PLATFORM_SPEED = 2
LIMIT_TIME = 30  # 制限時間(秒)

def load_img(name: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """
    画像を読み込み、サイズ変更を行う関数
    [ADD] docstringと型ヒントを追加
    """
    path = os.path.join(ASSET_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        # 画像ファイルが見つからない場合の代替描画
        surf = pygame.Surface(size if size else (TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill((100, 200, 255) if "fish" in name else (200, 200, 200, 255))
        pygame.draw.rect(surf, (0, 0, 255), surf.get_rect(), 2)
        return surf

def get_map() -> List[List[int]]:
    """[KEEP] マップデータを生成する関数"""
    MAP = [[0 for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
    # ... (元のマップ構成ロジック) ...
    for x in range(MAP_WIDTH):
        MAP[-1][x] = 1
    for x in range(MAP_WIDTH):
        if x >= 12 and x <= 13: MAP[-1][x] = 0
        if x >= 15 and x <= 17: MAP[-1][x] = 0
        if x >= 27 and x <= 36: MAP[-1][x] = 0
    for x in range(2, 6): MAP[-7][x] = 1
    for x in range(8, 13): MAP[-4][x] = 1
    for x in range(8, 12): MAP[-13][x] = 1
    for x in range(19, 23): MAP[-12][x] = 1
    for x in range(19, 33): MAP[-9][x] = 1
    for x in range(22, 24): MAP[-10][x] = 1
    for x in range(22, 25): MAP[-11][x] = 1
    for x in range(MAP_WIDTH):
        if x == 2: MAP[-8][x] = 1
        elif x == 7: MAP[-10][x] = 1
        elif x == 12: MAP[-5][x] = 1
        elif x == 19: MAP[-10][x] = 1; MAP[-11][x] = 1; MAP[-13][x] = 1
        elif x == 32: MAP[-10][x] = 1
        elif x == 35: MAP[-9][x] = 1
        elif x == 37: MAP[-7][x] = 1
        elif x == 38: MAP[-11][x] = 1
        elif x == 39: MAP[-4][x] = 1; MAP[-14][x] = 1
        elif x in (14, 18, 24): MAP[-2][x] = 1
        elif x in (30, 33): MAP[-3][x] = 1
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
            MAP[-3][x] = 8
       
        elif x == 35:
            MAP[-14][31] = 8  # スター配置（無敵）
    for x in range(MAP_WIDTH):
        if x == 0: MAP[-2][x] = 5
        if x == 1: MAP[-4][x] = 6
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
    for x in range(15, 18):
        MAP[-8][x] = 7
    return MAP


class Player(pygame.sprite.Sprite):
    """[ADD] プレイヤーキャラクターを管理するクラス"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.original_img = load_img("あるく.png", (TILE_SIZE, TILE_SIZE))
        self.jump_img = load_img("ジャンプ.png", (TILE_SIZE, TILE_SIZE))
        self.invincible_img = load_img("最強こうかとん.png", (TILE_SIZE, TILE_SIZE))  # 無敵画像の読み込み（無敵）
        self.image = self.original_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.dx, self.dy = 0, 0
        self.on_ground = False
        self.fish = 0
        self.facing_right = True
        self.jump_count = 0  # ジャンプ回数
        self.max_jump = 1  # 最大ジャンプ回数
        self.invincibility_timer = 0  # 無敵時間
        self.standing_on = None

    def update(self, keys: pygame.key.ScancodeWrapper, map_rects: List[pygame.Rect], platforms):
        """移動入力とマップとの衝突判定を処理"""
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
        
        if keys[pygame.K_SPACE] and self.on_ground:
            self.dy = JUMP_POWER
            self.on_ground = False
        
        self.dy += GRAVITY
        # 水平方向の移動と静的ブロックとの衝突
        # 横移動の衝突判定
        self.rect.x += self.dx
        for block in map_rects:
            if self.rect.colliderect(block):
                if self.dx > 0:
                    self.rect.right = block.left
                if self.dx < 0:
                    self.rect.left = block.right
        # 移動プラットフォームとの衝突（水平）
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.dx > 0:
                    self.rect.right = platform.rect.left
                if self.dx < 0:
                    self.rect.left = platform.rect.right
        # 垂直
        self.rect.y += self.dy
        self.on_ground = False
        self.standing_on = None
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
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # プレイヤーが落下中に乗る or リフトが上に押し上げてきた場合の処理
                overlap = self.rect.bottom - platform.rect.top
                if overlap > 0 and (self.dy >= 0 or getattr(platform, 'vy', 0) < 0):
                    # 足がリフトの上にあると判断して乗せる
                    self.rect.bottom = platform.rect.top
                    self.dy = 0
                    self.on_ground = True
                    self.standing_on = platform
                elif self.rect.top < platform.rect.bottom and self.dy < 0:
                    # 頭をぶつけた
                    self.rect.top = platform.rect.bottom
                    self.dy = 0
        # プラットフォームで運ぶ（垂直方向の移動をサポート）
        if self.standing_on:
            vx = getattr(self.standing_on, 'vx', 0)
            vy = getattr(self.standing_on, 'vy', 0)
            if vx:
                self.rect.x += vx
                for block in map_rects:
                    if self.rect.colliderect(block):
                        if vx > 0:
                            self.rect.right = block.left
                        elif vx < 0:
                            self.rect.left = block.right
            if vy:
                self.rect.y += vy
                for block in map_rects:
                    if self.rect.colliderect(block):
                        if vy > 0:
                            self.rect.bottom = block.top
                            self.on_ground = True
                        elif vy < 0:
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
    """地上を往復する敵クラス"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.original_img = load_img("inu.png", (TILE_SIZE, TILE_SIZE))
        self.image = self.original_img
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vx = DOG_SPEED
        self.dy = 0
        self.facing_right = True

    def update(self, map_rects: List[pygame.Rect], player: Optional[Player] = None):
        self.rect.x += self.vx
        hit = False
        for block in map_rects:
            if self.rect.colliderect(block):
                hit = True
                if self.vx > 0: self.rect.right = block.left
                else: self.rect.left = block.right
        if hit: self.vx *= -1
        # 向きに合わせて画像を反転
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
        if on_ground: self.dy = 0

class Ghost(pygame.sprite.Sprite):
    """目を合わせると止まる敵クラス"""
    def __init__(self, x: int, y: int):
        super().__init__()
        self.image_normal = load_img("yuurei.png", (TILE_SIZE, TILE_SIZE))
        self.image_stop = load_img("yuurei2.png", (TILE_SIZE, TILE_SIZE))
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.facing_right = True

    def update(self, player: Player):
        px, py = player.rect.center
        gx, gy = self.rect.center
        dx = 1 if px > gx else -1 if px < gx else 0
        dy = 1 if py > gy else -1 if py < gy else 0
        
        self.facing_right = dx > 0
        ghost_side = 'right' if gx > px else 'left'
        look_at_ghost = (ghost_side == 'right' and player.facing_right) or (ghost_side == 'left' and not player.facing_right)
        
        if look_at_ghost:
            self.image = pygame.transform.flip(self.image_stop, True, False) if self.facing_right else self.image_stop
            return
        
        self.image = pygame.transform.flip(self.image_normal, True, False) if self.facing_right else self.image_normal
        self.rect.x += dx * GHOST_SPEED
        self.rect.y += dy * GHOST_SPEED

class Fish(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int):
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
    def serihu(cls, x, y): return cls(x, y, "serihu.png")

class MovingPlatform(pygame.sprite.Sprite):
    def __init__(self, x, y, vx=PLATFORM_SPEED, range_pixels=PLATFORM_RANGE, vertical=False):
        super().__init__()
        self.image = load_img("platform.png", (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_x = x
        self.base_y = y
        self.vx = vx if not vertical else 0
        self.vy = 0 if not vertical else vx
        self.range = range_pixels
        self.vertical = vertical

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if not self.vertical:
            if self.rect.x < self.base_x - self.range or self.rect.x > self.base_x + self.range:
                self.vx *= -1
                self.rect.x = max(self.base_x - self.range, min(self.rect.x, self.base_x + self.range))
        else:
            if self.rect.y < self.base_y - self.range or self.rect.y > self.base_y + self.range:
                self.vy *= -1
                self.rect.y = max(self.base_y - self.range, min(self.rect.y, self.base_y + self.range))


pygame.init()
pg.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Kokaton World")
clock = pygame.time.Clock()
font = pygame.font.Font("C:/Windows/Fonts/msgothic.ttc", 32)
pygame.mixer.music.load("sound/BGM.mp3")  # BGMロード

game_state: str = "title"
start_time = 0

def reset_game():
    global all_sprites, enemies, fish_group, star_group, player, fish_total, map_rects, goal_rect, MAP, MAP_WIDTH, MAP_HEIGHT, platforms, start_time

    MAP = get_map()
    MAP_WIDTH = len(MAP[0])
    MAP_HEIGHT = len(MAP)

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    fish_group = pygame.sprite.Group()
    star_group = pygame.sprite.Group()  # スターグループの初期化（無敵）
    platforms = pygame.sprite.Group()
    all_sprites, enemies, fish_group, map_rects = pygame.sprite.Group(), pygame.sprite.Group(), pygame.sprite.Group(), []
    map_rects = []
    goal_rect = None

    for y, row in enumerate(MAP):
        for x, v in enumerate(row):
            px, py = x * TILE_SIZE, y * TILE_SIZE
            if v == 1: map_rects.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))
            elif v == 2:
                dog = Dog(px, py)
                all_sprites.add(dog); enemies.add(dog)
            elif v == 3:
                ghost = Ghost(px, py)
                all_sprites.add(ghost); enemies.add(ghost)
            elif v == 4:
                fish = Fish(px, py)
                all_sprites.add(fish); fish_group.add(fish)
            elif v == 5:
                goal = Goal(px, py)
                all_sprites.add(goal); goal_rect = goal.rect
            elif v == 6:
                image = Image.serihu(px, py)
                all_sprites.add(image)
                all_sprites.add(Image.serihu(px, py))
            elif v == 8:  # スターの配置（無敵）
                star = Star(px, py)
                all_sprites.add(star)
                star_group.add(star)
            elif v == 7:
                platform = MovingPlatform(px, py, vertical=True)
                all_sprites.add(platform)
                platforms.add(platform)

    player = Player(32, (len(MAP) - 3) * TILE_SIZE)
    all_sprites.add(player)
    fish_total = len(fish_group)
    global score
    score = 0
    start_time = pygame.time.get_ticks()

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
            pygame.quit(); sys.exit()
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
        # [追加] . 制限時間の計算
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        remaining_time = max(0, LIMIT_TIME - elapsed_time)
        if remaining_time <= 0:
            game_state = "gameover"

        # まず移動プラットフォームを更新
        for p in platforms:
            p.update()

        player.update(keys, map_rects, platforms)
        for enemy in enemies:
            if isinstance(enemy, Dog): enemy.update(map_rects, player)
            elif isinstance(enemy, Ghost): enemy.update(player)

        # 敵との衝突判定
        for enemy in enemies.copy():# score
            if player.rect.colliderect(enemy.rect):
                # 犬を踏みつけたら消える
                if player.invincibility_timer > 0:  # 0の場合敵を削除、そうでない場合は消せない（無敵）
                    enemies.remove(enemy)  # 無敵中なら敵を消す(無敵)
                    score += 100  # 敵を倒したらスコア加算
                    all_sprites.remove(enemy)
                else:
                    score += 100  # 敵を倒したらスコア加算
                    if isinstance(enemy, Dog) and player.dy > 0 and player.rect.bottom - enemy.rect.top < TILE_SIZE // 2:
                        if player.dy > 0 and player.rect.bottom - enemy.rect.top < TILE_SIZE // 2:
                            enemies.remove(enemy); all_sprites.remove(enemy)
                            all_sprites.remove(enemy)
                            player.dy = JUMP_POWER // 2
                        else:
                            game_state = "gameover"
                    else:
                        game_state = "gameover"

        # 魚獲得判定
        got_fish = pygame.sprite.spritecollide(player, fish_group, True)
        player.fish += len(got_fish)

        got_star = pygame.sprite.spritecollide(player, star_group, True)  # スタートの接触（タイマーの起動）「メインループ内の衝突判定でプレイヤーがスターに触れるタイマーがセット）（無敵）
        if got_star:
            player.invincibility_timer = INVINCIBLE_TIME

        # [追加2] . 魚をすべて獲得したらクリア
        if player.fish >= fish_total:
            game_state = "clear"

        if player.rect.top > SCREEN_HEIGHT:
            game_state = "gameover"
    

    camera_x = 0
    if 'player' in locals():
        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2, (MAP_WIDTH * TILE_SIZE) - SCREEN_WIDTH))
        screen.fill((110, 190, 255))

    if game_state == "title":
        txt1 = font.render("Super Kokaton World", True, (50, 50, 50))
        txt2 = font.render("スペースキーでスタート", True, (0,0,0))
        screen.blit(txt1, (SCREEN_WIDTH//2 - txt1.get_width()//2, 150))
        screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 260))
    else:
        for r in map_rects:
            pygame.draw.rect(screen, (130, 100, 70), (r.x - camera_x, r.y, TILE_SIZE, TILE_SIZE))
        for sprite in all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - camera_x, sprite.rect.y))

        # UI表示
        fish_txt = font.render(f"魚: {player.fish}/{fish_total}", True, (0,0,0))
        screen.blit(fish_txt, (10, 10))

        # [追加1]. 制限時間の表示（30秒以下で赤色）
        timer_color = (255, 0, 0) if remaining_time <= 30 else (0, 0, 0)
        time_txt = font.render(f"残り時間: {remaining_time}", True, timer_color)
        screen.blit(time_txt, (SCREEN_WIDTH - 200, 10))
        score_txt = font.render(f"スコア: {score}", True, (0,0,0)) # score表示
        screen.blit(score_txt, (10, 40))

        if game_state == "gameover":
            txt = font.render("GAME OVER", True, (255,0,0))
            # [追加3] . ゲームオーバー時の獲得数表示
            score_txt = font.render(f"獲得した魚の数: {player.fish}", True, (255, 255, 255))
            screen.blit(txt, (SCREEN_WIDTH//2 - txt.get_width()//2, 180))
            screen.blit(score_txt, (SCREEN_WIDTH//2 - score_txt.get_width()//2, 230))
            txt2 = font.render("スペースキーでタイトルへ", True, (255,255,255))
            screen.blit(txt2, (SCREEN_WIDTH//2 - txt2.get_width()//2, 280))
            
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