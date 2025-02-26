from gaze_tracking import GazeTracking
import pygame
import cv2
import tkinter
from PIL import ImageColor
import numpy as np

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

    def generateTargets(self, rows:int=3, cols:int=5, radius:int = 5):
        targets = []
        spacingX = self.screenInfo.resolution[0] // (cols + 1)
        spacingY = self.screenInfo.resolution[1] // (rows + 1)
        for row in range(rows):
            for col in range(cols):
                x = (col + 1) * spacingX
                y = (row + 1) * spacingY
                targets.append(Target(x, y, radius=radius))
        return targets

    def calibrateRound(self):
        ROWS, COLS = 3, 5
        RADIUS = 10
        state = "INIT"
        clock = pygame.time.Clock()
        running = True
        calibrationList = []
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
                            targetVis = np.zeros(ROWS * COLS)
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
                        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                            if targetId < (ROWS * COLS) - 1:
                                targetId = targetId + 1
                                targetVis[targetId] = True
                                ratios = (self.gaze.horizontal_ratio(), self.gaze.vertical_ratio())
                                self.calibrationData.append(ratios)
                            else:
                                state = "END"
                                break

                    # Draw targets if visible
                    if targetVis[targetId]:
                        targets[targetId].draw(self.screenSession)
                    
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
game = TEAGame(screenInfo=ScreenInfo(), cameraId=1)
game.calibrateRound()
print(game.calibrationData)