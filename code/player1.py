class Player(object):
	"""docstring for Player"""
	def __init__(self):
		self.cards = []
		self.main_value = 0
		self.main_color = 'Spade'
		self.snatch = False 
		self.role = 0
		self.all_cards = {}
		self.partner_cards_info = {}
		self.ememy_left_cards_info = {}
		self.ememy_right_cards_info = {}
		self.have_main = False 


	def add_card_and_is_snatch(self, current_card):
		self.cards.append(current_card)
		if self.snatch == current_card.value and self.have_main == False:
			return current_card
		else:
			return 'None'

	def delete_cards(self):
		left_cards = ()
		return left_cards

	def add_left_card(self, left_cards):
		self.cards += left_cards
		return delete_cards()

	def finish_one_round(self, current_turn_out_cards):
		pass

	def set_main_value(self, main_value):
		self.main_value = main_value
		return True 

	def set_mian_color(self, color):
		self.main_color = color
		return True

	def set_init(self):
		self.main_value = 0
		self.main_color = 'Spade'
		self.role = 0
		self.cards = []

	def  set_role(self, role):
		self.role = role

	def play_out_cards(self, turn, current_turn_out_cards):
		pass

	def show_cards(self):
		return self.cards

