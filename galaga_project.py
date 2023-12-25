"""
Comment: 

Video Links:

Additional Image Links:
Space image: https://i.imgur.com/0KzSXdk.jpeg
Galaga image: https://i.imgur.com/v8Zqc20.jpeg

## Galaga Features
# Milestone 1
[X] Spaceship exists
[X] Spaceship moves
[X] Holding keys
[X] Screen limits
# Milestone 2
[X] Aliens exist
[X] Aliens move
[X] Aliens wrap
[X] Aliens reset
[X] Aliens hurt
# Milestone 3
[X] Shoot lasers
[X] Lasers move
[X] Offscreen lasers
[X] Lasers hurt
[X] Game over
[X] Show stats
# Extra Credit
[X] Explosions
[X] Menus
[X] Items
[X] Tractor Beams

"""
#---------Import----------
from designer import *
from dataclasses import dataclass
from random import randint

#------------------Menu And Pause Screen Interface---------------------
@dataclass
class Button:
    background: DesignerObject
    border: DesignerObject
    label: DesignerObject
    
def make_button(message: str, x: int, y: int) -> Button:
    """
    Create interactable button with various functions.
    
    Args:
        message (str): word displayed on the button
        x (int): x-coordinate of the button
        y (int): y-coordinate of the button
        
    Returns:
        Button: a button dataclass that carries numerous DesignerObjects
    """
    label = text("forestgreen", message, 25, x, y, layer="top")
    x_padding = 10
    y_padding = 5
    return Button(rectangle("turquoise", label.width + x_padding,
                            label.height + y_padding, x, y),
                  rectangle("seagreen", label.width + x_padding,
                            label.height + y_padding, x, y, 3),
                  label)
    
@dataclass
class MenuScreen:
    header: DesignerObject
    play_button: Button
    quit_button: Button
    
def create_menuscreen() -> MenuScreen:
    """Create and decorate the menu screen of the game"""
    background_image("https://i.imgur.com/v8Zqc20.jpeg")
    return MenuScreen(text("chartreuse", "GALAGA", 100, 400,
                           120, font_name="Jokerman"),
                      make_button("Play Game", 400, 300),
                      make_button("Quit Game", 400, 420)
                      )

def handle_menuscreen(menu: MenuScreen):
    """
    Execute certain functions when button is clicked.
    Start game, or quit game.
    """
    if colliding_with_mouse(menu.play_button.background):
        change_scene("galaga")
    if colliding_with_mouse(menu.quit_button.background):
        quit()
        
@dataclass
class PauseScreen:
    header: DesignerObject
    resume_button: Button
    restart_button: Button
    return_to_menu: Button
    
def create_pausescreen() -> PauseScreen:
    """Create and decorate the pause screen of the game"""
    background_image("https://i.imgur.com/0KzSXdk.jpeg")
    return PauseScreen(text("chartreuse", "Game Paused", 100,
                            400, 120, font_name="Jokerman"),
                      make_button("Resume Game", 400, 300),
                      make_button("Restart Game", 400, 360),
                      make_button("Return to Menu", 400, 420)
                      )

def handle_pausescreen(pause: PauseScreen):
    """
    Execute certain functions when button is clicked.
    Resume/Restart the game, return to menu.
    """
    if colliding_with_mouse(pause.resume_button.background):
        pop_scene()
    if colliding_with_mouse(pause.restart_button.background):
        change_scene("galaga")
    if colliding_with_mouse(pause.return_to_menu.background):
        change_scene("menu")

#------------------OverWorld: Galaga game-----------------------
@dataclass
class GlobalData:
    ship_speed: int
    alien_x_speed: int
    alien_y_speed: int
    alien_spawn_rate: int
    laser_speed: int
    
@dataclass
class Spaceship:
    vehicle: DesignerObject
    left_active: bool
    right_active: bool
    skill_bar: list[DesignerObject]
    
@dataclass
class Enemyship:
    vehicle: DesignerObject
    move_switch: bool
    shoot_timer: int
    health: int
    health_bar: list[DesignerObject]
    
@dataclass
class Alien:
    creature: DesignerObject
    beam_timer: int
    tractor: list[DesignerObject]
    move_x_timer: int
    move_left: bool
    move_right: bool
    
@dataclass
class Laser: #Created in case of future properties.
    projectile: DesignerObject
    
#------Power ups------
@dataclass
class Powerup:
    decoration: list[DesignerObject]
    name: str
    
@dataclass
class ActivePower:
    triple_laser: bool
    timer: int

#----------------WORLD'S DATA-------------------
@dataclass
class World:
    constant: GlobalData
    ship: Spaceship
    background: list[DesignerObject]
    enemy_ship: list[Enemyship]
    enemy_laser: list[Laser]
    alien: list[Alien]
    laser: list[Laser]
    effect: list[DesignerObject]
    powerup: list[Powerup]
    active_skill: ActivePower
    laser_limit: int
    laser_max: int
    score: int
    lives: int
    raise_difficulty: bool
    score_stat: DesignerObject
    lives_stat: DesignerObject
    laser_lim_stat: DesignerObject
    pause_button: Button
    
#------Pause and Gameover Screen------
@dataclass
class GameoverScreen:
    header: DesignerObject
    gameover_text: DesignerObject
    play_again: Button
    return_to_menu: Button
        
def create_gameover_screen(score: int) -> GameoverScreen:
    """
    Create, decorate gameover screen,
    and show final score when player's live ran out.
    """
    background_image("https://i.imgur.com/0KzSXdk.jpeg")
    gameover_message = text("springgreen", "Your score is: ",
                            25, 400, 240, font_name = "Jokerman")
    gameover_message.text += str(score)
    return GameoverScreen(text("crimson", "Game Over!",
                               100, 400, 120, font_name="Jokerman"),
                          gameover_message,
                          make_button("Play Again", 400, 300),
                          make_button("Return to Menu", 400, 420)
                          )

def handle_gameover_screen(ended: GameoverScreen):
    """
    Execute certain functions when button is clicked.
    Play again, return to menu.
    """
    if colliding_with_mouse(ended.play_again.background):
        change_scene("galaga")
    if colliding_with_mouse(ended.return_to_menu.background):
        change_scene("menu")
        
def handle_pause_button(galaga: World):
    """
    Show pause screen when the pause button is clicked during the game.
    Ensure no movement is made when pausing to prevent 'auto move glitch'
    when resuming the game.
    """
    ship = galaga.ship
    if not ship.left_active and not ship.right_active:
        if colliding_with_mouse(galaga.pause_button.background):
            push_scene("pause")
    
#------------------Creating world and object--------------------s
def create_world() -> World:
    """ Creating the world where game is executed."""
    return World(GlobalData(10, 3, 3, 30, 10),
                 Spaceship(create_ship(45, 400, 480), False, False, []),
                 [create_background(0, 0, False), create_background(0, -600, True)],
                 [], [], [], [], [], [],
                 ActivePower(False, 0), 1, 10, 0, 3, False,
                 text("white", "", 25, get_width() * 0.9, get_height() * 0.08),
                 text("white", "", 25, get_width() * 0.9, get_height() * 0.12),
                 text("white", "", 25, get_width() * 0.9, get_height() * 0.16),
                 make_button("Pause", 50, 40)
                 )
def create_background(x: int, y: int, flip: bool) -> DesignerObject:
    """
    Creating the background of the game, adjusted with proper scale
    
    Args:
        x (int): x-coordinate where the image started to draw
        y (int): y-coordinate where the image started to draw
        flip (bool): Mirroring background
    
    Returns:
        DesignerObject: the background with image path
    """
    background = image("https://i.imgur.com/0KzSXdk.jpeg", x, y)
    background.anchor = "topleft"
    background.layer = "bottom"
    background.scale = [0.417, 0.556]
    background.flip_x = flip
    return background

def update_background(galaga: World):
    """
    Make background move inside the game to increase user's experience.
    Two images wrapping around and moving.
    """
    for background in galaga.background:
        background.y += 1
        if background.y == get_height():
            background.y = -get_height()

def create_ship(angle: int, x: int, y: int) -> DesignerObject:
    """
    Creating the ship and adjust its initial position
    and angle using xy-coordinate and angle.
    """
    ship = emoji("🚀", x, y)
    ship.angle = angle
    return ship

def create_alien() -> DesignerObject:
    """ Creating the alien and adjust its initial position"""
    monster = emoji("👾")
    monster.pos = [randint(1, get_width() - 1), 0]
    monster.anchor = "midtop"
    return monster

def create_tractor_beam(x: int, y: int) -> list[DesignerObject]:
    """
    Creating components of a tractor beam. Position adjusted
    using xy-coordinate of alien.
    """
    beam1 = arc("peachpuff", 225, 315, 20, 20, x, y + 30)
    beam2 = arc("limegreen", 220, 320, 25, 20, x, y + 45)
    beam3 = arc("peachpuff", 215, 325, 30, 20, x, y + 60)
    beam4 = arc("limegreen", 210, 330, 35, 20, x, y + 75)
    tractor_beam = [beam1, beam2, beam3, beam4]
    return tractor_beam

def create_laser(color: str, angle: int) -> DesignerObject:
    """
    Creating laser when the function is called.
    Different color assigned depend on feature.
    Angle affects the direction the laser will go.
    """
    laser = ellipse(color, 8, 25, anchor="midbottom")
    laser.angle = angle
    return laser

def create_bar(color: str, width: int, height: int,
               x: int, y: int) -> list[DesignerObject]:
    """
    Displaying bar for certain purposes: Health, timer...
    xy-coordinate is used to set its initial position.
    """
    bar = rectangle(color, width, height, x, y, anchor="midleft")
    border = rectangle("white", width, height, x, y, 2, anchor="midleft")
    health = [bar, border]
    return health

#------Powerup Item/Decoration-----------
"""x and y parameter in the functions below adjust the
spawn position of powerups"""

def power_item_laser(x: int, y: int) -> Powerup:
    """This powerup allows spaceship to shoot more laser at a time"""
    background = circle("lightcoral", 22, x, y)
    label = text("red", "+1", 15, x + 5, y + 10)
    laser = ellipse("red", 8, 25, x, y)
    laser.angle = -45
    return Powerup([background, label, laser], "LaserPlusOne")

def power_triple_laser(x: int, y: int) -> Powerup:
    """This powerup allows spaceship to triple and spread its laser"""
    background = circle("paleturquoise", 25, x, y)
    label = text("blue", "5 sec", 12, x, y + 15)
    laser1 = ellipse("deepskyblue", 6, 22, x - 10, y - 5)
    laser2 = ellipse("deepskyblue", 6, 22, x, y - 5)
    laser3 = ellipse("deepskyblue", 6, 22, x + 10, y - 5)
    laser1.angle = 25
    laser3.angle = -25
    return Powerup([background, label, laser1, laser2, laser3], "TripleLaser")

def power_plus_live(x: int, y: int) -> Powerup:
    """This powerup adds an extra live to the spaceship"""
    background = circle("purple", 22, x, y)
    label = text("fuchsia", "+1", 15, x + 10, y)
    heart = emoji("💖")
    heart.scale = 0.5
    heart.pos = [x - 8, y]
    return Powerup([background, label, heart], "LivePlusOne")

#----------Moving Ship----------
def activate_left_key(ship: Spaceship):
    """Check whether left arrow key or (a) is held down"""
    ship.left_active = True
    
def activate_right_key(ship: Spaceship):
    """Check whether right arrow key or (d) is held down"""
    ship.right_active = True
        
def deactivate_left_key(ship: Spaceship):
    """Check whether left arrow key or (a) is released"""
    ship.left_active = False
    
def deactivate_right_key(ship: Spaceship):
    """Check whether right arrow key or (d) is released"""
    ship.right_active = False
    
def press_key(galaga: World, key: str):
    """
    When specific key is pressed, ship will move.
    Press 'a' or 'left arrow' to move left.
    Press 'd' or 'right arrow' to move right.
    """
    if key == "a" or key == "left":
        activate_left_key(galaga.ship)
    if key == "d" or key == "right":
        activate_right_key(galaga.ship)
        
def release_key(galaga: World, key: str):
    """When key is released, ship will stop moving"""
    if key == "a" or key == "left":
        deactivate_left_key(galaga.ship)
    if key == "d" or key == "right":
        deactivate_right_key(galaga.ship)
        
def check_movement(galaga: World):
    """
    If left key or (a) is pressed, move spaceship to the left.
    If right key or (d) is pressed, move spaceship to the right.
    """
    if galaga.ship.left_active:
        move_ship(galaga, -galaga.constant.ship_speed)
    if galaga.ship.right_active:
        move_ship(galaga, galaga.constant.ship_speed)
        
def move_ship(galaga: World, speed: int):
    """
    Moving the x-coordinate of the spaceship. Stop ship from moving
    offscreen when it is on the edge by deactivating movement keys
    Ship will not move even when key is pressed.
    """
    ship = galaga.ship.vehicle
    width = get_width()
    if ship.x % width:
        ship.x += speed
    if ship.x <= 0:
        deactivate_left_key(galaga.ship)
    if ship.x >= width:
        deactivate_right_key(galaga.ship)

def enable_movement(galaga: World):
    """Reactivate movement keys when the ship is on the edge of screen"""
    ship = galaga.ship
    if not ship.left_active and ship.vehicle.x <= 0:
        ship.vehicle.x = 10
        activate_left_key(galaga.ship)
    if not ship.right_active and ship.vehicle.x >= get_width():
        ship.vehicle.x = get_width() - 10
        activate_right_key(galaga.ship)
        
def move_ship_bar(galaga: World):
    """Always station skill timer bar belows user's ship"""
    for bar in galaga.ship.skill_bar:
        bar.x = galaga.ship.vehicle.x - 30
    
#------------------Alien spawns, movement, limit-------------------
def spawn_alien(galaga: World):
    """
    Spawn alien at a random interval of time, and limit the number of
    alien spawned at a time.
    """
    alien_count_limit = len(galaga.alien) < 20
    random_chance = randint(1,galaga.constant.alien_spawn_rate) == 1
    if alien_count_limit and random_chance:
        galaga.alien.append(Alien(create_alien(), 0, [], 0, False, False))
        
def make_alien_move(galaga: World):
    """
    Make all aliens in the game automatically move downward
    after being spawned. Aliens will also loop back to the top
    when they go offscreen.
    """
    for alien in galaga.alien:
        alien.creature.y += galaga.constant.alien_y_speed
        if alien.creature.y >= get_height():
            alien.creature.y = 0
            
def move_x_timer(galaga: World):
    """
    Track and initiate horizontal movement of alien, increasing
    difficulty of the game after a certain score is reached.
    """
    if galaga.score >= 150:
        for alien in galaga.alien:
            if not alien.move_x_timer:
                alien.move_x_timer = 105
            if alien.move_x_timer > 0:
                alien.move_x_timer -= 1
                
def alien_direction(galaga: World):
    """
    Allow aliens to move horizontally for a certain amount of time.
    Then stay in its x position for a short amount of time.
    Then repeat.
    """
    for alien in galaga.alien:
        if alien.move_x_timer == 104:
            if randint(1,100) <= 50:
                alien.move_left = True
            else:
                alien.move_right = True
        if alien.move_x_timer == 30:
            alien.move_left = False
            alien.move_right = False
            
def move_x_alien(galaga: World):
    """Actual horizontal movement function of alien"""
    for alien in galaga.alien:
        if alien.move_left:
            alien.creature.x -= galaga.constant.alien_x_speed
        if alien.move_right:
            alien.creature.x += galaga.constant.alien_x_speed
                
def bounce_alien(galaga: World):
    """
    Bounce the alien the opposite way if it touches the
    left or right edge of the screen.
    """
    for alien in galaga.alien:
        if alien.creature.x <= 0:
            alien.move_left = False
            alien.move_right = True
        if alien.creature.x >= get_width():
            alien.move_left = True
            alien.move_right = False

#---------Alien Beam Tractor and associated ship mechanic---------
def alien_beam_chance(galaga: World):
    """
    Set the chance that alien will produce tractor beam
    for short amount of time, but appear regularly.
    """
    for alien in galaga.alien:
        if randint(1,200) == 50:
            alien.beam_timer = 60
        if alien.beam_timer > 0:
            alien.beam_timer -= 1
            
def alien_beaming(galaga: World):
    """
    Producing tractor beam when the chance occurs.
    Prepare to remove the beam when its timer run out.
    """
    expired_beam = []
    for alien in galaga.alien:
        if alien.beam_timer and not alien.tractor and alien.creature.y < 525:
            alien.tractor = create_tractor_beam(alien.creature.x, alien.creature.y)
        if not alien.beam_timer and alien.tractor:
            for tractor in alien.tractor:
                expired_beam.append(tractor)
        alien.tractor = filter_beam(alien.tractor, expired_beam)
            
def move_beam(galaga: World):
    """Make the beam always follow and stay below the alien position"""
    for alien in galaga.alien:
        if alien.tractor:
            for tractor in alien.tractor:
                tractor.x = alien.creature.x
                tractor.y += galaga.constant.alien_y_speed
                if tractor.y > get_height():
                    tractor.y = 0
                    
def filter_beam(all_beam: list[DesignerObject],
                expired_beam: list[DesignerObject]) -> list[DesignerObject]:
    """
    Check for beams that had their timer ran out,
    and remove them from the game's data.
    
    Args:
        all_beam (list[DesignerObject]): all beam in the world's data
        expired_beam (list[DesignerObject]): beam with expired timer
        
    Returns:
        list[DesignerObject]: beam with active timer
    """
    unexpired_beam = []
    for beam in all_beam:
        if beam in expired_beam:
            destroy(beam)
        else:
            unexpired_beam.append(beam)
    return unexpired_beam

#----------Respawning ship mechanic-------------
def respawn_ship(galaga: World):
    """Respawn the ship and ship loses a life"""
    ship = galaga.ship.vehicle
    ship.pos = [get_width() / 2, get_height() * 0.8]
    ship.alpha = 0.1
    galaga.lives -= 1
    
def reset_alpha(galaga: World):
    """
    The opacity of the spaceship, used as an indicator of invincibility
    after ship collision with alien.
    When opacity is less than 1, it stays invincible. If opacity is greater
    or equal to 1, the ship will then be able to take damage.
    Duration of invincibility: ~ 3 seconds
    """
    if galaga.ship.vehicle.alpha < 1.0:
        galaga.ship.vehicle.alpha += 0.01

#-----Collided ship to beam-----
def collide_ship_beam(galaga: World):
    """
    Check if user's ship collided with alien's tractor beam.
    If collided, spawn an enemy ship on top of screen to fight the user,
    show its health bar.
    Enemyship has 15 hitpoints.
    Effect added on beam collision.
    Ship respawn.
    """
    ship = galaga.ship.vehicle
    for alien in galaga.alien:
        for tractor in alien.tractor:
            if ship.alpha >= 1.0 and colliding(tractor, ship):
                galaga.enemy_ship.append(
                    Enemyship(create_ship(225,ship.x, 25), True, 0, 15,
                              create_bar("red", 60, 10, ship.x - 30, 60)))
                effect = emoji("💫", ship.x, ship.y)
                galaga.effect.append(effect)
                respawn_ship(galaga)
                
#---------------Enemy Ship Mechanic---------------         
def move_enemy_ship(galaga: World):
    """
    Configure the movement of enemy ships that were spawned
    when the user's ship collided with alien's tractor beam.
    """
    for enemy in galaga.enemy_ship:
        ship = enemy.vehicle
        if ship.x >= 0 and enemy.move_switch:
            ship.x += galaga.constant.ship_speed
        if ship.x <= 800 and not enemy.move_switch:
            ship.x -= galaga.constant.ship_speed
        if ship.x <= 0:
            enemy.move_switch = True
        if ship.x >= 800:
            enemy.move_switch = False
            
def move_enemy_health(galaga: World):
    """Set the health bar below the enemyship and always follow the ship"""
    for enemy in galaga.enemy_ship:
        for bar in enemy.health_bar:
            bar.x = enemy.vehicle.x - 30
            
def set_enemy_laser(laser: DesignerObject, ship: DesignerObject):
    """Set laser's initial position of enemy ship to its firing tip"""
    laser.x = ship.x
    laser.y = ship.y + ship.height
            
def enemy_ship_laser(galaga: World):
    """Make enemy ship shoot laser at a fixed time interval"""
    for enemy in galaga.enemy_ship:
        if enemy.shoot_timer < 2:
            laser = Laser(create_laser("khaki", 180))
            set_enemy_laser(laser.projectile, enemy.vehicle)
            galaga.enemy_laser.append(laser)
            
def move_enemy_laser(galaga: World):
    """
    Make enemyship's laser move down automatically,
    and prepare to remove it when it goes offscreen.
    """
    remove_laser = []
    for laser in galaga.enemy_laser:
        laser.projectile.y += galaga.constant.laser_speed
        if laser.projectile.y > get_height():
            remove_laser.append(laser)
    galaga.enemy_laser = filter_laser(galaga.enemy_laser, remove_laser)
            
def enemy_shoot_timer(galaga: World):
    """Adjust the interval of time the enemyship shoot"""
    for enemy in galaga.enemy_ship:
        if enemy.shoot_timer > 0:
            enemy.shoot_timer -= 1
        if enemy.shoot_timer <= 0:
            enemy.shoot_timer = 15

def collide_enemy_laser(galaga: World):
    """
    Check if enemyship's laser collided with the user's ship.
    If collided, player loses 1 life and respwawn.
    Effect added on collision.
    """
    collided_laser = []
    ship = galaga.ship.vehicle
    for laser in galaga.enemy_laser:
        if ship.alpha >= 1.0 and colliding(laser.projectile, ship):
            effect = emoji("💥", ship.x, ship.y)
            galaga.effect.append(effect)
            collided_laser.append(laser)
            respawn_ship(galaga)
    galaga.enemy_laser = filter_laser(galaga.enemy_laser, collided_laser)

#-------Attacking enemyship-------
def attack_enemy_ship(galaga: World):
    """
    Check if user's ship's laser hit the enemyship.
    If hit, decrease the enemy's hitpoint by 1.
    Health bar will also decreases.
    Remove collided lasers from the world's data.
    """
    remove_laser = []
    for laser in galaga.laser:
        for ship in galaga.enemy_ship:
            if colliding(laser.projectile, ship.vehicle):
                ship.health -= 1
                ship.health_bar[0].width -= 4
                remove_laser.append(laser)
                if ship.health > 0:
                    effect = emoji("🌟", ship.vehicle.x,
                                           ship.vehicle.y)
                    galaga.effect.append(effect)
    galaga.laser = filter_laser(galaga.laser, remove_laser)
                
def check_enemy_health(galaga: World):
    """
    Check if enemyship's health is greater than 0.
    If not, remove the ship, and player's gain 15 score.
    Effect added upon enemyship's destruction.
    """
    remove_ship = []
    for ship in galaga.enemy_ship:
        if not ship.health:
            effect = emoji("💥", ship.vehicle.x, ship.vehicle.y)
            galaga.effect.append(effect)
            remove_ship.append(ship)
            galaga.score += 15
    galaga.enemy_ship = filter_enemy_ship(galaga.enemy_ship, remove_ship)
            
    
def filter_enemy_ship(enemyship: list[Enemyship],
                      destroyed: list[Enemyship]) -> list[Enemyship]:
    """
    Actual function that filters destroyed ship out of the world's data.
    
    Args:
        enemy (list[Enemyship]): all enemyship existing in world's data
        destroyed (list[Enemyship]): enemyship that has no more health
        
    Returns:
        list[Enemyship]: returns list of surviving enemyship
    """
    intact_ship = []
    for enemy in enemyship:
        if enemy in destroyed:
            destroy(enemy.vehicle)
            for bar in enemy.health_bar:
                destroy(bar)
        else:
            intact_ship.append(enemy)
    return intact_ship
                
#----------Alien hurts-----------
def collide_ship_alien(galaga: World):
    """
    Check whether spaceship and alien are collided with each other.
    If they are collided, the damaged alien will be removed,
    the spaceship will lose a life and reset to its spawn position.
    After collision, the spaceship will have about 3 seconds grace period
    of invincibility.
    """
    collided_alien = []
    remove_beam = []
    ship = galaga.ship.vehicle
    for alien in galaga.alien:
        if ship.alpha >= 1.0 and colliding(alien.creature, ship):
            #Create explosion
            effect = emoji("💥", alien.creature.x,
                             (alien.creature.y + ship.y) / 2)
            galaga.effect.append(effect)
            #Damaged alien and respawn ship
            collided_alien.append(alien)
            respawn_ship(galaga)
            #Remove beam if exists
            for tractor in alien.tractor:
                remove_beam.append(tractor)
        alien.tractor = filter_beam(alien.tractor, remove_beam)       
    galaga.alien = filter_alien(galaga.alien, collided_alien)
                
def filter_alien(all_alien:list[Alien],
                 collided_alien:list[Alien]) -> list[Alien]:
    """
    This function removes collided alien from the list of Alien in game,
    keeping the good data and save memory, also preventing self-destroy
    object error.
    
    Args:
        all_alien (list[Alien]): All aliens in the game
        collided_alien (list[Alien]): List of collided alien
                                    
    Returns:
        list[Alien]: return a list of undamaged aliens
    """
    undamaged_alien = []
    for alien in all_alien:
        if alien in collided_alien:
            destroy(alien.creature)
        else:
            undamaged_alien.append(alien)
    return undamaged_alien
    
#------------------Laser Position and Movement-------------------
def set_laser_position(laser: DesignerObject, ship: DesignerObject):
    """Set laser's initial position to top of the spaceship when fired"""
    laser.x = ship.x
    laser.y = ship.y - ship.height / 2
    
def shoot_laser(galaga: World, key: str):
    """
    When spacebar is pressed, the spaceship will shoot a laser.
    Amount of laser is limited until powerup is obtained to ensure
    an enjoyable game.
    Configure the triple laser skill to overwrite normal laser when
    the powerup is active.
    """
    if key == "space":
        if galaga.active_skill.triple_laser:
            if len(galaga.laser) + 3 <= galaga.laser_limit:
                triple = [Laser(create_laser("deepskyblue", -25)),
                          Laser(create_laser("deepskyblue", 0)),
                          Laser(create_laser("deepskyblue", 25))]
                for laser in triple:
                    set_laser_position(laser.projectile, galaga.ship.vehicle)
                    galaga.laser.append(laser)
        elif len(galaga.laser) < galaga.laser_limit:
            norm_laser = Laser(create_laser("red", 0))
            set_laser_position(norm_laser.projectile, galaga.ship.vehicle)
            galaga.laser.append(norm_laser)
        
def laser_move(galaga: World, angles: int):
    """Make laser move toward the direction it faced after shooting"""
    for laser in galaga.laser:
        move_angle = laser.projectile.angle + 90
        move_forward(laser.projectile, galaga.constant.laser_speed, move_angle)

#------Offscreen laser------
def offscreen_laser(galaga: World):
    """Destroy all lasers that go offscreen"""
    remove_laser = []
    for laser in galaga.laser:
        if laser.projectile.y < 0:
            remove_laser.append(laser)
    galaga.laser = filter_laser(galaga.laser, remove_laser)
    
def filter_laser(keeping: list[Laser],
                 removing: list[Laser]) -> list[Laser]:
    """
    Remove unnecessary lasers from the game's data, saving memory.
    
    Args:
        keeping (list[Laser]): all lasers stored in the game
        removing (list[Laser]): unnecessary lasers that need to be removed
        
    Returns:
        list[Laser]: return list of lasers after removing all unneeded lasers
    """
    keep_laser = []
    for laser in keeping:
        if laser in removing:
            destroy(laser.projectile)
        else:
            keep_laser.append(laser)
    return keep_laser

#------Collided Laser & Alien------

def collide_laser_alien(galaga: World):
    """
    Check whether laser collided with alien. If they are collided,
    both the laser and alien will be destroyed, and player's score
    will increase by 1.
    Handle powerup drop chance and its spawn position.
    """
    collided_laser = []
    collided_alien = []
    remove_beam = []
    for laser in galaga.laser:
        for alien in galaga.alien:
            if colliding(alien.creature, laser.projectile):
                #Create explosion
                effect = emoji("💥", alien.creature.x, alien.creature.y)
                galaga.effect.append(effect)
                #Laser and alien collision mechanic + score
                collided_laser.append(laser)
                collided_alien.append(alien)
                galaga.score += 1
                #--------PowerUp Mechanic--------
                x = alien.creature.x
                y = alien.creature.y
                #LaserPlusOne drop chance (3.3%)
                lpo_drop_chance = randint(1,30) == 15
                if lpo_drop_chance:
                    lpo_drop = power_item_laser(x, y)
                    galaga.powerup.append(lpo_drop)
                #Triple Laser drop chance (2%)
                triple_laser_chance = randint(1,50) == 25
                if triple_laser_chance:
                    triple_drop = power_triple_laser(x, y)
                    galaga.powerup.append(triple_drop)
                #LivePlusOne drop chance (0.5%)
                plus_live_chance = randint(1,500) == 250
                if plus_live_chance:
                    live_drop = power_plus_live(x, y)
                    galaga.powerup.append(live_drop)
            #Remove beam if exists
                if alien.tractor:
                    for tractor in alien.tractor:
                        remove_beam.append(tractor)
            alien.tractor = filter_beam(alien.tractor, remove_beam)
        
    galaga.alien = filter_alien(galaga.alien, collided_alien)
    galaga.laser = filter_laser(galaga.laser, collided_laser)
    
#------Explosion handling------
def animate_effect(galaga: World):
    """
    Animate effect by growing its size while fading and
    disappearing after a certain amount of time. Remove all
    faded effect to prevent game lag and save memory.
    """
    faded_effect = []
    for effect in galaga.effect:
        effect.scale += 0.1
        effect.alpha -= 0.08
        effect.angle += 10
        if effect.alpha < 0.0:
            faded_effect.append(effect)
    galaga.effect = remove_effect(galaga.effect, faded_effect)
        
def remove_effect(visible: list[DesignerObject], faded: list[DesignerObject]) -> list[DesignerObject]:
    """
    Check whether the effect is visible or faded. If it
    is faded, destroy the effect.
    
    Args:
        visible (list[DesignerObject]): all effect occurred
        faded (list[DesignerObject]): effect that is completed faded
    
    Returns:
        list[DesignerObject]: return list of effects that are still visible.
    """
    visible_effect = []
    for effect in visible:
        if effect in faded:
            destroy(effect)
        else:
            visible_effect.append(effect)
    return visible_effect

#------------------Item/powerup Control-----------------------
def move_powerup(galaga: World):
    """Make dropped powerup move downward and wrap around when offscreened"""
    for power in galaga.powerup:
        for decorations in power.decoration:
            decorations.y += 3
            if decorations.y > get_height() + 50:
                decorations.y = -50
                
def consume_lpo_powerup(galaga: World):
    """
    Handle LaserPlusOne Powerup. Increase laser limit
    in the gamescreen by 1. Max allowed: 10.
    Also handle limit accordingly when triple laser skill
    is active.
    """
    consumed_power = []
    for power in galaga.powerup:
        if colliding(power.decoration[0], galaga.ship.vehicle):
            if power.name == "LaserPlusOne":
                consumed_power.append(power)
                if galaga.laser_limit < galaga.laser_max:
                    if galaga.active_skill.triple_laser:
                        galaga.laser_limit += 3
                    else:
                        galaga.laser_limit += 1
    galaga.powerup = handle_consumed_powerup(galaga.powerup, consumed_power)
    
def consume_triple_laser(galaga: World):
    """
    Handle triple laser powerup. Temporarily triple the laser limit.
    One shot will spread into 3 lasers. Prevent obtaining another
    triple laser powerup when current one is still active. Show status bar.
    Duration: ~ 5 seconds
    """
    ship = galaga.ship.vehicle
    skill = galaga.active_skill
    consumed_power = []
    if skill.triple_laser and not galaga.active_skill.timer:
        galaga.laser_limit //= 3
        galaga.laser_max //= 3
        skill.triple_laser = False
    for power in galaga.powerup:
        if colliding(power.decoration[0], ship) and not galaga.active_skill.timer:
            if power.name == "TripleLaser":
                galaga.ship.skill_bar = create_bar("deepskyblue", 60, 10,
                                   ship.x - 30, ship.y + 35)
                galaga.active_skill.timer = 150
                consumed_power.append(power)
                galaga.laser_limit *= 3
                galaga.laser_max *= 3
                skill.triple_laser = True
    
    galaga.powerup = handle_consumed_powerup(galaga.powerup, consumed_power)
    
def consume_plus_live(galaga: World):
    """Handle LivePlusOne powerup. Increase user's ship's lives by 1"""
    consumed_power = []
    for power in galaga.powerup:
        if colliding(power.decoration[0], galaga.ship.vehicle):
            if power.name == "LivePlusOne":
                galaga.lives += 1
                consumed_power.append(power)
    galaga.powerup = handle_consumed_powerup(galaga.powerup, consumed_power)
    
def handle_consumed_powerup(powerup: list[Powerup], consumed: list[Powerup]) -> list[Powerup]:
    """Removing consumed powerup when it collided with the user's ship"""
    unconsumed_power = []
    for power in powerup:
        if power in consumed:
            for decorations in power.decoration:
                destroy(decorations)
        else:
            unconsumed_power.append(power)
    return unconsumed_power

def skill_timer(galaga: World):
    """
    Used to time active/temporary powerup. Show the
    duration status of an active skill.
    """
    if galaga.active_skill.timer > 0:
        galaga.active_skill.timer -= 1
            
def remove_skill_bar(galaga: World):
    """Remove the duration status bar when certain powerup effect ended."""
    timer_bar = galaga.ship.skill_bar
    if galaga.active_skill.triple_laser and timer_bar:
        timer_bar[0].width -= 60/149
    if timer_bar:
        if timer_bar[0].width <= 0:
            for bar in timer_bar:
                destroy(bar)
            galaga.ship.skill_bar = []
            
#---------------Increase Difficulty----------------
def increase_difficulty(galaga: World):
    """
    Increase alien speed and spawn rate every 100 score.
    Max x_speed: 5, max y_speed: 10, max spawn rate 10% per update.
    """
    constant = galaga.constant
    if galaga.score and not galaga.score % 100 and not galaga.raise_difficulty:
        if constant.alien_y_speed < 10:
            constant.alien_y_speed += 1
        if constant.alien_x_speed < 5:
            constant.alien_x_speed += 1
        if constant.alien_spawn_rate > 10:
            constant.alien_spawn_rate -= 1
        galaga.raise_difficulty = True
    if galaga.score % 100 == 1:
        galaga.raise_difficulty = False

#------------------Game stats and ending------------------------
def show_stats(galaga: World):
    """
    Shows essential counter on the gamescreen:
    Live, Score, Laser Limit
    """
    lstat = galaga.laser_lim_stat
    galaga.score_stat.text = f"Score: {galaga.score}"
    galaga.lives_stat.text = f"Lives: {galaga.lives}"
    lstat.text = f"Laser: {galaga.laser_limit}/{galaga.laser_max}"
    
def flash_game_over(galaga: World):
    """
    Clean out all objects behind the scene when game ended. Not really
    needed with the presence of gameover scene, but can save some memory.
    """
    for alien in galaga.alien:
        destroy(alien.creature)
        for tractor in alien.tractor:
            destroy(tractor)
    galaga.alien = []
    for laser in galaga.laser:
        destroy(laser.projectile)
    galaga.laser = []
    for laser in galaga.enemy_laser:
        destroy(laser.projectile)
    galaga.enemy_laser = []
    for effect in galaga.effect:
        destroy(effect)
    galaga.effect = []
    for ship in galaga.enemy_ship:
        destroy(ship.vehicle)
        for objects in ship.health_bar:
            destroy(objects)
        ship.health_bar = []
    galaga.enemy_ship = []
    galaga.ship.vehicle.alpha = 0
    
def out_of_lives(galaga: World) -> bool:
    """Check if the ship ran out of lives. If it does, stop the game"""
    if not galaga.lives:
        flash_game_over(galaga)
        push_scene("gameover", score=galaga.score)

#------------------Game Running Commands------------------------
when("starting: menu", create_menuscreen)
when("clicking: menu", handle_menuscreen)

when("starting: galaga", create_world)
when("clicking: galaga", handle_pause_button)
when("typing: galaga", press_key)
when("done typing: galaga", release_key)
when("updating: galaga", update_background)
when("updating: galaga", check_movement, enable_movement, move_ship_bar)
when("updating: galaga", spawn_alien, make_alien_move, move_x_timer,
     move_x_alien, alien_direction, bounce_alien)
when("updating: galaga", alien_beam_chance,
     alien_beaming, move_beam)
when("updating: galaga", collide_ship_beam, collide_ship_alien,
     collide_enemy_laser, reset_alpha)
when("updating: galaga", move_enemy_ship, move_enemy_laser,
     enemy_ship_laser, move_enemy_health, enemy_shoot_timer)
when("updating: galaga", attack_enemy_ship, check_enemy_health)
when("typing: galaga", shoot_laser)
when("updating: galaga", laser_move, offscreen_laser)
when("updating: galaga", collide_laser_alien)
when("updating: galaga", animate_effect)
when("updating: galaga", move_powerup, consume_lpo_powerup,
     consume_triple_laser, consume_plus_live, skill_timer, remove_skill_bar)
when("updating: galaga", increase_difficulty)
when("updating: galaga", show_stats)
when("updating: galaga", out_of_lives)

when("starting: pause", create_pausescreen)
when("clicking: pause", handle_pausescreen)

when("starting: gameover", create_gameover_screen)
when("clicking: gameover", handle_gameover_screen)
start(scene = "menu")