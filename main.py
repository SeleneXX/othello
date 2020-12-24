import random, sys, pygame, time, copy
import numpy as np
#基础设定，窗口大小，游戏帧数
FPS = 10
WINDOWWID = 960
WINDOWHEI = 540
SPACESIZE = 50
BOARDWID = 8
BOARDHEI = 8
WHITE_TILE = 'WHITE_TILE'       #白子
BLACK_TILE = 'BLACK_TILE'       #黑子
EMPTY_SPACE = 'EMPTY_SPACE'     #空位
HINT_TILE = 'HINT_TILE'         #提示
RECOMMEND_TILE = 'RECOMMEND_TILE'   #推荐
ANIMATIONSPEED = 30

#棋盘边缘
XMARGIN = int((WINDOWWID-(BOARDWID*SPACESIZE))/2)
YMARGIN = int((WINDOWHEI - (BOARDHEI*SPACESIZE))/2)

#定义需要的颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 155, 0)
BLUE = (0, 50, 255)
BROWN = (174, 94, 0)
RED = (255, 0, 0)

#字体背景颜色
TEXTBGCOLOR1 = BLUE
TEXTBGCOLOR2 = GREEN
GRIDLINECOLOR = BLACK
TEXTCOLOR = WHITE
HINTCOLOR = BROWN
RECOMMENDCOLOR = RED

class nowboard(object):
    def __init__(self):
        self.width = BOARDWID
        self.height = BOARDHEI
        self.state = {}
        self.available = []
        self.players = [1, 2]  # player1 and player2
        self.player1tile = BLACK_TILE
        self.player2tile = WHITE_TILE
        self.lastmove = []

    def getBoardState(self, board):
        currentstate = np.zeros((4, self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                if board[x][y] == self.tile:
                    currentstate[0][x][y] = 1
                elif board[1][x][y] == self.player2tile:
                    currentstate[1][x][y] = 1
        currentstate[2][self.lastmove[0]][self.lastmove[1]]
        if len(self.states) % 2 == 0:
            currentstate[3][:, :] = 1.0  # indicate the colour to play
        return currentstate[:, ::-1, :]

    def availablemoves(self, board, tile):
        self.available = getValidmoves(board, tile)

    def setTile(self, tile):
        self.tile = tile

    def tilechange(self):
        if self.tile == BLACK_TILE:
            self.setTile(WHITE_TILE)
        elif self.tile == WHITE_TILE:
            self.setTile(BLACK_TILE)




def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE, ORIGINBGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWID, WINDOWHEI))           #游戏窗口
    pygame.display.set_caption('丁大佬牛逼')
    FONT = pygame.font.Font(None, 32)               #字体
    BIGFONT = pygame.font.Font(None, 48)
    boardImage = pygame.image.load('board.png')     #棋盘
    boardImage = pygame.transform.smoothscale(boardImage, (BOARDWID * SPACESIZE, BOARDHEI * SPACESIZE))     #对图片进行缩放，缩放为棋盘大小
    boardImageRect = boardImage.get_rect()          #获取图片的矩形坐标
    boardImageRect.topleft = (XMARGIN, YMARGIN)     #和棋盘左上角对齐
    BGIMAGE = pygame.image.load('bgimage.png')      #背景
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (WINDOWWID, WINDOWHEI))
    BGIMAGE.blit(boardImage, boardImageRect)        #绘制棋盘
    ORIGINBGIMAGE = pygame.image.load('bgimage.png')
    ORIGINBGIMAGE = pygame.transform.smoothscale(ORIGINBGIMAGE, (WINDOWWID, WINDOWHEI))

    while True:
        if runGame() == False:
            break

def runGame():
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    showHints = False
    showRecommend = False
    mode = enterGameMode()
    if mode == 'PVP':
        player1 = 'player1'
        player2 = 'player2'
        drawBoard(mainBoard)
        player1Tile, player2Tile = enterPlayerTile()
        turn = random.choice([player1, player2])  # 随机先后
        newGameSurf = FONT.render('New game', True, TEXTCOLOR, TEXTBGCOLOR2)  # 右上角功能
        newgameRect = newGameSurf.get_rect()
        newgameRect.topright = (WINDOWWID - 8, 10)
        hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
        hintsRect = hintsSurf.get_rect()
        hintsRect.topright = (WINDOWWID - 8, 40)
        recommendSurf = FONT.render('Recommend', True, TEXTCOLOR, TEXTBGCOLOR2)
        recommendRect = recommendSurf.get_rect()
        recommendRect.topright = (WINDOWWID - 8, 70)

        while True:  # 主循环
            if turn == player1:
                # 玩家1回合
                if getValidmoves(mainBoard, player1Tile) == []:
                    break  # 如果是玩家1回合但其不能移动，游戏结束
                movexy = None
                while movexy == None:
                    # 画出可落子范围和推荐落子位置
                    if showHints and showRecommend:
                        boardToDraw = getBoardWithValidandRecommendMoves(mainBoard, player1Tile)
                    elif showHints and not showRecommend:
                        boardToDraw = getBoardWithValidMoves(mainBoard, player1Tile)
                    elif not showHints and showRecommend:
                        boardToDraw = getBoardWithRecommendMOves(mainBoard, player1Tile)
                    else:
                        boardToDraw = mainBoard

                    checkForQuit()

                    # 捕获鼠标位置，查看是否点击了上述按钮
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True  # 新游戏
                            elif hintsRect.collidepoint((mouseX, mouseY)):
                                showHints = not showHints  # 显示提示
                            elif recommendRect.collidepoint((mouseX, mouseY)):
                                showRecommend = not showRecommend

                            movexy = getSpaceClicked(mouseX, mouseY)
                            if movexy != None and not isValidMove(mainBoard, player1Tile, movexy[0], movexy[1]):
                                # 判断 点击位置是否合法
                                movexy = None

                    drawBoard(boardToDraw)  # 画棋盘
                    drawInfo(boardToDraw, player1, player2, player1Tile, player2Tile, turn)  # 画底部提示信息

                    # 画三个按钮
                    DISPLAYSURF.blit(newGameSurf, newgameRect)
                    DISPLAYSURF.blit(hintsSurf, hintsRect)
                    DISPLAYSURF.blit(recommendSurf, recommendRect)

                    MAINCLOCK.tick(FPS)
                    pygame.display.update()

                makeMove(mainBoard, player1Tile, movexy[0], movexy[1], True)
                if getValidmoves(mainBoard, player2Tile) != []:
                    turn = player2  # 回合结束，如果玩家2能行动，则切换电脑玩家回合

            elif turn == player2:
                # 玩家2回合
                if getValidmoves(mainBoard, player2Tile) == []:
                    break  # 如果是玩家2回合但其不能移动，游戏结束
                movexy = None
                while movexy == None:

                    # 画出可落子范围和推荐落子位置
                    if showHints and showRecommend:
                        boardToDraw = getBoardWithValidandRecommendMoves(mainBoard, player2Tile)
                    elif showHints and not showRecommend:
                        boardToDraw = getBoardWithValidMoves(mainBoard, player2Tile)
                    elif not showHints and showRecommend:
                        boardToDraw = getBoardWithRecommendMOves(mainBoard, player2Tile)
                    else:
                        boardToDraw = mainBoard

                    checkForQuit()

                    # 捕获鼠标位置，查看是否点击了上述按钮
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True  # 新游戏
                            elif hintsRect.collidepoint((mouseX, mouseY)):
                                showHints = not showHints  # 显示提示
                            elif recommendRect.collidepoint((mouseX, mouseY)):
                                showRecommend = not showRecommend

                            movexy = getSpaceClicked(mouseX, mouseY)
                            if movexy != None and not isValidMove(mainBoard, player2Tile, movexy[0], movexy[1]):
                                # 判断 点击位置是否合法
                                movexy = None

                    drawBoard(boardToDraw)  # 画棋盘
                    drawInfo(boardToDraw, player1, player2, player1Tile, player2Tile, turn)  # 画底部提示信息

                    # 画三个按钮
                    DISPLAYSURF.blit(newGameSurf, newgameRect)
                    DISPLAYSURF.blit(hintsSurf, hintsRect)
                    DISPLAYSURF.blit(recommendSurf, recommendRect)

                    MAINCLOCK.tick(FPS)
                    pygame.display.update()

                makeMove(mainBoard, player2Tile, movexy[0], movexy[1], True)
                if getValidmoves(mainBoard, player1Tile) != []:
                    turn = player1  # 回合结束，如果玩家1能行动，则切换玩家1回合

        drawBoard(mainBoard)
        scores = getScoreOfBoard(mainBoard)  # 显示分数

        if scores[player1Tile] > scores[player2Tile]:  # 判断游戏结果
            text = 'Player1 win!'
        elif scores[player1Tile] < scores[player2Tile]:
            text = 'Player2 win!'
        else:
            text = 'The game was a tie!'

        textSurf = BIGFONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect = textSurf.get_rect()
        textRect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2))
        DISPLAYSURF.blit(textSurf, textRect)

        textSurf2 = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect2 = textSurf2.get_rect()
        textRect2.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2) + 50)

        yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
        yesRect = yesSurf.get_rect()
        yesRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 90)

        noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
        noRect = yesSurf.get_rect()
        noRect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 90)

        while True:
            checkForQuit()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseX, mouseY = event.pos
                    if yesRect.collidepoint((mouseX, mouseY)):
                        return True
                    elif noRect.collidepoint((mouseX, mouseY)):
                        return False
            DISPLAYSURF.blit(textSurf, textRect)
            DISPLAYSURF.blit(textSurf2, textRect2)
            DISPLAYSURF.blit(yesSurf, yesRect)
            DISPLAYSURF.blit(noSurf, noRect)
            pygame.display.update()
            MAINCLOCK.tick(FPS)
    elif mode == 'PVE':
        player1 = 'player'
        player2 = 'computer'
        drawBoard(mainBoard)
        playerTile, computerTile = enterPlayerTile()
        turn = random.choice([player1, player2])  # 随机先后
        newGameSurf = FONT.render('New game', True, TEXTCOLOR, TEXTBGCOLOR2)    #右上角功能
        newgameRect = newGameSurf.get_rect()
        newgameRect.topright = (WINDOWWID - 8, 10)
        hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
        hintsRect = hintsSurf.get_rect()
        hintsRect.topright = (WINDOWWID - 8, 40)
        recommendSurf = FONT.render('Recommend', True, TEXTCOLOR, TEXTBGCOLOR2)
        recommendRect = recommendSurf.get_rect()
        recommendRect.topright = (WINDOWWID - 8, 70)

        while True:     #主循环
            if turn == player1:
                #玩家回合
                if getValidmoves(mainBoard, playerTile) == []:
                    break           #如果是玩家回合但其不能移动，游戏结束
                movexy = None
                while movexy == None:

                    #画出可落子范围和推荐落子位置
                    if showHints and showRecommend:
                        boardToDraw = getBoardWithValidandRecommendMoves(mainBoard, playerTile)
                    elif showHints and not showRecommend:
                        boardToDraw = getBoardWithValidMoves(mainBoard, playerTile)
                    elif not showHints and showRecommend:
                        boardToDraw = getBoardWithRecommendMOves(mainBoard, playerTile)
                    else:
                        boardToDraw = mainBoard


                    checkForQuit()

                    #捕获鼠标位置，查看是否点击了上述按钮
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True     #新游戏
                            elif hintsRect.collidepoint((mouseX, mouseY)):
                                showHints = not showHints       #显示提示
                            elif recommendRect.collidepoint((mouseX, mouseY)):
                                showRecommend = not showRecommend

                            movexy = getSpaceClicked(mouseX, mouseY)
                            if movexy != None and not isValidMove(mainBoard, playerTile, movexy[0], movexy[1]):
                                #判断 点击位置是否合法
                                movexy = None

                    drawBoard(boardToDraw)          #画棋盘
                    drawInfo(mainBoard, player1, player2, playerTile, computerTile, turn)           #画底部提示信息

                    # 画三个按钮
                    DISPLAYSURF.blit(newGameSurf, newgameRect)
                    DISPLAYSURF.blit(hintsSurf, hintsRect)
                    DISPLAYSURF.blit(recommendSurf, recommendRect)

                    MAINCLOCK.tick(FPS)
                    pygame.display.update()

                makeMove(mainBoard, playerTile, movexy[0], movexy[1], True)
                if getValidmoves(mainBoard, computerTile) != []:
                    turn = player2       #回合结束，如果电脑玩家能行动，则切换电脑玩家回合

            elif turn == player2:
                #电脑玩家回合
                if getValidmoves(mainBoard, computerTile) == []:
                    break       #如果是电脑回合但其不能动，游戏结束

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouseX, mouseY = event.pos
                        if newgameRect.collidepoint((mouseX, mouseY)):
                            return True  # 新游戏

                drawBoard(mainBoard)
                drawInfo(mainBoard, player1, player2, playerTile, computerTile, turn)

                DISPLAYSURF.blit(newGameSurf, newgameRect)  # 画三个按钮
                DISPLAYSURF.blit(hintsSurf, hintsRect)
                DISPLAYSURF.blit(recommendSurf, recommendRect)

                pauseUntil = time.time() + random.randint(5, 15) * 0.1           #模拟电脑玩家思考时间，长度随机
                while time.time() < pauseUntil:
                    pygame.display.update()

                x,y = getComputerMove(mainBoard, computerTile)
                makeMove(mainBoard, computerTile, x, y, True)
                if getValidmoves(mainBoard, playerTile) != []:
                    turn = player1     #回合结束，如果玩家能行动，则切换玩家回合

        drawBoard(mainBoard)
        scores = getScoreOfBoard(mainBoard)         #显示分数

        if scores[playerTile] > scores[computerTile]:           #判断游戏结果
            text = 'You win!'
        elif scores[playerTile] < scores[computerTile]:
            text = 'You loss!'
        else:
            text = 'The game was a tie!'

        textSurf = BIGFONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect = textSurf.get_rect()
        textRect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2))
        DISPLAYSURF.blit(textSurf, textRect)

        textSurf2 = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect2 = textSurf2.get_rect()
        textRect2.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2) + 50)

        yesSurf =  BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
        yesRect = yesSurf.get_rect()
        yesRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 90)

        noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
        noRect = yesSurf.get_rect()
        noRect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 90)

        while True:
            checkForQuit()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseX, mouseY = event.pos
                    if yesRect.collidepoint((mouseX, mouseY)):
                        return True
                    elif noRect.collidepoint((mouseX, mouseY)):
                        return False
            DISPLAYSURF.blit(textSurf, textRect)
            DISPLAYSURF.blit(textSurf2, textRect2)
            DISPLAYSURF.blit(yesSurf, yesRect)
            DISPLAYSURF.blit(noSurf, noRect)
            pygame.display.update()
            MAINCLOCK.tick(FPS)
    elif mode == 'EVE':
        player1 = 'computer1'
        player2 = 'computer2'
        drawBoard(mainBoard)
        # computer1Tile = random.choice([BLACK_TILE, WHITE_TILE])
        computer1Tile = BLACK_TILE
        newGameSurf = FONT.render('New game', True, TEXTCOLOR, TEXTBGCOLOR2)  # 右上角功能
        newgameRect = newGameSurf.get_rect()
        newgameRect.topright = (WINDOWWID - 8, 10)
        if computer1Tile == BLACK_TILE:
            computer2Tile = WHITE_TILE
        else:
            computer2Tile = BLACK_TILE
        turn = random.choice([player1, player2])  # 随机先后


        while True:  # 主循环
            if turn == player1:
                # 电脑玩家1回合
                if getValidmoves(mainBoard, computer1Tile) == []:
                    break  # 如果是电脑2回合但其不能动，游戏结束
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouseX, mouseY = event.pos
                        if newgameRect.collidepoint((mouseX, mouseY)):
                            return True  # 新游戏

                drawBoard(mainBoard)
                drawInfo(mainBoard, player1, player2, computer1Tile, computer2Tile, turn)
                DISPLAYSURF.blit(newGameSurf, newgameRect)

                pauseUntil = time.time() + random.randint(5, 15) * 0.1  # 模拟电脑玩家思考时间，长度随机
                while time.time() < pauseUntil:
                    pygame.display.update()

                x, y = getComputerMove(mainBoard, computer1Tile)
                makeMove(mainBoard, computer1Tile, x, y, True)
                if getValidmoves(mainBoard, computer2Tile) != []:
                    turn = player2  # 回合结束，如果电脑玩家1能行动，则切换电脑玩家1回合

            elif turn == player2:
                # 电脑玩家2回合
                if getValidmoves(mainBoard, computer2Tile) == []:
                    break  # 如果是电脑2回合但其不能动，游戏结束

                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONUP:
                        mouseX, mouseY = event.pos
                        if newgameRect.collidepoint((mouseX, mouseY)):
                            return True  # 新游戏
                drawBoard(mainBoard)
                drawInfo(mainBoard, player1, player2, computer1Tile, computer2Tile, turn)
                DISPLAYSURF.blit(newGameSurf, newgameRect)


                pauseUntil = time.time() + random.randint(5, 15) * 0.1  # 模拟电脑玩家思考时间，长度随机
                while time.time() < pauseUntil:
                    pygame.display.update()

                x, y = prophet(mainBoard, computer2Tile)
                makeMove(mainBoard, computer2Tile, x, y, True)
                if getValidmoves(mainBoard, computer1Tile) != []:
                    turn = player1  # 回合结束，如果电脑玩家1能行动，则切换电脑玩家1回合


        drawBoard(mainBoard)
        scores = getScoreOfBoard(mainBoard)  # 显示分数

        if scores[computer1Tile] > scores[computer2Tile]:  # 判断游戏结果
            text = 'Computer1 win!'
        elif scores[computer1Tile] < scores[computer2Tile]:
            text = 'Computer2 win!'
        else:
            text = 'The game was a tie!'

        textSurf = BIGFONT.render(text, True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect = textSurf.get_rect()
        textRect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2))
        DISPLAYSURF.blit(textSurf, textRect)

        textSurf2 = BIGFONT.render('Play again?', True, TEXTCOLOR, TEXTBGCOLOR1)
        textRect2 = textSurf2.get_rect()
        textRect2.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2) + 50)

        yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
        yesRect = yesSurf.get_rect()
        yesRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 90)

        noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
        noRect = yesSurf.get_rect()
        noRect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 90)

        while True:
            checkForQuit()
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    mouseX, mouseY = event.pos
                    if yesRect.collidepoint((mouseX, mouseY)):
                        return True
                    elif noRect.collidepoint((mouseX, mouseY)):
                        return False
            DISPLAYSURF.blit(textSurf, textRect)
            DISPLAYSURF.blit(textSurf2, textRect2)
            DISPLAYSURF.blit(yesSurf, yesRect)
            DISPLAYSURF.blit(noSurf, noRect)
            pygame.display.update()
            MAINCLOCK.tick(FPS)


def translateBoardToPixelCoord(x, y):               #根据棋盘坐标转化出对应的像素坐标
    return XMARGIN + x * SPACESIZE +int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)

def animateTileChange(tulesToFlip, tileColor, additionalTile):
    if tileColor == WHITE_TILE:
        additionalTileColor = WHITE
    else:
        additionalTileColor = BLACK
    additionalTileX, additionalTileY =  translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2))
    pygame.display.update()

    for rgbValues in range (0, 255, int(ANIMATIONSPEED * 2)):            #点击棋子后颜色渐变，黑到白，白到黑
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0
        if tileColor == WHITE_TILE:
            color = tuple([rgbValues] * 3)
        elif tileColor == BLACK_TILE:
            color = tuple([255 - rgbValues] * 3)

        for x, y in tulesToFlip:
            centerX, centerY = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerX, centerY), int(SPACESIZE / 2))
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        checkForQuit()

def drawBoard(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())   #画背景
    for x in range (BOARDWID + 1):              #循环画出水平的棋盘线
        startX = (x * SPACESIZE) + XMARGIN
        startY = YMARGIN
        endX = (x * SPACESIZE) + XMARGIN
        endY = YMARGIN + (BOARDHEI * SPACESIZE)
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startX, startY), (endX, endY))    #按照起点和终点的左边画线

    for y in range (BOARDHEI + 1):              #循环画出垂直的棋盘线
        startX = XMARGIN
        startY = (y * SPACESIZE) + YMARGIN
        endX = XMARGIN + (BOARDWID * SPACESIZE)
        endY = (y * SPACESIZE) + YMARGIN
        pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startX, startY), (endX, endY))  # 按照起点和终点的左边画线

    for x in range(BOARDWID):
        for y in range(BOARDHEI):
            centerX, centerY = translateBoardToPixelCoord(x, y)
            if board[x][y] == WHITE_TILE or board[x][y] == BLACK_TILE:
                if board[x][y] == WHITE_TILE:
                    tileColor = WHITE
                else:
                    tileColor = BLACK
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerX, centerY), int(SPACESIZE / 2))
            if board[x][y] == HINT_TILE:
                pygame.draw.rect(DISPLAYSURF, HINTCOLOR, (centerX - 6, centerY - 6, 12, 12))
            if board[x][y] == RECOMMEND_TILE:
                pygame.draw.rect(DISPLAYSURF, RECOMMENDCOLOR, (centerX - 4, centerY - 4, 8, 8))

def getSpaceClicked(mouseX, mouseY):            #捕捉鼠标点击的格子
    for x in range(BOARDWID):
        for y in range(BOARDHEI):
            if  mouseX > x * SPACESIZE + XMARGIN and mouseX < (x + 1) * SPACESIZE + XMARGIN and mouseY > y * SPACESIZE + YMARGIN and mouseY < (y + 1) * SPACESIZE + YMARGIN:
                return(x, y)
    return None

def drawInfo(board, player1, player2, player1Tile, player2Tile, turn):            #在屏幕底部画出得分和谁的回合
    scores = getScoreOfBoard(board)
    if player1Tile == WHITE_TILE:
        p1 = 'White'
        p2 = 'Black'
    else:
        p1 = 'Black'
        p2 = 'White'

    scoreSurf = FONT.render("{} Score({}): {}  {} Score({}): {}  {}'s turn".format(player1, p1, scores[player1Tile], player2, p2, scores[player2Tile], turn), True, TEXTCOLOR, TEXTBGCOLOR1)
    scoreRect = scoreSurf.get_rect()
    scoreRect.bottomleft = (10, WINDOWHEI - 5)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

def resetBoard(board):
    #初始化棋盘
    for x in range(BOARDWID):
        for y in range(BOARDHEI):
            board[x][y] = EMPTY_SPACE
    board[3][3] = WHITE_TILE
    board[4][4] = WHITE_TILE
    board[3][4] = BLACK_TILE
    board[4][3] = BLACK_TILE
    # getBoardState(board)

def getNewBoard():
    #新建棋盘，棋盘由一个二维列表保存
    board = []
    for i in range(BOARDWID):
        board.append([EMPTY_SPACE] * 8)
    return board


def isValidMove(board, tile, xstart, ystart):
    #判断玩家行动是否合法，若不合法返回错误，若合法返回要翻转的棋子列表
    if board[xstart][ystart] != EMPTY_SPACE or not isOnBoard(xstart, ystart):   #点击不为空或者不在棋盘上
        return False

    board[xstart][ystart] = tile

    if tile == WHITE_TILE:
        otherTile = BLACK_TILE
    else:
        otherTile = WHITE_TILE

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1,0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:        #向每个方向依次移动3格，若出棋盘则换方向，若找到第一个相同颜色的棋子
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            if not isOnBoard(x, y):
                continue
            if board[x][y] == tile:         #等于时，代表找到，则记录路径上的棋子
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append(([x,y]))

    board[xstart][ystart] = EMPTY_SPACE
    if len(tilesToFlip) == 0:
        return False
    return tilesToFlip

def isOnBoard(x, y):
    return x >= 0 and x < BOARDWID and y >= 0 and y < BOARDHEI

def getBoardWithValidMoves(board, tile):
    #画出带提示的棋盘
    dupeBoard = copy.deepcopy(board)
    for x, y in getValidmoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    return dupeBoard

def getBoardWithRecommendMOves(board, tile):
    dupeBoard = copy.deepcopy(board)
    recommendMoves = getComputerMove(dupeBoard, tile)
    dupeBoard[recommendMoves[0]][recommendMoves[1]] = RECOMMEND_TILE
    return dupeBoard

def getBoardWithValidandRecommendMoves(board, tile):
    dupeBoard = copy.deepcopy(board)
    dupeBoard1 = copy.deepcopy(board)
    for x, y in getValidmoves(dupeBoard, tile):
        dupeBoard[x][y] = HINT_TILE
    recommendMoves = getComputerMove(dupeBoard1, tile)
    dupeBoard[recommendMoves[0]][recommendMoves[1]] = RECOMMEND_TILE
    return dupeBoard

def getValidmoves(board, tile):
    #返回所有可以走的位置
    validMoves = []     #定义位置列表
    for x in range(BOARDWID):
        for y in range(BOARDHEI):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves

def getScoreOfBoard(board):
    White_score = 0
    Black_score = 0
    for x in range(BOARDWID):
        for y in range(BOARDHEI):
            if board[x][y] == WHITE_TILE:
                White_score += 1
            if board[x][y] == BLACK_TILE:
                Black_score += 1
    return {WHITE_TILE:White_score, BLACK_TILE:Black_score}

def enterPlayerTile():
    #让玩家选择黑白，若选择白，返回[白，黑]
    textSurf = FONT.render('Do you want to be white or black?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2))

    WhiteSurf = BIGFONT.render("White", True, TEXTCOLOR, TEXTBGCOLOR1)
    WhiteRect = WhiteSurf.get_rect()
    WhiteRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 40)
    BlackSurf = BIGFONT.render("Black", True, TEXTCOLOR, TEXTBGCOLOR1)
    BlackRect = BlackSurf.get_rect()
    BlackRect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 40)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                mouseX, mouseY = event.pos
                if WhiteRect.collidepoint((mouseX, mouseY)):
                    return [WHITE_TILE, BLACK_TILE]
                elif BlackRect.collidepoint((mouseX, mouseY)):
                    return [BLACK_TILE, WHITE_TILE]
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(WhiteSurf, WhiteRect)
        DISPLAYSURF.blit(BlackSurf, BlackRect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)

def enterGameMode():
    #让玩家选择人机还是人人
    DISPLAYSURF.blit(ORIGINBGIMAGE, ORIGINBGIMAGE.get_rect())
    mode = ''
    textSurf = FONT.render('Which game mode do you want to play?', True, TEXTCOLOR, TEXTBGCOLOR1)
    textRect = textSurf.get_rect()
    textRect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2))
    PVPSurf = BIGFONT.render("P V P", True, TEXTCOLOR, TEXTBGCOLOR1)
    PVPRect = PVPSurf.get_rect()
    PVPRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 40)
    PVESurf = BIGFONT.render("P V E", True, TEXTCOLOR, TEXTBGCOLOR1)
    PVERect = PVESurf.get_rect()
    PVERect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 40)
    EVESurf = BIGFONT.render("E V E", True, TEXTCOLOR, TEXTBGCOLOR1)
    EVERect = EVESurf.get_rect()
    EVERect.center = (int(WINDOWWID / 2), int(WINDOWHEI / 2) + 70)

    while True:
        checkForQuit()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONUP:
                mouseX, mouseY = event.pos
                if PVPRect.collidepoint((mouseX, mouseY)):
                    mode = 'PVP'
                elif PVERect.collidepoint((mouseX, mouseY)):
                    mode = 'PVE'
                elif EVERect.collidepoint((mouseX, mouseY)):
                    mode = 'EVE'
        DISPLAYSURF.blit(textSurf, textRect)
        DISPLAYSURF.blit(PVPSurf, PVPRect)
        DISPLAYSURF.blit(PVESurf, PVERect)
        DISPLAYSURF.blit(EVESurf, EVERect)
        pygame.display.update()
        MAINCLOCK.tick(FPS)
        return mode


def makeMove(board, tile, xstart, ystart, realMove = False):
    #点击和反转棋子
    tilesToFlip = isValidMove(board,tile, xstart, ystart)
    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tilesToFlip, tile, (xstart, ystart))

    for x,y in tilesToFlip:
        board[x][y] = tile
    return True

def isOnCorner(x, y):
    return (x == 0 and y == 0) or (x == BOARDWID-1 and y == 0) or (x == 0 and y == BOARDHEI-1) or (x == BOARDWID-1 and y == BOARDHEI-1)

def getComputerMove(board, computerTile):
    #电脑玩家算法
    possibleMoves = getValidmoves(board, computerTile)
    random.shuffle(possibleMoves)

    for x, y in possibleMoves:
        if isOnCorner(x,y):
            return [x, y]

    bestScore = -1

    #复制一个新的棋盘，模拟所有可以走的位置，寻找分最高的位置
    for x, y in possibleMoves:
        dupeBoard = copy.deepcopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        score = getScoreOfBoard(dupeBoard)[computerTile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove

def prophet(board, tile):
    if tile == BLACK_TILE:
        othertile = WHITE_TILE
    else:
        othertile = BLACK_TILE
    possibleMoves = getValidmoves(board, tile)
    random.shuffle(possibleMoves)
    values = np.zeros((8, 8))
    for x in range(8):
        for y in range(8):
            values[x][y] = -100
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            values[x][y] = 100
        else:
            dupeboard = copy.deepcopy(board)
            scores = [0]
            if isValidMove(dupeboard, tile, x, y):
                score = len(isValidMove(dupeboard, tile, x, y))
                values[x][y] = 7 * score
            makeMove(dupeboard, tile, x, y)
            prophetpossibleMoves = getValidmoves(dupeboard, othertile)
            random.shuffle(prophetpossibleMoves)
            if not prophetpossibleMoves:
                values[x][y] = 100
            else:
                for a, b in prophetpossibleMoves:
                    if isOnCorner(a, b):
                        score = 25
                        scores.append(score)
                        break
                    else:
                        dupeboard1 = copy.deepcopy(dupeboard)

                        if isValidMove(dupeboard1, othertile, a, b):
                            score = len(isValidMove(dupeboard1, othertile, a, b))
                            scores.append(score)
                scores.sort(reverse=True)
                values[x][y] -= 7 * scores[0]

    bestvalue = 0
    bestmove = random.choice(possibleMoves)
    for x, y in possibleMoves:
        if values[x][y] >= bestvalue:
            bestvalue = values[x][y]
            bestmove = [x, y]
    return bestmove

def mctsmoves(board, tile):
    Board = nowboard()
    Board.getBoardState(board)
    if tile == BLACK_TILE:
        Board.setTile(BLACK_TILE)
    else:
        Board.setTile(WHITE_TILE)
    Board.availablemoves(board, tile)




def checkForQuit():
    for event in pygame.event.get((pygame.QUIT, pygame.KEYUP)):
        if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
            pygame.quit()
            sys.exit()

if __name__ == '__main__':
    main()


