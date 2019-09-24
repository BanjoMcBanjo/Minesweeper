# Importing necessary items
import random, pygame, sys, time
from pygame.locals import *

# Setting constants
FPS = 30  # Frames per second
WINDOWWIDTH = 500  # Width (across) of window in pixels
WINDOWHEIGHT = 500  # Height (vertically) of window in pixels
BOXSIZE = 30  # Size of each box
GAPSIZE = 10  # Gap between each box
BOARDWIDTH = 10  # Width of minesweeper boxes
BOARDHEIGHT = 10  # Height of minesweeper boxes
XMARGIN = int((WINDOWWIDTH - (BOARDWIDTH * (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = XMARGIN
TOTALMINES = 16  # Total number of mines in gameboard (can be changed)

# Create basic colors
LIGHTGRAY = (240, 240, 240)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 128, 0)

# Convenient color tags
BGCOLOR = WHITE  # Background color
BOARDCOLOR = GREEN  # Base color of field
BOXCOLOR_COVERED = BLUE  # Covered box color
BOXCOLOR_REVEALED = LIGHTGRAY  # Revealed box color
MINECOLOR = BLACK  # Color of mines
TEXTCOLOR_1 = BLUE  # Text color 1 - For lower numbers of adjacent mines
TEXTCOLOR_2 = RED  # Text color 2 - For higher numbers of adjacent mines
HILITECOLOR = GREEN  # Highlighting color
RESETBGCOLOR = LIGHTGRAY  # Resetting background color
MINEMARK_COVERED = RED  # Marker/Flag cover
FILLER = 'OUT'  # Filler return for when cursor is outside the board

# Setting up font
FONTTYPE = 'Comic Sans MS'
FONTSIZE = 15

# Initializing game
pygame.init()
pygame.display.set_caption('Something Minesweeper')


def main():
    # Initialize global variables & pygame module, set caption
    global DISPLAYSURFACE, CLOCK, FONT, OUT_SURF, OUT_RECT
    CLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    FONT = pygame.font.SysFont(FONTTYPE, FONTSIZE)

    # Handles when cursor is outside the board
    OUT_SURF, OUT_RECT = outsideBoard('', TEXTCOLOR_1, RESETBGCOLOR, 0, 0)

    # Stores mouse coordinates
    mouse_x = 0
    mouse_y = 0

    # Set up data structures and lists
    mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

    # Set background color
    DISPLAYSURFACE.fill(BGCOLOR)

    # Main game loop
    while True:

        # Check for quit function
        checkForKeyPressQuit()

        # Initialize input booleans - mouse click and spacebar press
        mouseClicked = False
        spacePressed = False

        # Draw board
        DISPLAYSURFACE.fill(BGCOLOR)
        pygame.draw.rect(DISPLAYSURFACE, BOARDCOLOR, (
            XMARGIN - 5, YMARGIN - 5, (BOXSIZE + GAPSIZE) * BOARDWIDTH + 5, (BOXSIZE + GAPSIZE) * BOARDHEIGHT + 5))
        text = 'Game reveals all mines upon a game over, then restarts automatically'
        text2 = 'Game will tell you if you win, then restart automatically'
        text3 = 'Press spacebar to mark boxes where you think mines are. You CAN lose instantly'
        theText = FONT.render(text, True, BLACK)
        theText2 = FONT.render(text2, True, BLACK)
        theText3 = FONT.render(text3, True, BLACK)
        DISPLAYSURFACE.blit(theText, (5, 0))
        DISPLAYSURFACE.blit(theText2, (5, 20))
        DISPLAYSURFACE.blit(theText3, (5, 450))
        drawGUI()
        drawMinesNumbers(mineField)

        # Event handling loop - for various user interactions
        for event in pygame.event.get():
            # Exiting out actually exits out
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # Keep track of cursor position
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            # Keep track of mouse clicks
            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                mouseClicked = True
            # Keep track of keyboard interactions
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    spacePressed = True
            elif event.type == KEYUP:
                if event.key == K_SPACE:
                    spacePressed = False

        # Draw covers over boxes
        # revealedBoxes is boxes that have been clicked on and revealed
        # markedMines represents covers for marked mines
        drawCovers(revealedBoxes, markedMines)

        # Determine boxes at clicked areas
        box_x, box_y = getBoxAtPixel(mouse_x, mouse_y)

        # Mouse not over a box in field - add after main game done?
        if (box_x, box_y) == (None, None):

            # Filler for possibilities for when cursor is outside board area? Currently just prevents crashing
            if OUT_RECT.collidepoint(mouse_x, mouse_y):
                return FILLER

        # Mouse currently over box in board
        else:
            # Highlight unrevealed box
            # "if not" checks if list is empty or not
            if not revealedBoxes[box_x][box_y]:

                # Mark mines
                if spacePressed:
                    markedMines.append([box_x, box_y])

                # Reveal clicked boxes
                if mouseClicked:
                    revealedBoxes[box_x][box_y] = True

                    # When 0 is revealed (no immediately adjacent mines), show relevant adjacent boxes
                    if mineField[box_x][box_y] == '[0]':
                        showBoardNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY)

                    # When mine is revealed, show other mines (NOT WORKING YET)
                    if mineField[box_x][box_y] == '[X]':
                        showMines(revealedBoxes, mineField, box_x, box_y)
                        drawMinesNumbers(mineField)
                        pygame.display.update()
                        time.sleep(1)
                        # before resetting
                        mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()

        # Check if player has won
        if gameWon(revealedBoxes, mineField):
            # MAKE WIN DISPLAY
            text4 = 'You WIN!'
            theText4 = FONT.render(text4, True, RED)
            DISPLAYSURFACE.blit(theText4, (5, 470))
            pygame.display.update()
            time.sleep(1)
            mineField, zeroListXY, revealedBoxes, markedMines = gameSetup()
        # Redraw screen, wait for clock tick
        pygame.display.update()
        CLOCK.tick(FPS)


def blankField():
    # Creates a blank BOARDWIDTH x BOARDHEIGHT data structure
    # "[]" creates a list; "()" creates a tuple
    board = []
    for x in range(BOARDWIDTH):
        board.append([])
        for y in range(BOARDHEIGHT):
            board[x].append('[]')
    return board


def mineMaker(board):
    # Places mines in BOARDWIDTH x BOARDHEIGHT data structure
    # Input is a blank board
    mineCounter = 0
    xy = []
    # Loop to place mines until set mine total is reached
    while mineCounter < TOTALMINES:
        x = random.randint(0, BOARDWIDTH - 1)
        y = random.randint(0, BOARDHEIGHT - 1)
        xy.append([x, y])
        if xy.count([x, y]) > 1:
            xy.remove([x, y])
        else:
            board[x][y] = '[X]'
            mineCounter += 1


def isThereMine(field, x, y):
    # Checks if there is a mine at the specified point in the 2D array
    return field[x][y] == '[X]'


def placeNumbers(field):
    # Places numbers in BOARDWIDTH x BOARDHEIGHT data structure
    # Requires field with mines as input

    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if not isThereMine(field, x, y):
                count = 0
                if x != 0:
                    if isThereMine(field, x - 1, y):
                        count += 1
                    if y != 0:
                        if isThereMine(field, x - 1, y - 1):
                            count += 1
                    if y != BOARDHEIGHT - 1:
                        if isThereMine(field, x - 1, y + 1):
                            count += 1
                if x != BOARDWIDTH - 1:
                    if isThereMine(field, x + 1, y):
                        count += 1
                    if y != 0:
                        if isThereMine(field, x + 1, y - 1):
                            count += 1
                    if y != BOARDHEIGHT - 1:
                        if isThereMine(field, x + 1, y + 1):
                            count += 1
                if y != 0:
                    if isThereMine(field, x, y - 1):
                        count += 1
                if y != BOARDHEIGHT - 1:
                    if isThereMine(field, x, y + 1):
                        count += 1
                field[x][y] = '[%s]' % (count)


def blankRevealedBoxData(val):
    # Returns BOARDWIDTH x BOARDHEIGHT data structure different from the field data structure
    # Each item in data structure is a boolean to show whether box at those BOARDWIDTH and BOARDHEIGHT coordinates -
    # should be revealed

    revealedBoxes = []
    for i in range(BOARDWIDTH):
        revealedBoxes.append([val] * BOARDHEIGHT)
    return revealedBoxes


def gameSetup():
    # Sets up mine field data structure, list of all zeroes for recursion, and revealed box boolean data structure

    mineField = blankField()
    mineMaker(mineField)
    placeNumbers(mineField)
    zeroListXY = []
    markedMines = []
    revealedBoxes = blankRevealedBoxData(False)

    return mineField, zeroListXY, revealedBoxes, markedMines


def drawGUI():
    # Draws field GUI

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_REVEALED, (left, top, BOXSIZE, BOXSIZE))


def drawMinesNumbers(board):
    # Draws mines and numbers onto GUI
    # Board should have mines and numbers
    # Used for revealing mines upon a game over

    half = int(BOXSIZE * 0.5)

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            center_x, center_y = getCenterXY(box_x, box_y)
            # If there's a mine...
            if board[box_x][box_y] == '[X]':
                pygame.draw.circle(DISPLAYSURFACE, MINECOLOR, (left + half, top + half), half)
            # If there's no mine...
            else:
                for i in range(1, 9):
                    if board[box_x][box_y] == '[' + str(i) + ']':
                        drawText(str(i), FONT, TEXTCOLOR_1, DISPLAYSURFACE, center_x, center_y)


def getAdjacentBoxesXY(mineField, box_x, box_y):
    # Gets box (x,y) coordinates for all adjacent boxes to (box_x, box_y)

    adjacentBoxesXY = []

    if box_x != 0:
        adjacentBoxesXY.append([box_x - 1, box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x - 1, box_y - 1])
        if box_y != BOARDHEIGHT - 1:
            adjacentBoxesXY.append([box_x - 1, box_y + 1])
    if box_x != BOARDWIDTH - 1:
        adjacentBoxesXY.append([box_x + 1, box_y])
        if box_y != 0:
            adjacentBoxesXY.append([box_x + 1, box_y - 1])
        if box_y != BOARDHEIGHT - 1:
            adjacentBoxesXY.append([box_x + 1, box_y + 1])
    if box_y != 0:
        adjacentBoxesXY.append([box_x, box_y - 1])
    if box_y != BOARDHEIGHT - 1:
        adjacentBoxesXY.append([box_x, box_y + 1])

    return adjacentBoxesXY


def revealAdjacentBoxes(revealedBoxes, box_x, box_y):
    # Modifies revealedBoxes data structure so that all adjacent boxes to (box_x, box_y) are set to True
    # Used in upcoming method to reveal board numbers recursively

    if box_x != 0:
        revealedBoxes[box_x - 1][box_y] = True
        if box_y != 0:
            revealedBoxes[box_x - 1][box_y - 1] = True
        if box_y != BOARDHEIGHT - 1:
            revealedBoxes[box_x - 1][box_y + 1] = True
    if box_x != BOARDWIDTH - 1:
        revealedBoxes[box_x + 1][box_y] = True
        if box_y != 0:
            revealedBoxes[box_x + 1][box_y - 1] = True
        if box_y != BOARDHEIGHT - 1:
            revealedBoxes[box_x + 1][box_y + 1] = True
    if box_y != 0:
        revealedBoxes[box_x][box_y - 1] = True
    if box_y != BOARDHEIGHT - 1:
        revealedBoxes[box_x][box_y + 1] = True


def showBoardNumbers(revealedBoxes, mineField, box_x, box_y, zeroListXY):
    # Modifies revealedBox data structure if chosen box_x & box_y is [0] (aka there's no mine)
    # RECURSIVE METHOD to show all boxes - should expand upon self to reach all-
    # relevant boxes

    revealedBoxes[box_x][box_y] = True
    revealAdjacentBoxes(revealedBoxes, box_x, box_y)
    for i, j in getAdjacentBoxesXY(mineField, box_x, box_y):
        if mineField[i][j] == '[0]' and [i, j] not in zeroListXY:
            zeroListXY.append([i, j])
            showBoardNumbers(revealedBoxes, mineField, i, j, zeroListXY)


def showMines(revealedBoxes, mineField, box_x, box_y):
    # box_x and box_y are used, just not within the method itself
    # Modifies revealedBox data structure if chosen box_x & box_y is [X] (has a mine)

    for i in range(BOARDWIDTH):
        for a in range(BOARDHEIGHT):
            if mineField[i][a] == '[X]':
                revealedBoxes[i][a] = True


def drawCovers(revealedBoxes, markedMines):
    # Uses revealedBox BOARDWIDTH x BOARDHEIGHT data structure to determine whether to draw box covering mine/number
    # Draw red cover instead of gray cover over marked mines - red cover triggered by
    # space bar

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            if not revealedBoxes[box_x][box_y]:
                left, top = getLeftTopXY(box_x, box_y)
                if [box_x, box_y] in markedMines:
                    pygame.draw.rect(DISPLAYSURFACE, MINEMARK_COVERED, (left, top, BOXSIZE, BOXSIZE))
                else:
                    pygame.draw.rect(DISPLAYSURFACE, BOXCOLOR_COVERED, (left, top, BOXSIZE, BOXSIZE))


def drawText(text, font, color, surface, x, y):
    # Function to easily draw text and also return object & rect pair

    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.centerx = x
    textrect.centery = y
    surface.blit(textobj, textrect)


def outsideBoard(text, color, bgcolor, center_x, center_y):
    # Can be used to make things outside the main gameboard. Not used for anything currently

    tempSurf = FONT.render(text, True, color, bgcolor)
    tempRect = tempSurf.get_rect()
    tempRect.centerx = center_x
    tempRect.centery = center_y

    return (tempSurf, tempRect)


def getLeftTopXY(box_x, box_y):
    # Get left & top coordinates - for various board interactions

    left = XMARGIN + box_x * (BOXSIZE + GAPSIZE)
    top = YMARGIN + box_y * (BOXSIZE + GAPSIZE)
    return left, top


def getCenterXY(box_x, box_y):
    # Get center coordinates - for various board interactions

    center_x = XMARGIN + BOXSIZE / 2 + box_x * (BOXSIZE + GAPSIZE)
    center_y = YMARGIN + BOXSIZE / 2 + box_y * (BOXSIZE + GAPSIZE)
    return center_x, center_y


def getBoxAtPixel(x, y):
    # Gets coordinates of box at mouse coordinates - for various board interactions

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            left, top = getLeftTopXY(box_x, box_y)
            boxRect = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
            if boxRect.collidepoint(x, y):
                return (box_x, box_y)
    return (None, None)


def gameWon(revealedBoxes, mineField):
    # Checks if player has revealed all boxes

    notMineCount = 0

    for box_x in range(BOARDWIDTH):
        for box_y in range(BOARDHEIGHT):
            if revealedBoxes[box_x][box_y] == True:
                if mineField[box_x][box_y] != '[X]':
                    notMineCount = notMineCount + 1

    if notMineCount >= (BOARDWIDTH * BOARDHEIGHT) - TOTALMINES:
        return True
    else:
        return False


def checkForKeyPressQuit():
    # Check if quit or any other key is pressed
    # len() method returns the number of items in an object
    if len(pygame.event.get(QUIT)) > 0:
        pygame.quit()
        sys.exit()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        pygame.quit()
        sys.exit()
    return keyUpEvents[0].key

    # Runs code


if __name__ == '__main__':
    main()
