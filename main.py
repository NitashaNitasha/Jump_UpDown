import pygame
from pygame.locals import *

import pickle
from os import path

pygame.init()
#time
clock= pygame.time.Clock()
fps=60

screen_width=500
screen_height=500

screen=pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("jump up")


#define font
font_score=pygame.font.SysFont('Bauhaus 93',25)
font=pygame.font.SysFont('Bauhaus 93',60)
#game var
tile_size=25
game=0
main_menu=True
level=3
max_levels=7
score=0

#images
bg_img=pygame.image.load("img/bg.png")
dirt_img=pygame.image.load("img/dirt.jpg")
restart_img=pygame.image.load("img/restart.png")
start_img=pygame.image.load("img/start.png")
exit_img=pygame.image.load("img/exit.png")


#draw text function
def draw_text(text,font,text_color,x,y):
    image=font.render(text,True,text_color)
    screen.blit(image,(x,y))


# reset_level
def reset_level(level):
    player.reset(50, screen_height - 65)
    blob_group.empty()
    lava_group.empty()
    platform_group.empty()
    exit_group.empty()
    data_game = open(f'level data/level{level}_data', 'rb')
    world_data = pickle.load(data_game)
    world = World(world_data)
    return world



class Button:
    def __init__(self,x,y,image):
        self.image=image
        self.rect=self.image.get_rect()
        self.rect.x=x
        self.rect.y=y
        self.clicked=False
    def draw(self):
        action=False
        #get mouse position
        position=pygame.mouse.get_pos()
        if self.rect.collidepoint(position):
            if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
                action=True
                self.clicked=True

        if pygame.mouse.get_pressed()[0]==0:
            self.clicked=False
        screen.blit(self.image,self.rect)
        return action



class Player:
    def __init__(self, x, y):
        self.reset(x,y)

    def update(self, game):
        #keys for moving
        dx=0
        dy=0
        col_tresh=10

        if game==0:
            #key commands
            key=pygame.key.get_pressed()
            if key[pygame.K_UP] and self.jumped == False and self.in_air==False:
                self.vel_y=-10
                self.jumped=True
            if not key[pygame.K_UP]:
                self.jumped=False
            if key[pygame.K_LEFT]:
                dx -= 1
            if key[pygame.K_RIGHT]:
                dx += 1

        #add gravity
            self.vel_y +=0.5
            if self.vel_y>1:
                self.vel_y = 1
            dy+= self.vel_y
        #check for collision
            self.in_air = True
            for tile in world.tile_list:
                # for collision in x:
                if tile[1].colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx=0
                #for collision in y:
                if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):
                    #check if below (jumping)
                    if self.vel_y<0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y=0
                    # check if above (falling)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y=0
                        self.in_air=False


        #check for enemy collision and lava collision
            if pygame.sprite.spritecollide(self,blob_group, False):
                game = -1
            if pygame.sprite.spritecollide(self,lava_group, False):
                game = -1
        #check for collision with gate
            if pygame.sprite.spritecollide(self,exit_group, False):
                game= 1
        #check for collision with platform
            for plat in platform_group:
                #collision in x
                if plat.rect.colliderect(self.rect.x+dx, self.rect.y, self.width, self.height):
                    dx=0
                #collision in y
                if plat.rect.colliderect(self.rect.x, self.rect.y+dy, self.width, self.height):
                    #check for collision from bottom
                    if abs((self.rect.top+dy)-plat.rect.bottom)<col_tresh:
                        self.vel_y =0
                        dy = plat.rect.bottom - self.rect.top
                        # check for collision from bottom
                    elif abs((self.rect.bottom + dy) - plat.rect.top) < col_tresh:
                        self.rect.bottom=plat.rect.top-1
                        self.in_air=False
                        dy = 0
                    #sideway collision
                    if plat.move_x!=0:
                        self.rect.x+=plat.move_direction



        #update position
            self.rect.x += dx
            self.rect.y += dy

        elif game == -1:
            self.image =self.dead
            draw_text("Game Over!",font,(0,0,255),screen_width//2-150,screen_width//2)
            if self.rect.y > 20:
                self.rect.y -= 1

    #player img
        screen.blit(self.image, self.rect)
    # drawing rect on screen
        #pygame.draw.rect(screen, (255, 255, 255), self.rect,2)

        return game
    def reset(self,x,y):
        img = pygame.image.load("img/girl.png")
        self.image = pygame.transform.scale(img, (20, 40))
        self.dead = pygame.image.load("img/ghost.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.jumped = False
        self.in_air=True


class World():

    def __init__(self, data):
        self.tile_list =[]
        grass_img=pygame.image.load("img/grass.jpg")
        r_count = 0
        for row in data:
            c_count=0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect=img.get_rect()
                    img_rect.x = c_count * tile_size
                    img_rect.y = r_count * tile_size
                    tile=(img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(grass_img,(tile_size, tile_size))
                    img_rect=img.get_rect()
                    img_rect.x = c_count * tile_size
                    img_rect.y = r_count * tile_size
                    tile=(img, img_rect)
                    self.tile_list.append(tile)
                if tile ==3:
                    blob=Enemy(c_count*tile_size,r_count*tile_size+10)
                    blob_group.add(blob)
                if tile ==4:
                    plat=Platform(c_count*tile_size,r_count*tile_size+(tile_size//2),1,0)
                    platform_group.add(plat)
                if tile ==5:
                    plat=Platform(c_count*tile_size,r_count*tile_size+(tile_size//2),0,1)
                    platform_group.add(plat)
                if tile ==6:
                    lava=Lava(c_count*tile_size,r_count*tile_size+(tile_size//2))
                    lava_group.add(lava)
                if tile==7:
                    coin = Coin(c_count * tile_size+(tile_size//2), r_count * tile_size + (tile_size // 2))
                    coin_group.add(coin)
                if tile==8:
                    exit = Exit(c_count*tile_size,r_count*tile_size-25)
                    exit_group.add(exit)

                c_count+=1
            r_count+=1
    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            #pygame.draw.rect(screen,(255,255,255),tile[1],1)


class Enemy(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image= pygame.image.load("img/sun.png")
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction=1
        self.move_counter=0
    def update(self):
        self.rect.x += self.move_direction
        self.move_counter+=1
        if abs(self.move_counter) >2:
            self.move_direction *= -1
            self.move_counter *= -1
blob_group = pygame.sprite.Group()


class Platform(pygame.sprite.Sprite):
    def __init__(self,x,y,move_x,move_y):
        pygame.sprite.Sprite.__init__(self)
        image= pygame.image.load("img/grass.jpg")
        self.image=pygame.transform.scale(image,(tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_counter=0
        self.move_direction=1
        self.move_x= move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_direction*self.move_x
        self.rect.y += self.move_direction*self.move_y
        self.move_counter += 1
        if abs(self.move_counter) > 20:
            self.move_direction *= -1
            self.move_counter *= -1

platform_group=pygame.sprite.Group()




class Lava(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        image= pygame.image.load("img/lava.png")
        self.image=pygame.transform.scale(image,(tile_size, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
lava_group=pygame.sprite.Group()


class Coin(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        image= pygame.image.load("img/coin.png")
        self.image=pygame.transform.scale(image,(tile_size//2, tile_size // 2))
        self.rect = self.image.get_rect()
        self.rect.center = x,y

coin_group=pygame.sprite.Group()


class Exit(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        image= pygame.image.load("img/gate.png")
        self.image=pygame.transform.scale(image,(tile_size, tile_size*2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
exit_group=pygame.sprite.Group()

#dummy coin
score_coin=Coin(tile_size//2,tile_size//2)
coin_group.add(score_coin)

player=Player(20, screen_height - 65)

# loading level data
if path.exists(f"level data/level{level}_data"):
    data_game = open(f"level data/level{level}_data", "rb")
    world_data = pickle.load(data_game)
world = World(world_data)

#create button
restart_button=Button(screen_width//2-25,screen_height//2-50, restart_img)
start_button=Button(screen_width//2-90,screen_height//2,start_img)
exit_button=Button(screen_width//2+75,screen_height//2,exit_img)

run=True
#game run(main game)
while run:

    clock.tick(fps)

    screen.blit(bg_img,(0,0))

    if main_menu==True:
        if start_button.draw():
            main_menu=False
        if exit_button.draw():
            run=False
    else:
        world.draw()
        if game==0:
            blob_group.update()
            platform_group.update()
            #update score,coin collection:
            if pygame.sprite.spritecollide(player,coin_group, True):
                score+=1
            draw_text(str(score),font_score, (255,255,0),25,0)
        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        game = player.update(game)


    #if player has died
        if game ==-1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game=0
                score=0
    #game complete
        if game == 1:
        #next level
            level+=1
            if level<=max_levels:
                world_data=[]
                world = reset_level(level)
                game=0
            else:
                draw_text("YOU WIN",font,(0,0,255),screen_width//2-100,screen_height//2)
                if restart_button.draw():
                    level=1
                    #restart game
                    world_data = []
                    world = reset_level(level)
                    game = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run=False
    pygame.display.update()

pygame.quit()
