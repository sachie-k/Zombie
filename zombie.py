import pyxel
import random

TILE_SPAWN1 = (2, 3)
TILE_SPAWN2 = (0, 3)

chkpoint = [(2, 0),(6, 0),(2, 7),(6, 7)] # girlの左上からのチェックする座標
coin_tile = []

def is_wall(cx, cy):
    c = False
    if cx < 0 or pyxel.width - 8 < cx:
        c = True
    return c

def is_floor(cx, cy):
    c = False
    for cpx, cpy in chkpoint:
        xi = (cx + cpx) // 8
        yi = (cy + cpy) // 8
        if pyxel.tilemap(0).pget(xi, yi) == (1, 0): # どこかが床に接触していたら
            c = True
    return c

def get_tile(tile_x, tile_y):
    return pyxel.tilemap(0).pget(tile_x, tile_y)

def cleanup_list(list):
    i = 0
    while i < len(list):
        elem = list[i]
        if elem.is_alive:
            i += 1
        else:
            list.pop(i)
class Girl:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.pldir = 1 # 方向（1:右、-1:左）
        self.is_alive = True
        self.jump = 0 # 0:床にいる状態，1:ジャンプ中，2:落下中
        self.score = 0
    
    def update(self):
        
        mx, my = get_tile(pyxel.mouse_x//8, pyxel.mouse_y//8)
        
        # キー操作で移動
        if (pyxel.btn(pyxel.KEY_LEFT) or \
                ((0 <= mx <= 1) and (4 <= my <= 5) and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT))):
            # -3まで徐々に変化
            if -3 < self.dx:
                self.dx -= 1
            self.pldir = -1
        elif pyxel.btn(pyxel.KEY_RIGHT) or \
                ((2 <= mx <= 3) and (4 <= my <= 5) and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)):
            # 3まで徐々に変化
            if self.dx < 3:
                self.dx += 1
            self.pldir = 1 
        else:
            # 急に止まれない
            self.dx = int(self.dx*0.7)       
        
        # 横方向の移動(1ずつ調べる)
        lr = pyxel.sgn(self.dx) # 引数が正なら1，0なら0，負のとき-1
        loop = abs(self.dx)
        while 0 < loop:
            if is_wall(self.x + lr, self.y) == True or is_floor(self.x + lr, self.y) == True:
                self.dx = 0
                break
            self.x += lr
            loop -= 1
            
        # ジャンプと落下
        if self.jump == 0: # 床
            if is_floor(self.x, self.y+1) == False : # 床がない時は落下
                self.jump = 2
            if pyxel.btnp(pyxel.KEY_SPACE) or \
                ((0 <= mx <= 3) and (6 <= my <= 7) and pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)):
                self.dy = 8
                self.jump = 1 # ジャンプ開始
                pyxel.play(3, 0)
        else:
            self.dy -= 1
            if self.dy < 0:
                self.jump = 2 # 頂点で落下開始 
        
        ud = pyxel.sgn(self.dy)
        loop = abs(self.dy)
        while 0 < loop:
            if is_floor(self.x, self.y - ud) == True:
                self.dy = 0
                if self.jump == 1: 
                    self.jump = 2 # 壁にぶつかって落下
                elif self.jump == 2:
                    self.jump = 0 # 着地(落下終了)
                break
            self.y -= ud
            loop -= 1
        
        # コイン判定
        xi = (self.x + 4) // 8
        yi = (self.y + 4) // 8
        if pyxel.tilemap(0).pget(xi, yi) == (1, 1): # コイン
            self.score += 1
            pyxel.tilemap(0).pset(xi, yi, (0, 0))
            coin_tile.append((xi, yi))
            pyxel.play(3, 1)
        
        return
    
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 8, self.pldir*8, 8, 0)
        
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = 0.05
        self.dy = 0
        self.endir = 1
        self.is_alive = True

    def update(self):
        
        if is_wall(self.x, self.y) == True:
            self.dx = self.dx * (-1)
            self.endir = self.endir * (-1) 
        
        if pyxel.frame_count % 500 == 0:
            self.endir = random.choices([-1,1])[0]
            if self.endir < 0:
                self.dx = -0.05
            else:
                self.dx = 0.05
        self.x += self.dx
        self.y += self.dy       

class EnemyA(Enemy):
    
    def update(self):
        
        super().update()
        
        if is_floor(self.x, self.y + 1) == False:
            self.dx = self.dx * (-1)
            self.endir = self.endir * (-1) 
            
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 0, 16, self.endir*8, 8, 0)
    
class EnemyB(Enemy):

    def update(self):
        
        super().update()
        
        if is_floor(self.x, self.y + 1) == True:
            self.dy = 0
        else:
            self.y -= -1
            
    def draw(self):
        pyxel.blt(self.x, self.y, 0, 8, 16, self.endir*8, 8, 0)    

class App:
    def __init__(self):
        pyxel.init(128, 160, title="ZOMBIE HUNTER")
        pyxel.load("zombie_ast.pyxres")
        
        self.enemies = []

        self.girl = Girl(8, 112)
        self.spawn_enemy(0, 127)
        pyxel.playm(0, loop=True)

        pyxel.run(self.update, self.draw)

    def update(self):
        
        self.girl.update()
        for enemy in self.enemies:
            if abs(self.girl.x - enemy.x) < 6 and abs(self.girl.y - enemy.y) < 6:
                self.girl.is_alive = False
                return
            enemy.update()
            
        cleanup_list(self.enemies)
        
        return
        
    def draw(self):
        pyxel.cls(0)
        pyxel.bltm(0, 0, 0, 0, 0, pyxel.width, pyxel.height, 0)
        
        # Change enemy spawn tiles invisible
        pyxel.image(0).rect(0, 24, 24, 8, 0)
        
        if self.girl.is_alive == True:
            self.girl.draw()
            for enemy in self.enemies:
                enemy.draw()       
            text = "SCORE:{}".format(self.girl.score)
            pyxel.text(45, 6, text, 8)
        else:
            pyxel.text(45, 60, "GAME OVER", 10)
            pyxel.stop()
            self.replay()
            
        if self.girl.score == 10:
            pyxel.text(45, 60, "GAME CLEAR", 9)
            pyxel.stop()
            self.replay()
            
        # mouse icon
        pyxel.blt(pyxel.mouse_x, pyxel.mouse_y, 0, 0, 64, 16, 16, 0)
        
        return
    
    def spawn_enemy(self, left_x, right_x):
        left_x = pyxel.ceil(left_x / 8) # x以上の最小の整数を返す
        right_x = pyxel.floor(right_x / 8) # x以下の最大の整数を返す
        for x in range(left_x, right_x + 1):
            for y in range(16):
                tile = get_tile(x, y)
                if tile == TILE_SPAWN1:
                    self.enemies.append(EnemyA(x * 8, y * 8))
                elif tile == TILE_SPAWN2:
                    self.enemies.append(EnemyB(x * 8, y * 8))
            
    def replay(self):
        # retry button
        pyxel.text(45, 100, "> REPLAY", 1)
                    
        if pyxel.btnp(pyxel.KEY_RETURN) or \
            (pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT) and (67 <= pyxel.mouse_x <= 99) and (90 <= pyxel.mouse_y <= 106)):
            self.girl = Girl(8, 112)
            self.enemies = []
            self.spawn_enemy(0, 127)
            for xi, yi in coin_tile:
                pyxel.tilemap(0).pset(xi, yi, (1, 1))
            pyxel.playm(0, loop=True)
            

App()
