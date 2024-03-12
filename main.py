from cmu_112_graphics import *
import random
import math
import time

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

# Customize color
def rgbString(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

# Turn degree measure into radian measure
def deg2Rad(degree):
    return degree * math.pi / 180

def make2dList(rows, cols): #From Lecture Notes
    return [ ([0] * cols) for row in range(rows) ]

def randColor():
    colorX = random.randint(0, 255)
    colorY = random.randint(0, 255)
    colorZ = random.randint(0, 255)
    return rgbString(colorX, colorY, colorZ)

def maxItemLength(a):
    maxLen = 0
    rows = len(a)
    cols = len(a[0])
    for row in range(rows):
        for col in range(cols):
            maxLen = max(maxLen, len(str(a[row][col])))
    return maxLen

# Because Python prints 2d lists on one row,
# we might want to write our own function
# that prints 2d lists a bit nicer.
def print2dList(a):
    if (a == []):
        # So we don't crash accessing a[0]
        print([])
        return
    rows, cols = len(a), len(a[0])
    fieldWidth = maxItemLength(a)
    print('[')
    for row in range(rows):
        print(' [ ', end='')
        for col in range(cols):
            if (col > 0): print(', ', end='')
            print(str(a[row][col]).rjust(fieldWidth), end='')
        print(' ]')
    print(']')

#################################################
#Play Screen Mode
#################################################

class PlayScreenMode(Mode):

    def appStarted(mode):
        mode.presses = 0
        mode.messages = ['There was once a rat who lived a happy life doing his rat things.',
                    'Then he got kidnapped by an evil scientist, who placed him in a maze.',
                    'You are the rat. Escape the maze.',
                    'Eat cheese to gain health points (yellow blocks with "Cs").',
                    'Avoid poison (green blocks with "Xs") and walls.',
                    'Keep a careful eye on your health bar (at the top of the screen).',
                    'Use WASD to move and cursor to turn.',
                    'You begin in the top left of the maze, try to get to the bottom right.',
                    'Press any key to beginpog.']
                    

    def redrawAll(mode, canvas):
        if (mode.presses < len(mode.messages) - 1):
            canvas.create_text(mode.width //2, mode.height * 0.9,
                           text = 'Press space to continue. Press "c" to skip intro.')
        
        canvas.create_text(mode.width//2, mode.height // 2, 
                           text = mode.messages[mode.presses], font = 'Times 30 bold')

    def keyPressed(mode, event):
        if (mode.presses < len(mode.messages) - 1): 
            if (event.key == 'c'):
                mode.app.setActiveMode(mode.app.gameMode)
            elif (event.key == 'Space'):
                if (mode.presses < len(mode.messages) - 1): mode.presses += 1
        else:
            mode.app.setActiveMode(mode.app.gameMode)

#################################################
# Game Mode
#################################################

class GameMode(Mode):

    # Starter Functions
    def appStarted(mode):
        makeMap(mode)
        placeCheese(mode)
        placePoison(mode)
        startRat(mode)
        startValues(mode)
        calculateRays(mode)
        
    def keyPressed(mode, event):
        if (not(mode.gameOver) and not(mode.victory)):
            movement(mode, event)
        elif (mode.gameOver):
            if (event.key == 'r'): 
                mode.appStarted()
        if (mode.victory):
            if (event.key == 'e'):
                mode.jokester = True
                mode.victory = False
        if (mode.jokester):
            if (event.key == 'r'):
                mode.appStarted()
        
    def mousePressed(mode, event):
        if (not(mode.gameOver) or not(mode.victory)):
            mode.prevx = None

    def mouseMoved(mode, event):
        if (not(mode.gameOver) or not(mode.victory)):
            if (mode.prevx == None): mode.prevx = event.x
            else: 
                x0 = mode.prevx
                x1 = event.x 
                if (x1 > x0): mode.ratAngle -= deg2Rad((x1 - x0) / (mode.width / 360))
                else: mode.ratAngle += deg2Rad((x0 - x1) / (mode.width / 360))
                calculateRays(mode)
                mode.prevx = x1

    def timerFired(mode):
        if (not(mode.gameOver) or not(mode.victory)):
            if (mode.poison): 
                elapsed = int(time.time() - mode.startPoison)
                if (elapsed < 6):
                    mode.health -= 0.5
                    if (mode.health <= 0): mode.gameOver = True
                else: 
                    mode.poison = False

    def redrawAll(mode, canvas):
        if (not(mode.gameOver) and not (mode.victory) and not(mode.jokester)):
            drawRoof(mode, canvas)
            drawFloor(mode, canvas)
            drawPOV(mode, canvas)
            drawNose(mode, canvas)
            drawHealth(mode, canvas)
        elif (mode.gameOver):
            canvas.create_text(mode.width//2, mode.height//4, 
                text = 'YOU LOSE YOU SUCK. But who is even surprised you are a dumb rat.', 
                font = 'Times 25 bold')
            canvas.create_text(mode.width//2, mode.height//4 + 50, 
                text = 'Press R to restart and play again.', font = 'Times 25 bold')
        elif (mode.victory):
            canvas.create_text(mode.width//2, mode.height//4, 
            text = 'POGGERS!! YOU ESCAPED THE MAZE. PRESS E TO EXIT THE GAME.', 
                font = 'Times 25 bold')
        elif (mode.jokester):
            canvas.create_text(mode.width//2, mode.height//4, 
                text = 'SIKE!! You are a rat. You have a tiny dumb rat brain.', 
                font = 'Times 25 bold')
            canvas.create_text(mode.width//2, mode.height//4 + 25, 
                text = 'How could you think you could ever escape a scientist with a big scientist brain.', 
                font = 'Times 25 bold')
            canvas.create_text(mode.width//2, mode.height//4 + 50, 
                text = 'Press R to restart and play again.', 
                font = 'Times 25 bold')

#################################################
# Starter Functions
#################################################

def startRat(mode):
    # View Settings
    mode.ratx, mode.raty = (1, 1) # Rat location
    mode.ratAngle = math.pi / 4 # Angle that the rat is looking at
    mode.fov = 120 # How much the rat can see
    mode.rays = { } # The rays shot out from the rat

    # Game Settings
    mode.health = 100
    mode.startPoison = None
    mode.poison = False
    mode.timerDelay = 100

    mode.gameOver = False
    mode.victory = False
    mode.jokester = False

    mode.clickx = None # Updates when mouse clicked 
    mode.releasex = None # Updates when mouse released
    mode.prevx = None # Updates every mouse pressed

def startValues(mode):
    mode.small = 0.002 # Amount to increment by for ray tracing
    mode.step = 0.5 # How much the rat moves in a step
    mode.margin = 20 # Margin for the screen 
                
#################################################
# Making Map
#################################################

def makeMap(mode): 
    mode.rows = 30
    mode.cols = 30
    mode.maze = make2dList(mode.rows, mode.cols)
    makeBoundaries(mode)
    recursiveDivision(mode, 1, 1, mode.rows - 1, mode.cols - 1)
    colorBlocks(mode)

def makeBoundaries(mode):
    #top row
    mode.maze[0] = [1] * mode.cols
    #bottom row
    mode.maze[mode.rows - 1] = [1] * mode.cols
    #left and right column
    for i in range(0, mode.rows):
        mode.maze[i][0] = 1
        mode.maze[i][mode.cols - 1] = 1

#yeah.
def recursiveDivision(mode, minRow, minCol, maxRow, maxCol):
    x = maxRow - minRow
    y = maxCol - minCol
    if ((x <= 2) or (y <= 2)):
        return mode.maze
    else:
        #generate the divisions
        row = random.randint(minRow + 1, maxRow - 2)
        col = random.randint(minCol + 1, maxCol - 2)
        #select the spaces in the divisions
        rowSpace1 = random.randint(minCol, col - 1)
        rowSpace2 = random.randint(col + 1, maxCol - 1)
        colSpace1 = random.randint(minRow, row - 1)
        colSpace2 = random.randint(row + 1, maxRow - 1)
        #make the divisions
        for i in range(minCol, maxCol):
            mode.maze[row][i] = 1
        for i in range(minRow, maxRow):
            mode.maze[i][col] = 1
        #make the randomized spaces
        mode.maze[row][rowSpace1] = 0
        mode.maze[row][rowSpace2] = 0
        mode.maze[colSpace1][col] = 0
        mode.maze[colSpace2][col] = 0
        recursiveDivision(mode, minRow, minCol, row, col)
        recursiveDivision(mode, minRow, col + 1, row, maxCol)
        recursiveDivision(mode, row + 1, minCol, maxRow, col)
        recursiveDivision(mode, row + 1, col + 1, maxRow, maxCol)

def placeCheese(mode):
    # pick random coordinate until it is empty
    row = random.randint(2, mode.cols - 2)
    col = random.randint(2, mode.cols - 2)
    if (mode.maze[row][col] == 0): mode.maze[row][col] = 2
    else:
        while (mode.maze[row][col] != 0):
            row = random.randint(2, mode.cols - 2)
            col = random.randint(2, mode.cols - 2)
            if (mode.maze[row][col] == 0):
                mode.maze[row][col] = 2
                break

def placePoison(mode):
    # pick random coordinate until it is empty
    row = random.randint(2, mode.cols - 2)
    col = random.randint(2, mode.cols - 2)
    if (mode.maze[row][col] == 0): mode.maze[row][col] = 3
    else:
        while (mode.maze[row][col] != 0):
            row = random.randint(2, mode.cols - 2)
            col = random.randint(2, mode.cols - 2)
            if (mode.maze[row][col] == 0):
                mode.maze[row][col] = 3
                break

def colorBlocks(mode): # Turns 1's into colors
    for row in range(len(mode.maze)):
        for col in range(len(mode.maze[0])):
            if (mode.maze[row][col] == 1):
                mode.maze[row][col] = randColor()

#################################################
# Ray Tracing Function
#################################################

# Calculates rays from player location 
def calculateRays(mode):
    mode.rays = { } # Resets mode.rays
    for i in range(mode.fov): # For each angle in FOV
        angle = mode.ratAngle - deg2Rad(i - mode.fov / 2) # Based off mode.ratAngle
        x, y = mode.ratx, mode.raty # Rat location 
        sin, cos = (mode.small * math.sin(angle), mode.small * math.cos(angle))
        distance = 0 # Original distance is 0
        while True:
            x, y = x + cos, y + sin
            distance = distance + 1
            if (mode.maze[int(x)][int(y)] != 0):
                height = 1 / (mode.small * distance) # Inverse of distance
                color = mode.maze[int(x)][int(y)]
                obj = (int(x), int(y))
                break
        mode.rays[i] = (height, color, obj)

#################################################
# Key Pressed and Co.
#################################################

def movement(mode, event):
    x, y = mode.ratx, mode.raty
    if (event.key == 'w'): # Forward
        x += mode.step * math.cos(mode.ratAngle)
        y += mode.step * math.sin(mode.ratAngle)
    elif (event.key == 's'): # Backward
        x -= mode.step * math.cos(mode.ratAngle)
        y -= mode.step * math.sin(mode.ratAngle)
    ninety = deg2Rad(90)
    if (event.key == 'a'): # Left
        x += mode.step * math.cos(mode.ratAngle + ninety)
        y += mode.step * math.sin(mode.ratAngle + ninety)
    elif (event.key == 'd'): # Right
        x += mode.step * math.cos(mode.ratAngle - ninety)
        y += mode.step * math.sin(mode.ratAngle - ninety)

    if (mode.maze[int(x)][int(y)] == 0): # empty
        mode.ratx, mode.raty = x, y
    elif (mode.maze[int(x)][int(y)] == 2): # cheese
        mode.ratx, mode.raty = x, y
        mode.maze[int(x)][int(y)] = 0
        if (mode.health < 90): mode.health += 10
        elif (90 <= mode.health <= 100): mode.health = 100
        placeCheese(mode)
    elif (mode.maze[int(x)][int(y)] == 3): # poison
        mode.ratx, mode.raty = x, y
        mode.maze[int(x)][int(y)] = 0
        mode.poison = True
        mode.startPoison = time.time()
        placePoison(mode)
    else: # Wall
        mode.health -= 20
        if (mode.health <= 0): mode.gameOver = True

    # Winner Winner Chicken Dinner
    winRow = mode.rows - 2
    winCol = mode.cols - 2
    if (int(mode.ratx) == winRow and int(mode.raty) == winCol):
        mode.victory = True
    calculateRays(mode)
    
#################################################
# Draw Functions and Co.
#################################################

def drawRoof(mode, canvas):
    width = mode.width / (mode.fov + 1)
    canvas.create_rectangle(mode.margin, mode.margin, 
                            mode.width - mode.margin - 2 * width, mode.height / 2,
                            fill = 'gray', width = 0)

def drawFloor(mode, canvas):
    width = mode.width / (mode.fov + 1)
    color = rgbString(34, 34, 34)
    canvas.create_rectangle(mode.margin, mode.height / 2, 
                            mode.width - mode.margin - 2 * width, 
                            mode.height - mode.margin, fill = color, width = 0)

def drawPOV(mode, canvas):
    width = (mode.width - 2 * mode.margin) / (mode.fov + 1) # Width of angle
    height = mode.height / 2
    for i in mode.rays:
        x0, yco0 = i, mode.rays[i]
        y0, color0, obj0 = yco0

        if (color0 == 2): color0 = 'yellow' # It is a cheese
        elif (color0 == 3): color0 = 'green' # It is poison

        y0 = min((y0 * height), (height - mode.margin)) # Height or screen
        if (i < mode.fov - 1): # Don't want this to run for last i
            x1 = x0 + 1 
            yco1 = mode.rays[x1]
            y1, color1, obj1 = yco1
            y1 = min((y1 * height), (height - mode.margin))
            if (obj0 == obj1):
                canvas.create_polygon((x0 * width + mode.margin, height - y0),
                                    (x0 * width + mode.margin, height + y0),
                                    (x1 * width + mode.margin, height + y1),
                                    (x1 * width + mode.margin, height - y1),
                                    fill = color0)
                if (color0 == 'yellow'): # Label Cheese Differently
                    y = random.randint(int(height - y0), int(height + y0))
                    canvas.create_text(x0 * width + mode.margin, y, 
                    text = 'C', font = 'Arial 12 bold')
                elif (color0 == 'green'): # Label Poison
                    y = random.randint(int(height - y0), int(height + y0))
                    canvas.create_text(x0 * width + mode.margin, y, 
                    text = 'X', font = 'Arial 12 bold', fill = 'Red')

            else:
                y2 = min(y1, y0)
                canvas.create_polygon((x0 * width + mode.margin, height - y2),
                                    (x0 * width + mode.margin, height + y2),
                                    (x1 * width + mode.margin, height + y2),
                                    (x1 * width + mode.margin, height - y2),
                                    fill = 'white')

def drawNose(mode, canvas):
    # Snout
    x0 = (mode.width - 2 * mode.margin) * 0.4
    x1 = (mode.width - 2 * mode.margin) * 0.6
    x2 = (mode.width - 2 * mode.margin) * 0.5
    y0 = (mode.height - mode.margin)
    y1 = (mode.height - mode.margin)
    y2 = (mode.height - mode.margin) * 0.75
    canvas.create_polygon(x0, y0, x1, y1, x2, y2, fill = 'gray', width = 1)

    # Nose
    r = 10
    canvas.create_oval(x2 - r, y2 - r, x2 + r, y2 + r, fill = 'black')

def drawHealth(mode, canvas):
    x0 = (mode.width - 2 * mode.margin) * 0.2
    x1 = (mode.width - 2 * mode.margin) * 0.8
    y = (mode.height - 2 * mode.margin) * 0.1
    # Canvas
    canvas.create_rectangle(x0, y, x1, y - 10, fill = 'white')

    # Health
    if (mode.health >= 0):
        length = x1 - x0
        length = length * (mode.health / 100)
        x2 = x0 + length
        canvas.create_rectangle(x0, y, x2, y - 10, fill = 'red')

class MyModalApp(ModalApp):
    def appStarted(app):
        app.playScreenMode = PlayScreenMode()
        app.gameMode = GameMode()
        app.setActiveMode(app.playScreenMode)

app = MyModalApp(width = 1000, height = 500)
