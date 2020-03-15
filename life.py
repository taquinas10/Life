#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
We will create boulncing balls with mass proportional to a random size that have prefectly elastic collisions 
and where collisions between a male and female ball has a chance of resulting in a pregnancy(after adolescence). 
The balls die after a set time and have a speed which is lower during pregnancy. Balls resulting from
a pregnancy inherit some characteristics of both parents. Initially the pregnancies were virus transmissions and
hence the rather politically incorrect "angry" images for pregnancies. 
Future thoughts: predator balls, partial seperation of areas to make populations heterogeneous.
Current settings gives a stable population between 100-150.


NOTE "IMAGEPATH" TO WHERE YOU HAVE PLACED THE Flushed_Face_Emoji.png and angrySmiley1.png IMAGES OF THE BALLS.
I used these images for my program:
https://www.pngfind.com/mpng/oRTwo_flushed-face-emoji-wide-eyed-emoji-png-transparent/
and 
https://imgbin.com/png/pZ9Gp7nb/emoji-emoticon-anger-smiley-face-png
but feel free to use whatever images you want.
"""
import numpy as np
import pygame
import sys
import random
from pygame.locals import*
import math
import operator

"""balls!"""

# Define some stuff
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BALL_SIZE =0.7
LOWSPEED=-7.0
HIGHSPEED=7.0
BALLMASS=1.0
CHANCEPREGNANT=45
TIMEBEFORERELAX=2.5
LIFESPAN=1500
IMAGEPATH= "/Users/martinskoglund1/Desktop/"

Smiley = pygame.sprite.Group()
others = pygame.sprite.Group()
Angry= pygame.sprite.Group()

class Ball(pygame.sprite.Sprite):
    """
        Class to keep track of a ball's location and vector. Female balls can turn pregnant through the "turn angry" 
        function
        """
    def __init__(self,Group,m=0):
        
        pygame.sprite.Sprite.__init__(self, Group, others)
        self.moveVector= np.array([0.0,0.0])
        self.b=max(random.randrange(1,20)+m,0.1)
        self.sex=random.randrange(0,2)
        self.age=0
        self.c=(BALL_SIZE*self.b)**2
        self.mass=self.c*BALLMASS
        self.angryFace=self.getAngry()
        self.relaxFace=self.getRelax()
        self.image=self.relaxFace
        self.rect = self.image.get_rect().clip(0,0,self.b*BALL_SIZE,self.b*BALL_SIZE)
        self.radius=self.b*BALL_SIZE/2.0
        self.timeLastHit=100
    def collisionCheck(self, ball2):
        col=pygame.sprite.collide_circle(self, ball2)
        if col:
            self.timeLastHit=min(self.timeLastHit,0)
            ball2.timeLastHit=min(ball2.timeLastHit,0)
        return col
    def move(self,x,y):
        self.rect.move_ip(x,y)
    def getCenter(self):
        center=np.array([self.rect[0]+self.b*BALL_SIZE/2.0,self.rect[1]+self.b*BALL_SIZE/2.0])
        return center
    def getRelax(self):
        path = IMAGEPATH+"Flushed_Face_Emoji.png"
        imag3 = pygame.image.load(path)
        basewidth = self.b*BALL_SIZE
        wpercent = (basewidth / float(imag3.get_rect().size[0]))
        hsize = int((float(imag3.get_rect().size[1]) * wpercent))
        imag3 =pygame.transform.smoothscale(imag3, (hsize, hsize))
        return imag3
    def getAngry(self):
        path = IMAGEPATH+"angrySmiley1.png"
        imag3 = pygame.image.load(path)
        basewidth = self.b*BALL_SIZE
        wpercent = (basewidth / float(imag3.get_rect().size[0]))
        hsize = int((float(imag3.get_rect().size[1]) * wpercent))
        imag3 =pygame.transform.smoothscale(imag3, (hsize, hsize))
        return imag3
    def turnAngry(self):
        self.image=self.angryFace
        Angry.add(self)
        self.moveVector*=0.5
    def turnRelax(self):
        self.image=self.relaxFace
        Angry.remove(self)
        self.moveVector*=2.0
        make_ball(Smiley,self)
        print("Current Population: ", len(others)+1)
#elastic collisions#
def collision(v1,v2,m1,m2,x1,x2):
    #x1 x2 are centers
    #v1, v2 are the old movevectors#
    #masspart
    m11=(2*m2/(m1+m2))
    #dotproductpart
    
    dot=np.dot(v1-v2,x1-x2)
    #normbit
    norm=np.dot(x1-x2,x1-x2)
    #pointvector
    pointV=x1-x2
    newV1=v1-m11/norm*dot*pointV
    return newV1
#to prevent balls from 'doublecolliding' with each other thus getting stuck
def overlappFix(b1,b2):
    centerb1=b1.getCenter()
    centerb2=b2.getCenter()
    c=centerb1-centerb2
    d1=np.dot(c,c)
    a= centerb1+1/10.0*b1.moveVector
    b=centerb2+1/10.0*b2.moveVector
    d2=np.dot(a-b, a-b)
    if d2<d1 or d2==d1:
        return 1
    return 0

def make_ball(Group,mom=0):
    """
        Function to make a new, random ball.
        """
    a=0
    if mom!=0:
        a=math.sqrt(mom.b)-2
    
        b=mom.getCenter()
        x=b[0]
        y=b[1]
    ball = Ball(Group,a)
    if mom==0:
    # Starting position of the ball.
    # Take into account the ball size so we don't spawn on the edge.
        x = random.randrange(int(ball.b*BALL_SIZE), int(SCREEN_WIDTH - ball.b*BALL_SIZE))
        y = random.randrange(int(ball.b*BALL_SIZE), int(SCREEN_HEIGHT - ball.b*BALL_SIZE)) 
    
    ball.rect.move_ip(x,y)
    
    # Speed and direction of rectangle
    for i in (0,1):
        ball.moveVector=setMoveVector(i,LOWSPEED,HIGHSPEED,ball.moveVector)
    return ball

def setMoveVector(index,loRange,range,vector):
    vector[index]=random.randrange(loRange,range)*0.9
    return vector

def getSign(x):
    return math.copysign(1, x)
def turn(b1,b2):
    if b2 not in Angry:
        if b2.sex==0 and b1.sex==1 and (min(b1.age,b2.age)>LIFESPAN/10.0):
            if random.randrange(0,100)<CHANCEPREGNANT:
                b2.turnAngry()

def main():
    """
        This is our main program.
        """
    pygame.init()
    # Set the height and width of the screen
    size = [SCREEN_WIDTH, SCREEN_HEIGHT]
    screen = pygame.display.set_mode(size)
    
    pygame.display.set_caption("Bouncing Balls")
    
    # Loop until the user clicks the close button.
    done = False
    
    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()
    angryBall=make_ball(Smiley)
    Angry.add(angryBall)
    angryBall.turnAngry()
#    angryBall.timeLastHit=-100
    for i in range(0,50):
        ball = make_ball(Smiley)
    
    # -------- Main Program Loop -----------
    while not done:
        # --- Event Processing
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                # Space bar! Spawn a new ball.
                if event.key == pygame.K_SPACE:
                    ball = make_ball(Smiley)
                elif event.key==pygame.K_ESCAPE:
                    pygame.display.quit()
                    pygame.quit()
                    return exit()
        # --- Logic
        for ball in Smiley:
            #remove ball from others
            others.remove(ball)
            ball.timeLastHit+=0.03
            if ball in Angry and (ball.timeLastHit>TIMEBEFORERELAX):
                ball.turnRelax()
            # Move the ball's center
            x = ball.moveVector[0]
            y = ball.moveVector[1]
            ball.move(x,y)
            
            # Bounce the ball if needed
            #y
            if ball.rect[1] > SCREEN_HEIGHT - ball.b*BALL_SIZE:
                ball.moveVector[1]= (-1)*abs(ball.moveVector[1]) 
            if ball.rect[1] < 0:
                ball.moveVector[1]= abs(ball.moveVector[1])
                #x
            if ball.rect[0] > SCREEN_WIDTH - ball.b*BALL_SIZE:
                ball.moveVector[0]= (-1)*abs(ball.moveVector[0])
            if ball.rect[0] < 0:
                ball.moveVector[0]= abs(ball.moveVector[0])
            #check for collision
            posColliders=pygame.sprite.spritecollideany(ball, others, collided = None)
            if posColliders:
                for b1 in others:
                    if ball.collisionCheck(b1) and (overlappFix(ball, b1)):
                        v1=ball.moveVector
                        v2=b1.moveVector
                        m1=ball.mass
                        m2=b1.mass
                        x1=ball.getCenter()
                        x2=b1.getCenter()
                        vect=collision(v1,v2,m1,m2,x1,x2)
                        ball.moveVector=vect
                        ball.move(vect[0],vect[1])
                        vect=collision(v2,v1,m2,m1,x2,x1)
                        b1.moveVector=vect
                        b1.move(vect[0],vect[1])
                        turn(ball,b1)
                        turn(b1,ball)
            
                        
            #add sprite bakc to others group#
            others.add(ball)
            ball.age+=1
            if ball.age>LIFESPAN and (random.randrange(0,1000)<5):
                ball.kill()
        # --- Drawing
        # Set the screen background
        screen.fill(BLACK)
        
        # Draw the balls
        for ball in Smiley:
            screen.blit(ball.image,ball.rect)
# --- Wrap-up
# Limit to 60 frames per second
        clock.tick(60)

# Go ahead and update the screen with what we've drawn.
        pygame.display.flip()
    
    
if __name__ == "__main__":
    main()


# In[7]:





# In[ ]:




