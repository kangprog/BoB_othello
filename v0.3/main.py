#! 클라이언트가 계산을 다해야한다. board도 새로...
# GUI도 board가 따로 존재 해야한다?
# 클라이언트에서 놓은 돌을 공유자원으로 받아서 GUI는 돌이 놓여지는것과 뒤집히는것을 보여주기만 한다. 
# [[상대방이 놓은돌], [내가 놓은돌]] 이런식으로 공유자원 !.

# pygame 소켓통신 하는 것좀 찾아봐야함. 매우중요

import pygame as pg
import numpy as np
import logging, log
import threading
import socket
from threading import Thread
from threading import Lock

import time
import random

from util import *
from protocol_enum import *

log = logging.getLogger("othello")

''' ===================================================  client setting '''
HOST = '127.0.0.1' # 이후에 파라미터로 서버 IP를 받게 하는게 다른 서버에 붙는데 편할거다.
PORT = 8472
		
''' ===================================================  color setting '''
GREEN = (34, 116, 28)
black = (0, 0, 0)

color = GREEN

''' ===================================================  size setting '''
window_size = [450, 450]
tile_size = 50

width = tile_size
height = tile_size
margin = 5
stone_margin = 6

''' ===================================================  array ( back ground ) '''

grid = np.zeros((8,8), dtype=int)

''' ===================================================  image setting '''
white_stone = pg.image.load("white_stone.png")
black_stone = pg.image.load("black_stone.png")

''' ===================================================  pygame main '''

to_flag = None
fm_flag = None
my_location = []
you_location = []
my_possible_location = []
my_color = None

mtx_lock = Lock()



TIMER_SEC = 2000 # 4000ms
TIMER_SEC_EVENT = pg.USEREVENT + 1
pg.time.set_timer(TIMER_SEC_EVENT, TIMER_SEC) # 4000ms 마다 이벤트 발생시키기.


class Othello():
	def __init__(self):
		global to_flag
		global fm_flag
		global my_location
		global you_location
		global my_possible_location
		global my_color
		global mtx_lock
		
		pg.init()

		self.screen = pg.display.set_mode(window_size) # window size setting
		pg.display.set_caption("Othello") # title setting
		self.clock = pg.time.Clock() # frame to seconds, normal 30, 60


		pg.image.load("white_stone.png")
		pg.image.load("black_stone.png")

		self.showBoard()

	def runGame(self):
		global to_flag
		global fm_flag
		global my_location
		global you_location
		global my_possible_location
		global my_color
		global mtx_lock
		#mtx_lock.acquire()
		
		self.done = False

		self.cnt = 0
		while not self.done:			
			for self.event in pg.event.get():
				if self.event.type == pg.QUIT:
					self.done = True
				#
				# 4000ms 마다 이벤트발생 (내가 놓은 돌의 위치 상대에 전송)
				# 만약 4000ms안에 상대방의 돌이 안온다면? 에러날꺼같은데?
				# 일단 내꺼 2개 켰을땐 문제 1도없음 .
				#
				elif fm_flag == True and self.event.type == TIMER_SEC_EVENT:
					random_put_stone = random.choice(my_possible_location)
					# try: # 놓을곳이 없는경우 턴을 그냥 넘기기위해 빈 값을 넘겨보자
						# random_put_stone = random.choice(my_possible_location)
					# except:
						# my_location = None
						# self.cnt = 0
						# fm_flag = None
						# to_flag = True
						# self.done = True
						# continue
					
					self.col = random_put_stone[1]
					self.row = random_put_stone[0]
					
					try: 
						#
						# 돌 중복 및 턴 체크
						#
						if grid[self.row][self.col] == 1 or grid[self.row][self.col] == 2:
							log.warning("location exist")
							continue
						else:
							#
							# 돌을 놓을 수 있는곳인지 체크
							#
							if not self.checkLocation(self.col, self.row, my_color):
								log.error("unavailable location")
								continue
							
							#
							# 내가 놓고자 하는곳에 놓는다.
							#
							if my_color == Color.BLACK:
								self.putStone(black_stone, self.col, self.row, my_color)
							else:
								self.putStone(white_stone, self.col, self.row, my_color)
							
							my_location = [self.row, self.col] # 상대에게 보내기 위해 내가 방금 놓은 위치를 저장한다.
							
							self.cnt = 0
							fm_flag = None # from_flag : 상대가 수를 놓았으면 = true, 내가 놓으면 = None
							to_flag = True # to_flag : 내가 상대에게 보낼 상태이다 = true , 상대를 기다린다 = None.
							
							#
							# 상대방에게 내가 놓은 수를 소켓을 통해 보낸다.
							#
							sockSend()
						
					except IndexError: # 바깥에 테두리 누를경우 out of boundary
						log.error(" out of boundary")
						continue


			#
			# 내 차례일때, 상대방이 놓은 수가 존재하면, 해당 위치에 상대 색의 돌을 놓고 해당되는 돌들을 뒤집는다.
			#
			if self.cnt != 1 and you_location != [] :				
				if fm_flag == True:
					if grid[you_location[0]][you_location[1]] == 1 or grid[you_location[0]][you_location[1]] == 2:
						log.warning("location exist")
						self.cnt = 1
						continue
					if my_color == Color.BLACK: #black
						self.putStone(white_stone, you_location[1], you_location[0], 2)
					if my_color == Color.WHITE: #white
						self.putStone(black_stone, you_location[1], you_location[0], 1)
					self.cnt = 1
					
			

			pg.display.update()
		
		#mtx_lock.release()	
		pg.quit()

	
	def showBoard(self): # 초기 보드판 (8x8 grid)		
		for self.row in range(8):
			for self.col in range(8):
				self.initStone((self.col, self.row))
					
		self.clock.tick(30)
		pg.display.flip()
	
	
	def initStone(self, location): # 초기 보드판 세팅, (흰 검 검 흰)
		self.location = location
		
		if (self.location == (3,3) or self.location == (4,4)):
			self.initPutStone(white_stone, self.location[0], self.location[1])
			grid[self.location[0]][self.location[1]] = Color.WHITE
			
		elif (self.location == (3,4) or self.location == (4,3)):
			self.initPutStone(black_stone, self.location[0], self.location[1])
			grid[self.location[0]][self.location[1]] = Color.BLACK
			
		else:
			pg.draw.rect(self.screen, color, [(margin + width) * self.location[0] + margin, (margin + height) * self.location[1] + margin, width, height])
		
		
	def initPutStone(self, obj, col, row): # 초기 돌 이미지 추가
		self.obj = obj
		self.col = col
		self.row = row
		
		self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
	
	
	def putStone(self, obj, col, row, color): # 돌 놓을때마다 이미지 추가
		self.obj = obj
		self.col = col
		self.row = row
		self.my_color = color
		
		#
		# 내가 놓은 곳의 위치를 표시하고, 뒤집히는 돌들까지 체크 후 뒤집는다.
		#
		if self.my_color == Color.BLACK: # 내가 검정색이면? or 상대방이 놓은 돌의 색이면?
			reverse_stone_list = self.getReversedPosition(grid, Color.BLACK, self.row, self.col)
			for y, x in reverse_stone_list:
				self.screen.blit(self.obj, ((margin + width) * x + margin, (margin + height) * y + margin))
				grid[y][x] = Color.BLACK
			self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
			grid[self.row][self.col] = Color.BLACK
		
		else: # 내가 하얀색이면? or 상대방이 놓은 돌의 색이면?
			reverse_stone_list = self.getReversedPosition(grid, Color.WHITE, self.row, self.col)
			for y, x in reverse_stone_list:
				self.screen.blit(self.obj, ((margin + width) * x + margin, (margin + height) * y + margin))
				grid[y][x] = Color.WHITE
			self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
			grid[self.row][self.col] = Color.WHITE
			
		print (grid) # [debug] board 진행 상황 print
		
		
	def checkLocation(self, col, row, color): # 놓을 수 있는곳인가?를 체크하는 함수.
		self.col = col
		self.row = row
		self.my_color = color

		if color == Color.BLACK:
			result = self.getAvailablePosition(grid, Color.BLACK)
			if not ((self.row, self.col) in result):
				return False				
		else:
			result = self.getAvailablePosition(grid, Color.WHITE)
			if not ((self.row, self.col) in result):
				return False	
				
		return True
		
	def chkArrow(self, map, color, x, y, direction):  # x,y 좌표로부터 direction방향까지 뒤집힐 수 있는 돌을 반환하는 함수
		result = []
		while True:
			x += direction[0]     #direction 방향으로 이동
			y += direction[1]
			if not ((0 <= x <= 7) and (0 <= y <= 7)): # 맵 바운더리 체크
				break
			nowPositionColor = map[x][y]   # 해당 위치에 있는 돌을 가져옴
			if nowPositionColor == 0:   # 공백이면 반환 x
				break
			if nowPositionColor == color:   # 내 돌 색깔이면 리스트 리턴  
				return result
			result.append((x, y))     # 상대 돌 색깔이면 리스트에 삽입
		return []
	
	def getReversedPosition(self, map, color, x, y):
		self.direction = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]   # 8개의 방향
		result = []
		for dir in self.direction:   # 모든 방향으로 탐색
			tmpList = self.chkArrow(map,color,x,y,dir)   # 해당 방향에 뒤집을 돌 리스트
			if tmpList:  # 뒤집을 돌 있냐?
				result += tmpList  # 리스트 추가
		return result  # 뒤집을 수 있는 돌 모두 리턴
	
	def getAvailablePosition(self, board, color):
		result = []
		for i, j in zip(*np.where(board == 0)):
			if self.getReversedPosition(board,color,i,j):  # 해당 좌표가 비어있고, 해당 방향에서 뒤집을 수 있는 돌 리스트가 비어있지 않으면
				result.append((int(i),int(j)))  #좌표 기입
		return result  # 착수 가능한 좌표 리스트 반환
	
	
	


''' =============================================== 통신!!! '''	
	
def sockRecv(): # 계속해서 받자받자받자~
	while 1:
		try:
			msg = deserialize(sock)
		except socket.timeout:
			continue
		
		print(msg)
		
		if msgTypeCheck(msg) == False: break
		
		
def sockSend(): # 보낼때만 보내보내보내~
	global to_flag
	global fm_flag
	global my_location
	global you_location
	global my_possible_location
	global my_color
	global mtx_lock

	#time.sleep(1)
	
	if to_flag == True:		
		sock.sendall(serialize({
			"type": ClntType.PUT,
			"point": my_location
			}))
		to_flag = None
	else:
		pass

	
def msgTypeCheck(msg):
	global to_flag
	global fm_flag
	global my_location
	global you_location
	global my_possible_location
	global my_color
	global mtx_lock

	if msg["type"] == MsgType.READY:
		log.info(" READY ")
		
	elif msg["type"] == MsgType.START:
		log.info(" GAME START ")
		my_color = msg["color"]		
		
	elif msg["type"] == MsgType.TURN:
		fm_flag = True
		time_limit = msg["time_limit"]
		opponent_put = msg["opponent_put"] # 상대방이 놓은 위치
		changed_points = msg["changed_points"] # 상대방이 놓은 수로 인해 뒤집어진 돌 리스트
		available_points = msg["available_points"] # 내가 놓을 수 있는 위치들.
		
		if opponent_put != None:
			you_location = opponent_put
		
		if available_points != None:
			my_possible_location = available_points

	
	elif msg["type"] == MsgType.NOPOINT:
		fm_flag = True
		opponent_put = msg["opponent_put"] # 상대방이 놓은 위치
		you_location = opponent_put
		
	elif msg["type"] == MsgType.GAMEOVER:
		# fm_flag = True
		# opponent_put = msg["opponent_put"] # 상대방이 마지막으로 놓은 위치
		# if opponent_put != None:
			# you_location = opponent_put
		#print (msg["result"])
		return False
		
	return True
	
'''=================================================================  '''
	
if __name__ == "__main__":
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	sock.settimeout(1)

	t3 = threading.Thread(target = sockRecv)
	t3.start()

	othello = Othello()
	othello.runGame()