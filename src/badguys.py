"""
badguys.py

Place for BadGuys class.
"""

# --- Import external modules ---
import arcade
import pymunk
# --- Import internal classes ---
import data
import assets

import math
import random

from particle import Particle

# --- Constants ---
param = data.load_parameters()
settings = data.load_settings()

# Control the physics of how the bad guy moves
MAX_VERTICAL_MOVEMENT_SPEED = int(param['BADGUY1']['MAX_VERTICAL_MOVEMENT_SPEED'])

SOUND_VOL = int(settings['AUDIO']['SOUND_VOL'])


class BadGuy(arcade.Sprite):
    """ Bad Guy """
    def __init__(self, parent, level_width, level_height, x=0, y=0, type=0, action_data=[]):
        """ Set up player """
        super().__init__()
        
        self.parent = parent
        self.face_right = True
        self.level_width = level_width
        self.level_height = level_height
        self.type = type
        self.action_data = []
        for action in action_data:
            self.action_data.append([action[0],action[1],False]) # type, data, completed?
        
        self.center_x = x
        self.center_y = y
        self.angle = 0.0
        self.track_y = y
        
        self.flash_ani = 0
        self.damage_to = 0
        
        self.controlled = False
        
        self.frame_ani = 0
        self.texture = assets.bad_guys[self.type][0][0]
        self.scale = 1.0
        
        if type == 0:
            self.maxhealth = int(param['BADGUY1']['HEALTH'])
        elif type == 1:
            self.maxhealth = int(param['BADGUY2']['HEALTH'])
        else:
            self.maxhealth = int(param['BADGUY1']['HEALTH'])
        self.health = self.maxhealth
        
        self.boost_to = 0
        self.bomblaunch_to = 0
    
    def hit(self, damage=1):
        self.track_y += 400*random.random()-200 # dodge vertically
        if self.track_y < 30:
            self.track_y = 30
        elif self.track_y > (self.level_height-30):
            self.track_y = (self.level_height-30)
        if self.flash_ani > 0:
            return
        if self.health <= 0:
            return
        self.health -= damage
        if self.health < 0:
            self.health = 0
        self.flash_ani = 10
        if self.health == 0:
            assets.game_sfx['scumbag'].play()
    
    def update(self):
        
        # Update position
        if self.health == 0: # floating
            self.change_x -= 0.05
            if self.change_x < 0:
                self.change_x = 0
            self.angle += 1
            self.change_y = 0.0
        else: # still driving
            dist2p = self.center_x-self.parent.player_sprite.center_x
            if self.boost_to > 0:
                vel_x = 600
            elif dist2p > 1200:
                vel_x = 100
            elif dist2p > 700:
                vel_x = 300
            elif dist2p > 400:
                vel_x = 400
            else:
                vel_x = 400+(400-dist2p)
        
            self.change_x = vel_x/60.0
            
            # track y position
            if math.fabs(self.track_y-self.center_y) < (MAX_VERTICAL_MOVEMENT_SPEED/60):
                self.change_y = 0.0
            else:
                self.change_y = (MAX_VERTICAL_MOVEMENT_SPEED/60)*(self.track_y-self.center_y)/math.fabs(self.track_y-self.center_y)
        
        self.center_x += self.change_x
        self.center_y += self.change_y
        
        if self.change_x >= 0:
            self.face_right = True
        else:
            self.face_right = False
        
        # Look for behaviours
        fraction = self.center_x/self.level_width
        for action in self.action_data:
            if action[2] == True: # already completed this action
                continue
            if action[0] == 'boost':
                if fraction > action[1]:
                    self.boost_to = 300
                    action[2] = True
                    assets.game_sfx['boost'].play()
            elif action[0] == 'bomb':
                if fraction > action[1]:
                    self.bomblaunch_to = 60
                    action[2] = True
                    assets.game_sfx['hehheh'].play()
        if self.boost_to > 0:
            self.boost_to -= 1
        if self.bomblaunch_to > 0:
            self.bomblaunch_to -= 1
            if self.bomblaunch_to == 0:
                sprite = FloatingBomb(self.parent,self.parent.space,self.center_x,self.center_y,self.change_x/10,20*random.random()-10)
                self.parent.bomb_sprite_list.append(sprite)
                assets.game_sfx['bomblaunch'].play()
        
        # breakdown sparks
        if self.health == 0 and self.frame_ani == 0:
            for i in range(5):
                particle = Particle(4, 4, arcade.color.ORANGE)
                while particle.change_y == 0 and particle.change_x == 0:
                    particle.change_y = random.randrange(-2, 3)
                    particle.change_x = random.randrange(-2, 3)
                particle.center_x = self.center_x
                particle.center_y = self.center_y
                self.parent.particle_sprite_list.append(particle)
        
        # Update sprite/animations
        if self.flash_ani > 8:
            flash = 1
        elif self.flash_ani > 4:
            flash = 0
        elif self.flash_ani > 0:
            flash = 1
        else:
            flash = 0
        if self.flash_ani > 0:
            self.flash_ani -= 1
        
        # update textures
        self.frame_ani += 1
        if self.health == 0:
            repeat = 10
        else:
            repeat = 10
        if self.frame_ani > repeat:
            self.frame_ani = 0
        if self.frame_ani < (repeat/2) or self.health == 0:
            ani_fram = 0
        else:
            ani_fram = 1
        if flash == 1:
            ani_fram = 2 # flash from hit
        if self.face_right:
            heading_ind = 0
        else:
            heading_ind = 1
        self.texture = assets.bad_guys[self.type][ani_fram][heading_ind]
        
    def postdraw(self):
        if self.health > 0:
            meter_x = 100*(self.health/self.maxhealth)
            arcade.draw_text("Shield", self.center_x-40, self.center_y+80, arcade.color.WHITE, 18)
            arcade.draw_rectangle_filled(center_x=self.center_x-(50-meter_x/2), center_y=self.center_y+75,
                                      width=meter_x, height=10,
                                      color=arcade.color.ORANGE)
            arcade.draw_rectangle_outline(center_x=self.center_x, center_y=self.center_y+75,
                                      width=100, height=10,
                                      color=arcade.color.WHITE)
            if self.boost_to > 0:
                arcade.draw_text("Boost!", self.center_x-100, self.center_y, arcade.color.YELLOW, 18)
        else:
            arcade.draw_text("Disabled", self.center_x-50, self.center_y+75, arcade.color.WHITE, 18)

class FloatingBomb(arcade.Sprite):
    """ FloatingBomb: dropped by some bad guys """

    def __init__(self, parent, space, x, y, vx, vy):
        super().__init__()
        
        self.parent = parent
        self.center_x = x
        self.center_y = y
        self.type = type
        self.texture = assets.bomb_textures[0]
        radius = 25
        mass = 3.0
                
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0, 0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = pymunk.Vec2d(x, y)
        self.body.velocity = pymunk.Vec2d(vx, vy)
        self.body.angular_velocity = 4
        self.body.angle = random.random()
        self.shape = shape = pymunk.Circle(self.body, radius, pymunk.Vec2d(0, 0))
        self.shape.elasticity = 0.99
        self.shape.friction = 0.9
        self.shape.collision_type = 4
        
        self.space = space
        self.space.add(self.body, self.shape)
        
        self.frame_ani = 0
        self.explode_to = 40
    
    def hit(self, bullet):
        if bullet.change_x > 0:
            self.body.apply_impulse_at_world_point((100,0),(bullet.center_x,bullet.center_y))
        else:
            self.body.apply_impulse_at_world_point((-100,0),(bullet.center_x,bullet.center_y))
        
        """
        if self.health == 0:
            self.space.remove(self.shape, self.body)
            self.remove_from_sprite_lists()
        """
    
    def update(self):
        self.center_x = self.shape.body.position.x
        self.center_y = self.shape.body.position.y
        self.angle = math.degrees(self.shape.body.angle)
        
        dx = self.parent.player_sprite.center_x-self.center_x
        dy = self.parent.player_sprite.center_y-self.center_y
        dist2p = math.sqrt(dx*dx + dy*dy)
        if self.explode_to == 40 and dist2p < 200:
            self.explode_to = 39
            assets.game_sfx['fastbeeps'].play()
        if self.explode_to < 40:
            self.explode_to -= 1
            if self.explode_to == 0:
                assets.game_sfx['explode'].play()
                assets.game_sfx['fastbeeps'].stop()
                explosion = BombExplosion(self.parent,self.center_x,self.center_y)
                self.parent.bomb_sprite_list.append(explosion)
                self.space.remove(self.shape, self.body)
                self.remove_from_sprite_lists()
        
        self.frame_ani += 1
        if self.explode_to < 40:
            repeat = 10
        else:
            repeat = 60
        if self.frame_ani > repeat:
            self.frame_ani = 0
            if self.explode_to == 40:
                assets.game_sfx['beep'].play()
        if self.frame_ani < (repeat/3):
            ani_fram = 0
        else:
            ani_fram = 1
            
        self.texture = assets.bomb_textures[ani_fram]
        
        # remove self if left behind
        if dx > 1500:
            self.space.remove(self.shape, self.body)
            self.remove_from_sprite_lists()
        
class BombExplosion(arcade.Sprite):
    """ BombExplosion """

    def __init__(self,parent,x,y):
        super().__init__()
        self.parent = parent
        self.center_x = x
        self.center_y = y
        self.texture = assets.explodeb_textures[0]
        self.death_to = 20
        
        asteroid_hit_list = arcade.check_for_collision_with_list(self, self.parent.asteroid_sprite_list)
        for asteroid in asteroid_hit_list:
            dx = asteroid.center_x-self.center_x
            dy = asteroid.center_y-self.center_y
            dist = math.sqrt(dx*dx+dy*dy)
            if dist > 0:
                asteroid.body.apply_impulse_at_world_point((300*dx/dist,300*dy/dist),(asteroid.center_x,asteroid.center_y))
            else:
                asteroid.body.apply_impulse_at_world_point((200,200),(asteroid.center_x,asteroid.center_y))
        
        dx = self.parent.player_sprite.center_x-self.center_x
        dy = self.parent.player_sprite.center_y-self.center_y
        dist = math.sqrt(dx*dx+dy*dy)
        if dist < 200 and dist > 0:
            self.parent.player_sprite.body.apply_impulse_at_world_point((500*dx/dist,500*dy/dist),(self.parent.player_sprite.center_x,self.parent.player_sprite.center_y))
            self.parent.player_sprite.hit(damage=10)
    
    def update(self):
        if self.death_to >= 18:
            self.texture = assets.explodeb_textures[0]
        elif self.death_to >= 12:
            self.texture = assets.explodeb_textures[1]
        elif self.death_to >= 6:
            self.texture = assets.explodeb_textures[2]
        elif self.death_to >= 0:
            self.texture = assets.explodeb_textures[3]
        self.death_to -= 1
        if self.death_to == 0:
            self.remove_from_sprite_lists()
