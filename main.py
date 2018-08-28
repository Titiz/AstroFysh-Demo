import numpy
import pygame
import copy
from pygame.locals import *
from PIL import Image
from random import randint
# from transforms import RGBTransform


class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """
 
    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """
 
        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load(file_name).convert()
 
 
    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """
 
        # Create a new blank image
        image = pygame.Surface([width, height]).convert()
 
        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
 
        # Assuming black works as the transparent color
        image.set_colorkey((0, 0, 0))
 
        # Return the image
        return image


def rotateImg(image, rect, angle):
    """Rotate the image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


def rotate(point, angle):
    x = point[0] * numpy.cos(angle) + point[1] * numpy.sin(angle)
    y = -point[0] * numpy.sin(angle) + point[1] * numpy.cos(angle)
    return [int(x),int(y)]

class Planet:
    def __init__(self, position, size, color):
        self.color = color
        self.size = size
        self.position = position
        self.image1 = None
        self.image2 = None
        self.cloudRot = 0
        self.cloudRotSpeed = 0
        
    

class TweenManager:
    def __init__(self):
        self.start = None
        self.destination = None
        self.planetNumber = None
        self.frames = -1
        self.top_frames = None
        
        self.vector = [0,0]
        self.angle = 0
        self.dangle = 0

    def setDestination(self, angle, planetNumber, frames = 300):
        self.planetNumber = planetNumber
        self.angle = angle
        self.frames = frames
        self.top_frames = frames



class PlanetHolder:
    def __init__(self):
        self.planets = []
    
    def add_planet(self, planet):
        self.planets.append(planet)

class PlayerHolder:
    def __init__(self):
        self.degree = numpy.pi/2
        self.planetNumber = 0
        self.state = "on_planet"
        self.pos = [0,0]
        self.width = 100
        self.height = 100
        self.direction = -1
        self.walking = False

        self.walkingAnim = SpriteSheet("walk_it_square.png")
        self.current_frame = 0
        self.current_frame_time = 0
        self.frame_duration = 5
        self.frame_count = 5
        self.frame_height = 1022
        self.frame_width = 1022

        self.stand = pygame.image.load("fushpng.png")
        self.surface = self.stand
        
        self.resizeImage()
        

    def setPlayerPlanetNumber(self, planetNumber):
        self.planetNumber = planetNumber

    def setDegree(self, degree):
        self.degree = degree

    def resizeImage(self):
        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))
       
    def rotateImage(self):
         self.surface = pygame.transform.rotate(self.surface, -self.degree*180/numpy.pi-90)

    def grabCurrentFrame(self):
        if (self.walking):
            self.surface =  self.walkingAnim.get_image(0, \
             (self.frame_count-1-self.current_frame)*self.frame_height, self.frame_width, self.frame_height)
        else:
            self.surface = self.stand.convert_alpha()
        
        print(self.current_frame)

        if (self.walking):
            self.current_frame_time += 1
            if (self.current_frame_time == self.frame_duration):
                self.current_frame += 1
                self.current_frame_time = 0
                self.current_frame %= self.frame_count

        self.resizeImage()
        if self.direction == 1:
            self.surface = \
            pygame.transform.flip(self.surface, 1, 0)
        self.rotateImage()
        
        


class WorldManipulator:
    def __init__(self):
        self.planetHolder = PlanetHolder()
        self.playerHolder = PlayerHolder()
        self.tweenManager = TweenManager()
        self.worldFile = None

        self.planetImages = []
        for i in range(1,6):
            self.planetImages.append(pygame.image.load("planet"+str(i)+".png"))
        self.cloudImages = []
        for i in range(1,6):
            self.cloudImages.append(pygame.image.load("cloud"+str(i)+".png"))
        

        #buttons:
        self.A_pressed = False
        self.D_pressed = False
    
    def setWorldFile(self, worldFile):
        self.worldFile = worldFile

    def getOnPlanetPos(self, planetNumber, degree):
        r = self.planetHolder.planets[planetNumber].size
        pos = self.planetHolder.planets[planetNumber].position
        degree = degree
        width = self.playerHolder.width
        height = self.playerHolder.height

        x = r * numpy.cos(degree) + pos[0] + width/2 * numpy.cos(degree)
        y = r * numpy.sin(degree) + pos[1] + height/2 * numpy.sin(degree)

        return x,y

    def getPlayerPos(self):
        # print(self.playerHolder.state)
        if self.playerHolder.state == "on_planet":
            x, y = self.getOnPlanetPos(self.playerHolder.planetNumber, self.playerHolder.degree)
            self.playerHolder.pos = [x,y]
        
        return self.playerHolder.pos

    def drawPlayer(self, screen):
        self.playerHolder.grabCurrentFrame()
        x, y = self.getPlayerPos()
        rect = self.playerHolder.surface.get_rect()
        rect.center = (x,y)
        screen.blit(self.playerHolder.surface, ((rect.x, rect.y)))


    def intersectPlanets(self):
        minimum = [None, None]
        planets = copy.deepcopy(self.planetHolder.planets)
        index = self.playerHolder.planetNumber
        angle = self.playerHolder.degree
        print("angle", angle)
        shift = (planets[index].position[0], planets[index].position[1])
        for i in range(len(planets)):

            planets[i].position[0] -= shift[0]
            planets[i].position[1] -= shift[1]
            planets[i].position = rotate(planets[i].position, angle)

            if(index == i):
                continue

            a, b = planets[i].position
            r = planets[i].size

            print(a,b,r)


            if(r*r-b*b < 0):
                continue
            
            x = 0
            xs = [a -numpy.sqrt(r*r-b*b), a +numpy.sqrt(r*r-b*b) ]
            print("xs:",xs)
            x = min(xs[0], xs[1])
            print("x:", x)
                
            if (x > 0):
                if (minimum[0] == None or x < minimum[1]):
                    minimum[0] = i
                    minimum[1] = x
        print(minimum)
        # self.planetHolder.planets = planets


        if (minimum[0] != None):
            intersectionPoint = rotate([minimum[1], 0], -angle)
            intersectionPoint[0] += shift[0]
            intersectionPoint[1] += shift[1]
            print("intersection Point:",intersectionPoint)
            # self.planetHolder.add_planet(Planet([intersectionPoint[0], intersectionPoint[1]], 5, (255,0,0)))

            vectorx =  intersectionPoint[0] - self.planetHolder.planets[minimum[0]].position[0]
            vectory =  intersectionPoint[1] - self.planetHolder.planets[minimum[0]].position[1]
            planet = planets[minimum[0]]
            theta = numpy.arctan2(vectory, vectorx)
            
            
            # print(theta)
            self.tweenManager.setDestination(theta, minimum[0])
            
    
    def updatePlayerStates(self):
        if (self.A_pressed or self.D_pressed):
            self.playerHolder.walking = True
        else:
            self.playerHolder.walking = False
        if (self.playerHolder.state != "on_planet"):
            self.playerHolder.walking = False
        

    def rotatePlayer(self, direction = 1, speed = 0.01):
        self.playerHolder.surface = self.playerHolder.stand
        self.playerHolder.surface = \
        pygame.transform.scale(self.playerHolder.surface, (self.playerHolder.width, self.playerHolder.height))
        self.playerHolder.degree += speed * direction
        newSurface = pygame.transform.rotate(self.playerHolder.surface, -self.playerHolder.degree/numpy.pi*180-90)
        self.playerHolder.surface = newSurface

    def rotateCloud(self, planetNumber):
        img2 = self.planetHolder.planets[planetNumber].image2
        surface = pygame.transform.rotate(img2, self.planetHolder.planets[planetNumber].cloudRot)
        self.planetHolder.planets[planetNumber].cloudRot += self.planetHolder.planets[planetNumber].cloudRotSpeed
        return surface



    def rotatePlayerConditional(self):
        if (self.playerHolder.state == "on_planet"):
            # self.walking = False    
            if (self.A_pressed):
                self.playerHolder.direction = -1
                self.rotatePlayer(-1)
            if (self.D_pressed):
                self.playerHolder.direction = 1
                self.rotatePlayer(1)

    def drawPlanets(self, screen):
        for i in range(len(self.planetHolder.planets)):
            planet = self.planetHolder.planets[i]
            rect = planet.image1.get_rect()
            rect.center = (planet.position[0], planet.position[1])
            
            image1 = planet.image1
            # image2 = self.rotateCloud(i)
            image2, newCenter = rotateImg(planet.image2, rect, planet.cloudRot)
            self.planetHolder.planets[i].cloudRot += self.planetHolder.planets[i].cloudRotSpeed

            screen.blit(image1, (planet.position[0]-planet.size, planet.position[1]-planet.size))
            screen.blit(image2, newCenter)

    def paintGrayScale(self, img):
        width, height = img.size
        px = img.load()
        for k in range(width):
            for j in range(height):
                # if px[k,j] == (255,255,255):
                    # continue
                x = (px[k,j][0] * 0.299) + (px[k,j][1] * 0.587) + (px[k,j][2] * 0.114)
                px[k,j] = (int(x), int(x), int(x))

        return img
    
    def randomizePlanets(self):
        for i in range(len(self.planetHolder.planets)):

            img1 = self.planetImages[randint(0,4)]
            img2 = self.cloudImages[randint(0,4)]


            img2.set_alpha(randint(0, 100))

            img1 = pygame.transform.flip(img1, randint(0, 1), randint(0, 1))
            img1 = \
            pygame.transform.scale(img1, (self.planetHolder.planets[i].size*2, self.planetHolder.planets[i].size*2))
            img2 = \
            pygame.transform.scale(img2, (self.planetHolder.planets[i].size*2, self.planetHolder.planets[i].size*2))
            
            self.planetHolder.planets[i].image1 = img1.convert_alpha()
            self.planetHolder.planets[i].image2 = img2.convert_alpha()

            self.planetHolder.planets[i].cloudRot = randint(0, 360)
            self.planetHolder.planets[i].cloudRotSpeed = randint(50,100)/1000


    def createWorld(self):
        with open(self.worldFile, 'r') as f:
            for line in f:
                if line[0:7] == "planet:":
                    line = line[7:].split(",")
                    pos = [int(line[0]), int(line[1])]
                    r = int(line[2])
                    color = [int(line[3]), int(line[4]), int(line[5])]
                    print(pos, r, color)
                    planet = Planet(pos, r, color)
                    self.planetHolder.add_planet(planet)
                if line[0:7] == "player:":
                    self.playerHolder.planetNumber = int(line[7:])
        
        self.randomizePlanets()

    def tweenPlayer(self):
        if self.tweenManager.top_frames == self.tweenManager.frames:
            self.tweenManager.vector[0] = (-self.playerHolder.pos[0] + self.getOnPlanetPos(self.tweenManager.planetNumber, self.tweenManager.angle)[0])/self.tweenManager.top_frames
            self.tweenManager.vector[1] = (-self.playerHolder.pos[1] + self.getOnPlanetPos(self.tweenManager.planetNumber, self.tweenManager.angle)[1])/self.tweenManager.top_frames
            angle = self.tweenManager.angle
            delta_angle = angle - self.playerHolder.degree
            # if numpy.sign(self.planetHolder.direction) != numpy.sign(delta_angle):
            if (self.playerHolder.direction == -1):
                delta_angle = 2*numpy.pi - delta_angle
            # delta_angle = angle - self.playerHolder.degree
            self.tweenManager.dangle = (delta_angle)/self.tweenManager.top_frames
            print(self.tweenManager.angle, self.playerHolder.degree)
            print("dangle:", self.tweenManager.dangle)
            print("direction", self.playerHolder.direction)
        if self.tweenManager.frames > 0:
            planet = self.planetHolder.planets[self.tweenManager.planetNumber]
            deltax = self.tweenManager.vector[0]
            deltay = self.tweenManager.vector[1]
            self.tweenManager.frames -= 1
            # print(deltax, deltay)
            self.playerHolder.pos[0] += deltax
            self.playerHolder.pos[1] += deltay
            

            self.rotatePlayer(self.playerHolder.direction, self.tweenManager.dangle)

            self.playerHolder.state = "flying"
        
        elif self.tweenManager.frames == 0:
            self.playerHolder.planetNumber = self.tweenManager.planetNumber
            self.playerHolder.degree = self.tweenManager.angle
            self.playerHolder.state = "on_planet"
            self.tweenManager.frames = -1

            # Just to renew the rotation right after landing
            self.rotatePlayer(self.playerHolder.direction)
                
        




class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 1280, 1080
 
    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE)
        self.worldManipulator = WorldManipulator()
        self.worldManipulator.setWorldFile("world1")
        self.worldManipulator.createWorld()
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                self.worldManipulator.A_pressed = False
            if event.key == pygame.K_d:
                self.worldManipulator.D_pressed = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                self.worldManipulator.A_pressed = True
                # self.worldManipulator.playerHolder.walking = True
            if event.key == pygame.K_d:
                self.worldManipulator.D_pressed = True
                # self.worldManipulator.playerHolder.walking = True
            if event.key == pygame.K_w:
                self.worldManipulator.intersectPlanets()


    def on_loop(self):
        self.worldManipulator.updatePlayerStates()
        self.worldManipulator.rotatePlayerConditional()
        self.worldManipulator.tweenPlayer()
    def on_render(self):
        self._display_surf.fill((0,0,0))
        # for planet in self.worldManipulator.planetHolder.planets:
        #     pygame.draw.circle(self._display_surf, planet.color, planet.position, planet.size)
        self.worldManipulator.drawPlanets(self._display_surf)
        self.worldManipulator.drawPlayer(self._display_surf)
        pygame.display.update()
    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()