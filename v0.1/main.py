import pygame as pg
import numpy as np
import logging, log

import threading


log = logging.getLogger("othello")

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
# grid = [ [0] * 8 for x in range(8)]

grid = np.zeros((8,8), dtype=int)

''' ===================================================  image setting '''
white_stone = pg.image.load("white_stone.png")
black_stone = pg.image.load("black_stone.png")

''' ===================================================  pygame main '''

class Othello():
	def __init__(self):
		pg.init()

		self.screen = pg.display.set_mode(window_size) # window size setting
		pg.display.set_caption("Othello") # title setting
		self.clock = pg.time.Clock() # frame to seconds, normal 30, 60


		pg.image.load("white_stone.png")
		pg.image.load("black_stone.png")

		self.show_board()
		
	def run_game(self):
		self.done = False
		
		self.cnt = 0
		while not self.done:
			for self.event in pg.event.get():
				if self.event.type == pg.QUIT:
					self.done = True
				elif self.event.type == pg.MOUSEBUTTONDOWN:
					self.pos = pg.mouse.get_pos()
					self.col = self.pos[0] // (width + margin)
					self.row = self.pos[1] // (height + margin)
			
					try: # 돌 중복 및 턴 체크
						if grid[self.row][self.col] == 1 or grid[self.row][self.col] == 2:
							print(grid[self.col][self.row])
							print (self.col, self.row)
							log.warning("location exist")
							continue
						else:
							if (self.cnt % 2 == 0):
								#
								# 돌을 놓을 수 있는곳만 정해주는 함수.
								# 놓았을 경우, 뒤집는거까지 해야한다.
								#
								if not self.check_location(self.col, self.row, self.cnt):
									log.error("unavailable location")
									continue
									
								self.put_stone(black_stone, self.col, self.row, self.cnt)
								# grid[self.col][self.row] = 1 # <value> black 1 , white 2
								
							else:
								if not self.check_location(self.col, self.row, self.cnt):
									log.error("unavailable location")
									continue
									
									
								self.put_stone(white_stone, self.col, self.row, self.cnt)
								# grid[self.col][self.row] = 2
							
							self.cnt += 1
						log.debug("col : " + str(self.col) + "\trow : " + str(self.row) + "\tdata : " + str(grid[self.col][self.row]) )
						
					except IndexError:
						log.error(" out of boundary")
					
			pg.display.update()
		pg.quit()

	
	def show_board(self): # 초기 보드판		
		for self.row in range(8):
			for self.col in range(8):
				self.init_stone((self.col, self.row))
					
		self.clock.tick(30)
		pg.display.flip()
	
	
	def init_stone(self, location): # 초기 보드판 세팅, (흰 검 검 흰)
		self.location = location
		
		if (self.location == (3,3) or self.location == (4,4)):
			self.init_put_stone(white_stone, self.location[0], self.location[1])
			grid[self.location[0]][self.location[1]] = 2
			
		elif (self.location == (3,4) or self.location == (4,3)):
			self.init_put_stone(black_stone, self.location[0], self.location[1])
			grid[self.location[0]][self.location[1]] = 1
			
		else:
			pg.draw.rect(self.screen, color, [(margin + width) * self.location[0] + margin, (margin + height) * self.location[1] + margin, width, height])
		
		
	def init_put_stone(self, obj, col, row): # 돌 놓을때마다 이미지 추가
		self.obj = obj
		self.col = col
		self.row = row
		
		self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
	
	def put_stone(self, obj, col, row, turn): # 돌 놓을때마다 이미지 추가
		self.obj = obj
		self.col = col
		self.row = row
		self.turn = turn
		
		if self.turn % 2 == 0:
			reverse_stone_list = self.getReversedPosition(grid, 1, self.row, self.col)
			#print(reverse_stone_list)
			for y, x in reverse_stone_list:
				self.screen.blit(self.obj, ((margin + width) * x + margin, (margin + height) * y + margin))
				grid[y][x] = 1
			self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
			grid[self.row][self.col] = 1
		
		else:
			reverse_stone_list = self.getReversedPosition(grid, 2, self.row, self.col)
			#print(reverse_stone_list)
			for y, x in reverse_stone_list:
				self.screen.blit(self.obj, ((margin + width) * x + margin, (margin + height) * y + margin))
				print ( y, x)
				grid[y][x] = 2
			self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
			grid[self.row][self.col] = 2
			
		print (grid)
		#self.screen.blit(self.obj, ((margin + width) * self.col + margin, (margin + height) * self.row + margin))
		
	def check_location(self, col, row, turn):
		self.col = col
		self.row = row
		self.turn = turn
	
		if (self.turn % 2 == 0):
			result = self.getAvailablePosition(grid, 1)
			print(result)
			if not ((self.row, self.col) in result):
				return False				
		else:
			result = self.getAvailablePosition(grid, 2)
			print(result)
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
			#print (i, j)
			if self.getReversedPosition(board,color,i,j):  # 해당 좌표가 비어있고, 해당 방향에서 뒤집을 수 있는 돌 리스트가 비어있지 않으면
				result.append((int(i),int(j)))  #좌표 기입
		return result  # 착수 가능한 좌표 리스트 반환
	
		
if __name__ == "__main__":
	othello = Othello()
	othello.run_game()
	
	#print(grid)