import pygame

from pygame import *

def AAfilledRoundedRect(surface,rect,color,radius=0.4):

    """
    AAfilledRoundedRect(surface,rect,color,radius=0.4)

    surface : destination
    rect    : rectangle
    color   : rgb or rgba
    radius  : 0 <= radius <= 1
    """

    rect         = Rect(rect)
    color        = Color(*color)
    alpha        = color.a
    color.a      = 0
    pos          = rect.topleft
    rect.topleft = 0,0
    rectangle    = Surface(rect.size,SRCALPHA)

    circle       = Surface([min(rect.size)*3]*2,SRCALPHA)
    draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
    circle       = transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

    radius              = rectangle.blit(circle,(0,0))
    radius.bottomright  = rect.bottomright
    rectangle.blit(circle,radius)
    radius.topright     = rect.topright
    rectangle.blit(circle,radius)
    radius.bottomleft   = rect.bottomleft
    rectangle.blit(circle,radius)

    rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
    rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

    rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
    rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

    return surface.blit(rectangle,pos)

class SudokuSquare:
    """A sudoku square class."""
    def __init__(self, number=None, offsetX=0, offsetY=0, edit="Y", xLoc=0, yLoc=0):
        if number != None:
            number = str(number)
            self.color = (2, 204, 186)
        else:
            number = ""
            self.color = (255, 255, 255)
        # print("FONTS", pygame.font.get_fonts())
        self.font = pygame.font.SysFont('opensans', 21)
        self.text = self.font.render(number, 1, (255, 255, 255))
        self.textpos = self.text.get_rect()
        self.textpos = self.textpos.move(offsetX + 17, offsetY + 4)

        # self.collide = pygame.Surface((25, 22))
        # self.collide = self.collide.convert()
        # AAfilledRoundedRect(pygame.display.get_surface(), (xLoc, yLoc, 25, 22), (255, 255, 255))
        # self.collide.fill((2, 204, 186))
        # self.collideRect = self.collide.get_rect()
        # self.collideRect = self.collideRect.move(offsetX + 1, offsetY + 1)
        # The rect around the text is 11 x 28

        self.edit = edit
        self.xLoc = xLoc
        self.yLoc = yLoc
        self.offsetX = offsetX
        self.offsetY = offsetY

    def draw(self):
        screen = pygame.display.get_surface()
        AAfilledRoundedRect(screen, (self.offsetX, self.offsetY, 45, 40), self.color)

        # screen.blit(self.collide, self.collideRect)
        screen.blit(self.text, self.textpos)


    def checkCollide(self, collision):
        if len(collision) == 2:
            return self.collideRect.collidepoint(collision)
        elif len(collision) == 4:
            return self.collideRect.colliderect(collision)
        else:
            return False


    def highlight(self):
        self.collide.fill((190, 190, 255))
        self.draw()


    def unhighlight(self):
        self.collide.fill((255, 255, 255, 255))
        self.draw()


    def change(self, number):
        if number != None:
            number = str(number)
        else:
            number = ""
        
        if self.edit == "Y":
            self.text = self.font.render(number, 1, (0, 0, 0))
            self.draw()
            return 0
        else:
            return 1


    def currentLoc(self):
        return self.xLoc, self.yLoc