#!/usr/bin/python3

import os
import pygame
import random
import math
from settings import *

# Set up assets folders
game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "img")
snd_folder = os.path.join(game_folder, "snd")

class Tile(pygame.sprite.Sprite):
    # Sprite for a tile
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, "rock_tile.png")).convert()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)

    def update(self):
        pass

class Egg(pygame.sprite.Sprite):
    # Sprite for a tile
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, "egg.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)

    def update(self):
        pass        

class Enemy(pygame.sprite.Sprite):
    # Sprite for the redshirt(s)
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, "redshirt.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.direction = None
        self.x_speed = REDSHIRT_SPEED
        self.y_speed = REDSHIRT_SPEED   
        self.x_index = 0
        self.y_index = 0   
        self.dir_change = True
        self.firing = False
        self.old_dir = 0
        self.id = None

    def update(self):
      
        if self.direction == DIR_RIGHT:
            self.rect.x += self.x_speed
            if self.rect.right == WIDTH:
                self.direction = DIR_LEFT
                self.dir_change = True
        elif self.direction == DIR_LEFT:
            self.rect.x -= self.x_speed  
            if self.rect.left == 0:
                self.direction = DIR_RIGHT  
                self.dir_change = True        
        elif self.direction == DIR_UP:
            self.rect.y -= self.y_speed
            if self.rect.top == 0:
                self.direction = DIR_DOWN
                self.dir_change = True
        elif self.direction == DIR_DOWN:
            self.rect.y += self.y_speed  
            if self.rect.bottom == HEIGHT:
                self.direction = DIR_UP  
                self.dir_change = True

        if self.dir_change == True:
            self.dir_change = False
            self.rect.centerx = (self.rect.centerx//TILESIZE)*TILESIZE + TILESIZE/2
            self.rect.centery = (self.rect.centery//TILESIZE)*TILESIZE + TILESIZE/2  

            # Reset image orientation
            if self.old_dir == DIR_LEFT or self.old_dir == DIR_RIGHT:
                if self.old_dir == DIR_RIGHT:
                    self.image = pygame.transform.flip(self.image, True, False) 
            self.old_dir = self.direction

            # Set new image orientation
            if self.direction == DIR_RIGHT:
                self.image = pygame.transform.flip(self.image, True, False)                 

                     
class Player(pygame.sprite.Sprite):
    # Sprite for the player
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, "horta.png")).convert()
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.x_speed = 2
        self.y_speed = 2
        self.orientation = VERTICAL
        self.orientation_change = False
        self.dir = DIR_UP

    def update(self):
        if self.rect.bottom > HEIGHT - 1:
            self.rect.bottom = HEIGHT - 1
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH - 1:
            self.rect.right = WIDTH - 1 

        if self.orientation_change:
            self.orientation_change = False
            angle = 0
            #self.image = pygame.transform.rotate(self.image, angle) 
            if self.orientation == VERTICAL:
                self.orientation = HORIZONTAL
                if self.dir == DIR_LEFT:
                    angle = 90
                else:
                    angle = 270
            else:
                self.orientation = VERTICAL
                if self.dir == DIR_UP:
                    angle = 0
                else:
                    angle = 180
            #self.image = pygame.transform.rotate(self.image, angle) 

            # Adjust creature position to align with ground tiles
            self.rect.centerx = (self.rect.centerx//TILESIZE)*TILESIZE + TILESIZE/2
            self.rect.centery = (self.rect.centery//TILESIZE)*TILESIZE + TILESIZE/2   
                                           
       
    def move(self, keys):

        dir = self.dir

        # Process keydowns
        if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
            if self.orientation != HORIZONTAL:
                self.orientation_change = True
        if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            if self.orientation != VERTICAL:
                self.orientation_change = True           
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.x_speed
            self.dir = DIR_LEFT
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.x_speed 
            self.dir = DIR_RIGHT
        if keys[pygame.K_UP]:
            self.rect.y -= self.y_speed
            self.dir = DIR_UP
        if keys[pygame.K_DOWN]:
            self.rect.y += self.y_speed        
            self.dir = DIR_DOWN
        if keys[pygame.K_SPACE]:
            pass

        if dir != self.dir:
            dir *= -1
            self.image = pygame.transform.rotate(self.image, dir) 
            self.image = pygame.transform.rotate(self.image, self.dir) 

    def set_speed(self, xspeed, yspeed):
        self.x_speed = xspeed
        self.y_speed = yspeed


class Game:
    def __init__(self):
        # Initialize game window
        pygame.mixer.pre_init(48000, -16, 2, 2048)
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()        
        self.running = True
        self.tile_img = pygame.image.load(os.path.join(img_folder, "rock_tile.png")).convert()
        self.tile_map = None
        self.all_sprites = None
        self.creature = None
        self.tile_list = None
        self.egg_list = None
        self.creature_x_index = 0
        self.creature_y_index = 0
        self.redshirt = None
        self.redshirts = []
        self.redshirts_pos = []
        self.redshirt_list = None
        self.phaser = []
        self.phaserfire = False
        self.phasercountdown = PHASER_COUNTDOWN
        self.phasersnd = pygame.mixer.Sound(os.path.join(snd_folder, "tos_phaser_7.wav"))
        self.squashsnd = pygame.mixer.Sound(os.path.join(snd_folder, "squash.wav"))
        self.mandiesnd1 = pygame.mixer.Sound(os.path.join(snd_folder, "man_die_1.wav"))
        self.mandiesnd2 = pygame.mixer.Sound(os.path.join(snd_folder, "man_die_2.wav"))
        self.mandiesnd3 = pygame.mixer.Sound(os.path.join(snd_folder, "man_die_3.wav"))
        self.mandiesnd4 = pygame.mixer.Sound(os.path.join(snd_folder, "man_die_4.wav"))
        self.mandiesnd5 = pygame.mixer.Sound(os.path.join(snd_folder, "man_die_5.wav"))                                
        self.redshirt_count = REDSHIRT_COUNT
        self.old_num = 0

    def new(self):
        # Start a new grame
        xmax = int(WIDTH/TILESIZE)
        ymax = int(HEIGHT/TILESIZE)       
        self.tile_map = [[1]*ymax for i in range(xmax)]

        # Generate random tunnels
        self.redshirts_pos = []
        for i in range(0, NUMTUNNELS):
            xpos = random.randint(0, int((xmax-1)/2))*2
            ypos = random.randint(0, int((ymax-1)/2))*2
            dir = random.randint(0, 2)
            if dir == 0:
                if ypos > ymax/2:
                    for y in range(0, ypos):
                        self.tile_map[xpos][y] = 0
                    self.redshirts_pos.append((xpos, ypos-1, DIR_UP))
                else:                  
                    for y in range(ypos, ymax):
                        self.tile_map[xpos][y] = 0 
                    self.redshirts_pos.append((xpos, ypos, DIR_DOWN))                        
            else:
                if xpos > xmax/2:                   
                    for x in range(0, xpos):
                        self.tile_map[x][ypos] = 0    
                    self.redshirts_pos.append((xpos-1, ypos, DIR_LEFT))                                          
                else:                   
                    for x in range(xpos, xmax):
                        self.tile_map[x][ypos] = 0        
                    self.redshirts_pos.append((xpos, ypos, DIR_RIGHT))                                     
  
        # Setup sprites
        self.tile_list = pygame.sprite.Group()
        self.egg_list = pygame.sprite.Group()
        self.redshirt_list = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        # Create tile sprites
        for x in range(0, int(WIDTH/TILESIZE)):
            for y in range(0, int(HEIGHT/TILESIZE)):
                if self.tile_map[x][y]:  
                    tile = Tile()    
                    tile.rect.x = x*TILESIZE
                    tile.rect.y = y*TILESIZE
                    self.tile_list.add(tile)
                    self.all_sprites.add(tile)    

        # Create egg sprites
        for x in range(0, int(WIDTH/TILESIZE)):
            for y in range(0, int(HEIGHT/TILESIZE)):
                if not self.tile_map[x][y]:  
                    egg = Egg()    
                    egg.rect.x = x*TILESIZE
                    egg.rect.y = y*TILESIZE
                    self.egg_list.add(egg)
                    self.all_sprites.add(egg)                                            

        # Create creature sprite
        self.creature = Player()
        self.creature.rect.x = (random.randrange(WIDTH)//TILESIZE)*TILESIZE
        self.creature.rect.y = (random.randrange(HEIGHT)//TILESIZE)*TILESIZE
        self.all_sprites.add(self.creature)  

        # Create redshirt sprites
        self.redshirt_count = REDSHIRT_COUNT
        self.redshirts = []
        for i in range(0, REDSHIRT_COUNT):
            redshirt = Enemy()
            redshirt.rect.x = self.redshirts_pos[i][0]*TILESIZE
            redshirt.rect.y = self.redshirts_pos[i][1]*TILESIZE
            redshirt.direction = self.redshirts_pos[i][2]
            self.all_sprites.add(redshirt) 
            self.redshirts.append(redshirt)   
            self.redshirt_list.add(redshirt)  
            redshirt.id = i  

        # Background sound
        pygame.mixer.music.load(os.path.join(snd_folder, "tos_planet_3.wav"))
        pygame.mixer.music.play(-1)  
        pygame.mixer.music.set_volume(0.2)   

        # Set sound levels
        self.squashsnd.set_volume(0.25) 
        self.phasersnd.set_volume(0.25)   
        #self.mandiesnd.set_volume(0.25)         

        # Let 'er rip!      
        self.run()

    def random_pos(self, range):
        pos = rand.randrange(range)//TILESIZE
        return pos

    def run(self):
        # Game loop
        self.clock.tick(FPS)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def mandiesnd(self):
        num = random.randint(1,5)
        while self.old_num == num:
            num = random.randint(1,5)
        self.old_num = num
        if num == 1:
            self.mandiesnd1.play()
        elif num == 2:
            self.mandiesnd2.play()
        elif num == 3:
            self.mandiesnd3.play()
        elif num == 4:
            self.mandiesnd4.play()
        elif num == 5:
            self.mandiesnd5.play()

    def update(self):
        # Game loop - update
        self.all_sprites.update()

        # Check for collisions with creature and rock tiles
        pygame.sprite.spritecollide(self.creature, self.tile_list, True)

        # Check for collisions with creature and reshirts
        redshirt_kill_list = pygame.sprite.spritecollide(self.creature, self.redshirt_list, True)
        for redshirt in redshirt_kill_list:
            self.mandiesnd()
            count = self.redshirt_count
            for j in range(0, count):
                if self.redshirts[j].id == redshirt.id:
                    del self.redshirts[j] 
                    self.redshirt_count -= 1
                    break
        
        # Check for collisions with redshirts and eggs
        for i in range(0, self.redshirt_count):
            egg = pygame.sprite.spritecollide(self.redshirts[i], self.egg_list, True) 
            if egg:
                self.squashsnd.play() 
        
        # Determine if creature is tunneling
        x_index = self.creature.rect.centerx//TILESIZE
        y_index = self.creature.rect.centery//TILESIZE
        if x_index != self.creature_x_index or y_index != self.creature_y_index:
            self.creature_x_index = x_index
            self.creature_y_index = y_index
            if self.tile_map[x_index][y_index]:
                self.tile_map[x_index][y_index] = 0
                self.creature.set_speed(1, 1)
            else:
                self.creature.set_speed(3, 3)

        # Determine if redshirts need to manuver in tunnel
        for i in range(0, self.redshirt_count):
            x_index = self.redshirts[i].rect.x//TILESIZE
            y_index = self.redshirts[i].rect.y//TILESIZE           
            dir = self.redshirts[i].direction
            if dir == DIR_LEFT or dir == DIR_RIGHT:
                if x_index != self.redshirts[i].x_index:
                    self.redshirts[i].x_index = x_index
                    if dir == DIR_LEFT:
                        if x_index < (WIDTH/TILESIZE-1) and x_index > 0:                  
                            if self.tile_map[x_index+1][y_index+1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_DOWN
                                    self.redshirts[i].dir_change = True
                            if self.tile_map[x_index+1][y_index-1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_UP 
                                    self.redshirts[i].dir_change = True  
                            if self.tile_map[x_index][y_index] == 1:
                                self.redshirts[i].direction = DIR_RIGHT 
                                self.redshirts[i].dir_change = True 
                            if self.redshirts[i].dir_change != True:
                                if not random.randint(0,DIR_CHANGE):
                                    self.redshirts[i].direction = DIR_RIGHT
                                    self.redshirts[i].dir_change = True                                                                                   
                    elif dir == DIR_RIGHT:
                        if x_index < (WIDTH/TILESIZE-1) and x_index > 0:
                            if self.tile_map[x_index][y_index+1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_DOWN
                                    self.redshirts[i].dir_change = True
                            if self.tile_map[x_index][y_index-1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_UP  
                                    self.redshirts[i].dir_change = True 
                            if self.tile_map[x_index+1][y_index] == 1:
                                self.redshirts[i].direction = DIR_LEFT
                                self.redshirts[i].dir_change = True
                            if self.redshirts[i].dir_change != True:
                                if not random.randint(0,DIR_CHANGE):
                                    self.redshirts[i].direction = DIR_LEFT
                                    self.redshirts[i].dir_change = True                                 
            else: # dir == DIR_UP or dir == DIR_DOWN
                if y_index != self.redshirts[i].y_index:
                    self.redshirts[i].y_index = y_index 
                    if dir == DIR_UP:
                        if y_index < (HEIGHT/TILESIZE-1) and y_index > 0:
                            if self.tile_map[x_index-1][y_index+1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_LEFT
                                    self.redshirts[i].dir_change = True                                    
                            if self.tile_map[x_index+1][y_index+1] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_RIGHT 
                                    self.redshirts[i].dir_change = True   
                            if self.tile_map[x_index][y_index] == 1:
                                self.redshirts[i].direction = DIR_DOWN   
                                self.redshirts[i].dir_change = True 
                            if self.redshirts[i].dir_change != True:
                                if not random.randint(0,DIR_CHANGE):
                                    self.redshirts[i].direction = DIR_DOWN 
                                    self.redshirts[i].dir_change = True                                 
                    elif dir == DIR_DOWN:
                        if y_index < (HEIGHT/TILESIZE-1) and y_index > 0:
                            if self.tile_map[x_index-1][y_index] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_LEFT
                                    self.redshirts[i].dir_change = True 
                            if self.tile_map[x_index+1][y_index] == 0:
                                heads = random.randint(0,1)
                                if heads:
                                    self.redshirts[i].direction = DIR_RIGHT 
                                    self.redshirts[i].dir_change = True   
                            if self.tile_map[x_index][y_index+1] == 1:
                                self.redshirts[i].direction = DIR_UP  
                                self.redshirts[i].dir_change = True 
                            if self.redshirts[i].dir_change != True:
                                if not random.randint(0,DIR_CHANGE):
                                    self.redshirts[i].direction = DIR_UP 
                                    self.redshirts[i].dir_change = True    

        # Determine if a redshirt should fire on the creature  
        creature_x_index = self.creature.rect.x//TILESIZE   
        creature_y_index = self.creature.rect.y//TILESIZE 
        self.phaserfire = False    
        self.phaser = []                            
        for i in range(0, self.redshirt_count):
            # Check for horizontal line of site
            redshirt_x_index = self.redshirts[i].rect.x//TILESIZE
            redshirt_y_index = self.redshirts[i].rect.y//TILESIZE  
            self.redshirts[i].x_speed = REDSHIRT_SPEED                                
            if redshirt_y_index == creature_y_index:
                line_of_sight = False
                dist = (redshirt_x_index - creature_x_index)
                if dist > 0 and self.redshirts[i].direction == DIR_LEFT:
                    for x in range(creature_x_index, redshirt_x_index):
                        if self.tile_map[x][redshirt_y_index]:
                            line_of_sight = True
                    if not line_of_sight:
                        self.phaserfire = True
                        self.phaser.append(self.creature.rect.centerx)
                        self.phaser.append(self.redshirts[i].rect.centery)
                        dist = self.redshirts[i].rect.centerx - self.creature.rect.centerx
                        self.phaser.append(self.creature.rect.x + dist)
                        self.phaser.append(self.redshirts[i].rect.centery)
                elif dist < 0 and self.redshirts[i].direction == DIR_RIGHT:
                    for x in range(redshirt_x_index, creature_x_index):
                        if self.tile_map[x][redshirt_y_index]:
                            line_of_sight = True
                    if not line_of_sight:
                        self.phaserfire = True
                        self.phaser.append(self.redshirts[i].rect.centerx)
                        self.phaser.append(self.redshirts[i].rect.centery)
                        dist = self.creature.rect.centerx - self.redshirts[i].rect.centerx
                        self.phaser.append(self.redshirts[i].rect.centerx + dist)
                        self.phaser.append(self.redshirts[i].rect.centery) 

                if not self.phasercountdown:
                    self.redshirts[i].x_speed = 0
                    self.creature.x_speed = 0

                                    
    def events(self):
       # Game loop - Events

        # Check for keys pressed
        keys = pygame.key.get_pressed()
        self.creature.move(keys)

        # Check for queued events        
        for event in pygame.event.get():
            # Quit game
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # Reset game
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.playing = False                                               

    def draw_background(self):
        for x in range(0, int(WIDTH/TILESIZE)):
            for y in range(0, int(HEIGHT/TILESIZE)):
                if self.tile_map[x][y]:
                    self.screen.blit(self.tile_img, (x*TILESIZE, y*TILESIZE, TILESIZE, TILESIZE))

    def draw(self):
        # Game loop - Draw
        self.screen.fill(BLACK)

        # Draw phaser fire
        if self.phaserfire:
            if not self.phasercountdown:
                pygame.draw.line(self.screen,WHITE,(self.phaser[0], self.phaser[1]),(self.phaser[2], self.phaser[3]))
                self.phasersnd.play()                   

            else:
                self.phasercountdown -= 1
        else:
            self.phasercountdown = random.randint(PHASER_COUNTDOWN/2,PHASER_COUNTDOWN)
            if self.phasersnd != None:
                self.phasersnd.stop()

        self.all_sprites.draw(self.screen)            

        # After drawing everything, flip the display
        pygame.display.flip()

    def show_start_screen(self):
        # Game splash/start screen
        pass

    def show_go_screen(self):
        # Game over/continue
        pass
    
g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pygame.quit()