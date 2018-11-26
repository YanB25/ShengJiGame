import random

class Player(object):
    """docstring for Player"""
    def __init__(self):
        '''
        构造函数不会接受任何参数
        会用如下方法构造你的对象
        >>> player1 = Player()
        '''
        self.cards = {'!':[], '&':[], '%':[], '#':[], '?':[]}
        self.main_value = None
        self.main_suit = None
        self.role = None
        self.have_main = False 
        self.snatch = None # ???
        self.all_cards = {}
        self.partner_cards_info = {}
        self.enemy_left_cards_info = {}
        self.enemy_right_cards_info = {}

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
        self.cards[current_card[0]].append(current_card)
        # if self.snatch == current_card.value and self.have_main == False:
        if self.have_main == False:
            # TODO: judge snatch or not
            for suit in self.cards.keys():
                if suit + self.main_value in self.cards[suit]:
                    # I have main value card
                    if len(self.cards[suit]) > 10:
                        return suit + self.main_value
            # return current_card
        # else:
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
            self.cards[suit].append(card)
        return self.__delete_cards(len(left_cards))

    def finish_one_round(self, current_turn_out_cards):
        # TODO: do something
        pass

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
        # return True

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
        #TODO: get cards should be played out
        # play out cards randomly
        current_suit = '!'
        card_index = 0
        if len(current_turn_out_cards) > 0:
            current_suit = current_turn_out_cards[0][0]
        if len(self.cards[current_suit]) != 0:
            card_index = random.randint(0, len(self.cards[current_suit]) - 1)
        else:
            for suit in self.cards.keys():
                if len(self.cards[suit]) == 0:
                    continue
                card_index = random.randint(0, len(self.cards[suit]) - 1)
                current_suit = suit
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
            for suit in ['!', '&', '%', '#']:
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
        suits = ['!', '&', '%', '#']
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'J', 'Q', 'K']
        for suit in suits:
            for value in values:
                all_cards.append(suit + value)
        all_cards.append("?G")
        all_cards.append("?g")

    def __update_other_players_cards(self, current_turn_out_cards):
        '''
        记录更新左手边、对面、右手边玩家出过的牌
        @return :: nothing
        '''
        for people in range(len(current_turn_out_cards) - 1, 0, -1):
            for card in current_turn_out_cards[people]:
                suit = card[0]
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
    suit = '!'
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
