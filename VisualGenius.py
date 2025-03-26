from gaze_tracking import GazeTracking
import pygame
import cv2
import tkinter
from PIL import ImageColor
import numpy as np
import time
from FPGAController import FPGAController

class ScreenInfo:
    def __init__(self):
        session = tkinter.Tk()
        self.resolution:tuple[int, int] = (session.winfo_screenwidth(), session.winfo_screenheight())

class Target:
    def __init__(self, x:int, y:int, radius:int = 5):
        self.x = x
        self.y = y
        self.radius = radius

    def draw(self, screen):
        pygame.draw.circle(screen, ImageColor.getrgb('crimson') , (self.x, self.y), self.radius)

class TEAGame:
    def __init__(self, screenInfo:ScreenInfo, cameraId:int = 0):
        pygame.init()
        pygame.display.set_caption("Visual Genius")

        self.screenSession = pygame.display.set_mode(screenInfo.resolution)
        self.font1 = pygame.font.SysFont('Comic Sans MS', 30)
        self.font2 = pygame.font.SysFont('Comic Sans MS', 40)
        self.screenInfo = screenInfo
        self.gaze = GazeTracking()
        self.camera = cv2.VideoCapture(cameraId)
        self.fPS = self.camera.get(cv2.CAP_PROP_FPS)
        self.calibrationData:list[tuple[float]] = []
        self.centerCoord = tuple(a//2 for a in self.screenInfo.resolution)
        self.thresholds = self.thresholds = {
            'Line1': 0.67,
            'Line2': 0.57,
            'Line3': 0.47
            }

    def generateTargets(self, rows:int=3, cols:int=5, radius:int = 5):
        
        maxRes = self.screenInfo.resolution
        deltaX = maxRes[0] // rows
        deltaY = maxRes[1] // cols

        targets = []
        for j in range (cols - 1):
            for i in range (rows - 1):
                targets.append(Target(deltaX * (j+1), deltaY * (i + 1)))
        return targets

    def calibrateRound(self):
        ROWS, COLS = 5, 4
        RADIUS = 20
        state = "INIT"
        running = True
        '''
        15 targets and the gaze horizontal and vertical ratios

        x x x x x
        x x x x x
        x x x x x
        
        TODO: I have to find the best operator to transform the ratios in the commands 
        '''        

        # The state machine follows us in the hardest moments 
        while running:
            self.screenSession.fill(ImageColor.getrgb('lightgrey'))
            _, frame = self.camera.read()
            # Process the gaze tracker
            self.gaze.refresh(frame)
            match state:
                case "INIT":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            state = "TARGETS"
                            targets = self.generateTargets(rows=ROWS, cols=COLS, radius=RADIUS)
                            targetVis = np.zeros(len(targets))
                            targetId = 0
                            targetVis[targetId] = True
                            break

                    frame = self.gaze.annotated_frame()
                    #Pygame exhibits in RGB and openCV in BGR
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = np.rot90(frame) 

                    frameSurface = pygame.surfarray.make_surface(frame)
                    # Centralize the camera surface
                    frameCenter = frameSurface.get_rect()
                    frameCenter.center = self.centerCoord
                    # Exhibits the frame as a Surface
                    self.screenSession.blit(frameSurface, frameCenter)
                    
                    textSurface = self.font2.render('Pressione Espaço para iniciar a Calibração', False, ImageColor.getrgb('crimson'))
                    textCenter = textSurface.get_rect()
                    textCenter.center = self.centerCoord
                    self.screenSession.blit(textSurface, textCenter)

                    pygame.display.flip()

                case "TARGETS": 
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            self.calibrationData.append(self.gaze.horizontal_ratio())

                            if targetId < len(targets) - 1:
                                targetId = targetId + 1
                                targetVis[targetId] = True

                            else:
                                state = "END"
                                try:
                                    self.genThresholds(ROWS)
                                except: 
                                    state = "ERROR"
                                

                    if targetVis[targetId] and targetId < len(targets):
                        time.sleep(.1)
                        targets[targetId].draw(self.screenSession)
                    
                    pygame.display.flip()

                case "ERROR":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            state = "INIT"
                            
                    textSurface = self.font2.render('Erro na Calibração! Pressione Espaço para Recomeçar', False, ImageColor.getrgb('crimson'))
                    textCenter = textSurface.get_rect()
                    textCenter.center = self.centerCoord
                    self.screenSession.blit(textSurface, textCenter)
                    pygame.display.flip()
                    
                case "END":
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            running = False

                    textSurface = self.font2.render('Calibração finalizada! Pressione Espaço para iniciar o Jogo', False, ImageColor.getrgb('crimson'))
                    textCenter = textSurface.get_rect()
                    textCenter.center = self.centerCoord
                    self.screenSession.blit(textSurface, textCenter)
                    pygame.display.flip()
    
    def playRound(self):

        WIDTH, HEIGHT = self.screenInfo.resolution[0], self.screenInfo.resolution[1]
        ALPHA_START = 0  # Initial transparency (0 = fully transparent, 255 = fully opaque)
        ALPHA_INCREMENT = 20  # Speed of transparency decrease

        quadrants = {
            "blue": pygame.Surface((WIDTH // 4, HEIGHT), pygame.SRCALPHA),
            "green": pygame.Surface((WIDTH // 4, HEIGHT), pygame.SRCALPHA),
            "red": pygame.Surface((WIDTH // 4, HEIGHT), pygame.SRCALPHA),
            "yellow": pygame.Surface((WIDTH // 4, HEIGHT), pygame.SRCALPHA),
        }

        # Set initial transparency
        alpha = np.full(4, ALPHA_START)

        decreaseAlpha = np.zeros(4, dtype=np.bool_)  # Control transparency change

        state = 'TEST'

        posEdgeIsShowing = False

        eventKSpace = False
        # Main loop
        running = True
        fpgaController = FPGAController()
        while running:
            self.screenSession.fill(ImageColor.getrgb('lightgrey'))
            _, frame = self.camera.read()
            
            # Process the gaze tracker
            self.gaze.refresh(frame)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    eventKSpace = True

            quadrant = self.getQuadrant()
            decreaseAlpha[:] = False
            if quadrant > -1:
                decreaseAlpha[quadrant] = True

            match state:
                case 'TEST':

                    alpha[decreaseAlpha] = np.minimum(255, alpha[decreaseAlpha] + ALPHA_INCREMENT)
                    alpha[~decreaseAlpha] = np.maximum(0, alpha[~decreaseAlpha] - ALPHA_INCREMENT)
                    if eventKSpace: state = 'START'
                
                case 'START':
                    alpha = np.full(4, ALPHA_START)
                    fpgaController.triggerReset() 
                    fpgaController.triggerStart()
                    state = 'SHOW'
                
                case 'SHOW':
                    isDisplayActive = fpgaController.isDisplayActive()

                    if not posEdgeIsShowing:
                        posEdgeIsShowing = isDisplayActive                            
                    
                    if posEdgeIsShowing:
                        alphaIncrement = np.array(fpgaController.readLedSignal())
                        
                        alpha[:] = 0
                        alpha[alphaIncrement == 1] = 255
                        
                        if not isDisplayActive:
                            state = 'PLAY'
                            posEdgeIsShowing = False
                            alpha = np.full(4, ALPHA_START)
                    
                    if fpgaController.checkLoseCondition(): state = 'ERROR'

                case 'PLAY':
                    isDisplayActive = fpgaController.isDisplayActive()
                    isError = fpgaController.checkLoseCondition()
                    isWin = fpgaController.checkWinCondition()

                    if isDisplayActive: state = 'SHOW'
                    elif isError: state = 'ERROR'
                    elif isWin: state = 'WIN'
                    else: 
                        alpha[decreaseAlpha] = np.minimum(255, alpha[decreaseAlpha] + ALPHA_INCREMENT)
                        alpha[~decreaseAlpha] = np.maximum(0, alpha[~decreaseAlpha] - ALPHA_INCREMENT)
                       
                        if max(alpha) >= 255:
                            fpgaController.writeLedSignal(np.argmax(alpha))
                            alpha = np.full(4, ALPHA_START)
                            

                case 'ERROR':
                    alpha = np.full(4, ALPHA_START)
                    if eventKSpace == True:
                        state = 'TEST'
                case 'WIN':
                    alpha = np.full(4, ALPHA_START)
                    if eventKSpace == True:
                        state = 'TEST'
            # Update quadrants with current alpha
            quadrants["blue"].fill((*ImageColor.getrgb('blue'), alpha[0]))
            quadrants["green"].fill((*ImageColor.getrgb('green'), alpha[1]))
            quadrants["red"].fill((*ImageColor.getrgb('red'), alpha[2]))
            quadrants["yellow"].fill((*ImageColor.getrgb('yellow'), alpha[3]))

            # Draw quadrants
            self.screenSession.blit(quadrants["blue"], (0, 0))
            self.screenSession.blit(quadrants["green"], (WIDTH // 4, 0))
            self.screenSession.blit(quadrants["red"], (WIDTH //2, 0))
            self.screenSession.blit(quadrants["yellow"], (3*WIDTH//4,0))

            # Draw black cross in the center
            pygame.draw.rect(self.screenSession, ImageColor.getrgb('black'), (WIDTH // 4 - 5, 0, 10, HEIGHT))  # Vertical line
            pygame.draw.rect(self.screenSession, ImageColor.getrgb('black'), (WIDTH // 2 - 5, 0, 10, HEIGHT))  # Vertical line
            pygame.draw.rect(self.screenSession, ImageColor.getrgb('black'), (3 * WIDTH // 4 - 5, 0, 10, HEIGHT))  # Vertical line

            textSurface = self.font2.render(state, False, ImageColor.getrgb('crimson'))
            textCenter = textSurface.get_rect()
            textCenter.center = self.centerCoord
            self.screenSession.blit(textSurface, textCenter)

            pygame.display.flip()
            pygame.time.delay(50)
            eventKSpace = False


    def genThresholds(self, rows):
        data = np.array(self.calibrationData)
        rowData = [data[i:i + rows - 1] for i in range(0, len(data), rows - 1)]
        statistics = [np.mean(row, axis=0) for row in rowData]


        self.thresholds = {
            'Line1': statistics[0],
            'Line2': statistics[1],
            'Line3': statistics[2]
            }
        
    def getQuadrant(self):

        ratios = self.gaze.horizontal_ratio()
        thresholds = self.thresholds

        if not ratios:
            return -1
        if ratios > thresholds['Line1']:
            return 0  # First Quadrant (Up & Left)
        elif ratios > thresholds['Line2']:
            return 1  # Second Quadrant (Up & Right)
        elif ratios > thresholds['Line3']:
            return 2  # Third Quadrant (Down & Left)
        else:
            return 3  # Center (No quadrant detected)

game = TEAGame(screenInfo=ScreenInfo(), cameraId=1)
game.calibrateRound()
game.playRound()