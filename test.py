from main import *
m = input()
n = int(m)
win1 = 0
win2 = 0
for _ in range(int(m)):
    player1 = 'computer1'
    player2 = 'computer2'
    mainBoard = getNewBoard()
    resetBoard(mainBoard)
    computer1Tile = BLACK_TILE
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


            x, y = getComputerMove(mainBoard, computer1Tile)
            makeMove(mainBoard, computer1Tile, x, y)
            if getValidmoves(mainBoard, computer2Tile) != []:
                turn = player2  # 回合结束，如果电脑玩家1能行动，则切换电脑玩家1回合

        elif turn == player2:
            # 电脑玩家2回合
            if getValidmoves(mainBoard, computer2Tile) == []:
                break  # 如果是电脑2回合但其不能动，游戏结束

            x, y = prophet(mainBoard, computer2Tile)
            makeMove(mainBoard, computer2Tile, x, y)
            if getValidmoves(mainBoard, computer1Tile) != []:
                turn = player1

    scores = getScoreOfBoard(mainBoard)  # 显示分数
    if scores[computer1Tile] > scores[computer2Tile]:  # 判断游戏结果
        win1 += 1
    elif scores[computer1Tile] < scores[computer2Tile]:
        win2 += 1
    print(win1, win2)
print("winrate of prophet = {:.2%}".format(win2 / n))