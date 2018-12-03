# (D,C,H,S) + (A,2,3,4,5,6,7,8,9,0,J,Q,K)   用"jk"、"JK"分别表示小王、大王
# 黑桃-spade 红桃-heart 方快-diamond 草花-club
from os import rename
from os import listdir
from os.path import isfile, join
def rename_puke():
	pukes = []
	for f in listdir():
		if isfile(f):
			if f == 'back.jpg':
				continue
			fix = f.split('.')
			if fix[1] == 'jpg':
				pukes.append(int(fix[0]))

	pukes.sort()
	colors = ('S','H','C','D')
	nums = ('3','4','5','6','7','8','9','0','J','Q','K','A','2',)
	#print(str(pukes[0])+'.jpg', 'jk'+'.jpg')
	#print(str(pukes[1])+'.jpg', 'JK'+'.jpg')
	rename(str(pukes[0])+'.jpg', 'jk1'+'.jpg')
	rename(str(pukes[1])+'.jpg', 'jk2'+'.jpg')
	for puke in pukes[2:]:
		index = puke - 3
		color =  index // 13
		num = index % 13
		before = str(puke) + '.jpg'
		after = colors[color] + nums[num] + '.jpg'
		#print(before, after)
		rename(before, after)

rename_puke()