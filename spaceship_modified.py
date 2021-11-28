import pygame
import random
import numpy as np

# Set up Global 'constants'
FRAME_REFRESH_RATE = 30
DISPLAY_WIDTH = 300
DISPLAY_HEIGHT = 400
STARSHIP_SPEED = 20
BACKGROUND=(0,0,0)
INITIAL_METEOR_Y_LOCATION = 10
MAX_METEOR_SPEED = 5
INITIAL_NUMBER_OF_METEORS = 3
MAX_NUMBER_OF_CYCLES = 1000
DISPLAYON=False

class Game:
    """ Represents the game itself and game playing
    loop """
    def __init__(self):
        #print('Initialising PyGame')
        pygame.init()
        # Set up the display 
        self.display_surface =pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption('Starship Meteors')
        # Used for timing within the program.
        self.clock = pygame.time.Clock()
        # Set up the starship
        self.starship = Starship(self)
        # Set up meteors
        self.meteors = [Meteor(self) for _ in range(0, INITIAL_NUMBER_OF_METEORS)]
    def _check_for_collision(self):
        """ Checks to see if any of the meteors have collided with
        the starship """
        result = False
        for meteor in self.meteors:
            if self.starship.rect().colliderect(meteor.rect()):
                result = True
                break
        return result
    

    def playfirststep(self): 
        cycle_count=0
        # Work out what the user wants to do 
        # Move the Meteors
        for event in pygame.event.get():
            #print('in event queue')
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    is_running = False
        action=self.starship.policy()
        if action==1:
            # Right action 
            # move the player right 
            #print('right')
            self.starship.move_right()
        elif action==-1:
            # Left action 
            # move the player left 
            #print('left')
            self.starship.move_left()
        elif action==0:
            pass
        elif action==-2:
            self.starship.move_down()
        elif action==2:
            self.starship.move_up()
            #print('stay')
        
        # Move the Meteors
        for meteor in self.meteors:
            meteor.move_down()
        if DISPLAYON:
            # Clear the screen of current contents
            self.display_surface.fill(BACKGROUND)
            # Draw the starship
            self.starship.draw()
            for meteor in self.meteors:
                meteor.draw()
            # Update the display
            pygame.display.update()
            # Defines the frame rate
            self.clock.tick(FRAME_REFRESH_RATE)
        cycle_count+=1
        
        starship_state=[self.starship.x,self.starship.y]
        meteor_state=[]
        reward=0
        for meteor in self.meteors:
            dist=np.sqrt((meteor.x-self.starship.x)**2+(meteor.y-self.starship.y)**2)
            reward+=-np.exp((10*(100-dist)/500))
            meteor_state.append([meteor.x,meteor.y,meteor.speed,meteor.x-self.starship.x,meteor.y-self.starship.y,dist])
        # Check to see if a meteor has hit the ship
        if self._check_for_collision():
            starship_collided = True
            end=True
            reward=-5000
            #print('Score : ',cycle_count)
        # See if the player has won
        elif cycle_count == MAX_NUMBER_OF_CYCLES:
            end=True
            #print('WINNER!')
            reward=+5000
            if DISPLAYON:
                pygame.quit()
        else:
            end=False
        return starship_state,meteor_state,end,cycle_count,reward

    def playstep(self,starship_state,meteor_state,cycle_count,action): 
        self.starship.x,self.starship.y=starship_state[0],starship_state[1]
        for meteor,state in zip(self.meteors,meteor_state):
            meteor.x,meteor.y,meteor.speed=state[0],state[1],state[2]
        # Work out what the user wants to do 
        for event in pygame.event.get():
            #print('in event queue')
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    is_running = False
        if action==1:
            # Right action 
            # move the player right 
            #print('right')
            self.starship.move_right()
        elif action==-1:
            # Left action 
            # move the player left 
            #print('left')
            self.starship.move_left()
        elif action==0:
            pass
        elif action==-2:
            self.starship.move_down()
        elif action==2:
            self.starship.move_up()
            #print('stay')
        
        # Move the Meteors
        for meteor in self.meteors:
            meteor.move_down()
        if DISPLAYON:
            # Clear the screen of current contents
            self.display_surface.fill(BACKGROUND)
            # Draw the starship
            self.starship.draw()
            for meteor in self.meteors:
                meteor.draw()
            # Update the display
            pygame.display.update()
            # Defines the frame rate
            self.clock.tick(FRAME_REFRESH_RATE)
        cycle_count+=1
        
        starship_state=[self.starship.x,self.starship.y]
        meteor_state=[]
        reward=0
        for meteor in self.meteors:
            dist=np.sqrt((meteor.x-self.starship.x)**2+(meteor.y-self.starship.y)**2)
            reward+=-np.exp((10*(100-dist)/500))
            meteor_state.append([meteor.x,meteor.y,meteor.speed,meteor.x-self.starship.x,meteor.y-self.starship.y,dist])
        # Check to see if a meteor has hit the ship
        if self._check_for_collision():
            starship_collided = True
            end=True
            reward=-5000
            #print('Score : ',cycle_count)
        # See if the player has won
        elif cycle_count == MAX_NUMBER_OF_CYCLES:
            end=True
            #print('WINNER!')
            reward=+5000
            if DISPLAYON:
                pygame.quit()
        else:
            end=False
        return starship_state,meteor_state,end,cycle_count,reward
        
    # Let pygame shutdown gracefully
    

class GameObject:
    def load_image(self, filename):
        self.image = pygame.image.load(filename).convert()
        self.image = pygame.transform.scale(self.image, (30, 30))
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    def rect(self):
        """ Generates a rectangle representing the objects
        location and dimensions """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    def draw(self):
        """ draw the game object at the
        current x, y coordinates """
        self.game.display_surface.blit(self.image, (self.x, self.y))

class Starship(GameObject):
    """ Represents a starship"""
    def __init__(self, game):
        self.game = game
        self.x = DISPLAY_WIDTH / 2
        self.y = DISPLAY_HEIGHT - 40
        self.load_image('starship.png')
    def policy(self):
        actions=[-1,0,1]
        return np.random.choice(actions)
    def move_right(self):
        """moves the star ship to the right across the screen"""
        self.x=self.x+STARSHIP_SPEED
        if self.x+self.width>DISPLAY_WIDTH:
            self.x=DISPLAY_WIDTH-self.width
    def move_left(self):
        """moves the star ship to the left across the screen"""
        self.x=self.x-STARSHIP_SPEED
        if self.x<0:
            self.x=0
    def move_up(self):
        """moves the star ship up the screen"""
        self.y=self.y-STARSHIP_SPEED
        if self.y<0:
            self.y=0
    def move_down(self):
        """moves the star ship up the screen"""
        self.y=self.y+STARSHIP_SPEED
        if self.y+self.height>DISPLAY_HEIGHT:
            self.y=DISPLAY_HEIGHT-self.height
    def __str__(self):
        return 'Starship('+str(self.x)+','+str(self.y)+')'

class Meteor(GameObject):
    """ represents a meteor in the game """
    def __init__(self, game):
        self.game = game
        self.x = random.randint(0, DISPLAY_WIDTH)
        self.y = INITIAL_METEOR_Y_LOCATION
        self.speed = random.randint(1, MAX_METEOR_SPEED)
        self.load_image('meteor.png')
    def move_down(self):
        """ Move the meteor down the screen """
        self.y = self.y + self.speed
        if self.y > DISPLAY_HEIGHT:
            self.y = 5
            self.x = random.randint(0, DISPLAY_WIDTH)
    def __str__(self):
        return 'Meteor(' + str(self.x) + ', ' + str(self.y) +')'

def main(): 
    print('Starting Game')
    game = Game()
    #game.play()
    starship_state,meteor_state,end,cycle_count,reward=game.playfirststep()
    while not end:
        action = np.random.choice([-1,0,1])
        #action =0
        starship_state,meteor_state,end,cycle_count,reward=\
            game.playstep(starship_state,meteor_state,cycle_count,action)
        print(starship_state,meteor_state,end,cycle_count,reward)
    print('Game Over')
if __name__ == '__main__':
    main()