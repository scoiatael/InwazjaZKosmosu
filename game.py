#!/bin/python2
import pygame, math, sys, random, pickle, thread, datetime, copy, time
from pygame.locals import *

SCREENX = 800
SCREENY = 600
FPS = 30
BLACK = (0,0,0)

MENU_COLOR = (95, 20, 20)
LOGO_COLOR = (15, 15, 45)
OFFSET = 200

class Actor:
    def __init__(self,g):
        self.pos_x = 0
        self.pos_y = 0
        self.speed = 15
        self.size_x = 50
        self.size_y = 50
        self.image_path = 'ship.png'
        self.image = pygame.image.load(self.image_path)
        self.game = g
        self.collided = 0

    def move(self, x, y):
        self.pos_x += x
        self.pos_y += y 

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def update(self):
        return

    def perform_destruction(self):
        try:
            self.game.actors.remove(self)
            return True
        except ValueError:
            pass
        return False
        del(self)

    def pickable(self):
        self.image = 0 
        self.game = 0
        return self

    def unpickable(self, g):
        self.image = pygame.image.load(self.image_path)
        self.game = g
        return self

class Player(Actor):
    def __init__(self,g):
        Actor.__init__(self,g)
        self.set_position(SCREENX/2,2*SCREENY/3)
        self.health = 100

    def move(self, x, y):
        self.pos_x += x
        self.pos_y += y
        if self.pos_x < 0: self.pos_x = 0
        if self.pos_y < SCREENY/2: self.pos_y = SCREENY/2
        if self.pos_x > SCREENX - self.size_x: self.pos_x = SCREENX - self.size_x
        if self.pos_y > SCREENY - self.size_y: self.pos_y = SCREENY- self.size_y

    def shot(self):
        self.game.actors.append(PlayerBullet(self.game,self))

    def get_hit(self, h):
        if(isinstance(h,EnemyBullet)):
            self.health -= h.damage
        elif(isinstance(h,Enemy)):
            self.health = 0
        elif(isinstance(h,Bonus)):
            h.action()

        if self.health <= 0:
            self.perform_destruction()

    def perform_destruction(self):
        print "Przegrales! Zabiles", self.game.enemies_killed, "wrogow!"
        Actor.perform_destruction(self)
        self.game.game_state=0

class Enemy(Actor):
    def __init__(self,g):
        Actor.__init__(self,g)
        self.set_position(self.game.rnd.randint(0,SCREENX-self.size_x),0)
        self.direction = 2*self.game.rnd.randint(0,1) - 1

    def get_hit(self,h):
        if(isinstance(h,PlayerBullet)):
            self.health -= h.damage
            if self.health <= 0: 
                if(self.perform_destruction()):
                     self.game.enemies_killed += 1
        elif(isinstance(h,Player)):
            self.perform_destruction()

    def update(self):
        self.collided = 0

    def perform_destruction(self):
        ok = Actor.perform_destruction(self)
        if(ok):
            self.game.enemies -= 1
            k = self.game.rnd.randint(1,100)
            if(k <= 5):
                self.game.actors.append(TNTBonus(self.game,self))
            elif(k >= 6 and k <= 20):
                self.game.actors.append(HealthBonus(self.game,self))
        return ok

class Enemy1(Enemy):
    def __init__(self,g):
        Enemy.__init__(self,g)
        self.image_path = 'enemy1.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_x = self.game.rnd.randint(10,20)
        self.speed_y = self.game.rnd.randint(1,4)
        self.health = 10
        
    def update(self):
        Enemy.update(self)
        self.shot()
        self.move(self.direction*self.speed_x,self.speed_y)
        if(self.pos_x >= SCREENX - self.size_x): self.direction = -1
        elif(self.pos_x <= 0): self.direction = 1

    def get_hit(self,h):
        Enemy.get_hit(self,h)

    def shot(self):
        prob = 50
        if(self.game.rnd.randint(1,1000) <= prob):
            self.game.actors.append(Enemy1Bullet(self.game,self))

class Enemy2(Enemy):
    def __init__(self,g):
        Enemy.__init__(self,g)
        self.image_path = 'enemy2.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_x = self.game.rnd.randint(10,30)
        self.speed_y = self.game.rnd.randint(10,20)
        self.health = 10

    def update(self):
        Enemy.update(self)
        self.shot()
        self.move(self.direction*self.speed_x,0)
        if(self.pos_x >= SCREENX - self.size_x): 
            self.direction = -1
            self.move(0,self.speed_y)
        elif(self.pos_x <= 0): 
            self.direction = 1
            self.move(0,self.speed_y)

    def get_hit(self,h):
        Enemy.get_hit(self,h)

    def shot(self):
        prob = 10
        if(self.game.rnd.randint(1,1000) <= prob):
            self.game.actors.append(Enemy2Bullet(self.game,self))


class Enemy3(Enemy):
    def __init__(self,g):
        Enemy.__init__(self,g)
        self.image_path = 'enemy3.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_x = self.game.rnd.randint(40,60)
        self.speed_y = self.game.rnd.randint(5,10)
        self.health = 5

    def update(self):
        Enemy.update(self)
        
        px = self.game.player.pos_x
        self.move(self.speed_x * (px - self.pos_x) / SCREENX ,self.speed_y)
        
    def get_hit(self,h):
        if(isinstance(h,Bullet)):
            self.health -= h.damage
            if self.health <= 0: 
                if(self.perform_destruction()):
                    self.game.enemies_killed += 1
        elif(isinstance(h,Player)):
            self.perform_destruction()

        
class Bullet(Actor):
    def __init__(self, g, s):
        Actor.__init__(self, g)
        owner = s
        self.set_position(owner.pos_x+owner.size_x/2,owner.pos_y+owner.size_y/2)
        self.size_x = 6
        self.size_y = 15
        
class PlayerBullet(Bullet):
    def __init__(self,g,owner):
        Bullet.__init__(self,g,owner)
        self.image_path = 'shipbullet.png'
        self.image = pygame.image.load(self.image_path)
        self.damage = 5
        
    def update(self):
        self.move(0,-self.speed)

    def get_hit(self, h):
        if(isinstance(h,Enemy) or isinstance(h,EnemyBullet)): self.perform_destruction()

class EnemyBullet(Bullet):
    def __init__(self,g,owner):
        Bullet.__init__(self,g,owner)
        self.image_path = 'alienbullet.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_x = 0
        self.speed_y = 20
        self.size_x = 9
        self.size_y = 16
        self.damage = 5
        
    def update(self):
        self.move(self.speed_x, self.speed_y)

    def get_hit(self, h):
        if(isinstance(h, Player) or isinstance(h, PlayerBullet)):
            self.perform_destruction()

class Enemy1Bullet(EnemyBullet):
    def __init__(self,g,owner):
        EnemyBullet.__init__(self,g,owner)
        self.image_path = 'enemy1bullet.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_y = 25
        self.damage = 5

class Enemy2Bullet(EnemyBullet):
    def __init__(self,g,owner):
        EnemyBullet.__init__(self,g,owner)
        self.image_path = 'enemy2bullet.png'
        self.image = pygame.image.load(self.image_path)
        self.speed_y = 15
        self.damage = 20

class Bonus(Actor):
    def __init__(self, g, s):
        Actor.__init__(self, g)
        owner = s
        self.set_position(owner.pos_x+owner.size_x/2,owner.pos_y+owner.size_y/2)
        self.size_x = 35
        self.size_y = 35
        self.speed_x = 0
        self.speed_y = self.game.rnd.randint(5,12)

    def update(self):
        self.move(0,self.speed_y)

    def get_hit(self,h):
         if(isinstance(h, Player)):
             self.perform_destruction()
        
class TNTBonus(Bonus):
    def __init__(self,g,s):
        Bonus.__init__(self,g,s)
        self.image_path = 'tntbonus.png'
        self.image = pygame.image.load(self.image_path)

    def action(self):
        to_destroy = []
        for actor in self.game.actors:
            if (not isinstance(actor,Player) and
                not isinstance(actor,Bonus) and
                not isinstance(actor,PlayerBullet) ): 
                to_destroy.append(actor)
                
        for actor in to_destroy:
            actor.perform_destruction()

class HealthBonus(Bonus):
    def __init__(self,g,s):
        Bonus.__init__(self,g,s)
        self.image_path = 'healthbonus.png'
        self.image = pygame.image.load(self.image_path)
        self.recover = self.game.rnd.randint(20,50)

    def action(self):
        self.game.player.health = min(100,self.recover+self.game.player.health)

def make_pickable(var):
    return var.pickable() 

class Highscore:
    def __init__(self):
        self.highscore_lock = thread.allocate_lock()
        self.highscore = None
        self.should_stop = False

    def unsafe_load(self):
        try:
            highscore_handle = open("highscores.pkl", "rb")
            self.highscore = pickle.load(highscore_handle)
        except Exception, e:
            print(e)
            print("Creating file 'highscores.pkl'")
            highscore_handle = open("highscores.pkl", "wb")
            self.highscore = []
        if self.should_stop:
            raise Exception("interruption")

    def load(self):
        self.highscore_lock.acquire()
        self.should_stop = False
        try:
            if(self.highscore == None):
                    self.unsafe_load()
        except Exception, e:
            print("Loading highscore failed")
            print(e)
        self.highscore_lock.release()
        return self.highscore

    def unsafe_add(self, (hscore, hstamp)):
        if self.highscore != []:
            added = False
            new_highscore = []
            for (score, stamp) in self.highscore:
                if self.should_stop:
                    raise Exception("interruption")
                if not added:
                    if hscore > score:
                        added = True
                        new_highscore.append((hscore, hstamp))
                new_highscore.append((score, stamp))
            if not added:
                new_highscore.append((hscore, hstamp))
            self.highscore = new_highscore
        else:
            self.highscore = [(hscore, hstamp)] 

    def unsafe_dump(self):
        highscore_handle = open("highscores.pkl", "wb")
        self.highscore = self.highscore[:100]
        pickle.dump(self.highscore, highscore_handle)
       
    def add(self, highscore_entry):
        self.highscore_lock.acquire()
        self.should_stop = False
        try:
            if(self.highscore == None):
                self.unsafe_load()
            self.unsafe_add(highscore_entry)
            self.unsafe_dump()
        except Exception, e:
            print("Dumping highscore failed")
            print(e)
        self.highscore_lock.release()


class Game:
    def __init__(self):
        pygame.init()
        self.rnd = random.Random()
        self.screen = pygame.display.set_mode((SCREENX,SCREENY ), DOUBLEBUF)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Troche Inna Inwazja z Kosmosu")
        self.actors = []
        self.init_player()
        self.enemies = 0
        self.level = 1
        self.enemies_killed = 0
        self.game_state = 2
        self.MENUS = [["New game", "Load game", "Highscores", "Exit"], ["Continue", "Save game", "Abandon game"], ["Cancel"], ["Back"]]
        self.MENUS_Orig = copy.deepcopy(self.MENUS)
        self.highscore = Highscore()
        self.worker_thread = None

    def add_highscore(self):
        score = (self.level, self.enemies_killed)
        highscore_entry = (score, datetime.datetime.now())
        self.highscore.add(highscore_entry)

    def thread_wrapper(self, func, clean):
        func()
        self.worker_thread = None
        clean()

    def thread_starter(self, func, clean):
        while self.worker_thread != None:
            time.sleep(1)
        self.worker_thread = thread.start_new(Game.thread_wrapper, (self, func, clean))

    def async_add_highscore(self):
        self.thread_starter((lambda: self.add_highscore()), (lambda: None))
        return

    def set_game_state(self, val):
        if val >=0 and val < len(self.MENUS) + 2:
            self.game_state = val

    def async_load_highscores(self):
        self.thread_starter((lambda: self.highscore.load()), (lambda: self.set_game_state(5)))
        return

    def async_abandon(self):
        self.highscore.should_stop = True
        return

    def from_pickable(self):
        return (lambda x: x.unpickable(self)) 

    def save_game(self):
        obj = (map(make_pickable, self.actors), self.enemies, self.enemies_killed)
        try:
            save = open("save.pkl", "wb");
            pickle.dump(obj, save)
            print("Game saved");
            self.MENUS[self.get_menu()][1] += " done"
        except Exception, e:
            print("Saving failed!")
            print(e)
            self.MENUS[self.get_menu()][1] += " failed"
        map(self.from_pickable(), self.actors)

    def load_game(self):
        try:
            save = open("save.pkl", "rb");
            (act, ene, ene_k) = pickle.load(save)
            act = filter(lambda x: x != None, act)
            self.actors = map(self.from_pickable(), act)
            self.enemies = ene
            self.enemies_killed = ene_k
            self.player = self.actors[0]
        except Exception, e:
            print("Loading failed")
            print(e)
            self.game_state = 2
            pass

    def menu_choose(self):
        self.MENUS = copy.deepcopy(self.MENUS_Orig)
        if(self.game_state == 1):
            self.game_state = 3
            return
        menu = self.get_menu()
        item = self.get_menu_item()
        if(menu == 0):
            if(item == 0):
                self.game_state = 1
            if(item == 1):
                self.game_state = 3
                self.load_game()
            if(item == 2):
                self.game_state = 4
                self.async_load_highscores()
            if(item == 3):
                sys.exit(0)
        if(menu == 1):
            if(item == 0):
                self.game_state = 1
            if(item == 1):
                self.save_game()
            if(item == 2):
                self.game_state = 0
        if(menu == 2):
            if(item == 0):
                self.game_state = 2
                self.async_abandon()
        if(menu == 3):
            if(item == 0):
                self.game_state = 2

    def get_menu_item(self):
        if(self.game_state < 2):
            return 
        return self.game_state / 8

    def get_menu(self):
        if(self.game_state < 2):
            return 
        return self.game_state % 8 - 2
        
    def incr_menu(self):
        if(self.game_state < 2):
            return
        if(self.get_menu_item() < len(self.MENUS[self.get_menu()]) - 1):
            self.game_state += 8

    def decr_menu(self):
        if(self.game_state < 2):
            return
        if(self.get_menu_item() > 0):
            self.game_state -= 8

    def init_player(self):
        self.x_move = 0
        self.y_move = 0
        self.player = Player(self)
        self.actors.append(self.player)

    def spawn_enemy(self):
        k = self.rnd.randint(1,1000)
        if(k < 30*self.level and self.enemies < self.max_enemies()):
            return True
        return False

    def max_enemies(self):
        return 3*self.level
    
    def handle_events(self):
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            if event.key == K_ESCAPE: sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == K_LEFT: self.x_move = -1
                if event.key == K_RIGHT: self.x_move = 1
                if event.key == K_UP: 
                    self.y_move = -1
                    self.decr_menu();
                if event.key == K_DOWN: 
                    self.y_move = 1
                    self.incr_menu()
                if event.key == K_SPACE: 
                    if self.game_state == 1:
                        self.player.shot()
                if event.key == K_RETURN:
                    self.menu_choose()

            elif event.type == pygame.KEYUP:
                if event.key == K_LEFT and self.x_move == -1: self.x_move = 0
                if event.key == K_RIGHT and self.x_move == 1: self.x_move = 0
                if event.key == K_UP and self.y_move == -1: self.y_move = 0
                if event.key == K_DOWN and self.y_move == 1: self.y_move = 0

    def move_player(self):
        self.player.move(self.x_move*self.player.speed, self.y_move*self.player.speed)

    def destroy_out_of_screen(self):
        to_remove = []
        for actor in self.actors:
            if (not isinstance(actor,Player)):
                if(actor.pos_x < -100 or actor.pos_y < -100 or
                   actor.pos_x > SCREENX+100 or actor.pos_y > SCREENY+100):
                    to_remove.append(actor)
        for actor in to_remove:
            actor.perform_destruction()

    def update_game_state(self):
        self.move_player()
        
        for actor in self.actors: 
            actor.update()
        if(self.spawn_enemy()):
            self.enemies += 1
            n = self.rnd.randint(1,3)
            if(n==1): e = Enemy1(self)
            elif(n==2): e = Enemy2(self)
            elif(n==3): e = Enemy3(self)
            while(self.try_collision_with_on_board(e)):
                e.pos_x = self.rnd.randint(0,SCREENX-e.size_x)
            self.actors.append(e)

        self.detect_collisions()
        self.level = int(math.floor(math.log((self.enemies_killed+5)/5,3))) + 1
        self.destroy_out_of_screen()
        
    def try_collision(self, actor1, actor2):
        x_down = actor1.pos_x
        x_up = actor1.pos_x + actor1.size_x
        y_down = actor1.pos_y
        y_up = actor1.pos_y + actor1.size_y
        x, y = actor2.pos_x, actor2.pos_y
        
        detected = 0
        for o in range(2):
            for p in range(2):
                if(detected == 0 and x_down <= x + o*actor2.size_x and
                   x + o*actor2.size_x  <= x_up and
                   y_down <= y + p*actor2.size_y and
                   y + p*actor2.size_y  <= y_up):
                    detected = 1
        return detected

    def try_collision_with_on_board(self,act):
        for actor in self.actors:
            ans = max(0,max(self.try_collision(act,actor),self.try_collision(actor,act)))
        return ans

    def detect_collisions(self):
        collision_queue = []
        for i in range(len(self.actors)):
            for j in range(i):
                if(self.try_collision(self.actors[i],self.actors[j]) == 1):
                    collision_queue.append((self.actors[i],self.actors[j]))
                elif(self.try_collision(self.actors[j],self.actors[i]) == 1):
                    collision_queue.append((self.actors[i],self.actors[j]))
                        
        for (actor1,actor2) in collision_queue:
            self.handle_collision(actor1,actor2)
                            
    def handle_collision(self, act1, act2):
        act1.get_hit(act2)
        act2.get_hit(act1)    

    def draw_actors(self):
        for actor in self.actors:
            self.screen.blit(actor.image, (actor.pos_x, actor.pos_y))

    def draw_controlls(self):
        font = pygame.font.Font(None, 24)
        text = font.render("Zycie "+str(self.player.health), 1, (255, 0, 0))
        textpos = (20,30)
        self.screen.blit(text, textpos)
        text = font.render("Zabito "+str(self.enemies_killed), 1, (0,255, 0))
        textpos = (20,50)
        self.screen.blit(text, textpos)
        text = font.render("Level "+str(self.level), 1, (0,0, 255))
        textpos = (20,70)
        self.screen.blit(text, textpos)

    def draw_menu(self):
        if(self.game_state < 2):
            return # paranoid?
        surf = pygame.Surface(self.screen.get_size())
        surf.set_alpha(128)
        surf.fill((155,155,155))
        self.screen.blit( surf ,(0,0))
        font = pygame.font.Font(None, 64)
        rtext = font.render("Inwazja Z Kosmosu", 1, LOGO_COLOR)
        textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,20)
        self.screen.blit(rtext, textpos)
        item = self.get_menu_item()
        menu = self.get_menu()
        font = pygame.font.Font(None, 32)
        offset = OFFSET
        for text in self.MENUS[menu]:
            rtext = font.render(text, 1, MENU_COLOR)
            textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
            offset += rtext.get_size()[1] + 5;
            if(self.MENUS[menu][item] == text):
                surf = pygame.Surface(rtext.get_size())
                surf.set_alpha(128)
                surf.fill((255,255, 255))
                self.screen.blit( surf , textpos)
            self.screen.blit(rtext, textpos)

        if menu == 2:
            offset += 100
            rtext = font.render("LOADING...", 1, (255, 0, 0))
            textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
            offset += rtext.get_size()[1] + 5;
            self.screen.blit(rtext, textpos)
            rtext = font.render(".........."[:pygame.time.get_ticks() / 100 % 10], 1, MENU_COLOR)
            textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
            offset += rtext.get_size()[1] + 5;
            self.screen.blit(rtext, textpos)
        if menu == 3:
            if self.highscore.highscore == None:
                rtext = font.render("Sorry, an error occured..", 1, MENU_COLOR)
                textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
                offset += rtext.get_size()[1] + 5;
                self.screen.blit(rtext, textpos)
                return

            rtext = font.render("No. Level  Score     Time                                 ", 1, MENU_COLOR)
            textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
            offset += rtext.get_size()[1] + 5;
            self.screen.blit(rtext, textpos)
            for i,((l,s), dt) in enumerate(self.highscore.highscore[:10]):
                text = '%(i)02d   %(l)02d        %(s)06d  %(dt)s' % { 'i':i, 'l':l, 's':s, 'dt': dt.ctime() }
                rtext = font.render(text, 1, MENU_COLOR)
                textpos = (( self.screen.get_size()[0] - rtext.get_size()[0]) / 2,offset)
                offset += rtext.get_size()[1] + 5;
                self.screen.blit(rtext, textpos)



    def draw_screen(self):
        self.screen.fill(BLACK)
        self.draw_controlls()
        self.draw_actors()
        if self.game_state > 1:
            self.draw_menu()

    def update(self):
        self.handle_events()
        if self.game_state == 1:
            self.update_game_state()
        self.draw_screen()

if __name__ == '__main__':
    while 1:
        game = Game()
        while (game.game_state != 0):
            game.clock.tick(FPS)
            game.update()
            pygame.display.flip()
        game.async_add_highscore()
        del(game)
