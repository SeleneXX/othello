from board import Board
import random
m = input()
n = int(m)
win1 = 0
win2 = 0
board = Board()
for _ in range(int(m)):
    player1 = 'computer1'
    player2 = 'computer2'
    board.init_state()
    board.init_board()
    round = 0
    computer1Tile = 'BLACK_TILE'
    if computer1Tile == 'BLACK_TILE':
        computer2Tile = 'WHITE_TILE'
    else:
        computer2Tile = 'BLACK_TILE'
    turn = random.choice([player1, player2])  # 随机先后
    while True:  # 主循环
        if turn == player1:
            # 电脑玩家1回合
            if board.getValidmoves(board.boardstate, computer1Tile) == []:
                break  # 如果是电脑1回合但其不能动，游戏结束

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
            x, y = board.mctsmove(n_play_out)
            board.makeMove(board.boardstate, computer1Tile, x, y)
            if board.getValidmoves(board.boardstate, computer2Tile) != []:
                turn = player2  # 回合结束，如果电脑玩家2能行动，则切换电脑玩家2回合
            round += 1
        elif turn == player2:
            # 电脑玩家2回合
            if board.getValidmoves(board.boardstate, computer2Tile) == []:
                break  # 如果是电脑2回合但其不能动，游戏结束

            x, y = board.prophet(board.boardstate, computer2Tile)
            board.makeMove(board.boardstate, computer2Tile, x, y)
            if board.getValidmoves(board.boardstate, computer1Tile) != []:
                turn = player1  # 回合结束，如果电脑玩家1能行动，则切换电脑玩家1回合

    scores = board.getScoreOfBoard()  # 显示分数
    if scores[computer1Tile] > scores[computer2Tile]:  # 判断游戏结果
        win1 += 1
    elif scores[computer1Tile] < scores[computer2Tile]:
        win2 += 1
    print('1:', win1, '2:', win2)
print("winrate of mcts = {:.2%}".format(win1 / n))