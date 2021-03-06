import random, sys, pygame, time, copy
import numpy as np
import  mcts_pure
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
XMARGIN = int((WINDOWWID - (BOARDWID * SPACESIZE)) / 2)
YMARGIN = int((WINDOWHEI - (BOARDHEI*SPACESIZE)) / 2)

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

global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE, ORIGINBGIMAGE

class Board(object):
    def __init__(self):
        self.width = BOARDWID
        self.height = BOARDHEI
        self.state= []
        self.available = []
        self.tile = {}
        self.boardstate = []
        self.players = [1, 2]
        self.current_player = 1
        self.winner = -1

    def init_board(self, start_player = 0, start_tile = BLACK_TILE):
        self.init_state()
        if start_tile == BLACK_TILE:
            other_tile = WHITE_TILE
        else:
            other_tile = BLACK_TILE
        self.current_player = self.players[start_player]
        if start_player == 0:
            follow_player = 1
        elif start_player == 1:
            follow_player = 0
        self.tile = {self.current_player: start_tile, self.players[follow_player]: other_tile}
        self.states = []
        self.last_move = -1
        self.winner = -1
        for x in range(self.width):
            for y in range(self.height):
                self.boardstate[x][y] = EMPTY_SPACE
        self.boardstate[3][3] = WHITE_TILE
        self.boardstate[4][4] = WHITE_TILE
        self.boardstate[3][4] = BLACK_TILE
        self.boardstate[4][3] = BLACK_TILE


    def init_state(self):
        self.boardstate = []
        for i in range(BOARDWID):
            self.boardstate.append([EMPTY_SPACE] * 8)

    def isValidMove(self, boardstate, tile, xstart, ystart):
        # 判断玩家行动是否合法，若不合法返回错误，若合法返回要翻转的棋子列表
        if boardstate[xstart][ystart] != EMPTY_SPACE or not self.isOnBoard(xstart, ystart):  # 点击不为空或者不在棋盘上
            return False

        boardstate[xstart][ystart] = tile

        if tile == WHITE_TILE:
            otherTile = BLACK_TILE
        else:
            otherTile = WHITE_TILE

        tilesToFlip = []
        for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
            x, y = xstart, ystart
            x += xdirection
            y += ydirection
            if self.isOnBoard(x, y) and boardstate[x][y] == otherTile:  # 向每个方向依次移动3格，若出棋盘则换方向，若找到第一个相同颜色的棋子
                x += xdirection
                y += ydirection
                if not self.isOnBoard(x, y):
                    continue
                while boardstate[x][y] == otherTile:
                    x += xdirection
                    y += ydirection
                    if not self.isOnBoard(x, y):
                        break
                if not self.isOnBoard(x, y):
                    continue
                if boardstate[x][y] == tile:  # 等于时，代表找到，则记录路径上的棋子
                    while True:
                        x -= xdirection
                        y -= ydirection
                        if x == xstart and y == ystart:
                            break
                        tilesToFlip.append(([x, y]))

        boardstate[xstart][ystart] = EMPTY_SPACE
        if len(tilesToFlip) == 0:
            return False
        return tilesToFlip

    def isOnBoard(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def isOnCorner(self, x, y):
        return (x == 0 and y == 0) or (x == BOARDWID - 1 and y == 0) or (x == 0 and y == BOARDHEI - 1) or (
                    x == BOARDWID - 1 and y == BOARDHEI - 1)

    def getValidmoves(self, boardstate, tile):
        # 返回所有可以走的位置
        self.available = []  # 定义位置列表
        for x in range(self.width):
            for y in range(self.height):
                if self.isValidMove(boardstate, tile, x, y) != False:
                    self.available.append((x, y))
        return self.available

    def get_move_list(self, availables):
        possible_move_list = []
        for x in availables:
            possible_move_list.append(self.location_to_move(x[0], x[1]))
        return list(set(possible_move_list))

    def getScoreOfBoard(self, boardstate = 0):
        if boardstate == 0:
            boardstate = self.boardstate
        White_score = 0
        Black_score = 0
        for x in range(self.width):
            for y in range(self.height):
                if boardstate[x][y] == WHITE_TILE:
                    White_score += 1
                if boardstate[x][y] == BLACK_TILE:
                    Black_score += 1
        return {WHITE_TILE: White_score, BLACK_TILE: Black_score}

    def get_current_player(self):
        return self.current_player

    def get_opponent_player(self):
        return 2 if self.current_player == 1 else 1

    def move_to_location(self, move: int) -> (int, int):
        x = move // self.width
        y = move % self.width
        return x, y

    def location_to_move(self, x: int, y: int) -> int:
        return ((x * self.width) + y)

    def makeMove(self, board, tile, xstart, ystart):
        # 点击和反转棋子
        move = (xstart, ystart)
        if tile == BLACK_TILE:
            othertile = WHITE_TILE
        else:
            othertile =BLACK_TILE
        self.lastmove = move
        tilesToFlip = self.isValidMove(board, tile, xstart, ystart)
        if tilesToFlip == False:
            return 0
        board[xstart][ystart] = tile
        for x, y in tilesToFlip:
            board[x][y] = tile

        self.states.append((xstart, ystart))
        self.current_player = (
            self.players[0] if self.current_player == self.players[1]
            else self.players[1]
        )

        self.available = self.getValidmoves(self.boardstate, othertile)
        return tilesToFlip, tile, xstart, ystart

    def getBoardState(self, boardstate = 0):
        if boardstate == 0:
            boardstate = self.boardstate
        currentstate = np.zeros((4, self.width, self.height))
        for x in range(self.width):
            for y in range(self.height):
                if boardstate[x][y] == self.tile[1]:
                    currentstate[0][x][y] = 1
                elif boardstate[x][y] == self.tile[2]:
                    currentstate[1][x][y] = 1
        if len(self.states) > 0:
            x, y = self.states[len(self.states) - 1]
            currentstate[2][x][y] = 1.0
        if self.get_current_player == 1:
            currentstate[3][:, :] = 1.0  # indicate the colour to play
        return currentstate[:, ::-1, :]

    def has_a_winner(self):
        if len(self.getValidmoves(self.boardstate, self.tile[self.get_current_player()])):
            return -1
        else:
            if len(self.getValidmoves(self.boardstate, self.tile[self.get_opponent_player()])):
                return -1
            else:
                x = self.getScoreOfBoard(self.boardstate)[self.tile[1]]
                y = self.getScoreOfBoard(self.boardstate)[self.tile[2]]
                self.winner = 1 if x > y else 2 if x < y else 0
                return self.winner


    def getNewBoard(self, start_player, start_tile):
        # 新建棋盘，棋盘由一个二维列表保存
        self.init_board(start_player, start_tile)
        return self.boardstate

    def getBoardWithValidMoves(self, boardstate, tile):
        # 画出带提示的棋盘
        dupeBoard = copy.deepcopy(boardstate)
        for x, y in self.getValidmoves(dupeBoard, tile):
            dupeBoard[x][y] = HINT_TILE
        return dupeBoard

    def getBoardWithRecommendMOves(self, boardstate, tile):
        dupeBoard = copy.deepcopy(boardstate)
        recommendMoves = self.prophet(dupeBoard, tile)
        dupeBoard[recommendMoves[0]][recommendMoves[1]] = RECOMMEND_TILE
        return dupeBoard

    def getBoardWithValidandRecommendMoves(self, boardstate, tile):
        dupeBoard = copy.deepcopy(boardstate)
        dupeBoard1 = copy.deepcopy(boardstate)
        for x, y in self.getValidmoves(dupeBoard, tile):
            dupeBoard[x][y] = HINT_TILE
        recommendMoves = self.getComputerMove(dupeBoard1, tile)
        dupeBoard[recommendMoves[0]][recommendMoves[1]] = RECOMMEND_TILE
        return dupeBoard

    def getComputerMove(self, boardstate, computerTile):
        # 电脑玩家算法
        possibleMoves = self.getValidmoves(boardstate, computerTile)
        random.shuffle(possibleMoves)

        for x, y in possibleMoves:
            if self.isOnCorner(x, y):
                return [x, y]

        bestScore = -1

        # 复制一个新的棋盘，模拟所有可以走的位置，寻找分最高的位置
        for x, y in possibleMoves:
            dupeBoard = copy.deepcopy(boardstate)
            self.makeMove(dupeBoard, computerTile, x, y)
            score = self.getScoreOfBoard(dupeBoard)[computerTile]
            if score > bestScore:
                bestMove = [x, y]
                bestScore = score
        return bestMove

    def prophet(self, boardstate, tile):
        if tile == BLACK_TILE:
            othertile = WHITE_TILE
        else:
            othertile = BLACK_TILE
        possibleMoves = self.getValidmoves(boardstate, tile)
        random.shuffle(possibleMoves)
        values = np.zeros((8, 8))
        for x in range(8):
            for y in range(8):
                values[x][y] = -100
        for x, y in possibleMoves:
            if self.isOnCorner(x, y):
                values[x][y] = 100
            else:
                dupeboard = copy.deepcopy(boardstate)
                scores = [0]
                if self.isValidMove(dupeboard, tile, x, y):
                    score = len(self.isValidMove(dupeboard, tile, x, y))
                    values[x][y] = 7 * score
                self.makeMove(dupeboard, tile, x, y)
                prophetpossibleMoves = self.getValidmoves(dupeboard, othertile)
                random.shuffle(prophetpossibleMoves)
                if not prophetpossibleMoves:
                    values[x][y] = 100
                else:
                    for a, b in prophetpossibleMoves:
                        if self.isOnCorner(a, b):
                            score = 50
                            scores.append(score)
                            break
                        else:
                            dupeboard1 = copy.deepcopy(dupeboard)

                            if self.isValidMove(dupeboard1, othertile, a, b):
                                score = len(self.isValidMove(dupeboard1, othertile, a, b))
                                scores.append(score)
                    scores.sort(reverse=True)
                    values[x][y] -= 7 * scores[0]

        bestvalue = -100
        bestmove = random.choice(possibleMoves)
        for x, y in possibleMoves:
            if values[x][y] >= bestvalue:
                bestvalue = values[x][y]
                bestmove = [x, y]
        return bestmove

    def  game_end(self):
        winner = self.has_a_winner()
        if winner != -1:
            return True, winner
        elif winner == 0:
            return True, -1
        return False, -1

class Game(object):

    def __init__(self, board):
        pygame.init()
        self.board = board




    def animateTileChange(self, tulesToFlip, tileColor, additionalTile):
        if tileColor == WHITE_TILE:
            additionalTileColor = WHITE
        else:
            additionalTileColor = BLACK
        additionalTileX, additionalTileY = self.translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
        pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2))
        pygame.display.update()

        for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2)):  # 点击棋子后颜色渐变，黑到白，白到黑
            if rgbValues > 255:
                rgbValues = 255
            elif rgbValues < 0:
                rgbValues = 0
            if tileColor == WHITE_TILE:
                color = tuple([rgbValues] * 3)
            elif tileColor == BLACK_TILE:
                color = tuple([255 - rgbValues] * 3)

            for x, y in tulesToFlip:
                centerX, centerY = self.translateBoardToPixelCoord(x, y)
                pygame.draw.circle(DISPLAYSURF, color, (centerX, centerY), int(SPACESIZE / 2))
            pygame.display.update()
            MAINCLOCK.tick(FPS)
            self.checkForQuit()

    def drawBoard(self, board):
        DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())  # 画背景
        for x in range(BOARDWID + 1):  # 循环画出水平的棋盘线
            startX = (x * SPACESIZE) + XMARGIN
            startY = YMARGIN
            endX = (x * SPACESIZE) + XMARGIN
            endY = YMARGIN + (BOARDHEI * SPACESIZE)
            pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startX, startY), (endX, endY))  # 按照起点和终点的左边画线

        for y in range(BOARDHEI + 1):  # 循环画出垂直的棋盘线
            startX = XMARGIN
            startY = (y * SPACESIZE) + YMARGIN
            endX = XMARGIN + (BOARDWID * SPACESIZE)
            endY = (y * SPACESIZE) + YMARGIN
            pygame.draw.line(DISPLAYSURF, GRIDLINECOLOR, (startX, startY), (endX, endY))  # 按照起点和终点的左边画线

        for x in range(BOARDWID):
            for y in range(BOARDHEI):
                centerX, centerY = self.translateBoardToPixelCoord(x, y)
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

    def translateBoardToPixelCoord(self, x, y):  # 根据棋盘坐标转化出对应的像素坐标
        return XMARGIN + x * SPACESIZE + int(SPACESIZE / 2), YMARGIN + y * SPACESIZE + int(SPACESIZE / 2)

    def animateTileChange(self, tulesToFlip, tileColor, additionalTile):
        if tileColor == WHITE_TILE:
            additionalTileColor = WHITE
        else:
            additionalTileColor = BLACK
        additionalTileX, additionalTileY = self.translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
        pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(SPACESIZE / 2))
        pygame.display.update()

        for rgbValues in range(0, 255, int(ANIMATIONSPEED * 2)):  # 点击棋子后颜色渐变，黑到白，白到黑
            if rgbValues > 255:
                rgbValues = 255
            elif rgbValues < 0:
                rgbValues = 0
            if tileColor == WHITE_TILE:
                color = tuple([rgbValues] * 3)
            elif tileColor == BLACK_TILE:
                color = tuple([255 - rgbValues] * 3)

            for x, y in tulesToFlip:
                centerX, centerY = self.translateBoardToPixelCoord(x, y)
                pygame.draw.circle(DISPLAYSURF, color, (centerX, centerY), int(SPACESIZE / 2))
            pygame.display.update()
            MAINCLOCK.tick(FPS)
            self.checkForQuit()

    def getSpaceClicked(self, mouseX, mouseY):  # 捕捉鼠标点击的格子
        for x in range(BOARDWID):
            for y in range(BOARDHEI):
                if mouseX > x * SPACESIZE + XMARGIN and mouseX < (
                        x + 1) * SPACESIZE + XMARGIN and mouseY > y * SPACESIZE + YMARGIN and mouseY < (
                        y + 1) * SPACESIZE + YMARGIN:
                    return (x, y)
        return None

    def drawInfo(self, board, player1, player2, player1Tile, player2Tile, turn):  # 在屏幕底部画出得分和谁的回合
        scores = self.board.getScoreOfBoard()
        if player1Tile == WHITE_TILE:
            p1 = 'White'
            p2 = 'Black'
        else:
            p1 = 'Black'
            p2 = 'White'

        scoreSurf = FONT.render(
            "{} Score({}): {}  {} Score({}): {}  {}'s turn".format(player1, p1, scores[player1Tile], player2, p2,
                                                                   scores[player2Tile], turn), True, TEXTCOLOR,
            TEXTBGCOLOR1)
        scoreRect = scoreSurf.get_rect()
        scoreRect.bottomleft = (10, WINDOWHEI - 5)
        DISPLAYSURF.blit(scoreSurf, scoreRect)

    def enterPlayerTile(self):
        # 让玩家选择黑白，若选择白，返回[白，黑]
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
            self.checkForQuit()
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

    def enterGameMode(self):
        # 让玩家选择人机还是人人
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
            self.checkForQuit()
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

    def makeMove(self, tilesToFlip, tile, xstart, ystart):
        # 点击和反转棋子
            self.animateTileChange(tilesToFlip, tile, (xstart, ystart))

    def checkForQuit(self):
        for event in pygame.event.get((pygame.QUIT, pygame.KEYUP)):
            if event.type == pygame.QUIT or (event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
    def mctsmove(self, n_play_out):
        print(self.board.tile[self.board.get_current_player()])
        print(self.board.getValidmoves(self.board.boardstate, self.board.tile[self.board.get_current_player()]))
        if len(self.board.getValidmoves(self.board.boardstate, self.board.tile[self.board.get_current_player()])) > 1:
            mctsplayer = mcts_pure.MCTSPlayer(c_puct=5, n_playout=n_play_out)

            move = mctsplayer.get_action(self.board)
            return self.board.move_to_location(move)
        else:
            return self.board.getValidmoves(self.board.boardstate, self.board.tile[self.board.get_current_player()])[0]


    def runGame(self):
        showHints = False
        showRecommend = False
        mode = self.enterGameMode()
        if mode == 'PVP':
            self.board.init_state()
            player1 = 0
            player2 = 1
            self.drawBoard(self.board.boardstate)
            player1Tile, player2Tile = self.enterPlayerTile()
            turn = random.choice([player1, player2])  # 随机先后
            if turn == player1:
                start__tile = player1Tile
            elif turn == player2:
                start__tile = player2Tile
            self.board.init_board(start_player = turn, start_tile = start__tile)
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
                    if self.board.getValidmoves(self.board.boardstate, player1Tile) == []:
                        break  # 如果是玩家1回合但其不能移动，游戏结束
                    movexy = None
                    while movexy == None:
                        # 画出可落子范围和推荐落子位置
                        if showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithValidandRecommendMoves(self.board.boardstate, player1Tile)
                        elif showHints and not showRecommend:
                            boardToDraw = self.board.getBoardWithValidMoves(self.board.boardstate, player1Tile)
                        elif not showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithRecommendMOves(self.board.boardstate, player1Tile)
                        else:
                            boardToDraw = self.board.boardstate

                        self.checkForQuit()

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

                                movexy = self.getSpaceClicked(mouseX, mouseY)
                                if movexy != None and not self.board.isValidMove(self.board.boardstate, player1Tile, movexy[0], movexy[1]):
                                    # 判断 点击位置是否合法
                                    movexy = None

                        self.drawBoard(boardToDraw)  # 画棋盘
                        self.drawInfo(boardToDraw, player1, player2, player1Tile, player2Tile, turn)  # 画底部提示信息

                        # 画三个按钮
                        DISPLAYSURF.blit(newGameSurf, newgameRect)
                        DISPLAYSURF.blit(hintsSurf, hintsRect)
                        DISPLAYSURF.blit(recommendSurf, recommendRect)

                        MAINCLOCK.tick(FPS)
                        pygame.display.update()

                    a = self.board.makeMove(self.board.boardstate, player1Tile, movexy[0], movexy[1])
                    if a != False:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)

                    self.board.getBoardState()
                    if self.board.getValidmoves(self.board.boardstate, player2Tile) != []:
                        turn = player2  # 回合结束，如果玩家2能行动，则切换电脑玩家回合

                elif turn == player2:
                    # 玩家2回合
                    if self.board.getValidmoves(self.board.boardstate, player2Tile) == []:
                        break  # 如果是玩家2回合但其不能移动，游戏结束
                    movexy = None
                    while movexy == None:

                        # 画出可落子范围和推荐落子位置
                        if showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithValidandRecommendMoves(self.board.boardstate, player2Tile)
                        elif showHints and not showRecommend:
                            boardToDraw = self.board.getBoardWithValidMoves(self.board.boardstate, player2Tile)
                        elif not showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithRecommendMOves(self.board.boardstate, player2Tile)
                        else:
                            boardToDraw = self.board.boardstate

                        self.checkForQuit()

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

                                movexy = self.getSpaceClicked(mouseX, mouseY)
                                if movexy != None and not self.board.isValidMove(self.board.boardstate, player2Tile, movexy[0], movexy[1]):
                                    # 判断 点击位置是否合法
                                    movexy = None

                        self.drawBoard(boardToDraw)  # 画棋盘
                        self.drawInfo(boardToDraw, player1, player2, player1Tile, player2Tile, turn)  # 画底部提示信息

                        # 画三个按钮
                        DISPLAYSURF.blit(newGameSurf, newgameRect)
                        DISPLAYSURF.blit(hintsSurf, hintsRect)
                        DISPLAYSURF.blit(recommendSurf, recommendRect)

                        MAINCLOCK.tick(FPS)
                        pygame.display.update()
                    a = self.board.makeMove(self.board.boardstate, player2Tile, movexy[0], movexy[1])
                    if a != False:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)
                    self.board.getBoardState()
                    if self.board.getValidmoves(self.board.boardstate, player1Tile) != []:
                        turn = player1  # 回合结束，如果玩家1能行动，则切换玩家1回合

            self.drawBoard(self.board.boardstate)
            scores = self.board.getScoreOfBoard()  # 显示分数

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
                self.checkForQuit()
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
            self.board.init_state()
            player1 = 0
            player2 = 1
            self.drawBoard(self.board.boardstate)
            playerTile, computerTile = self.enterPlayerTile()
            turn = random.choice([player1, player2])  # 随机先后
            if turn == player1:
                start__tile = playerTile
            elif turn == player2:
                start__tile = computerTile
            self.board.init_board(start_player=turn, start_tile=start__tile)
            newGameSurf = FONT.render('New game', True, TEXTCOLOR, TEXTBGCOLOR2)  # 右上角功能
            newgameRect = newGameSurf.get_rect()
            newgameRect.topright = (WINDOWWID - 8, 10)
            hintsSurf = FONT.render('Hints', True, TEXTCOLOR, TEXTBGCOLOR2)
            hintsRect = hintsSurf.get_rect()
            hintsRect.topright = (WINDOWWID - 8, 40)
            recommendSurf = FONT.render('Recommend', True, TEXTCOLOR, TEXTBGCOLOR2)
            recommendRect = recommendSurf.get_rect()
            recommendRect.topright = (WINDOWWID - 8, 70)
            round = 0
            while True:  # 主循环
                if turn == player1:
                    # 玩家回合
                    self.board.current_player = 1
                    if self.board.getValidmoves(self.board.boardstate, playerTile) == []:
                        break  # 如果是玩家回合但其不能移动，游戏结束
                    movexy = None
                    while movexy == None:

                        # 画出可落子范围和推荐落子位置
                        if showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithValidandRecommendMoves(self.board.boardstate, playerTile)
                        elif showHints and not showRecommend:
                            boardToDraw = self.board.getBoardWithValidMoves(self.board.boardstate, playerTile)
                        elif not showHints and showRecommend:
                            boardToDraw = self.board.getBoardWithRecommendMOves(self.board.boardstate, playerTile)
                        else:
                            boardToDraw = self.board.boardstate

                        self.checkForQuit()

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

                                movexy = self.getSpaceClicked(mouseX, mouseY)
                                if movexy != None and not self.board.isValidMove(self.board.boardstate, playerTile, movexy[0], movexy[1]):
                                    # 判断 点击位置是否合法
                                    movexy = None

                        self.drawBoard(boardToDraw)  # 画棋盘
                        self.drawInfo(self.board.boardstate, player1, player2, playerTile, computerTile, turn)  # 画底部提示信息

                        # 画三个按钮
                        DISPLAYSURF.blit(newGameSurf, newgameRect)
                        DISPLAYSURF.blit(hintsSurf, hintsRect)
                        DISPLAYSURF.blit(recommendSurf, recommendRect)

                        MAINCLOCK.tick(FPS)
                        pygame.display.update()

                    a = self.board.makeMove(self.board.boardstate, playerTile, movexy[0], movexy[1])
                    if a != False:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)

                    self.board.getBoardState()
                    if self.board.getValidmoves(self.board.boardstate, computerTile) != []:
                        turn = player2  # 回合结束，如果电脑玩家能行动，则切换电脑玩家回合

                elif turn == player2:
                    # 电脑玩家回合
                    self.board.current_player = 1
                    if self.board.getValidmoves(self.board.boardstate, computerTile) == []:
                        break  # 如果是电脑回合但其不能动，游戏结束

                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True  # 新游戏
                    self.board.current_player = 2
                    self.drawBoard(self.board.boardstate)
                    self.drawInfo(self.board.boardstate, player1, player2, playerTile, computerTile, turn)

                    DISPLAYSURF.blit(newGameSurf, newgameRect)  # 画三个按钮
                    DISPLAYSURF.blit(hintsSurf, hintsRect)
                    DISPLAYSURF.blit(recommendSurf, recommendRect)
                    pauseUntil = time.time() + random.randint(5, 15) * 0.1  # 模拟电脑玩家思考时间，长度随机
                    while time.time() < pauseUntil:
                        pygame.display.update()

                    if round <= 2:
                        n_play_out = 100
                    elif round <= 6:
                        n_play_out = 400
                    elif round <= 10:
                        n_play_out = 800
                    elif round <= 15:
                        n_play_out = 1100
                    elif round <= 20:
                        n_play_out = 1400
                    elif round <= 25:
                        n_play_out = 1200
                    else:
                        n_play_out = 1000
                    x, y = self.mctsmove(n_play_out)
                    a = self.board.makeMove(self.board.boardstate, computerTile, x, y)
                    if a != 0:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)
                    self.board.getBoardState()
                    if self.board.getValidmoves(self.board.boardstate, playerTile) != []:
                        turn = player1  # 回合结束，如果玩家能行动，则切换玩家回合
                    round += 1
            self.drawBoard(self.board.boardstate)
            scores = self.board.getScoreOfBoard()  # 显示分数

            if scores[playerTile] > scores[computerTile]:  # 判断游戏结果
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

            yesSurf = BIGFONT.render('Yes', True, TEXTCOLOR, TEXTBGCOLOR1)
            yesRect = yesSurf.get_rect()
            yesRect.center = (int(WINDOWWID / 2) - 60, int(WINDOWHEI / 2) + 90)

            noSurf = BIGFONT.render('No', True, TEXTCOLOR, TEXTBGCOLOR1)
            noRect = yesSurf.get_rect()
            noRect.center = (int(WINDOWWID / 2) + 60, int(WINDOWHEI / 2) + 90)

            while True:
                self.checkForQuit()
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
            round = 0
            self.board.init_state()
            player1 = 0
            player2 = 1
            self.drawBoard(self.board.boardstate)
            computer1Tile, computer2Tile = self.enterPlayerTile()
            turn = random.choice([player1, player2])  # 随机先后
            if turn == player1:
                start__tile = computer1Tile
            elif turn == player2:
                start__tile = computer2Tile
            self.board.init_board(start_player=turn, start_tile=start__tile)
            newGameSurf = FONT.render('New game', True, TEXTCOLOR, TEXTBGCOLOR2)  # 右上角功能
            newgameRect = newGameSurf.get_rect()
            newgameRect.topright = (WINDOWWID - 8, 10)

            while True:  # 主循环
                if turn == player1:
                    # 电脑玩家1回合
                    if self.board.getValidmoves(self.board.boardstate, computer1Tile) == []:
                        break  # 如果是电脑1回合但其不能动，游戏结束
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True  # 新游戏

                    self.drawBoard(self.board.boardstate)
                    self.drawInfo(self.board.boardstate, player1, player2, computer1Tile, computer2Tile, turn)
                    DISPLAYSURF.blit(newGameSurf, newgameRect)
                    pauseUntil = time.time() + random.randint(5, 15) * 0.1  # 模拟电脑玩家思考时间，长度随机
                    while time.time() < pauseUntil:
                        pygame.display.update()
                    print(computer1Tile)
                    self.board.current_player = 1
                    print(self.board.getValidmoves(self.board.boardstate, computer1Tile))
                    if round <= 1:
                        n_play_out = 100
                    elif round <= 5:
                        n_play_out = 600
                    elif round <= 10:
                        n_play_out = 1500
                    elif round <= 15:
                        n_play_out = 2000
                    elif round <= 20:
                        n_play_out = 2500
                    elif round <= 25:
                        n_play_out = 2000
                    else:
                        n_play_out = 1000
                    x, y = self.mctsmove(n_play_out)
                    a = self.board.makeMove(self.board.boardstate, computer1Tile, x, y)
                    if a != False:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)
                    if self.board.getValidmoves(self.board.boardstate, computer2Tile) != []:
                        turn = player2  # 回合结束，如果电脑玩家2能行动，则切换电脑玩家2回合
                    round += 1
                elif turn == player2:
                    # 电脑玩家2回合
                    if self.board.getValidmoves(self.board.boardstate, computer2Tile) == []:
                        break  # 如果是电脑2回合但其不能动，游戏结束

                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONUP:
                            mouseX, mouseY = event.pos
                            if newgameRect.collidepoint((mouseX, mouseY)):
                                return True  # 新游戏
                    self.drawBoard(self.board.boardstate)
                    self.drawInfo(self.board.boardstate, player1, player2, computer1Tile, computer2Tile, turn)
                    DISPLAYSURF.blit(newGameSurf, newgameRect)

                    pauseUntil = time.time() + random.randint(5, 15) * 0.1  # 模拟电脑玩家思考时间，长度随机
                    while time.time() < pauseUntil:
                        pygame.display.update()

                    x, y = self.board.prophet(self.board.boardstate, computer2Tile)
                    a = self.board.makeMove(self.board.boardstate, computer2Tile, x, y)
                    if a != 0:
                        tilestoflip, tile, x, y = a
                        self.makeMove(tilestoflip, tile, x, y)
                    if self.board.getValidmoves(self.board.boardstate, computer1Tile) != []:
                        turn = player1  # 回合结束，如果电脑玩家1能行动，则切换电脑玩家1回合

            self.drawBoard(self.board.boardstate)
            scores = self.board.getScoreOfBoard()  # 显示分数

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
                self.checkForQuit()
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

    def start_self_play(self, player, temp = 1e-3):
        self.board.init_board()
        states, mcts_probs, current_player = [], [], []
        while self.board.winner == -1:
            move, move_probs = player.get_action(self.board, temp = temp)
            states.append(self.board.getBoardState())
            mcts_probs.append(move_probs)
            current_player.append(self.board.get_current_player())

            x, y = self.board.move_to_location(move)
            self.board.makeMove(self.board.boardstate, self.tile[self.board.get_current_player()], x, y)
            winner = self.board.has_a_winner()
            if winner != -1:
                winners_z = np.zeros(len(current_player))
                if winner != -1:
                    winners_z[np.array(current_player) == winner] = 1.0
                    winners_z[np.array(current_player) != winner] = -1.0
                player.reset_player()
                return zip(states, mcts_probs, winners_z)


pygame.init()
global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE, ORIGINBGIMAGE
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



