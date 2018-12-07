import pygame
import time
import os
import sys
# (D,C,H,S) + (A,2,3,4,5,6,7,8,9,0,J,Q,K)   用"jk"、"JK"分别表示小王、大王
# 黑桃-spade 红桃-heart 方快-diamond 草花-club
class Setting(object):
	"""docstring for Setting"""
	def __init__(self):
		super(Setting, self).__init__()
		self.SCREEN_WIDTH = 1000
		self.SCREEN_HEIGHT = 650

		self.background_image = 'background1.jpg'
		self.puke_backface_image = 'puke/back.jpg'
		self.master_image = 'master.jpg'

		self.scale_puke = 0.8
		self.scale_puke_back = 0.2

		self.cards_gap = 500/12

	def load_puke_backface_image(self):
		image = pygame.image.load(self.puke_backface_image)
		rect = image.get_rect()
		width, height = rect.width*self.scale_puke_back, rect.height*self.scale_puke_back
		image = pygame.transform.scale(image, (int(width), int(height)))
		image = pygame.transform.rotate(image, 90)
		return image

	def load_face_image(self, face, role):
		if face == 'JK':
			face_image = 'jk1'
		elif face == 'jk':
			face_image = 'jk2'
		else:
			face_image = face

		face_image = 'puke/' + face_image + '.jpg'
		image = pygame.image.load(face_image)
		rect = image.get_rect()
		width, height = rect.width*self.scale_puke, rect.height*self.scale_puke
		image = pygame.transform.scale(image, (int(width), int(height)))
		'''
		East means right
		South means bottom
		West means left
		North means up
		'''
		# counterclockwise rotation
		if role=='East' or role=='West':
			angle = 90
		else:
			angle = 180
		image = pygame.transform.rotate(image, angle)
		return image

	def load_master_image(self, role):
		image = pygame.image.load(self.master_image)
		if role == 'East':
			angle = 90
		elif role == 'West':
			angle = 270
		elif role == 'North':
			angle = 180
		else:
			angle = 0
		image = pygame.transform.rotate(image, angle)
		return image

class Background(object):
	"""docstring for Background"""
	def __init__(self, screen, setting):
		super(Background, self).__init__()
		self.screen = screen

		background_image = setting.background_image
		self.image = pygame.image.load(background_image)
		self.rect = self.image.get_rect()
		self.rect.width = setting.SCREEN_WIDTH
		self.rect.height = setting.SCREEN_HEIGHT

		self.image_backface = setting.load_puke_backface_image()
		self.rect_backface = self.image_backface.get_rect()
		self.rect_backface.centerx = self.rect.centerx
		self.rect_backface.centery = self.rect.centery

		self.roles = ['East', 'North', 'West', 'South']
		self.players = {}
		for role in self.roles:
			player = Player(screen, setting, role)
			self.players[role] = player

		self.point = 0
		self.level1 = 0
		self.level2 = 0

		self.clock = pygame.time.Clock()

	def initial(self):
		for role in self.roles:
			self.players[role].initial()

		self.point = 0

	# add a card in a player
	def add_card(self, card, turn):
		#pygame.time.wait(80)
		role = self.roles[turn]
		self.players[role].add_card(card)

		self.blitme()
		pygame.display.update()

	def push_cards(self, cards, turn):
		pygame.time.wait(10)
		role = self.roles[turn]
		for card in cards:
			print(role, card)
			self.players[role].push_cards(card)

		self.blitme()
		pygame.display.update()

	def make_master_player(self, inputs, outputs, turn):
		role = self.roles[turn]
		self.players[role].make_master()
		self.players[role].add_left_cards(inputs, outputs)

		self.blitme()
		pygame.display.update()

	def add_cards_over(self, inputs, outputs, main_color, master):
		self.make_master_player(inputs, outputs, master)
		for player in self.players.values():
			player.sort_cards(main_color)

		self.blitme()
		pygame.display.update()

	def turn_over(self):
		pygame.time.wait(50)
		for player in self.players.values():
			player.del_out_cards()
		self.blitme()
		pygame.display.update()

	def update_point(self, point, level1, level2):
		self.point = point
		self.level1 = level1
		self.level2 = level2
		self.blitme()
		pygame.display.update()

	def draw_level(self):
		text = 'E,W: ' + str(self.level1) + ' -- ' + 'S,N: ' + str(self.level2)
		textSurface = self.text_image(text, (255, 0, 0), 20)
		textRect = textSurface.get_rect()
		textRect.bottom = self.rect.height
		textRect.left = 0

		self.screen.blit(textSurface, textRect)

	def text_image(self, text, color, size):
		font = pygame.font.Font('freesansbold.ttf', size)
		textSurface = font.render(text, True, color)
		return textSurface

	def draw_point(self):
		text = 'Point: ' + str(self.point)
		textSurface = self.text_image(text, (255,0,0), 35)
		textRect = textSurface.get_rect()
		textRect.bottom = self.rect.height
		textRect.right = self.rect.width

		self.screen.blit(textSurface, textRect)

	def draw_fps(self):
		fps = self.clock.get_fps()
		text = 'FPS: ' + str(int(fps))
		textSurface = self.text_image(text, (255,255,255), 20)
		textRect = textSurface.get_rect()
		textRect.top = 0
		textRect.left = 0

		self.screen.blit(textSurface, textRect)

	def blitme(self):
		self.clock.tick(30)
		self.screen.blit(self.image, self.rect)
		# draw fps
		self.draw_fps()
		# draw level
		self.draw_level()
		# draw center puke card
		rect_temp = pygame.Rect(self.rect_backface)
		for a in range(5):
			rect_temp.centerx = int(rect_temp.centerx - a*0.5)
			rect_temp.centery = int(rect_temp.centery - a*0.5)
			self.screen.blit(self.image_backface, rect_temp)
		# draw each player
		for player in self.players.values():
			player.blitme()
		# draw point
		self.draw_point()

class Puke(object):
	"""dscreen, settingtring for Puke"""
	def __init__(self, screen, setting, face, role):
		super(Puke, self).__init__()
		self.screen = screen
		self.face = face

		self.image = setting.load_face_image(face, role)
		self.rect = self.image.get_rect()

	def blitme(self, centerx, centery):
		self.rect.centerx = int(centerx)
		self.rect.centery = int(centery)
		self.screen.blit(self.image, self.rect)
		
class Player(object):
	"""dscreen, settingtring for Player"""
	def __init__(self, screen, setting, role):
		self.screen = screen
		self.setting = setting
		self.gap = setting.cards_gap
		width, height = setting.SCREEN_WIDTH, setting.SCREEN_HEIGHT
		if role == 'East':
			self.centerx = width - width / 10
			self.centery = height / 2
			self.out_centerx = 7 * width / 10
		elif role == 'South':
			self.centerx = width / 2 
			self.centery = height - height / 10
			self.out_centery = 7 * height / 10
		elif role == 'West':
			self.centerx = width / 10 
			self.centery = height / 2
			self.out_centerx = 3 * width / 10
		else:
			self.centerx = width / 2 
			self.centery = height / 10
			self.out_centery = 3 * height / 10

		self.role = role
		self.cards = []
		self.out_cards = []

		# master player
		self.master = False
		self.master_image = ''
		self.master_rect = ''

	def initial(self):
		for card in self.cards:
			del card
		for card in self.out_cards:
			del card
		self.cards = []
		self.out_cards = []
		self.master = False

	def add_card(self, face):
		new_card = Puke(self.screen, self.setting, face, self.role)
		self.cards.append(new_card)

	def make_master(self):
		self.master = True
		self.master_image = self.setting.load_master_image(self.role)
		self.master_rect = self.master_image.get_rect()
		width, height = self.setting.SCREEN_WIDTH, self.setting.SCREEN_HEIGHT
		if self.role == 'East':
			self.master_rect.centerx = width - width/10
			self.master_rect.centery = height/2 + self.gap*7
		elif self.role == 'West':
			self.master_rect.centerx = width/10
			self.master_rect.centery = height/2 - self.gap*7
		elif self.role == 'North':
			self.master_rect.centerx = width/2 + self.gap*7
			self.master_rect.centery = height / 10
		else:
			self.master_rect.centerx = width/2 - self.gap*7
			self.master_rect.centery = height - height/10

	def sort_cards(self, main_color):
		colors = ('H', 'S', 'D', 'C')
		nums = ('A', 'K', 'Q', 'J', '0', '9','8','7','6','5','4','3','2')
		power = {nums[index]: index for index in range(13)}
		cards = []
		color_cards = {color: [] for color in colors}
		for card in self.cards:
			face = card.face
			# big queen and small queen
			if face=='JK' or face=='jk':
				cards.append(card)
				continue
			color, num = face[0], face[1]
			color_cards[color].append((power[num], card))
 
		for L in color_cards.values():
			L.sort(key=lambda e: e[0])
		# main_colors
		for p, card in color_cards[main_color]:
			cards.append(card)
		# other color
		for color in colors:
			if color == main_color:
				continue
			for p, card in color_cards[color]:
				cards.append(card)

		self.cards = cards

	def push_cards(self, face):
		for card in self.cards.copy():
			if card.face == face:
				self.out_cards.append(card)
				self.cards.remove(card)
				return

	def add_left_cards(self, inputs, outputs):
		for face in inputs:
			self.add_card(face)

		for face in outputs:
			self.push_cards(face)

		self.del_out_cards()

	def del_out_cards(self):
		for card in self.out_cards:
			del card
		self.out_cards = []		

	def blitme(self):
		#draw master
		if self.master:
			self.screen.blit(self.master_image, self.master_rect)
		# draw cards in hand of each player
		n = len(self.cards)
		if self.role == 'West':
			y1 = (2*self.centery - (n-1)*self.gap)/2
			for a in range(n):
				self.cards[a].blitme(self.centerx, y1)
				y1 += self.gap
		elif self.role == 'East':
			yn = (2*self.centery + (n-1)*self.gap)/2
			for a in range(n):
				self.cards[a].blitme(self.centerx, yn)
				yn -= self.gap
		elif self.role == 'South':
			x1 = (2*self.centerx - (n-1)*self.gap)/2
			for a in range(n):
				self.cards[a].blitme(x1, self.centery)
				x1 += self.gap
		else:
			xn = (2*self.centerx + (n-1)*self.gap)/2
			for a in range(n):
				self.cards[a].blitme(xn, self.centery)
				xn -= self.gap

		# draw the cards pushing out
		m = len(self.out_cards)
		if m == 0:
			return
		if self.role == 'West':
			y = (2*self.centery - (m-1)*self.gap)/2
			for a in range(m):
				self.out_cards[a].blitme(self.out_centerx, y)
				y += self.gap
		elif self.role == 'East':
			y = (2*self.centery + (m-1)*self.gap)/2
			for a in range(m):
				self.out_cards[a].blitme(self.out_centerx, y)
				y -= self.gap
		elif self.role == 'South':
			x = (2*self.centerx - (m-1)*self.gap)/2
			for a in range(m):
				self.out_cards[a].blitme(x, self.out_centery)
				x += self.gap
		else:
			x = (2*self.centerx + (m-1)*self.gap)/2
			for a in range(m):
				self.out_cards[a].blitme(x, self.out_centery)
				x -= self.gap

def check_events():
    """Respond to keypresses and mouse events."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
        	sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
        	mouse_x, mouse_y = pygame.mouse.get_pos()
        	#check_play_button(mouse_x, mouse_y)

def play_game():
    # Initialize pygame
    pygame.init()
    setting = Setting()

    SCREEN_WIDTH, SCREEN_HEIGHT = setting.SCREEN_WIDTH, setting.SCREEN_HEIGHT
    x, y = 150, 60
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("升级")

    background = Background(screen, setting)
    # (main loop)
    background.turn_over()
    while True:

        check_events()
        background.blitme()
        pygame.display.update()

if __name__=="__main__":
	play_game()
