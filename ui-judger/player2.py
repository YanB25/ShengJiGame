import random

class Player(object):
    """docstring for Player"""
    def __init__(self, role):
        '''
        构造函数不会接受任何参数
        会用如下方法构造你的对象
        >>> player1 = Player()
        '''
        self.cards = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.main_value = None
        self.main_suit = None
        self.role = None
        self.have_main = False 
        self.snatch = None # ???
        self.all_cards = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.partner_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.enemy_left_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.enemy_right_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.set_role(role)

    def add_card_and_is_snatch(self, current_card):
        '''
        在发牌阶段中,每发一张牌，都会调用一次这个函数。
        如果你在得到该牌后，想要抢庄，请返回你要用来抢庄的牌，
        否则返回''

        @param current_card :: String, 
        这是一个长度为2的字符串，发牌阶段你得到的一张牌。

        @return card :: String, 
        你应该返回一个字符串。如果不抢庄，则返回空字符串 ''。
        否则返回你用来抢庄的牌，
        例如 '!3'。
        '''
        if current_card[1] == self.main_value:
            self.cards['?'].append(current_card)
        elif self.have_main and current_card[0] == self.main_suit or current_card[0] == 'j' or current_card[0] == 'J':
            self.cards['?'].append(current_card)
        else:
            self.cards[current_card[0]].append(current_card)
        if self.have_main == False and current_card[1] == self.main_value:
            return current_card
        return ''

    def add_left_cards(self, left_cards):
        '''
        只有压底牌的庄家(house_master)会被调用这个函数。
        会在发牌结束后调用。
        该函数的参数是一系列你获得的底牌（字符串列表），
        你需要返回相同数量的牌，作为你压下的底牌。

        @param left_cards :: [String]. 
        该参数是字符串列表，用于表示你得到的底牌。
        例如
        >>> player.add_left_cards(
        ...    ['!3', '#3', '%4', '&3', '?G', '#Q']
        ... )

        @return return_cards :: [String]. 
        返回字符串列表，用于表示你压下的底牌。
        注意，你必须返回与left_cards长度一样的列表。
        列表中的每个元素代表你压下的牌。请确保你压下的牌中，每张牌都是你拥有的。
        '''
        for card in left_cards:
            suit = card[0]
            if card[1] == self.main_value or suit == 'j' or suit == 'J':
                suit = '?'
            self.cards[suit].append(card)
        return self.__delete_cards(len(left_cards))

    def finish_one_round(self, current_turn_out_cards, my_turn_order):
        for people in range(my_turn_order + 1, len(current_turn_out_cards)):
            card = current_turn_out_cards[people]
            suit = card[0]
            if card[1] == self.main_value or suit == 'j' or suit == 'J':
                suit = '?'
            if people == my_turn_order + 1:
                # the people of your right hand size
                self.enemy_right_cards_info[suit].append(card)
            elif people == my_turn_order + 2:
                # the people of your partner
                self.partner_cards_info[suit].append(card)
            elif people == my_turn_order + 3:
                # the people of your left hand size
                self.enemy_left_cards_info[suit].append(card)

    def set_main_value(self, main_value):
        self.main_value = main_value
        return True 

    def set_main_color(self, suit):
        '''
        设置当前局的主花色

        @param suit :: String
        主花色
        
        @return : Nothing
        '''
        self.main_suit = suit
        self.have_main = True

    def set_role(self, role):
        '''
        **** 这一段请大家帮忙修改 ****
        通过参数role告知你，你当前的角色是什么。 
        会在发牌前调用。你不需要返回任何值。

        @param role :: String, 
        in [
            'house_master', 
            'house_peer', 
            'player_left', 
            'player_right'
        ]

        house_master: 庄家，且需要领取底牌
        house_peer: 庄家，但你不需要领取底牌（你的对家领取）
        player_left: 非庄家，且你坐在house_master的左手边
        player_right: 非庄稼，且你坐在house_master的右手边
        '''
        self.role = role

    def play_out_cards(self, turn, current_turn_out_cards):
        '''
        每次出牌时都会调用的函数。
        第一个参数告知你，现在出牌出到第几轮了。
        第二个参数告知你，这一轮已经出了牌的玩家们，出了哪些牌。

        @param turn :: integer. 
        一个整数，告诉你现在到出牌到第几轮了（从1开始算）

        @param current_turn_out_cards :: [String].
        一个字符串列表。列表的长度可能为0, 1, 2, 3,取决于你是第几个出牌的人。
        若你是第一个出牌的人，列表的长度为0.
        以此类推，若你是最后一个出牌的人，列表的长度为3.
        列表中的每个元素都是长度为2的字符串，代表牌。
        例如
        >>> player.play_out_cards(6, ['#2', '#K', '#10'])
        '''
        self.__update_other_players_cards(current_turn_out_cards)
        current_suit = 'S'
        card_index = 0
        if len(current_turn_out_cards) > 0:
            if current_turn_out_cards[0][1] == self.main_value or current_turn_out_cards[0][0] == self.main_suit or current_turn_out_cards[0][0] == 'j' or current_turn_out_cards[0][0] == 'J':
                # 如果当前轮打的是主牌
                current_suit = '?'
            else:
                current_suit = current_turn_out_cards[0][0] 
        if len(self.cards[current_suit]) > 0:
            card_index = random.randint(0, len(self.cards[current_suit]) - 1)
        else:
            for suit in self.cards.keys():
                if len(self.cards[suit]) == 0:
                    continue
                current_suit = suit
            card_index = random.randint(0, len(self.cards[current_suit]) - 1)
        card = self.cards[current_suit][card_index]
        self.cards[current_suit].remove(card)
        return card

    def show_cards(self):
        '''
        返回自己当前所有的手牌
        @return :: List of string(card)
        '''
        cards = []
        for suit in self.cards.keys():
            cards += self.cards[suit]
        return cards

    def player_init(self):
        self.cards = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.main_value = None
        self.main_suit = None
        self.role = None
        self.have_main = False 
        self.snatch = None # ???
        self.all_cards = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.partner_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.enemy_left_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}
        self.enemy_right_cards_info = {'S':[], 'H':[], 'C':[], 'D':[], '?':[]}

    def clear(self):
        self.__init__()

    def __delete_cards(self, number):
        '''
        庄家决定从手牌中放回 number 张牌作为底牌
        @return :: List of string(card)
        '''
        left_cards = []
        for i in range(number):
            # TODO: which card should be deleted
            # randomly
            card = None
            for suit in ['S', 'H', 'C', 'D']:
                if len(self.cards[suit]) > 0:
                    card_index = random.randint(0, len(self.cards[suit]) - 1)
                    card = self.cards[suit][card_index]
            self.cards[card[0]].remove(card)
            left_cards.append(card)
        return left_cards

    def __init_all_cards(self):
        '''
        初始化所有的牌 if need
        @return :: Nothing
        '''
        suits = ['S', 'H', 'C', 'D']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'J', 'Q', 'K']
        for suit in suits:
            for value in values:
                all_cards.append(suit + value)
        all_cards.append("JK")
        all_cards.append("jk")

    def __update_other_players_cards(self, current_turn_out_cards):
        '''
        记录更新左手边、对面、右手边玩家出过的牌
        @return :: nothing
        '''
        for people in range(len(current_turn_out_cards) - 1, 0, -1):
            card = current_turn_out_cards[people]
            suit = card[0]
            if card[1] == self.main_value or suit == 'J' or suit == 'j':
                suit = '?'
            if people == len(current_turn_out_cards) - 1:
                # the people of your left hand size
                self.enemy_left_cards_info[suit].append(card)
            elif people == len(current_turn_out_cards) - 2:
                # the people of your partner
                self.partner_cards_info[suit].append(card)
            else:
                # the people of your right hand size
                self.enemy_right_cards_info[suit].append(card)


if __name__ == "__main__":
    test_player1 = Player()
    test_player1.set_main_value('2')
    suit = 'S'
    for value in ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'J', 'Q', 'K']:
        card = suit + value
        return_card = test_player1.add_card_and_is_snatch(card)
        if return_card != '':
            test_player1.set_main_color(return_card[0])
            print(return_card)
    print("Before play one turn: ", end='')
    print(test_player1.show_cards())
    
    print("play out: ", end='')
    print(test_player1.play_out_cards(1, []))

    print("Before play one turn: ", end='')
    print(test_player1.show_cards())

    test_player1.clear()
    print(test_player1.show_cards())
    
