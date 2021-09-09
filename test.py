import random
from itertools import permutations



class Mahjong(object):
    def __init__(self):
        self.count_tiles = 70 #ツモれる牌数
        self.dora_passive = [Red_Characters_5(5), Red_Circles_5(5), Red_Bamboo_5(5)] #元々ドラであるもの
        self.dora_active = [] #後から追加されるドラ. 仮に赤ドラをドラとして引いてしまっても, ここに追加すればちゃんと盤面からいなくなる.
        self.is_finished = False
        self.winner = None #self.turnでも勝者は管理できるが, 流局が判定し辛い


    def run(self):
        
        #プレイヤー4人の盤面と残り牌を設定
        self.set_tiles()
        
        #親が最初にプレイ
        self.turn = -1 #mod4で手番を管理したい



        while True:
            self.print_all()
            #誰のターン?
            player = self.get_current_player()

            #ツモって門前清自摸和 or ツモって切る or ツモって明槓
            #ツモったらfinish変数とwinner変数を変更
            player.play(self)

            self.turn = player.get_wind()


            #ツモ和了り用
            if self.is_finished:
                break

            #他の人がロンできる? 
            #ロンできたらwinner変数を変更
            self.others_ron()

            if self.is_finished:
                break

            #他の人がポン, チー, カンができる?
            #3人ずつ, 何か操作するかを入力させ, 入力結果が合わなかったら選択し直しさせたい
            self.others_play()
            print()

            if self.count_tiles == 0:
                berak

            if self.is_finished:
                break


        #勝者, 役を出力
        self.print_result()

    def print_result(self):
        if self.count_tiles == 0:
            print("流局です")
        else:
            print(self.player[self.winner], "が勝利しました!")

    def print_all(self):
        for i in range(4):
            self.player[i].print_hand()
        print()
        for i in range(4):
            print(self.player[0], "の捨て牌:", *self.player[i].discarded_tiles)
        print()
            
    def others_ron(self):
        #他のplayerにロンの選択肢を与える
        #ロンしたらself.winnerを書き換えて終了
        for i in range(1, 4):
            #他playerの3人
            player = self.player[(self.turn+i)%4]
            if self.player[self.turn].discarded_tiles:
                player.ron(self.player[self.turn].discarded_tiles[-1], self)
                if self.is_finished:
                    break


    def others_play(self):
        #他のplayerにポン, チー, カンの選択を与えたい
        for i in range(1, 4):
            player = self.player[(self.turn+i)%4] #他の3人を順番に
            player.print_hand()
            discarded_tile = self.player[self.turn].discarded_tiles[-1] #最新の捨て牌

            #ポン, チー, カンの選択を与える. できるかどうかは入力の時点では関係ない
            player.play_for_waiting(self, self.player[self.turn])
            if player.did_act:
                self.turn = player.wind
                player.did_act = False
                self.others_play() #鳴きが発生し, 捨て牌が新たに出た時点でもう一度
                break
            

    def get_current_player(self):
        self.turn = (self.turn + 1)%4

        if self.turn == 0:
            return self.player[0]

        if self.turn == 1:
            return self.player[1]

        if self.turn == 2:
            return self.player[2]

        if self.turn == 3:
            return self.player[3]


    
    def set_tiles(self):
        self.rest_of_tiles = []
        self.discarded_tiles = []
        self.player = []

        self.rest_of_tiles = []

        #全牌を格納
        for i in range(1, 10):
            for j in range(4):
                if i != 5:
                    self.rest_of_tiles.append(Characters(i))
                    self.rest_of_tiles.append(Circles(i))
                    self.rest_of_tiles.append(Bamboo(i))
                else:
                    if j == 0:
                        self.rest_of_tiles.append(Red_Characters_5(i))
                        self.rest_of_tiles.append(Red_Circles_5(i))
                        self.rest_of_tiles.append(Red_Bamboo_5(i))
                    else:
                        self.rest_of_tiles.append(Characters(i))
                        self.rest_of_tiles.append(Circles(i))
                        self.rest_of_tiles.append(Bamboo(i))
        for i in range(4):
            for j in range(4):
                self.rest_of_tiles.append(Winds(j))
                if j != 3:
                    self.rest_of_tiles.append(Dragons(j))
        
        #プレイヤー設定
        for i in range(4):
            self.player.append(Player(i))
        #牌を配る
        #current_tilesから牌をランダムで引っこ抜く
        for i in range(4):
            for _ in range(13):
                self.player[i].draw(self.rest_of_tiles)
            self.player[i].hand.sort()


        #for i in range(4):
            #self.player[i].print_hand()

        self.dora_active.append(self.rest_of_tiles.pop(random.randrange(len(self.rest_of_tiles))))
        print("ドラは", *self.dora_active)
        print()


class Player(object):
    def __init__(self, wind):
        self.hand = [] #自分の牌
        self.claimed = [] #鳴いた牌
        self.discarded_tiles = [] #捨て牌 フリテンor鳴き用
        self.wind = wind #東:0, 南:1, 西:2, 北:3
        self.is_call_done = False #鳴いたかどうか
        self.count_call = 0 #何回鳴いたか
        self.is_pung_done = False #ポンしたかどうか 加槓が実装しやすいため
        self.is_riichi = False #立直のツモ切り用
        self.is_tenpai = False #テンパイ判定
        self.doubles = 0 #飜数
        self.did_act = False #他家が牌を捨てた際に, 鳴いたかどうかの判定. ターン更新のときだけTrueにする.

        self.pung_done = False
        self.chow_done = False
        self.kong_done = False

    def __str__(self):
        return "player" + str(self.wind)

    def input_index(self, message):
        #文字列とか入力されてエラー起こしたり, リストの長さより大きい数字入れられてエラー起こしたりしないように
        while True:
            value = input(message)
            try:
                index = int(value)
                #リストでIndexErrorを起こさないように
                assert 1 <= index <= len(self.hand)
                return index

            except:
                print("正しく入力してください")
                print()

    def print_hand(self):
        print(self, ": ", end="")
        for i in range(len(self.hand)):
            print(self.hand[i], end="")
        print(" ", end="")
        for i in range(len(self.claimed)):
            for j in range(len(self.claimed[i])):
                print(self.claimed[i][j], end="")

        print()

        print("           ", end="")
        for i in range(1, len(self.hand)+1):
            print(str(i).zfill(2), end="  ")
        print()



    def get_wind(self):
        return self.wind

    def get_discarded_tiles(self):
        return self.discarded_tiles

    def play(self, mahjong):
        #rest_of_tilesはMahjongクラスの山札
        #mahjongクラスは, self.turnを使うためだけに使用

        
        
        #ツモる
        
        self.draw(mahjong.rest_of_tiles)
        mahjong.count_tiles -= 1
        print("残り牌はあと", mahjong.count_tiles)
        print()
        self.print_hand()

        if self.is_riichi:
            #和了りorツモ切り
            #あらゆる鳴きはできないこととする
            while True:
                print("ツモならばt")
                what_to_do = input("牌を捨てるならばd, と入力してください: ")
                print()

                if what_do_you_do == "t":
                    self.win_on_self_draw()
                    break
            
                if what_do_you_do == "d":
                    self.discard()
                    break
                

        else:
            #ツモった後にできること
            ############################
            #例外未処理
            ############################
            while True:
                print("立直ならばr")
                print("暗槓ならばck")
                print("加槓ならばlk")
                print("ツモならばt")
                what_to_do = input("牌を捨てるならばd, と入力してください: ")
                print()
            
                #各種操作ができるかどうかはそのメソッド内で判断してもらう


                #暗槓
                if what_to_do == "ck":
                    self.closed_kong()
                    if self.kong_done:
                        self.kong_done = False #次またカン成功するまでFalse
                        #ドラ追加
                        mahjong.dora_active.append(mahjong.rest_of_tiles.pop(random.randrange(len(mahjong.rest_of_tiles))))
                        print("ドラは", *mahjong.dora_active)
                        print()
    
                        self.play(mahjong)
                        break
    
                #加槓
                if what_to_do == "lk":
                    self.late_kong()
                    if self.kong_done:
                        self.kong_done = False #次またカン成功するまでFalse
                        #ドラ追加
                        mahjong.dora_active.append(mahjong.rest_of_tiles.pop(random.randrange(len(mahjong.rest_of_tiles))))
                        print("ドラは", *mahjong.dora_active)
                        print()

                        self.play(mahjong)
                        break

                #ツモ
                if what_to_do == "t":
                    self.win_on_self_draw(mahjong)
                    if mahjong.is_finished:
                        break

                #牌を捨てる
                if  what_to_do == "d":
                    self.discard()
                    break


    def play_for_waiting(self, mahjong, other):
        #otherはPlayerクラスの人
        #ポン, チー, カンするかどうかをの選択を与え, 入力に応じてそれらを実行する.
        #######################
        #######例外未処理
        #######################
        while True:
            if self.wind == (other.wind + 1)%4: #チーの選択肢をわざわざ示す必要がないときがある

                print("ポンならばp")
                print("チーならばc")
                print("大明槓ならばk")
                what_to_do = input("何もしないならばn, と入力してください: ")
                print()
    
                #ポン
                if what_to_do == "p":
                    self.pung(other)

                    if self.pung_done: #ポンが成功したかどうか
                        self.pung_done = False #次またポンが成功するまでFalse
                        mahjong.turn = self.wind #ターン更新
                        break
                    
                #チー
                if what_to_do == "c":
                    self.chow(other)

                    if self.chow_done: #チーが成功したかどうか
                        self.chow = False
                        mahjong.turn = self.wind #ターン更新
                        break
    
                #大明槓
                if what_to_do == "k":
                    self.opened_kong(other)

                    if self.kong_done:
                        self.kong_done = False #次またカン成功するまでFalse
                        #ドラ追加
                        mahjong.dora_active.append(mahjong.rest_of_tiles.pop(random.randrange(len(mahjong.rest_of_tiles))))
                        print("ドラは", *mahjong.dora_active)
                        print()

                        self.play(mahjong)
    
                        mahjong.turn = self.wind #ターン更新
                        break
    
                if what_to_do == "n":
                    break

            else:
                print("ポンならばp")
                print("大明槓ならばk")
                what_to_do = input("何もしないならばn, と入力してください: ")
                print()
    
                #ポン
                if what_to_do == "p":
                    self.pung(other)

                    if self.pung_done: #ポンが成功したかどうか
                        self.pung_done = False #次にカンが成功するまでFalse
                        mahjong.turn = self.wind #ターン更新
                        break
                    
                #大明槓
                if what_to_do == "k":
                    self.opened_kong(other)

                    if self.kong_done: #カンが成功したかどうか
                        self.kong_done = False #次またカン成功するまでFalse
                        #ドラ追加
                        mahjong.dora_active.append(mahjong.rest_of_tiles.pop(random.randrange(len(mahjong.rest_of_tiles))))
                        print("ドラは", *mahjong.dora_active)
                        print()
    
                        self.play(mahjong)
        
                        mahjong.turn = self.wind #ターン更新
                        break
        
                if what_to_do == "n":
                    break

    def judge_win(self, hand):

        characters = []
        circles = []
        bamboo = []
        honors = []
        for tile in hand:
            if isinstance(tile, Characters):
                characters.append(tile)
            if isinstance(tile, Circles):
                circles.append(tile)
            if isinstance(tile, Bamboo):
                bamboo.append(tile)
            if isinstance(tile, Honors):
                honors.append(tile)

        combi_of_characters = []
        combi_of_circles = []
        combi_of_bamboo = []
        pung_of_honors = []


        for perm in permutations(characters):
            count_of_pung_or_chow = 0
            count_of_pair = 0
            if len(perm)%3 != 1 and len(perm) >= 3: #テンパイのときは必ず3n or 3n+2
                for i in range(len(perm)//3): #刻子もしくは順子の数
                    if self.is_pung(perm[i], perm[i+1], perm[i+2]) or self.is_chow(perm[i], perm[i+1], perm[i+2]):
                        count_of_pung_or_chow += 1
                if len(perm)%3 == 2:
                    if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                        count_of_pair += 1
            if len(perm)== 2:
                if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                    count_of_pair += 1

            combi_of_characters.append([count_of_pung_or_chow, count_of_pair])
            
        for perm in permutations(circles):
            count_of_pung_or_chow = 0
            count_of_pair = 0
            if len(perm)%3 != 1 and len(perm) >= 3: #テンパイのときは必ず3n or 3n+2
                for i in range(len(perm)//3): #刻子もしくは順子の数
                    if self.is_pung(perm[i], perm[i+1], perm[i+2]) or self.is_chow(perm[i], perm[i+1], perm[i+2]):
                        count_of_pung_or_chow += 1
                if len(perm)%3 == 2:
                    if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                        count_of_pair += 1
            if len(perm)== 2:
                if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                    count_of_pair += 1
            combi_of_circles.append([count_of_pung_or_chow, count_of_pair])

        for perm in permutations(bamboo):
            count_of_pung_or_chow = 0
            count_of_pair = 0
            if len(perm)%3 != 1 and len(perm) >= 3: #テンパイのときは必ず3n or 3n+2
                for i in range(len(perm)//3): #刻子もしくは順子の数
                    if self.is_pung(perm[i], perm[i+1], perm[i+2]) or self.is_chow(perm[i], perm[i+1], perm[i+2]):
                        count_of_pung_or_chow += 1
                if len(perm)%3 == 2:
                    if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                        count_of_pair += 1
            if len(perm)== 2:
                if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                    count_of_pair += 1
            combi_of_bamboo.append([count_of_pung_or_chow, count_of_pair])

        for perm in permutations(honors):
            count_of_pung_or_chow = 0
            count_of_pair = 0

            if len(perm)%3 != 1 and len(perm) >= 3: #テンパイのときは必ず3n or 3n+1
                for i in range(len(perm)//3): #刻子もしくは順子の数
                    if self.is_pung(perm[i], perm[i+1], perm[i+2]):
                        count_of_pung_or_chow += 1
                if len(perm)%3 == 2:
                    if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                        count_of_pair += 1
            if len(perm)== 2:
                if perm[-1].get_number_for_sort() == perm[-2].get_number_for_sort():
                    count_of_pair += 1
            pung_of_honors.append([count_of_pung_or_chow, count_of_pair])
        
        for i in range(len(combi_of_characters)):
            for j in range(len(combi_of_circles)):
                for k in range(len(combi_of_bamboo)):
                    for l in range(len(pung_of_honors)):
            #総当りで刻子または順子が計4個, 対子が1個ならば良い
                        #print(combi_of_characters[i], combi_of_circles[j], combi_of_bamboo[k], pung_of_honors[l])
                        count_of_three = combi_of_characters[i][0] + combi_of_circles[j][0] + combi_of_bamboo[k][0] + pung_of_honors[l][0]
                        count_of_two = combi_of_characters[i][1] + combi_of_circles[j][1] + combi_of_bamboo[k][1] + pung_of_honors[l][1]
                        if count_of_three == 4 - self.count_call and count_of_two == 1:
                            return True
        return False



            


    

    def draw(self, rest_of_tiles):
        ##########
        ##ツモる##
        ##########
        #残り牌からランダムに引っこ抜く
        #Playerクラスから直接残り牌にアクセスできないので引数としている
        self.hand.sort()
        self.hand.append(rest_of_tiles.pop(random.randrange(0, len(rest_of_tiles))))
    
    def discard(self):
        ########
        ##切る##
        ########
        index = self.input_index("捨てる牌は左から何番目: ")
        
        #手牌から添字を指定して引っこ抜いて, 捨て牌リストにぶっこむ
        self.discarded_tiles.append(self.hand.pop(index-1))
        self.hand.sort()
        print(self, "が捨てたのは", self.discarded_tiles[-1])
        print()

    def win_on_self_draw(self, mahjong):
        if self.judge_win(self.hand):
            print(self, "がツモしました!")
            print()
            self.hand.sort()
            mahjong.is_finished = True
            mahjong.winner = self.wind

        else:
            print("ツモできませんでした")
            print()


    def ron(self, tile_discarded, mahjong):
        ########
        ##ロン##
        ########
        #otherの最新の捨て牌に対して, ロンするかどうか判定したのち, ロンするならself.is_finishedを書き換える.
        #立直してるなら必ずロンする
        #役判定はしない
        temporary_hand = self.hand + [tile_discarded]
        if self.judge_win(temporary_hand):
            yes_or_no = input("ロンしますか? するならばyes, しないならばno: ")

            if yes_or_no == "yes":
                print(self, "がロンしました!")
                print()
                self.hand.append(tile_discarded)
                self.hand.sort()
                mahjong.is_finished = True
                mahjong.winner = self.wind



    def riichi(self):
        #立直
        self.discard()
        print(self, "が立直しました!")
        print()
        self.is_riichi = True
        self.have_not_done = False

    def is_able_to_pung(self):
        #対子が存在するかどうか
        #重複している場合は牌の個数を返す.
        #重複していないならば0を返す
        for i in range(len(self.hand)-1):
            if self.hand[i].get_number_for_sort() == self.hand[i+1].get_number_for_sort():
                return True
        return False

    def is_pung(self, tile_00, tile_01, tile_02):
        #牌を3つ選択して, 刻子であるかどうか判定する
        if tile_00.get_number_for_sort() == tile_01.get_number_for_sort() == tile_02.get_number_for_sort():
            return True
        else:
            return False
        
    def pung(self, other):
        #############
        #例外未処理
        #############
        #ポン
        #otherはPlayerクラスの人
        #"ポン"と入力させたならばこれを実行する. 入力の時点でできるかどうかは関係ない.
        if self.is_able_to_pung():
            index_pung_00 = self.input_index("ポンに使う1つ目の牌は左から何番目?→") - 1
            index_pung_01 = self.input_index("ポンに使う2つ目の牌は左から何番目?→") - 1
            index_discarded = self.input_index("捨てる牌は左から何番目?→") - 1
            print()


            #まずは非破壊的操作で牌を取り出しておく
            tile_pung_00 = self.hand[index_pung_00]
            tile_pung_01 = self.hand[index_pung_01]
            tile_pung_02 = other.discarded_tiles[-1]
            tile_discarded = self.hand[index_discarded]

            if self.is_pung(tile_pung_00, tile_pung_01, tile_pung_02):
                index_pung = [index_pung_00, index_pung_01, index_discarded]
                index_pung.sort() #ソートしないとpopでうまく取り出せない

                #指定の添字の牌を手札から引っこ抜き, 相手の捨て牌からも最新の捨て牌を引っこ抜く
                self.hand.pop(index_pung[2])
                self.hand.pop(index_pung[1])
                self.hand.pop(index_pung[0])
                other.discarded_tiles.pop(-1)

                #鳴いた牌リストへぶっこむ
                self.claimed.append([tile_pung_00, tile_pung_01, tile_pung_02])

                #選択した牌を捨てる
                self.discarded_tiles.append(tile_discarded)
                print(self, "が捨てたのは", tile_discarded)
                print()

                self.is_pung_done = True
                self.is_call_done = True
                self.did_act = True
                self.pung_done = True
                self.count_call += 1
                print(self, "がポンしました!")
                print()
            else:
                print("あなたはポンできませんでした")
                print()
        else:
            print("あなたはポンできません")
            print()


    def is_able_to_make_chow(self, tile_00, tile_01):
        #牌を2つ選択して, それが順子をつくれる可能性があるかどうか調べる

        is_serial = 1 <= abs(tile_00.get_number_for_sort() - tile_01.get_number_for_sort()) <= 2 #連続判定

        #赤ドラを各クラスのサブクラスとして実装してしまったので, こうするしかなかった
        #ソート用変数が連続だとしても, |M9|と|P1|とかかもしれないので, クラスが同じかどうか判定する必要がある.
        is_both_Characters = isinstance(tile_00, Characters) and isinstance(tile_01, Characters)
        is_both_Circles = isinstance(tile_00, Circles) and isinstance(tile_01, Circles)
        is_both_Bamboo = isinstance(tile_00, Bamboo) and isinstance(tile_01, Bamboo)

        return is_serial and (is_both_Characters or is_both_Circles or is_both_Bamboo)


    def is_chow(self, tile_00, tile_01, tile_02):
        #牌を3つ選択して, それが順子かどうか調べる
        tile = [tile_00, tile_01, tile_02]
        tile.sort()
        #print(*tile, "hey")
        is_serial = (tile[1].get_number_for_sort() - tile[0].get_number_for_sort()) == (tile[2].get_number_for_sort() - tile[1].get_number_for_sort()) #順子判定 クラス違いは別の関数で判定する
        if self.is_able_to_make_chow(tile[0], tile[2]) and is_serial: #ソート済みだから両端だけ合えばok
            return True
        else:
            return False
        

    def exist_chow_missing(self):
        #順子を作れる可能性があるか判定する
        for i in range(len(self.hand)-1):
            if self.is_able_to_make_chow(self.hand[i], self.hand[i+1]): #順子判定
                return True
        return False

    def chow(self, other):
        #############
        #例外未処理
        #############
        #チー
        #otherはPlayerクラスの人
        #"チー"と入力させたならばこれを実行する. 入力の時点でできるかどうかは関係ない.
        if self.exist_chow_missing():
            index_chow_00 = self.input_index("チーに使う1つ目の牌は左から何番目: ") - 1
            index_chow_01 = self.input_index("チーに使う2つ目の牌は左から何番目: ") - 1
            index_discarded = self.input_index("捨てる牌は左から何番目: ") - 1
            print()

            #まずは非破壊的操作で牌をとってくる. 判定のために
            tile_chow_00 = self.hand[index_chow_00]
            tile_chow_01 = self.hand[index_chow_01]
            tile_chow_02 = other.discarded_tiles[-1]
            tile_discarded = self.hand[index_discarded]


            if self.is_chow(tile_chow_00, tile_chow_01, tile_chow_02): #選択した牌がチーする条件に合っているのならば
                index = [index_chow_00, index_chow_01, index_discarded]
                index.sort() #sortしないとpopでリストが破壊されて予想外のpopが起こる

                for i in range(3):
                    self.hand.pop(index[2-i]) #指定したindexの牌を引っこ抜く

                tile_chow = [tile_chow_00, tile_chow_01, tile_chow_02]
                tile_chow.sort()
                self.claimed.append(tile_chow)

                self.discarded_tile.append(tile_discarded)
                self.is_call_done = True
                self.did_act = True
                self.chow_done = True
                self.count_call += 1
                print(self, "がチーしました!")
                print()
                
            else:
                print("あなたはチーできませんでした")
                print()
        else:
            print("あなたはチーできません")
            print()


    def exist_pung(self):
        #刻子があるかどうかを判定する
        for i in range(len(self.hand)-2):
            if self.hand[i].get_number_for_sort() == self.hand[i+1].get_number_for_sort() == self.hand[i+2].get_number_for_sort():
                return True
        return False

    def exist_kong(self):
        #槓子があるかどうか判定する
        for i in range(len(self.hand)-3):
            if self.hand[i].get_number_for_sort() == self.hand[i+1].get_number_for_sort() == self.hand[i+2].get_number_for_sort() == self.hand[i+3].get_number_for_sort():
                return True
        return False


    def is_kong(self, tile_00, tile_01, tile_02, tile_03):
        #4つの牌が槓子であるか判定する
        if tile_00.get_number_for_sort() == tile_01.get_number_for_sort() == tile_02.get_number_for_sort() == tile_03.get_number_for_sort():
            return True
        else:
            return False


    def is_able_to_late_kong(self, tile_kong):
        #手牌の1つの牌を引数として, 加槓ができるかどうか判定する.
        #また, self.claimedのどこにその刻子があるのかを示すindexを返す
        index = None
        true_or_false = False
        for i in range(len(self.claimed)):
            #self.claimedに何も入っていないとき, for文が実行されずFalseが返される
            #self.claimedに何か入っているならば, 後のfor文が実行されるからカンできなかったらFalseに書き換える
            #最初からTrueにしてしまうと, for文を通らなかったときにTrueを返してしまう
            true_or_false = True

            for tile in self.claimed[i]:
                #カンは4牌, ポンとチーは3牌あるため, self.claimedにある全ての牌がtile_kongと等しいならば加槓ができる
                true_or_false = true_or_false and tile_kong.get_number_for_sort() == tile.get_number_for_sort()

            #この時点でTrueならばその添字iのところに刻子がある
            if true_or_false:
                index = i
                return index, true_or_false
        return index, true_or_false


    def late_kong(self):
        #加槓
        ############
        #例外未処理
        #ツモって捨てるまでは実装してない
        #################################
        #otherはPlayerクラスの人
        #"カン"と入力させたならばこれを実行する. 入力の時点でできるかどうかは関係ない.
        if self.is_pung_done: #ポンしていないと加槓はできない
            #1つの添字を受け取ったら自動で加槓する
            index_kong_00 = self.input_index("加槓に使う牌は左から何番目: ") - 1
            print()
            tile_kong_00 = self.hand[index_kong_00]
            
            #タプルのアンパック.
            #index_pung_in_claimedは, self.claimedの中での刻子の位置
            #is_late_kongは, 該当する刻子があるかどうかの真偽値
            index_pung_in_claimed, is_late_kong = self.is_able_to_late_kong(tile_kong_00)
            if is_late_kong:
                self.claimed[index_pung_in_claimed].append(tile_kong_00)
                self.is_call_done = True
                self.kong_done = True
                self.count_call += 1
                print(self, "がカンしました!")
                print()
            else:
                print("カンできませんでした")
                print()
        else:
            print("あなたはカンできません")
            print()
                

    def closed_kong(self):
        #暗槓
        ############
        #例外未処理
        #ツモって捨てるまでは実装してない
        #################################
        #otherはPlayerクラスの人
        #"カン"と入力させたならばこれを実行する. 入力の時点でできるかどうかは関係ない.
        if self.exist_kong():
            index_kong_00 = self.input_index("暗槓に使う1つ目の牌は左から何番目: ") - 1
            index_kong_01 = self.input_index("暗槓に使う2つ目の牌は左から何番目: ") - 1
            index_kong_02 = self.input_index("暗槓に使う3つ目の牌は左から何番目: ") - 1
            index_kong_03 = self.input_index("暗槓に使う4つ目の牌は左から何番目: ") - 1
            print()

            #まずは非破壊的操作で牌を取り出して判定
            tile_kong_00 = self.hand[index_kong_00]
            tile_kong_01 = self.hand[index_kong_01]
            tile_kong_02 = self.hand[index_kong_02]
            tile_kong_03 = self.hand[index_kong_03]

            if self.is_kong(tile_kong_00, tile_kong_01, tile_kong_02, tile_kong_03): #槓子かどうか
                index_kong = [index_kong_00, index_kong_01, index_kong_02, index_kong_03]
                index_kong.sort() #ソートしないとpopでうまく取り出せない
                
                #破壊的操作なので後ろから
                self.hand.pop(index_kong[3])
                self.hand.pop(index_kong[2])
                self.hand.pop(index_kong[1])
                self.hand.pop(index_kong[0])

                self.claimed.append([tile_kong_00, tile_kong_01, tile_kong_02, tile_kong_03])
                self.is_call_done = True
                self.kong_done = True
                self.count_call += 1
                print(self, "がカンしました!")
                print()
            else:
                print("あなたはカンできませんでした")
                print()
        else:
            print("あなたはカンできません")
            print()



    def opened_kong(self, other):
        #大明槓
        #############
        #例外未処理
        #ツモって捨てるまでは実装してない
        #################################
        #otherはPlayerクラスの人
        #"カン"と入力させたならばこれを実行する. 入力の時点でできるかどうかは関係ない.
        if self.exist_pung():
            index_kong_00 = self.input_index("カンに使う1つ目の牌は左から何番目: ") - 1
            index_kong_01 = self.input_index("カンに使う2つ目の牌は左から何番目: ") - 1
            index_kong_02 = self.input_index("カンに使う3つ目の牌は左から何番目: ") - 1
            print()


            #まずは非破壊的操作で牌を取り出しておく
            tile_kong_00 = self.hand[index_kong_00]
            tile_kong_01 = self.hand[index_kong_01]
            tile_kong_02 = self.hand[index_kong_02]
            tile_kong_03 = other.discarded_tiles[-1]

            if self.is_kong(tile_kong_00, tile_kong_01, tile_kong_02, tile_kong_03): #槓子かどうか
                index_kong = [index_kong_00, index_kong_01, index_kong_02]
                index_kong.sort() #ソートしないとpopでうまく取り出せない

                #指定の添字の牌を手札から引っこ抜き, 相手の捨て牌からも最新の捨て牌を引っこ抜く
                self.hand.pop(index_kong[2])
                self.hand.pop(index_kong[1])
                self.hand.pop(index_kong[0])
                other.discarded_tiles.pop(-1)
                #鳴いた牌リストへぶっこむ
                self.claimed.append([tile_kong_00, tile_kong_01, tile_kong_02, tile_kong_03])
                self.is_call_done = True
                self.did_act = True
                self.kong_done = True
                self.count_call += 1
                print(self, "がカンしました!")
                print()
            else:
                print("あなたはカンできませんでした")
                print()
        else:
            print("あなたはカンできません")
            print()


class Tile(object):
    def __init__(self):
        #ソート用変数
        self.number_for_sort = 0

    def __lt__(self, other):
        return self.number_for_sort < other.number_for_sort

    def get_number_for_sort(self):
        return self.number_for_sort

class Suit(Tile):
    #数牌
    #ソート用変数は0から始まる
    def __init__(self, order):
        super().__init__()
        self.order = order

    def get_order(self):
        return self.order

class Honors(Tile):
    #字牌
    #ソート用変数は数牌の27の分遅れた, 28から始まる.
    def __init__(self):
        super().__init__()
        self.number_for_sort += 28


class Characters(Suit):
    #萬子
    #ソート用変数は0~8
    def __init__(self, order):
        super().__init__(order)
        self.mark = 0
        self.number_for_sort += order #orderは1~9だから

    def __str__(self):
        return "|" + "M" + str(self.order) + "|"

class Circles(Suit):
    #筒子
    #ソート用変数は10~18
    def __init__(self, order):
        super().__init__(order)
        self.number_for_sort += order + 9 #orderは1~9だから
    
    def __str__(self):
        return "|" + "P" + str(self.order) + "|"

class Bamboo(Suit):
    #索子
    #ソート用変数は18~26
    def __init__(self, order):
        super().__init__(order)
        self.number_for_sort += order + 18 #orderは1~9だから

    def __str__(self):

        return "|" + "S" + str(self.order) + "|"

class Red_Characters_5(Characters):
    #赤ドラ五萬
    def __init__(self, order):
        super().__init__(order)

    def __str__(self):
        return "|" + "m" + str(self.order) + "|"

class Red_Circles_5(Circles):
    #赤ドラ五筒
    def __init__(self, order):
        super().__init__(order)

    def __str__(self):
        return "|" + "p" + str(self.order) + "|"

class Red_Bamboo_5(Bamboo):
    #赤ドラ五索
    def __init__(self, order):
        super().__init__(order)

    def __str__(self):
        return "|" + "s" + str(self.order) + "|"

class Winds(Honors):
    #東, 南, 西, 北
    #ソート用変数は28, 29, 30, 31
    def __init__(self, wind):
        super().__init__()
        self.wind = wind
        self.number_for_sort += wind

    def get_wind(self):
        return self.wind

    def __str__(self):
        if self.wind == 0:
            return "|" + "東" + "|"

        if self.wind == 1:
            return "|" + "南" + "|"

        if self.wind == 2:
            return "|" + "西" + "|"

        if self.wind == 3:
            return "|" + "北" + "|"

class Dragons(Honors):
    #白, 發, 中
    #ソート用変数は32, 33, 34
    def __init__(self, three):
        super().__init__()
        self.three = three
        self.number_for_sort += three + 4 #東南西北の分の4

    def __str__(self):
        if self.three == 0:
            return "|" + "  " + "|"

        if self.three == 1:
            return "|" + "發" + "|"

        if self.three == 2:
            return "|" + "中" + "|"

play = Mahjong()
play.run()
