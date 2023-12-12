#! /usr/bin/env python3

"""Flappy Lizard"""

import math
import os
import time
from random import randint
from collections import deque

import pygame
from pygame.locals import *


FPS = 60
ANIMATION_SPEED = 0.18  # pixels per millisecond
WINDOW_WIDTH = 284 * 2     #image size for the games terminal window: 284x512
WINDOW_HEIGHT = 512


class Lizard(pygame.sprite.Sprite):
    """ This class represents the player-controlled lizard in the game.
The lizard serves as the player and responds to player input. 
It can ascend when prompted (space bar up arrow), or descend due to gravity when not climbing. 
The main objective is to navigate the lizard through the openings between Cactus, earning one point for each successful passage. 
Colliding with a cactus results in the end of the game.

Attributes:
- x: The X coordinate of the lizard.
- y: The Y coordinate of the lizard.
- MAX_REMAINING_FLY_TIME: The remaining milliseconds for the lizard to complete its climb. 
A full climb takes lizard.FLY_TIME milliseconds.

Constants:
- WIDTH: The width, in pixels, of the lizard's image.
- HEIGHT: The height, in pixels, of the lizard's image.
- GRAVITY_SPEED: The speed, in pixels per millisecond, at which the lizard descends when not climbing.
- FLYING_SPEED: The speed, in pixels per millisecond, at which the lizard ascends while climbing, on average. Refer to the lizard.update docstring for more details.
- FLY_TIME: The number of milliseconds required for the lizard to execute a complete fly.
"""

    WIDTH = HEIGHT = 32
    GRAVITY_SPEED = 0.12
    FLYING_SPEED = 0.4
    FLY_TIME = 111.3

    def __init__(self, x, y, MAX_REMAINING_FLY_TIME, images):
        """ Parameters:
          - x: Initial X coordinate of the lizard.
          - y: Initial Y coordinate of the lizard.
          - MAX_REMAINING_FLY_TIME: The max amount of milliseconds for the lizard to climb from its location. 
          - A complete climb takes the time that lizard.FLY_TIME milliseconds is set too. 
          
        """

        super(Lizard, self).__init__()
        self.x, self.y = x, y
        self.MAX_REMAINING_FLY_TIME = MAX_REMAINING_FLY_TIME
        self._img_FacingUp, self._img_FacingDown = images
        self._mask_FacingUp = pygame.mask.from_surface(self._img_FacingUp)
        self._mask_FacingDown = pygame.mask.from_surface(self._img_FacingDown)

    def update(self, Frame_Counter=1):
        """This function employs the function to ensure a gradual ascent:
        The lizard makes minimal upward movement in the initial and final frames,
        while experiencing significant ascent in the middle frames.
        A complete ascent cycle takes FLY_TIME milliseconds, with the lizard
        ascending at an average speed of FLYING_SPEED px/ms.
        If the lizard's MAX_REMAINING_FLY_TIME attribute was > 0 when this method
        is called, it will be automatically decremented accordingly.

        Parameters:
        Frame_Counter: The number of frames that have passed since the last call
         of this method starts @ 1.
        """

        if self.MAX_REMAINING_FLY_TIME > 0:
            Lizzard_Climb_Finished = 1 - self.MAX_REMAINING_FLY_TIME/Lizard.FLY_TIME
            self.y -= (Lizard.FLYING_SPEED * frames_to_msec(Frame_Counter) *
                       (1 - math.cos(Lizzard_Climb_Finished * math.pi)))
            self.MAX_REMAINING_FLY_TIME -= frames_to_msec(Frame_Counter)
        else:
            self.y += Lizard.GRAVITY_SPEED * frames_to_msec(Frame_Counter)

    @property
    def image(self):
        """

        This will decide whether to return an image where the lizard
         is pointing upward or where it is pointing downward
        based on pygame.time.get_ticks().  This will animate the
        lizard going up & Down, Since pygame doesn't support animated GIFs.
        """
        if pygame.time.get_ticks() % 500 >= 250:
            return self._img_FacingUp
        else:
            return self._img_FacingDown

    @property
    def mask(self):
        """Generate a collision detection bitMask by excluding pixels in self.image 
        with any transparency levels exceeding 127"""
        if pygame.time.get_ticks() % 500 >= 250:
            return self._mask_FacingUp
        else:
            return self._mask_FacingDown

    @property
    def rect(self):
        """Retrieve the lizard's coordinates, width, and height information in the form of a pygame.Rect."""
        return Rect(self.x, self.y, Lizard.WIDTH, Lizard.HEIGHT)


class Cactus_Pair(pygame.sprite.Sprite):
    """Defines a Cactus Pair object representing obstacles in the game.

    A Cactus Pair consists of a top and bottom cactus, creating a passage
    for the lizard to navigate through. Colliding with either part of
    the Cactus Pair results in the end of the game.

    Attributes:
    x: Float representing the X position of the Cactus Pair for smooth
        movement. There is no y attribute, as it is always set to 0.
    image: Pygame.Surface that can have the pixels rendered to the display surface to
        visually represent the Cactus Pair.
    Mask: BitMask excluding pixels in self.image with transparency
        greater than 127, useful for collision detection.
    Top_Cactus_Pair_Pieces: Number of pieces, including the end piece, in the top cactus.
    Bottom_Cactus_Pair_Pieces: Number of pieces, including the end piece, in the
        bottom cactus.

    Constants:
    WIDTH: Width of a cactus piece and the Cactus Pair's image in pixels.
    PIECE_HEIGHT: Height of a cactus piece in pixels.
    ADD_INTERVAL: time in milliseconds between adding new cactus peices.
    """

    WIDTH = 80
    PIECE_HEIGHT = 32
    ADD_INTERVAL = 3000

    def __init__(self, Cactus_Tip_img, Cactus_body_img):
        """Initialises a new random Cactus_Pair.

        The new Cactus_Pair will automatically be assigned an x attribute of
        float(WINDOW_WIDTH - 1).

        Arguments:
        Cactus_Tip_img: The image to use to represent a cactus end piece.
        Cactus_body_img: The image to use to represent one horizontal slice
            of a cactus body.
        """
        self.x = float(WINDOW_WIDTH - 1)
        self.Recorded_Score = False

        self.image = pygame.Surface((Cactus_Pair.WIDTH, WINDOW_HEIGHT), SRCALPHA)
        self.image.convert()   # speeds up blitting
        self.image.fill((0, 0, 0, 0))
        total_Cactus_body_pieces = int(
            (WINDOW_HEIGHT -                  # fill window from top to bottom
             3 * Lizard.HEIGHT -             # make room for lizard to fit through
             3 * Cactus_Pair.PIECE_HEIGHT) /  # 2 end pieces + 1 body piece
            Cactus_Pair.PIECE_HEIGHT          # to get number of cactus pieces
        )
        self.Bottom_Cactus_Pair_Pieces = randint(1, total_Cactus_body_pieces)
        self.Top_Cactus_Pair_Pieces = total_Cactus_body_pieces - self.Bottom_Cactus_Pair_Pieces

        # bottom cactus
        for i in range(1, self.Bottom_Cactus_Pair_Pieces + 1):
            piece_pos = (0, WINDOW_HEIGHT - i*Cactus_Pair.PIECE_HEIGHT)
            self.image.blit(Cactus_body_img, piece_pos)
        bottom_Cactus_Tip_y = WINDOW_HEIGHT - self.bottom_height_px
        bottom_end_piece_pos = (0, bottom_Cactus_Tip_y - Cactus_Pair.PIECE_HEIGHT)
        self.image.blit(Cactus_Tip_img, bottom_end_piece_pos)

        # top cactus
        for i in range(self.Top_Cactus_Pair_Pieces):
            self.image.blit(Cactus_body_img, (0, i * Cactus_Pair.PIECE_HEIGHT))
        top_Cactus_Tip_y = self.top_height_px
        self.image.blit(Cactus_Tip_img, (0, top_Cactus_Tip_y))

        # compensate for added end cactus tip
        self.Top_Cactus_Pair_Pieces += 1
        self.Bottom_Cactus_Pair_Pieces += 1

        # for detection of collision of lizard
        self.mask = pygame.mask.from_surface(self.image)

    @property
    def top_height_px(self):
        """Get the top cactus's height, in pixels."""
        return self.Top_Cactus_Pair_Pieces * Cactus_Pair.PIECE_HEIGHT

    @property
    def bottom_height_px(self):
        """Get the bottom cactus's height, in pixels."""
        return self.Bottom_Cactus_Pair_Pieces * Cactus_Pair.PIECE_HEIGHT

    @property
    def visible(self):
        """Get whether this Cactus_Pair on screen, visible to the player."""
        return -Cactus_Pair.WIDTH < self.x < WINDOW_WIDTH

    @property
    def rect(self):
        """Get the Rect which contains this Cactus_Pair."""
        return Rect(self.x, 0, Cactus_Pair.WIDTH, Cactus_Pair.PIECE_HEIGHT)

    def update(self, Frame_Counter=1):
        """Update the Cactus_Pair's position.

        Arguments:
        Frame_Counter: The number of frames elapsed since this method was
            last called.
        """
        self.x -= ANIMATION_SPEED * frames_to_msec(Frame_Counter)

    def collides_with(self, lizard):
        """Get whether the lizard collides with a cactus in this Cactus_Pair.

        Arguments:
        lizard: The lizard which should be tested for collision with this
            Cactus_Pair.
        """
        return pygame.sprite.collide_mask(self, lizard)


def load_images():
    """Load all images required by the game.

    The returned has the following keys:
    background: The game's background image.
    lizard-FacingUp: An image of the lizard with its wing pointing upward.
        Use this and lizard-FacingDown to create a flapping lizard.
    lizard-FacingDown: An image of the lizard with its wing pointing downward.
        Use this and lizard-FacingUp to create a flapping lizard.
    Cactus-Tip: An image of a cactus end piece.
        Use this and cactus-body to make cactus peices.
    Cactus-body: An image of a slice of a cactus body.  Use this and
        cactus-body to make Cactus.
    """

    def load_image(img_file_name):
        """Return the loaded pygame image with the specified file name.

        This function looks for images in the game's images folder
        (dirname(__file__)/images/). All images are converted before being
        returned to speed up blitting.

        Arguments:
        img_file_name: The file name (including its extension, e.g.
            '.png') of the required image, without a file path.
        """
    
        file_name = os.path.join(os.path.dirname(__file__),
                                 'images', img_file_name)
        img = pygame.image.load(file_name)
        img.convert()
        return img

    return {'background': load_image('background.png'),
            'Cactus-Tip': load_image('Cactus_Tip.png'),
            'Cactus-body': load_image('Cactus_body.png'),
            'lizard-FacingUp': load_image('lizard_Facing_Up.png'),
            'lizard-FacingDown': load_image('lizard_Facing_Down.png')}


def frames_to_msec(frames, fps=FPS):
    """Convert frames to milliseconds at the specified framerate.

    Arguments:
    frames: How many frames to convert to milliseconds.
    fps: The framerate to use for conversion.  Default: FPS.
    """
    return 1000.0 * frames / fps


def msec_to_frames(milliseconds, fps=FPS):
    """Convert milliseconds to frames at the specified framerate.

    Arguments:
    milliseconds: How many milliseconds to convert to frames.
    fps: The framerate to use for conversion.  Default: FPS.
    """
    return fps * milliseconds / 1000.0

pygame.init()

font = pygame.font.SysFont("arialblack", 20)
TEXT_COL = (255, 255, 255)

display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flappy Lizard')

clock = pygame.time.Clock()
score_font = pygame.font.SysFont(None, 32, bold=True)  # default font
images = load_images()

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    display_surface.blit(img,(x, y))
    
    
"""
This is the start menu loop where the player starts out
it shows a little start prompt and message for the player
to get started
"""

def startMenuLoop():
    run = True
    while run:
        display_surface.fill((52, 78, 91))
        draw_text("Press SPACE to jump", font, TEXT_COL, 50, 200)
        
        #Detects button press that finishes this function and since
        #it is run in main, it goes right into the main game loop
        #and runs the game
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    run = False
        if event.type == pygame.QUIT:
            run = False
            pygame.display.quit()
        pygame.display.update()

def gameLoop():
    """The application's entry point.

    If someone executes this module (instead of importing it, for
    example), this function is called.
    """
    
    """
    Updated gameplay loop to be within this function as opposed to main
    """
    
    # the lizard stays in the same x position, so lizard.x is a constant
    # center lizard on screen
    lizard = Lizard(50, int(WINDOW_HEIGHT/2 - Lizard.HEIGHT/2), 2,
                (images['lizard-FacingUp'], images['lizard-FacingDown']))

    Cactus = deque()

    Counter_For_Frames = 0  # this counter is only incremented if the game isn't paused
    score = 0
    done = paused = False
    while not done:
        clock.tick(FPS)
        
        # Did this manualy because.  If we used pygame.time.set_timer(),
        # The cactuses being added would be messed up if a player pauses game(using p).
        if not (paused or Counter_For_Frames % msec_to_frames(Cactus_Pair.ADD_INTERVAL)):
            pp = Cactus_Pair(images['Cactus-Tip'], images['Cactus-body'])
            Cactus.append(pp)

        for e in pygame.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                done = True
                break
            elif e.type == KEYUP and e.key in (K_PAUSE, K_p):
                paused = not paused
            elif e.type == MOUSEBUTTONUP or (e.type == KEYUP and
                    e.key in (K_UP, K_RETURN, K_SPACE)):
                lizard.MAX_REMAINING_FLY_TIME = Lizard.FLY_TIME

        if paused:
            continue  

        # checks for collisions
        Cactus_Collision = any(p.collides_with(lizard) for p in Cactus)
        if Cactus_Collision or 0 >= lizard.y or lizard.y >= WINDOW_HEIGHT - Lizard.HEIGHT:
            done = True

        for x in (0, WINDOW_WIDTH / 2):
            display_surface.blit(images['background'], (x, 0))

        while Cactus and not Cactus[0].visible:
            Cactus.popleft()

        for p in Cactus:
            p.update()
            display_surface.blit(p.image, p.rect)

        lizard.update()
        display_surface.blit(lizard.image, lizard.rect)

        # update and display score
        for p in Cactus:
            if p.x + Cactus_Pair.WIDTH < lizard.x and not p.Recorded_Score:
                score += 1
                p.Recorded_Score = True

        score_surface = score_font.render(str(score), True, (255, 255, 255))
        score_x = WINDOW_WIDTH/2 - score_surface.get_width()/2
        display_surface.blit(score_surface, (score_x, Cactus_Pair.PIECE_HEIGHT))

        pygame.display.flip()
        Counter_For_Frames += 1
        
    #Runs the end menu loop with the score variable so that it can be displayed to the user
    endMenuLoop(score)
    print('You Lost, Game over! Your Score Was: %i' % score)
    print('   Thanks For Playing! :) -From Tiger Team (Johnathan S, Dylan, John M, Mincie)')
    
"""
This is the end menu loop that is run at the end of the main gameplay loop.
This function prompts the user if they want to play again or if they
want to quit the game.
It also displays the user's score from their previous play
"""
def endMenuLoop(score):
    run = True
    while run:
        display_surface.fill((52, 78, 91))
        draw_text("GAME OVER! Your Score Was: %i" %score, font, TEXT_COL, 50, 200)
        draw_text("Press Space to Play again", font, TEXT_COL, 50, 300)
        draw_text("Press ESC to Quit", font, TEXT_COL, 50, 400)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    gameLoop()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    pygame.display.quit()
        pygame.display.update()

def main():
    startMenuLoop()
    gameLoop()
    pygame.quit()

main()