import random

# import player1.Player as PlayerOne
# #TODO: below three line should change
# import player1.Player as PlayerTwo
# import player1.Player as PlayerThree
# import player1.Player as PlayerFour
from player1 import Player

# pl1 = PlayerOne
# pl2 = PlayerTwo
# pl3 = PlayerThree
# pl4 = PlayerFour
# player_ls = [pl1, pl2, pl3, pl4]
pl1 = Player()
pl2 = Player()
pl3 = Player()
pl4 = Player()
player_ls = [pl1, pl2, pl3, pl4]
class Judger():
    def __init__(self, player_ls):
        '''
        @param player_ls :: [Player], a list of player objects.

        >>> judger = Judger([pl1, pl2, pl3, pl4])
        >>> judger.run()
        '''
        self.__main_card = None # 主牌
        self.__main_value = '2' # 先打2
        self.__main_suit = None
        self.__deskcards = None # 底牌
        self.__points = 0 # 这一轮拿到的分

        # 下面四个是四个角色在 self.player_ls 里的索引
        self.house_master_id = None
        self.house_peer_id = None
        self.player_left_id = None
        self.player_right_id = None

        self.player_ls = player_ls

    def run(self):
        self.startPrepare() # Judger类的内部初始化工作
        self.startGame()

    def startPrepare(self):
        # 类里会用self.player_card_tracking来存储玩家的牌
        # 关于这个结构的具体格式见下面这个函数
        self.__init_tracking()
        self.__init_cards() # 初始化self.__cards为乱序的全部的牌

    def startGame(self):
        # 公布这一轮打几
        for player in self.player_ls:
            player.clear()
            player.set_main_value(self.__main_value)

        self.hand_out_cards() #发牌
        self.play_out() # 打牌
    
    def hand_out_cards(self):
        '''
        发牌
        '''
        # 决定先发谁的牌
        first_player = Judger.cards2int(self.__cards[0]) % 4
        # 少发6张留做底牌
        i = first_player
        for card in self.__cards[:-6]:
            suit = card[0]
            ret = self.player_ls[i].add_card_and_is_snatch(card)
            self.__tracking[i][suit].append(card) # 记录玩家获得的牌
            self.show_all() 
            if ret != '':
                if ret == '?G' or ret == '?g' or ret[1] != self.__main_value:
                    print("ERROR 02: {} use {} to be house, which is not allowed".format(i, ret))
                    self.exit()
                # 玩家想要抢庄
                if not ret in self.__tracking[i][ret[0]]:
                    print('ERROR 01: {} use {} to be house, but he do not have it.'.format(i, ret))
                    self.exit()
                # 检验通过
                self.__main_card = ret
                self.__main_suit = ret[0]
                print('house card is {}'.format(self.__main_card))

                self.player_ls[i].set_role('house_master')
                self.house_master_id = i
                self.player_ls[(i+1) % 4].set_role('player_right')
                self.player_right_id = (i + 1) % 4
                self.player_ls[(i+2) % 4].set_role('house_peer')
                self.house_peer_id = (i + 2) % 4
                self.player_ls[(i+3) % 4].set_role('player_left')
                self.player_left_id = (i + 3) % 4

                for player in self.player_ls:
                    player.set_main_color(self.__main_suit)
            
            i = (i + 1) % 4
        # 有人做庄吗？
        if self.house_master_id is None:
            assert(self.__main_card is None)
            print('MSG 01: no one choose to be house.')
            self.player_ls[0].set_role('house_master')
            self.house_master_id = 0
            self.player_ls[1].set_role('player_right')
            self.player_right_id = 1
            self.player_ls[2].set_role('house_peer')
            self.house_peer_id = 2
            self.player_ls[3].set_role('house_left')
            self.player_left_id = 3

            main_suit = self.__cards[-3][0]
            self.__main_suit = main_suit
            self.__main_card = '' + self.__main_suit + self.__main_value
            for player in self.player_ls:
                player.set_main_color(self.__main_suit)
        if self.__main_suit is None:
            print('MSG 02: no one put the main suit. again.')
            self.__main_card = self.__cards[-3]
            self.__main_suit = self.__main_card[0]
            for player in self.player_ls:
                player.set_main_color(self.__main_suit)
        print('main card {}, main suit {}, main value {}'.format(
            self.__main_card,
            self.__main_suit,
            self.__main_value
        ))
        
        # 下面压底牌
        deskcards = self.__cards[-6:]
        print('deskcards {}'.format(deskcards))

        self.__deskcards = self.player_ls[self.house_master_id].add_left_cards(deskcards)
        print('return deskcards {}'.format(self.__deskcards))
        assert(len(self.__deskcards) == len(deskcards))

        # 记录一下庄主有的牌
        hi = self.house_master_id
        for card in deskcards:
            self.__tracking[hi][card[0]].append(card)

        print('send deskcard to house master.')
        self.show_all()

        # 检查一下庄主的返回是否正确
        for card in self.__deskcards:
            suit = card[0]
            if card not in self.__tracking[hi][suit]:
                # 庄主有这张牌吗？
                print('ERROR 03: house return {}({}) as deskcard but he do not have it.'.format(self.__deskcards, card))
                self.exit()
            else:
                # 检查通过
                self.__tracking[hi][suit].remove(card)

        # 把主牌移到主牌的位置
        for i in range(4):
            self.__tracking[i]['?'] += [i for i in self.__tracking[i][self.__main_suit]]
            self.__tracking[i][self.__main_suit] = []
            for suit in ['#', '%', '&', '!']:
                mc = '' + suit + self.__main_value
                if mc in self.__tracking[i][suit]:
                    self.__tracking[i][suit].remove(mc)
                    self.__tracking[i]['?'].append(mc)
        print('after house return deskcards')
        self.show_all()

    def play_out(self):
        start_index = self.house_master_id
        for round in range(12):
            has_send = []
            record_send = ['--' for i in range(4)]
            max_card = None
            max_idx = None
            first_card = None
            points = 0
            for who in range(4):
                i = (start_index + who) % 4
                ret = self.player_ls[i].play_out_cards(round, has_send)
                # 下面检测 ret是否合法
                self.__check_follow_suit(first_card, i, ret)
                self.__check_exist_and_remove(i, ret)

                if max_card is None: 
                    max_card = ret
                    max_idx = i
                if first_card is None:
                    first_card = ret

                has_send.append(ret)
                record_send[i] = ret
                if ret[1] == '5':
                    points += 5
                elif ret[1] == 'X' or ret[1] == 'K':
                    points += 10

                if self.__card_lt(first_card, max_card, ret):
                    # print('DEBUG: cards {} > max card {}'.format(ret, max_card))
                    max_card = ret
                    max_idx = i
                print(record_send, max_card)
            # 通知所有玩家所有的牌
            for player in self.player_ls:
                player.finish_one_round(has_send)
            # 结算分
            if max_idx == self.player_left_id or max_idx == self.player_right_id:
                self.__points += points
                print('({}) win, get point {}[{}]'.format(max_idx, points, self.__points))
            else:
                print('({}) win, point not change(this round {})[{}]'.format(max_idx, points, self.__points))
            # 更新下一轮的出牌者
            start_index = max_idx
                
    def __is_main(self, card):
        assert(len(card) == 2)
        return card[0] == self.__main_suit or card[0] == '?' or card[1] == self.__main_value
    def __card_lt(self, first_card, left_card, right_card):
        '''
        这个比较函数有一个重要的隐含规则
        *** left card 比 right card 先出 ***
        '''
        orders = list('23456789XJQKAgG')
        left_main = self.__is_main(left_card)
        right_main = self.__is_main(right_card)
        if left_main and not right_main:
            return False
        if not left_main and right_main:
            return True
        if not left_main and not right_main:
            # 都不是主牌
            left_follow_suit = left_card[0] == first_card[0]
            right_follow_suit = right_card[0] == first_card[0]
            if left_follow_suit and not right_follow_suit:
                return False
            elif not left_follow_suit and right_follow_suit:
                True
            elif not left_follow_suit and not right_follow_suit:
                return False
            else:
                # both follow suit
                return orders.index(left_card[1]) < orders.index(right_card[1])
        else:
            # 都是主牌
            if (left_card[1] == right_card[1] == self.__main_value):
                left_pivot_value = left_card[0] == self.__main_suit
                right_pivot_value = right_card[0] == self.__main_suit
                if (left_pivot_value):
                    return False
                if (right_pivot_value):
                    return True
                # 两个都是主牌面，但是都不是主色的主牌
                return False
            m_orders = orders[:]
            m_orders.remove(self.__main_value)
            m_orders.insert(len(m_orders)-2, self.__main_value)
            return m_orders.index(left_card[1]) < m_orders.index(right_card[1])


    def __init_tracking(self):
        '''
        初始化self.player_cards_tracking
        它是个长度为4的列表，对应4个玩家。每个元素是一个字典
        字典的格式如`obj`所示。
        '''
        self.__tracking = [
            {
                '#': [],
                '%': [],
                '&': [],
                '!': [],
                '?': []
            } for i in range(4)
        ]
    def __init_cards(self):
        '''
        get self.__cards ready.
        self.__cards, [Str], a whole list of cards in random order.
        '''
        suits = list('#%&!')
        nums = list('A23456789XJQK')
        self.__cards = ['?g', '?G']
        for suit in suits:
            for num in nums:
                # it is just suit + num. I write in this way to be more clear
                self.__cards.append('{}{}'.format(suit, num))
        random.shuffle(self.__cards)
    @staticmethod
    def cards2int(card):
        '''
        接受一张牌，返回它的面值
        @param card :: Str, of length 2
        @return Int, the num of the cards
        A23456789XJQK to 1 ~ 13
        ghost and Ghost to 0
        '''
        assert(len(card) == 2)
        if card == '?g' or card == '?G':
            return 0
        ls = list('A23456789XJQK')
        return ls.index(card[1]) + 1
    def exit(self):
        self.show_all()
        exit(1)
    def show_all(self):
        for i in range(4):
            print(self.__tracking[i])
        print('house is {}'.format(self.house_master_id))
        # print('main card {}, main value {}, main suit {}'.format(
        #     self.__main_card,
        #     self.__main_value,
        #     self.__main_suit
        # ))
        print()
    def __check_exist(self, player_id, card):
        '''
        检查玩家是否有这张牌
        '''
        suit = '?' if self.__is_main(card) else card[0]
        if card not in self.__tracking[player_id][suit]:
            print('ERROR 05: player {} not have cards {}'.format(player_id, card))
            self.exit()
    def __check_exist_and_remove(self, player_id, card):
        self.__check_exist(player_id, card)
        suit = '?' if self.__is_main(card) else card[0]
        self.__tracking[player_id][suit].remove(card)
    def __check_follow_suit(self, first_card, player_id, card):
        '''
        检查 player_id出的牌card，是否符合first_card的花色
        '''
        if first_card is None:
            return
        first_suit = '?' if self.__is_main(first_card) else first_card[0]
        card_suit = '?' if self.__is_main(card) else card[0]
        has_suit = self.__tracking[player_id][first_suit] != []
        if has_suit and card_suit != first_suit:
            print('ERROR 06. player {} send card {}, not follow card {}'.format(player_id, card, first_card))
            print('ERROR 06. first_suit {}, card_suit{}'.format(first_suit, card_suit))
            self.exit()


if __name__ == "__main__":
    judger = Judger(player_ls)
    judger.run()
