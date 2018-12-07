import os



class Player():
    def __init__(self, location):
        self.location = location
        self.my_card = []
        self.main_color = "H"
        self.banker_grade = "2"
        self.my_role = "banker"
        self.numbers = ['2', '3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A']
        self.hidden_score = 0
        self.unknown_cards = {}  # 用来记录没有出的牌
        self.poss_no_color = {}  # 用来记录每个玩家每个花色可能没有的概率,1为确定没有
        self.role_order = ['banker', 'banker_left', 'banker_opposite', 'banker_right']
        self.color_kind = ['S', 'H', 'D', 'C']
        self.unknown_cards_init()
        self.poss_no_color_init()

    def set_main_value(self, main_value):                   #A
        """
        设置主牌面值
        :param main_value: char, 主牌面值
        :return: None
        """
        self.banker_grade = main_value

    def set_main_color(self, _main_color):                   #A
        """
        设置主牌花色
        :param main_color: char, 主牌花色
        :return: None
        """
        self.main_color = _main_color

    def player_init(self):                                  #A
        """
        开始一局新的游戏，初始化相关变量
        :return: None
        """
        self.my_card.clear()
        self.main_value = None
        
        self.unknown_cards_init()
        self.poss_no_color_init()



    def set_role(self, role):                               #A
        """
        设置角色
        :param role: str， 玩家角色
        :return: None
        """
        #self.my_role = role
        pass

    def get_role(self):                             
        return self.my_role

    def show_cards(self):                                   #A
        """
        查看手里的所有牌
        :return: list of str, 玩家手里的所有牌
        """
        return self.my_card

    def _finish_one_round(self, current_turn_out_cards):     #A
        """
        一轮出牌结束，4个玩家的出牌信息
        :param current_turn_out_cards: list of (order, role, card), 本轮出牌
        :return: None
        """
        self.cal_unknown_cards([i[2] for i in current_turn_out_cards])
        self.cal_poss_no_card(current_turn_out_cards)


    #初始化unknown_cards
    def unknown_cards_init(self):
        self.unknown_cards = {} #用来记录没有出的牌
        self.unknown_cards['always'] = []
        for color in self.color_kind:
            self.unknown_cards[color] = self.numbers.copy()
            self.unknown_cards[color].remove(self.banker_grade)
            self.unknown_cards['always'].append(color + self.banker_grade)
        self.unknown_cards['always'].append('JK')
        self.unknown_cards['always'].append('jk')


    #初始化poss_no_color
    def poss_no_color_init(self):
        self.poss_no_color = {} #用来记录每个玩家每个花色可能没有的概率
        for role in self.role_order:
            self.poss_no_color[role] = {}
            for color in self.color_kind:
                self.poss_no_color[role][color] = 0


    def calculate_score(self, cards):#计算cards牌的分数和
        score = 0
        for i in cards:
            if  (i[1] == '5'):
                score += 5
            elif  (i[1] == '0' or i[1] == 'K'):
                score += 10
        return score


    def add_card_and_is_snatch(self, current_card):
        '''
        拿发的牌并选择是否叫主
        :param current_card: a string like 'S2'
        :return: a string
        '''
        self.my_card.append(current_card)
        if self.main_color == "":  #庄还没定
            banker_card_color = [i[0] for i in self.my_card if i[1] == self.banker_grade]  # 把可叫花色筛出来
            if banker_card_color != []:
                for color in banker_card_color:
                    color_card_cnt = len([i[1] for i in self.my_card if i[0] == color and i[1] != self.banker_grade])
                    if  color_card_cnt >= 3:       # 如果自己相应花色很多就叫主
                        return color + self.banker_grade
        return ""

    def cardToNum(self, card, score_higher = 0):
        '''
        将card面值变为数字
        :param card: a char in ['2','3', '4', '5', '6', '7', '8', '9', '0', 'J', 'Q', 'K', 'A']
        :return: int of the char input
        '''
        if card == '0':res = 10
        elif card == 'J':res = 11
        elif card == 'Q':res = 12
        elif card == 'K':res = 13
        elif card == 'A':res = 14
        else:res = int(card)
        if score_higher and (card == 'K' or card == '5' or card == '0'):
            res = res + 10
        return res


    def key_value_sort(self,card):
        '''
        对牌张面值排序时使用
        :param card: str(2), eg:'C2'
        :return: color, num of value
        '''

        return card[0], self.cardToNum(card[1])


    def key_score_advance(self, card): # 排序时分数排在后面，其余按照面值大小排序
        return self.cardToNum(card[1], 1)


    def eva_main_card(self, main_card):
        '''
        给主牌实力打分
        :param main_card: a list with element of str(2)
        :return: mark(int)
        '''
        mark = len(main_card) #初始分为将牌张数
        if 'JK' in main_card:
            mark += 3
        return mark

    def find_player_role(self, player_turn, my_turn):
        distance = player_turn - my_turn
        my_index = self.role_order.index(self.my_role)
        player_index = my_index + distance
        if player_index < 0:
            player_index += 4
        return self.role_order[player_index % 4]


    def find_card_to_settle(self, main_mark, vice_card_sep):
        '''
        找到要埋的底牌，可能不够6张，因为副牌可能很少
        :param main_mark: 主牌的实力，mark越大，实力越强
        :param vice_card_sep: 按照花色放的副牌 eg:[['S3', 'S4', 'S8'], [], ['C3', 'C5', 'C9'], ['D5', 'D0']]
        :return: choose: a list with element of str(2), size <= 6
        '''
        choose = []
        if main_mark >= 10:  # 将牌实力很强，优先选择埋更多花色
            vice_card_sep.sort(key=lambda x: len(x), reverse=False)
            for cards in vice_card_sep:
                if len(choose) + len(cards) <= 6:
                    choose.extend(cards)
                else:
                    choose.extend(cards[0: 6 - len(choose)])
                if len(choose) == 6:
                    break

        elif main_mark > 6:  # 优先选择埋绝一门分最少的花色(但最多埋15分)
            vice_card_sep.sort(key=lambda x: self.calculate_score(x), reverse=False)
            score = 0
            for cards in vice_card_sep:
                if len(choose) + len(cards) <= 6 and self.calculate_score(cards) + score < 20:
                    choose.extend(cards)
                else:
                    no_score = [i for i in cards if i[1] != '5' and i[1] != '0' and i[1] != 'K']
                    if len(choose) + len(no_score) <= 6:
                        choose.extend(no_score)
                    else:
                        choose.extend(no_score[0: 6 - len(choose)])
                if len(choose) == 6:
                    break

        else:  # 尽量一分不埋
            vice_card_sep.sort(key=lambda x: self.calculate_score(x), reverse=False)
            for cards in vice_card_sep:
                no_score = [i for i in cards if i[1] != '5' and i[1] != '0' and i[1] != 'K']
                if len(choose) + len(no_score) - 1 <= 6:
                    choose.extend(no_score[:-1])
                else:
                    choose.extend(cards[0: 6 - len(choose)])
                if len(choose) == 6:
                    break
        return choose




    def add_left_cards(self, left_cards):
        '''
        埋牌
        :param left_cards: a list with element of str(2), size = 6
        :return: choose: a list with element of str(2), size = 6
        '''
        self.my_card.extend(left_cards)
        vice_card = [i for i in self.my_card if i[1] != self.banker_grade and self.card_color(i) != self.main_color]
        main_card = [i for i in self.my_card if i not in vice_card]
        self.color_kind = ['S', 'H', 'C', 'D']
        vice_card.sort(key = self.key_value_sort)
        vice_card_sep = []
        order = "AKQJ098765432"
        for color in self.color_kind:
            tmp = [i for i in vice_card if i[0] == color]
            big = 0
            for i in range(len(tmp) - 1, -1, -1):  # 去掉所有顶张大牌如AKQ
                if order[big] == self.banker_grade:
                    big = big + 1
                if tmp[i][1] == order[big]:
                    big = big + 1
                else:
                    break

            if big != 0:
                tmp = tmp[:-big]
                tmp.sort(key = self.key_score_advance)

            vice_card_sep.append(tmp)
        main_mark = self.eva_main_card(main_card)
        choose = self.find_card_to_settle(main_mark, vice_card_sep)
        if len(choose) < 6:
            left_vice = [i for i in vice_card if i not in choose]
            left_vice.sort(key=self.key_score_advance)
            if len(left_vice) + len(choose) > 6:
                choose.extend(left_vice[0: 6 - len(choose)])
            else:
                choose.extend(left_vice)
        if len(choose) < 6:
            main_card_to_settle = [i for i in main_card if i[1] != self.banker_grade and i != 'JK' and i != 'jk']
            main_card_to_settle.sort(key = self.key_score_advance)
            choose.extend(main_card_to_settle[0: 6 - len(choose)])

        self.hidden_score = self.calculate_score(choose)
        self.cal_unknown_cards(choose)
        cards = [i for i in self.my_card if i not in choose]
        self.my_card = cards
        return choose


    def cal_unknown_cards(self, cards):
        '''
        更新一下未出现的card有哪些(去掉cards)
        :param cards: 新出现的cards
        :return: none
        '''
        for card in cards:
            if card in self.unknown_cards['always']:
                self.unknown_cards['always'].remove(card)
            elif card != 'jk' and card != 'JK' and card[1] in self.unknown_cards[card[0]]:
                self.unknown_cards[card[0]].remove(card[1])


    def card_color(self, card):
        '''
        找到一张card的颜色,JK或庄牌为主牌花色
        :param card: str(2), eg:'C2'
        :return: 花色
        '''
        if card == 'JK' or card == 'jk' or card[1] == self.banker_grade or card[0] == self.main_color:
            return self.main_color
        return card[0]



    def cal_poss_no_card(self, current_turn_out_cards):
        '''
        计算每个玩家每种花色没有的可能性，1为一定没有该花色
        :param cards: 新出的牌
        :return: none
        '''

        must = self.card_color(current_turn_out_cards[0][2])
        for i in range(1, len(current_turn_out_cards)):
            if current_turn_out_cards[i][1] != self.my_role:
                if self.card_color(current_turn_out_cards[i][2]) != must: # 没出指定花色
                    self.poss_no_color[current_turn_out_cards[i][1]][must] = 1

        for color in self.color_kind:
            if len(self.unknown_cards[color]) == 0: #另外三人都没有了
                for role in self.role_order:
                    if role != self.my_role:
                        self.poss_no_color[role][color] = 1
                        break
            to_cal = 3   # 初始设为计算除了自己以外的三家的某花色概率
            for role in self.role_order:
                if self.poss_no_color[role][color] == 1:
                    to_cal -= 1  # 某人已确定无此花色，已确定概率为1，不参与计算
            for role in self.role_order:
                if role != self.my_role and self.poss_no_color[role][color] != 1:
                    length = len(self.unknown_cards[color])
                    if to_cal == 1:
                        self.poss_no_color[role][color] = 0
                    else:
                        self.poss_no_color[role][color] = pow(to_cal-1, length) / pow(to_cal, length)

    def find_opp(self, role):
        '''
        找到对家
        :param role: string in ['banker','banker_left', 'banker_opposite', 'banker_right']
        :return: string in ['banker','banker_left', 'banker_opposite', 'banker_right']
        '''
        my_index = self.role_order.index(role)
        return self.role_order[(my_index + 2) % 4]


    def find_next(self, role):
        '''
        找到下家
        :param role: string in ['banker','banker_left', 'banker_opposite', 'banker_right']
        :return: string in ['banker','banker_left', 'banker_opposite', 'banker_right']
        '''
        my_index = self.role_order.index(role)
        return self.role_order[(my_index + 1) % 4]

    def find_score_in_cards(self, color, cards):
        '''
        找到一些牌中的某花色的分数牌，找到即返回
        :param color: HSCD
        :param cards: a list with element of str(2) eg:['C2','C0']
        :return: card with score of 'no'(can't find)
        '''
        if (color + '0') in cards: return color + '0'
        if (color + 'K') in cards: return color + 'K'
        if (color + '5') in cards: return color + '5'
        return 'no'

    def card_to_num_main(self, card):
        '''
        给主牌打分
        :param card: a card of self.main_color
        :return: score
        '''
        if card == 'JK': return 20
        if card == 'jk': return 19
        if card[0] == self.main_color and card[1] == self.banker_grade: return 18
        if card[1] == self.banker_grade: return 17
        return self.cardToNum(card[1])



    def find_most_card(self, color):
        '''
        找顶张大牌(找到即返回)
        :param color: HSCD
        :return: top card or 'no'(can't find)
        '''
        my_color_card = [i for i in self.my_card if self.card_color(i) == color]
        if my_color_card == []: return 'no'
        if self.unknown_cards[color] == []: return my_color_card[-1]
        if color != self.main_color and self.cardToNum(my_color_card[-1][1]) > self.cardToNum(self.unknown_cards[color][-1]):
            put_most = 1 # 出顶张大牌
            for role in self.role_order:
                if role == self.my_role or role == self.find_opp(self.my_role): continue
                if self.poss_no_color[role][color] == 1:
                    put_most = 0
            if put_most == 1:
                return my_color_card[-1]
        if color == self.main_color:
            if len(my_color_card) == 0: return 'no'
            my_color_card.sort(key = self.card_to_num_main)
            if self.unknown_cards['always'] != [] and self.card_to_num_main(my_color_card[-1]) > self.card_to_num_main(self.unknown_cards['always'][-1]):
                return my_color_card[-1]
        return "no"


    def score_in_current_turn_out_cards(self, current_turn_out_cards):
        '''
        找到current_turn_out_cards中有多少分
        :param current_turn_out_cards: list of 三元组(order, role, card)
        :return: score
        '''
        score = 0
        for item in current_turn_out_cards:
            if item[2][1] == '5':
                score += 5
            if item[2][1] == '0' or item[2][1] == 'K':
                score += 10
        return score



    def find_biggest_card(self, cards):
        '''
        返回一轮最大的牌
        :param cards: a list with element of str(2)
        :return: the biggest card in cards
        '''
        main_cards = [i for i in cards if self.card_color(i) == self.main_color]
        if main_cards != []:
            return max(main_cards, key = self.card_to_num_main)
        else:
            card_to_compare = [i for i in cards if i[0] == cards[0][0]]
            return max(card_to_compare, key = self.key_value_sort)


    # 第一家
    def first_hand_output(self):
        for color in self.color_kind:
            if color != self.main_color and self.find_most_card(color) != 'no':
                return self.find_most_card(color)

        for color in self.color_kind:
            if color != self.main_color and self.poss_no_color[self.find_opp(self.my_role)][color] == 1 and \
                            self.poss_no_color[self.find_next(self.find_opp(self.my_role))][color] != 1:
                if self.find_score_in_cards(color, self.my_card) != 'no':
                    return self.find_score_in_cards(color, self.my_card)
                card_can_put = [i for i in self.my_card if self.card_color(i) == color]
                if card_can_put != []:
                    return card_can_put[0]

        main_color_cards = [i for i in self.my_card if self.card_color(i) == self.main_color]
        for i in range(len(main_color_cards)):
            if main_color_cards[i][1] != '5' and main_color_cards[i][1] != '0' and main_color_cards[i][1] != 'K':
                return main_color_cards[i]
        return self.my_card[0]



    #第二家
    def second_hand_output(self, current_turn_out_cards):
        need_color = self.card_color(current_turn_out_cards[0][2]) #先判断是否要按要求出牌
        card_can_put = [i for i in self.my_card if self.card_color(i) == need_color]
        if  (len(card_can_put) > 0):
            must = need_color
        else:
            must = ''
        if must != '' and need_color != self.main_color:
            if self.poss_no_color[self.find_opp(self.my_role)][must] > 0.85 and self.poss_no_color[self.find_opp(self.my_role)][self.main_color] < 0.5: #第四家没有这门花色有主牌
                if self.find_score_in_cards(must, card_can_put) != 'no':
                    return self.find_score_in_cards(must, card_can_put)
            elif self.poss_no_color[self.find_next(self.my_role)][must] != 1 and self.find_most_card(must) != 'no':
                return self.find_most_card(must)
            return card_can_put[0]
        if must != '' and need_color == self.main_color:
            card_can_put.sort(key = self.card_to_num_main)
            for color in self.color_kind:
                if color == self.main_color: continue
                if self.find_most_card(color) != 'no' and self.hidden_score == 0:
                    if self.card_to_num_main(card_can_put[-1]) > self.card_to_num_main(current_turn_out_cards[0][2]):
                        return card_can_put[-1]
            return card_can_put[0]
        if must == '' and need_color != self.main_color:
            main_card = [i for i in self.my_card if self.card_color(i) == self.main_color]
            if main_card == []: return self.my_card[0]
            main_card.sort(key = self.card_to_num_main)
            if self.poss_no_color[self.find_next(self.my_role)][need_color] < 0.85: #第三家有这门花色
                if self.find_score_in_cards(self.main_color, main_card) != 'no':
                    return self.find_score_in_cards(self.main_color, main_card)
                return main_card[0]
            return self.my_card[0]
        if must == '' and need_color == self.main_color:
            return self.my_card[0]




    # 第三家
    def third_hand_output(self, current_turn_out_cards):
        need_color = self.card_color(current_turn_out_cards[0][2])  # 先判断是否要按要求出牌
        card_can_put = [i for i in self.my_card if self.card_color(i) == need_color]
        score = self.score_in_current_turn_out_cards(current_turn_out_cards)
        if card_can_put != []:
            must = need_color
        else:
            must = ''

        if must != '' and need_color != self.main_color:
            if self.card_color(current_turn_out_cards[1][2]) == self.main_color:  # 第二家主牌毙了
                for card in card_can_put:  # 出最小不是分的
                    if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                        return card
                return card_can_put[0]
            if self.unknown_cards[must] != []:
                biggest_in_unknown = self.cardToNum(self.unknown_cards[must][-1])
            else:
                biggest_in_unknown = 0
            if self.cardToNum(current_turn_out_cards[0][2][1]) > biggest_in_unknown and self.cardToNum(
                    current_turn_out_cards[0][2][1]) > self.cardToNum(current_turn_out_cards[1][2][1]):
                # 第一家出的是顶张大牌
                if self.poss_no_color[self.find_next(self.my_role)] != 1:  # 第四家还有该花色
                    if self.find_score_in_cards(must, card_can_put) != 'no':  # 我有分
                        return self.find_score_in_cards(must, card_can_put)
            elif self.score_in_current_turn_out_cards(current_turn_out_cards) != 0:  # 12家有分,4有该花色，我有顶张
                if self.poss_no_color[self.find_next(self.my_role)] != 1 and self.find_most_card(must) != 'no':
                    return self.find_most_card(must)
            for card in card_can_put:  # 其他情况，出最小不是分的
                if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                    return card
            return card_can_put[0]

        if must != '' and need_color == self.main_color:
            print(must)
            print(card_can_put)
            card_can_put.sort(key=self.card_to_num_main)
            if score != 0 and self.hidden_score < 10:  # 有分，不用看护底牌,出大牌
                if self.card_to_num_main(card_can_put[-1]) > self.card_to_num_main(current_turn_out_cards[0][2]) and self.card_to_num_main(
                        card_can_put[-1]) > self.card_to_num_main(current_turn_out_cards[1][2]):
                    return card_can_put[-1]

            if self.card_to_num_main(current_turn_out_cards[0][2]) < 14 and self.card_to_num_main(
                    current_turn_out_cards[1][2]) < 14:  # 第三家出大
                for card in card_can_put:
                    if self.card_to_num_main(card) > 14 and self.card_to_num_main(card) < 20:
                        return card
            if self.unknown_cards['always'] != [] and self.card_to_num_main(current_turn_out_cards[0][2]) > self.card_to_num_main(
                    self.unknown_cards['always'][-1]):
                if self.find_score_in_cards(must, card_can_put) != 'no':  # 第一家大，出分
                    return self.find_score_in_cards(must, card_can_put)
            for card in card_can_put:  # 其他情况，出最小不是分的
                if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                    return card
            return card_can_put[0]

        if must == '' and need_color != self.main_color:
            main_card = [i for i in self.my_card if self.card_color(i) == self.main_color]
            if main_card == []: return self.my_card[0]
            main_card.sort(key=self.card_to_num_main)
            if self.card_color(current_turn_out_cards[1][2]) == self.main_color:  # 第二家毙了，出比第二家大的主牌
                for card in main_card:
                    if self.card_to_num_main(card) > self.card_to_num_main(current_turn_out_cards[1][2]):
                        return card
            elif self.poss_no_color[self.find_next(self.my_role)][need_color] < 0.85 and self.card_color(
                    current_turn_out_cards[1][2]) != self.main_color:  # 第四家有这门花色
                if self.find_score_in_cards(self.main_color, main_card) != 'no':
                    return self.find_score_in_cards(self.main_color, main_card)
                else:
                    return main_card[0]
            vice_card = [i for i in self.my_card if self.card_color(i) != self.main_color]
            if vice_card != []: return vice_card[0]
            return self.my_card[0]

        if must == '' and need_color == self.main_color:
            return self.my_card[0]


    # 第四家
    def forth_hand_output(self, current_turn_out_cards):
        need_color = self.card_color(current_turn_out_cards[0][2])  # 先判断是否要按要求出牌
        card_can_put = [i for i in self.my_card if self.card_color(i) == need_color]
        score = self.score_in_current_turn_out_cards(current_turn_out_cards)
        if card_can_put != []:
            must = need_color
        else:
            must = ''
        cards = [i[2] for i in current_turn_out_cards]
        biggest_card = str(self.find_biggest_card(cards))
        if must != '' and need_color != self.main_color:
            if biggest_card == cards[1]:  # 对家大，优先出分
                if self.find_score_in_cards(must, card_can_put) != 'no':  # 我有分
                    return self.find_score_in_cards(must, card_can_put)

            elif self.card_color(biggest_card) != self.main_color and self.cardToNum(card_can_put[-1][1]) > self.cardToNum(biggest_card[1]):  # 我最大
                if (must + 'K') in card_can_put:
                    return (must + 'K')
                elif score != 0:
                    for card in card_can_put:
                        if self.cardToNum(card[1]) > self.cardToNum(biggest_card[1]):
                            return card
            else:
                for card in card_can_put:
                    if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                        return card
            return card_can_put[0]

        if must != '' and need_color == self.main_color:
            card_can_put.sort(key=self.card_to_num_main)
            if biggest_card == cards[1]:  # 对家大，优先出分
                if self.find_score_in_cards(must, card_can_put) != 'no':  # 我有分
                    return self.find_score_in_cards(must, card_can_put)
            elif self.card_to_num_main(card_can_put[-1]) > self.card_to_num_main(biggest_card):  # 我最大
                if score != 0:
                    if (must + 'K') in card_can_put and self.card_to_num_main(must + 'K') > self.card_to_num_main(biggest_card):
                        return (must + 'K')
                    else:
                        for card in card_can_put:
                            if self.card_to_num_main(card) > self.card_to_num_main(biggest_card):
                                return card
                else:
                    for card in card_can_put:
                        if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                            return card
            return card_can_put[0]

        if must == '' and need_color != self.main_color:
            if biggest_card == cards[1]:  # 对家大
                score_card_vice = [i for i in self.my_card if (i[1] == '0' or i[1] == 'K' or i[1] == '5') and i[0] != self.main_color]
                if score_card_vice != []:
                    return score_card_vice[-1]
                else:
                    score_card_main = [i for i in self.my_card if
                                       i[0] == self.main_color and (i[1] == '0' or i[1] == 'K' or i[1] == '5')]
                    if score_card_main != []:
                        return score_card_main[0]
            main_card = [i for i in self.my_card if self.card_color(i) == self.main_color]
            if main_card == []: return self.my_card[0]  # 我没将
            if self.card_color(biggest_card) == self.main_color:  # 被毙了
                main_card = [i for i in self.my_card if self.card_color(i) == self.main_color]
                if main_card == []: return self.my_card[0]  # 我没将
                main_card.sort(key=self.card_to_num_main)
                if self.card_to_num_main(main_card[-1]) > self.card_to_num_main(biggest_card):  # 我最大
                    if (self.main_color + 'K') in main_card and self.card_to_num_main(self.main_color + 'K') > self.card_to_num_main(biggest_card):
                        return self.main_color + 'K'
                    elif score != 0:
                        for card in main_card:
                            if self.card_to_num_main(card) > self.card_to_num_main(biggest_card):
                                return card
            else:  # 没被毙
                if self.find_score_in_cards(self.main_color, self.my_card) != 'no':  # 我有主牌分
                    return self.find_score_in_cards(self.main_color, self.my_card)
                elif score != 0:
                    return main_card[0]
            for card in self.my_card:
                if card[1] != '5' and card[1] != '0' and card[1] != 'K' and self.card_color(card) != self.main_color:
                    return card
            return self.my_card[0]

        if must == '' and need_color == self.main_color:
            if biggest_card == cards[1]:  # 对家大
                score_card = [i for i in self.my_card if i[1] == '0' or i[1] == 'K' or i[1] == '5']
                if score_card != []:
                    return score_card[-1]
            else:
                for card in self.my_card:
                    if card[1] != '5' and card[1] != '0' and card[1] != 'K':
                        return card
            return self.my_card[0]



    def _play_out_cards(self, current_turn_out_cards):
        '''
        决定要出哪张牌
        :param turn: 第几轮出牌
        :param current_turn_out_cards: 目前出了的牌
        :return: 要出的牌str(2)
        '''
        my_turn = len(current_turn_out_cards) + 1
        if len(self.my_card) == 12:
            my_card_vice = [i for i in self.my_card if self.card_color(i) != self.main_color]
            my_card_vice.sort(key = self.key_value_sort)
            my_card_main = [i for i in self.my_card if self.card_color(i) == self.main_color]
            my_card_main.sort(key = self.card_to_num_main)
            self.my_card = my_card_vice + my_card_main
            self.cal_unknown_cards(self.my_card)
            self.my_role = self.role_order[len(current_turn_out_cards) % 4]

        cards = [i[2] for i in current_turn_out_cards]
        if my_turn != 1:
            self.cal_unknown_cards(cards)
            self.cal_poss_no_card(current_turn_out_cards)

        if my_turn == 1:
            play_out = self.first_hand_output()
        elif my_turn == 2:
            play_out = self.second_hand_output(current_turn_out_cards)
        elif my_turn == 3:
            play_out = self.third_hand_output(current_turn_out_cards)
        else:
            play_out = self.forth_hand_output(current_turn_out_cards)
        if play_out in self.my_card:
            self.my_card.remove(play_out)
        return play_out


    def play_out_cards(self, my_turn, cards):
        current_turn_out_cards = []
        for i in range(len(cards)):
            current_turn_out_cards.append((i+1, self.find_player_role(i+1, my_turn+1), cards[i]))
        return self._play_out_cards(current_turn_out_cards)


    def finish_one_round(self, cards, my_turn):
        current_turn_out_cards = []
        for i in range(4):
            current_turn_out_cards.append((i + 1, self.find_player_role(i + 1, my_turn + 1), cards[i]))
        self._finish_one_round(current_turn_out_cards)


if __name__ == "__main__":
    play = Player()
    card_test = ['S3', 'S4', 'C5', 'S0', 'S7', 'D5', 'H3', 'H0', 'H9', 'jk', 'C2', 'C3']
    for card in card_test:
        play.add_card_and_is_snatch(card)
        print (play.my_card)
    left_cards = ['S5', 'S6', 'CA', 'CK', 'C0', 'H7']
    left_cards = play.add_left_cards(left_cards)
    print ("left cards are = ", left_cards)
    print(play.my_card)
    print (play.play_out_cards(1, []))
    #此处接收通知给current_turn_out_cards，并调用cal_self.unknown_cards()和cal_poss_no_card(current_turn_out_cards)
    print(play.play_out_cards(2, [(1, 'banker_left', 'C3'), (2, 'banker_opposite', 'S2')]))
    print (play.my_card)
    print (play.poss_no_color)