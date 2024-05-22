import pygame 
import random
import time
from PIL import Image

pygame.init()
#test_puc = pygame.transform.scale(pygame.image.load("685607_72.webp"),(50,50))
FPS=20
window = pygame.display.set_mode((48*14,48*14))
window.fill((0,0,0))
clock = pygame.time.Clock()

class Sprite(pygame.sprite.Sprite):
    def __init__(self,image,size,x,y,direction=None):
        self.prop = image
        self.w,self.h = size  
        self.x = x
        self.y = y
        self.image = pygame.image.load(self.prop)
        self.image = pygame.transform.scale(self.image,(self.w,self.h))
        self.rect = self.image.get_rect()
        self.direction = direction
        self.mask_t = pygame.mask.from_surface(self.image)
        self.size= size

    def show(self):
        window.blit(self.image,(self.x,self.y))#ОТОБРАЖАЕМ SELF.image на window в кардинатах self.x self.y

class Map():
    def __init__(self,file_name):
        self.max_tank = 2
        self.now_tank = 0
        self.tank_in_map = list()
        self.tanks = list()
        self.boom_list = list()
        self.map_list = self.map_surse(file_name)
        self.create_tank(total_tanks=10)
        self.start = time.time()
    
    def spawn_tank(self):
        self.stop = time.time()   
        
        if self.stop-self.start >= 1:
            self.start = self.stop
            if  len(self.tank_in_map)  < self.max_tank:
                if len(self.tanks) != 0:
                    self.tank_in_map.append(self.tanks[0])
                    self.tanks.pop(0)
            
    def create_tank(self,total_tanks,):
        for i in range(total_tanks):
            self.tanks.append(Enemy(image="751.png",
                            size= (40,40),
                            x=random.choice([49, 9*48+1, 6*48+1, ]),
                            y=random.choice([150, 150, 150, ])))
            
    def map_surse(self,file_name):
        my_map = list()
        with open(file_name,"r") as file :
            reade = file.readlines()
            for i in range(14):
                reade[i] = reade[i].split(",")
            x,y = 0,0
            for y1 in range(14):
                for x1 in range(14):
                    if reade[y1][x1] in ("0","0\n"):
                        pass
                    if reade[y1][x1] in ('1',"1\n"):
                        my_map.append(WallSprite(file_name="туша.png",part_size= (48/4,48/4),position=(x1 *48,y1*48) ))
                    if reade[y1][x1] in ('2',"2\n"):
                        my_map.append(WallSprite(file_name="steel.png",part_size= (48/4,48/4),position=(x1 *48,y1*48) ))

        return my_map 

class WallSprite(pygame.sprite.Sprite):
    def __init__(self, file_name, part_size, position):
        super().__init__()
        self.x = position[0]
        self.y = position[1]
        self.part_size = part_size
        self.rows, self.cols = 4, 4  # количество рядов и колонн
        # Создаем Surface с поддержкой альфа-канала для прозрачности
        self.image = pygame.Surface((part_size[0] * self.cols, part_size[1] * self.rows), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=position)
        self.parts = [[None for _ in range(self.rows)] for _ in range(self.cols)]

        # Загрузка и отрисовка каждого кусочка с поддержкой альфа-канала
        for i in range(self.cols):
            for j in range(self.rows):
                part = pygame.image.load(f'textures/{file_name[:-4]}_{i}_{j}.png').convert_alpha()
                self.parts[i][j] = part  # сохраняем ссылку на часть
                self.image.blit(part, (j * part_size[0], i * part_size[1]))
        
        # Создание маски, исключая черный цвет
        self.mask_t = pygame.mask.from_surface(self.image, threshold=127)

    def remove_row_top(self):
        # Удаление верхнего ряда
        for i in range(self.rows):
            if any(self.parts[i]):
                for j in range(self.cols):
                    self.parts[i][j] = None
                break
        self._update_image()

    def remove_row_bottom(self):
        # Удаление нижнего ряда
        for i in reversed(range(self.rows)):
            if any(self.parts[i]):
                for j in range(self.cols):
                    self.parts[i][j] = None
                break
        self._update_image()

    def remove_column_left(self):
        # Удаление левой колонки
        for j in range(self.cols):
            if any(self.parts[i][j] for i in range(self.rows)):
                for i in range(self.rows):
                    self.parts[i][j] = None
                break
        self._update_image()

    def remove_column_right(self):
        # Удаление правой колонки
        for j in reversed(range(self.cols)):
            if any(self.parts[i][j] for i in range(self.rows)):
                for i in range(self.rows):
                    self.parts[i][j] = None
                break
        self._update_image()

    def show(self ):
        window.blit(self.image, self.rect)

    def _update_image(self):
        # Очищаем изображение, делая его полностью прозрачным
        self.image.fill((0, 0, 0, 0))
        for i, row in enumerate(self.parts):
            for j, part in enumerate(row):
                if part is not None:
                    self.image.blit(part, (j * self.part_size[0], i * self.part_size[1]))
        # Обновляем маску после изменений в изображении
        self.mask_t = pygame.mask.from_surface(self.image, threshold=127)
class Steel(WallSprite):
    def __init__(self, file_name, part_size, position):
        super().__init__(file_name, part_size, position)


class Player(Sprite):
    def __init__(self,image,size,x,y,direction="вверх"):
        Sprite.__init__(self,image,size,x,y,direction )
        self.bullets = list()
        self.image_norm = self.image
        self.image_left = pygame.transform.rotate(self.image, 90)
        self.image_right = pygame.transform.rotate(self.image, 270)
        self.image_bakc = pygame.transform.rotate(self.image, 180 )
        self.speed_x = 0
        self.speed_y = 0
        self.direction = direction
        self.mask_norm = pygame.mask.from_surface(self.image_norm) 
        self.mask_left = pygame.mask.from_surface(self.image_left)
        self.mask_right = pygame.mask.from_surface(self.image_right)
        self.mask_back= pygame.mask.from_surface(self.image_bakc)
        self.mask = self.mask_norm
        self.song_tank = pygame.mixer.music.load("battle-city-sfx-16.mp3")
        self.song_motor = pygame.mixer.Sound("4 - Track 4.mp3")
        self.counter = 0
        self.speed_bullset = 8
        self.rect = pygame.Rect(self.x,self.y,self.size[0],self.size[1])
        self.rect_mask = pygame.mask.Mask((self.size[0],self.size[1]))
        self.rect_mask.fill()

       

    def shoot(self):
        if self.counter > self.speed_bullset and len(self.bullets)<=100:
            self.counter = 0 
            self.bullets.append(Bullet(image= "bullet-fotor-bg-remover-20231121185548.png",
                            size= (35//2,50//2),
                            x= self.x + 20,
                            y= self.y + 20, 
                            direction=self.direction,#направление
                            tank=self  
       ))    
        #   self.bullets.append(Bullet(image= "04b08a910161a029fc591a35387fab6b (1).png",
        #                   size= (35//2,50//2),
        #                   x= self.x + 20,
        #                   y= self.y + 20, 
        #                   direction=self.direction,#направление
        #                   tank=self  
        #   ))
            
    def tank_player(self):
        self.new_x,self.new_y = self.x,self.y
        flag = True
        self.counter += 1
        keys_pressed=pygame.key.get_pressed()
        any_key_pressed = keys_pressed[pygame.K_w] or keys_pressed[pygame.K_s] or keys_pressed[pygame.K_d] or keys_pressed[pygame.K_a] 
        if  keys_pressed[pygame.K_SPACE]:
            self.shoot()
        if keys_pressed[pygame.K_w]:
            self.speed_y = -5
            self.new_y += self.speed_y
            self.image= self.image_norm
            self.mask = self.mask_norm
            self.direction = "с"
            
        elif keys_pressed[pygame.K_s]:
            self.speed_y = 5
            self.new_y += self.speed_y
            self.image=self.image_bakc
            self.mask = self.mask_left
            self.direction = "ю"
            
        elif keys_pressed[pygame.K_d]:
            self.speed_x = 5
            self.new_x += self.speed_x
            self.image= self.image_right 
            self.mask = self.mask_right
            self.direction = "в"
            
        elif keys_pressed[pygame.K_a]:
            self.speed_x = -5
            self.new_x += self.speed_x
            self.image= self.image_left
            self.mask = self.mask_back
            self.direction = "з"

        for enemy in level.tank_in_map:
            offset = (enemy.x - self.new_x, enemy.y - self.new_y)    
            if self.mask_t.overlap_area(enemy.mask_t,offset):
                flag = False

        for wall in level.map_list :
            offset = (wall.x - self.new_x, wall.y - self.new_y)    
            if self.mask_t.overlap_area(wall.mask_t,offset):
                flag = False
        if flag: 
            self.x,self.y = self.new_x,self.new_y  
        if not any_key_pressed :
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()  
        self.new_x,self.new_y = self.x, self.y

class Enemy(Player):
    def __init__(self, image, size, x, y, direction="ю",):
        super().__init__(image, size, x, y, direction,)
        self.image = self.image_bakc
        self.song_tank = None
        self.song_motor = None
        self.speed = 5
        self.timer = random.randint(500, 2000)  # Инициализируем таймер для случайного изменения направления
        self.speed_x = 0
        self.speed_y = self.speed
        self.o = 0
        self.direction = direction
        self.new_x = self.x
        self.new_y = self.y
        
    def random_tiptop(self, wall,):
        
            #print(self.direction)
            
            # Откатываем последнее движение
        
        self.counter += 1
        offset = (wall.x - self.rect.x, wall.y - self.rect.y)
        collision = self.rect_mask.overlap(wall.mask_t, offset) 
        if collision:
            self.x -= self.speed_x
            self.y -= self.speed_y
            self.speed_x = 1
            self.speed_y = 1
            self.stop_and_turn()
            print("Dddd")
        else:
            if self.speed_x > 0:
                self.direction = "в"
                self.image = self.image_right
                self.mask = self.mask_right
            elif self.speed_x < 0:
                self.direction = "з"
                self.image = self.image_left
                self.mask = self.mask_left
            if self.speed_y > 0:
                self.direction = "ю"
                self.image = self.image_bakc
                self.mask = self.mask_back
            elif self.speed_y < 0:
                self.direction = "с"
                self.image = self.image_norm
                self.mask = self.mask_norm
        
        
        
        self.check_bounds()  # Проверка границ

    def tank_colision(self,enemy):
    
        pass
    def run_to_base(self,wall):
        offset = (wall.x - self.rect.x, wall.y - self.rect.y)
        collision = self.rect_mask.overlap(wall.mask_t, offset)
        if collision:
            self.x -= self.speed_x
            self.y -= self.speed_y
            if self.direction == "ю" or self.direction== "с":
                d =random.randint(0,2)
                if d == 0:
                    self.direction = "ю"
                    self.speed_x = 0
                    self.speed_y= self.speed
                elif d == 1:
                    self.direction = "в"
                    self.image = self.image_right
                    self.mask = self.mask_right
                    self.speed_x = self.speed
                    self.speed_y= 0


                else:
                    self.direction = "з"
                    self.image = self.image_left
                    self.mask = self.mask_left
                    self.speed_x = -self.speed
                    self.speed_y= 0
            elif self.direction == "з" or self.direction == "в":
                self.direction = "ю"
                self.speed_x = 0
                self.speed_y= self.speed
            print("Dddd")


                    
        
            
            

    def stop_and_turn(self):
        """if self.direction == "с":
            self.image = self.image_norm
            self.mask = self.mask_norm
            self.speed_y = -self.speed
            self.speed_x = 0
            self.direction= random.choice(["з","в"])
        if self.direction == "ю":
            self.image = self.image_bakc
            self.mask = self.mask_back
            self.speed_y = self.speed
            self.speed_x = 0
            self.direction= random.choice(["з","в"])
        if self.direction == "з":
            self.direction = "з"
            self.image = self.image_left
            self.mask = self.mask_left
            self.speed_x = -self.speed
            self.speed_y = 0
            self.direction= random.choice(["c","c","ю"])"""
        
        if self.direction == "с"or self.direction == "ю":
            dd= random.randint(0,1)
            if dd == 1 :
                self.direction = "з"
                self.image = self.image_left
                self.mask = self.mask_left
                self.speed_x = -self.speed
                self.speed_y = 0
            else:
                self.direction = "в"
                self.image = self.image_right
                self.mask = self.mask_right
                self.speed_x = self.speed
                self.speed_y = 0
        elif self.direction == "в" or self.direction =="з":
            df = random.randint(2,3)
            if df == 2:
                self.direction = "с"
                self.image = self.image_norm
                self.mask = self.mask_norm
                self.speed_y = -self.speed
                self.speed_x = 0
            else:
                self.direction = "ю"
                self.image = self.image_bakc
                self.mask = self.mask_back
                self.speed_y = self.speed
                self.speed_x = 0

    def check_bounds(self): # выпезд за пределы карты
        if self.x < 0:
            self.x = 0
            self.speed_y = random.choice([-self.speed, self.speed])
            self.speed_x = 0
        elif self.x > 48*14-40:  # предполагаемая ширина карты минус ширина танка
            self.x = 48*14-40
            self.speed_y = random.choice([-self.speed, self.speed])
            self.speed_x = 0
        if self.y < 0:
            self.y = 5
            self.speed_y = random.choice([-self.speed, self.speed])
            self.speed_x = 0
        elif self.y > 48*14-40:  # предполагаемая высота карты минус высота танка
            self.y = 48*14-40
           
            if self.x < base.x:
                self.direction = "в"  
                self.image = self.image_right
                self.mask = self.mask_right
                self.speed_x = self.speed
                self.speed_y = 0
            else:
                self.direction = "з"
                self.image = self.image_left
                self.mask = self.mask_left
                self.speed_x = -self.speed
                self.speed_y = 0


    def show(self):
        window.blit(self.image,(self.x,self.y))  
        self.o += 1
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x =self.x
        self.rect.y =self.y
        if self.o == 1:
            self.shoot()
            self.o = 0  
           

class Base(Sprite):
    def __init__(self,size,x,y,image):
       super().__init__(image,size,x,y)
       self.over = pygame.image.load("nobase.png")
       self.game_ower = False
       self.over = pygame.transform.scale(self.over,size)

    def show(self):
        window.blit(self.image,(self.x,self.y))
     
class Bullet(Sprite):
    def __init__(self,size,image,x,y,tank,direction=None):
        direction=tank.direction
        Sprite.__init__(self,image,size,x,y,direction)
        self.image_bullet_norm = self.image
        self.image_bullet_left =  pygame.transform.rotate(self.image, 90)
        self.image_bullet_right =  pygame.transform.rotate(self.image, 270)
        self.image_bullet_back =  pygame.transform.rotate(self.image, 180)
        self.mask_norm_B = pygame.mask.from_surface(self.image_bullet_norm) 
        self.mask_left_B = pygame.mask.from_surface(self.image_bullet_left)
        self.mask_right_B = pygame.mask.from_surface(self.image_bullet_right)
        self.mask_back_B = pygame.mask.from_surface(self.image_bullet_back)
        self.speed_x, self.speed_y = 0, 0
        if direction == 'с':
            self.image = self.image_bullet_norm
            self.mask_t = self.mask_norm_B
            self.speed_y = -15
        if direction == 'ю':
            self.image = self.image_bullet_back
            self.mask_t = self.mask_back_B
            self.speed_y = 15
        if direction == 'з':
            self.image = self.image_bullet_left
            self.mask_t = self.mask_left_B
            self.speed_x = -15
        if direction == 'в':
            self.image = self.image_bullet_right
            self.mask_t = self.mask_right_B
            self.speed_x = 15

    def collide_wall(self,wall,sprite):
        offset = (wall.x - self.x,wall.y - self.y)
        if self.mask_t.overlap_area(wall.mask_t, offset) > 0 :
            if self.direction == 'с':
                wall.remove_row_bottom()
            if self.direction == 'ю':
                wall.remove_row_top()
            if self.direction == 'з':
                wall.remove_column_right()
            if self.direction == 'в':
                wall.remove_column_left()
            if self in sprite.bullets:
                sprite.bullets.remove(self)
                


        
    def collide_tank(self,tank,sprite):
        offset = (tank.x - self.x,tank.y - self.y)
        if self.mask_t.overlap_area(tank.mask_t, offset) > 0 :
            #sprite.bullets.remove(self)
            if isinstance(sprite, Player ) and isinstance(tank, Enemy):
                level.boom_list.append(Boom(image ="04b08a910161a029fc591a35387fab6b (1).png", x = tank.x, y = tank.y, size = (30,30)))
                level.tank_in_map.remove(tank)
                sprite.bullets.remove(self)


            if isinstance(tank, Player ) and isinstance(sprite, Enemy):
                player.x = 48*4
                player.y = 48*13

    def collide_bounds(self,tank):
        if self.x < 0:
            tank.bullets.remove(self)
        if self.y < 0:
            tank.bullets.remove(self)
        if self.x > 48*14:
            tank.bullets.remove(self)
        if self.y > 48*14:
            tank.bullets.remove(self)


            



    def collide_base(self,base,sprite):
        offset = (base.x - self.x,base.y - self.y )
        if self.mask_t.overlap_area(base.mask_t, offset) > 0 :
            base.game_ower = True
            try:
                sprite.bullets.remove(self)
            except ValueError:
                pass
        if base.game_ower == True :
            base.image = base.over
            

    def show(self):
        self.x += self.speed_x
        self.y += self.speed_y
        window.blit(self.image,(self.x ,self.y))

class Over(Sprite):
    def __init__(self,image,size,x,y):
        Sprite.__init__(self,image,size,x,y,)

    def over_up(self):
        if self.y != 5*70:
            self.y -= 5
            print(self.y)

class Boom(Sprite):
    def __init__(self,image,size,x,y):
        Sprite.__init__(self,image,size,x,y,)
        self.image_2 = pygame.image.load("04b08a910161a029fc591a3b6b.png")
        self.image_1 = pygame.image.load("04b08a910161a029fc591a35387fab6b (1).png")
        self.image_3 = pygame.image.load("04b08a910161a029f35387fab6b.png")
        self.image_1 = pygame.transform.scale(self.image_1,(25,25))
        self.image_2 = pygame.transform.scale(self.image_2,(30,30))
        self.image_3 = pygame.transform.scale(self.image_3,(40,40))
        self.i = 0
    def animation(self):
        self.i += 1
        if self.i == 1 :
            self.image = self.image_1
        
        if self.i == 4 :
            self.image = self.image_2
        elif self.i == 8:
            self.image = self.image_3
        elif self.i == 12:
            level.boom_list.remove(self)

    
    def show(self):
        self.animation()
        window.blit(self.image,(self.x,self.y))







       
base = Base(image="base.png",
    size = (50,50),
    x=48*7 ,
    y=48*13)



enemy = Enemy(image="751.png",
    size= (40,40),
    x=50,
    y=200)

enemies = [enemy]
player = Player(image="685607_72.png",
    size= (40,40),
    direction="с",
    x=48*4,
    y=48*13)

over = Over(image="game (1).png",
            size=(235,140),
            x = 48*5,
            y= 48*15
            )

bullet = Bullet(image= "bullet-fotor-bg-remover-20231121185548.png",
size= (35//2,50//2),
    x=3300,
    y=3300,
    tank=player
)    
#bullet_boom = Bullet(image = "04b08a910161a029fc591a35387fab6b (1).png",
#size = (20//2,20//2),
#    x= 10,
#    y= 100,
#    tank = player
#
#)
game_ower = False
level_1 = Map(file_name = 'map_1.txt') 
player.song_motor.play(-1)
pygame.mixer.music.play(-1)
start = time.time()

#АБСТРАКЦИЯ
level = level_1

while game_ower == False:
    if time.time() - start > 7:
        
        start = time.time()
    level.spawn_tank()   
    player.tank_player()
    window.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_ower = True 
    for texture in level.map_list:
        texture.show()
       
        #player.player_daun(texture)
        for enemy in level.tank_in_map:
            enemy.run_to_base(texture)

    for enemy in level.tank_in_map:
        enemy.show()
        enemy.new_x,enemy.new_y = enemy.x,enemy.y
        enemy.new_x+=  enemy.speed_x
        enemy.new_y += enemy.speed_y
        
        enemy.random_tiptop(player)
        '''for enemy1 in level.tank_in_map:
            if enemy1== enemy :
                continue
            else:
                enemy1.random_tiptop(enemy)'''
        
        for bullet in enemy.bullets:
            bullet.show()  
            for texture in level.map_list:
                bullet.collide_wall(texture,enemy)  
            bullet.collide_tank(player,enemy)  
            bullet.collide_base(base,enemy) 
    if base.game_ower == True and base.image != base.over:
        base.image = base.over
        
    if base.game_ower == True:
        over.over_up()
    base.show() 
    player.show()
    over.show()
    
    for boom in level.boom_list:
        boom.show()
    for bullet in player.bullets:
        bullet.collide_base(base,player)
        
        bullet.collide_bounds(player)
        bullet.show()
        
        for texture in level.map_list:
        
            
            bullet.collide_wall(texture,player)#player тот кто выпустил пулю,bullet пуля
        for enemy in level.tank_in_map:
            bullet.collide_tank(enemy,player)

    
    pygame.display.update()
    clock.tick(FPS)

    #доделать run_to_base
    