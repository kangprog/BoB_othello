import socket
import threading
from threading import Thread
from threading import Lock
import time

import main
from protocol_enum import *
from util import *


# global to_flag # main에 정의되어있는 flag , 
# global fm_flag
# # #false = 내가 놓았을떄 서버로 전송
# # #true = 상대방이 놓은 자리를 내가 받아서 처리할때.
# global my_location # 내가 놓은 자리, main에 정의됨.
# global you_location
# global my_color

# global mtx_lock

class Client(main.Othello):
	def __init__(self):
		self.HOST = '127.0.0.1'
		self.PORT = 8472
		
		#print (fm_flag)
		#main.fm_flag = True
		
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect((self.HOST, self.PORT))
		self.sock.settimeout(1)
		
		self.t3 = threading.Thread(target = self.sock_recv)
		self.t3.start()
		
		
		self.t2 = threading.Thread(target = self.sock_send)
		self.t2.start()
		
		
		othello = main.Othello()
		othello.runGame()
		# self.t3 = threading.Thread(target = othello.runGame)
		# self.t3.start()
		
		
		
		
	def sock_recv(self):
		#main.mtx_lock.acquire()
		while 1:
			try:
				msg = deserialize(self.sock)
			except socket.timeout:
				continue
			
			print(msg)
			
			if self.msgTypeCheck(msg) == False: break
	
	def sock_send(self):

		if main.to_flag == True:
			print(main.my_location)
			
			self.sock.sendall(serialize({
				"type": ClntType.PUT,
				"point": main.my_location
				}))
			main.to_flag = None
			#time.sleep(2)
		else:
			pass
		#main.mtx_lock.release()
		
		
		#othello.runGame()

		
		
		
	def msgTypeCheck(self, msg):
		self.msg = msg
		
		if self.msg["type"] == MsgType.READY:
			print(" STATUS : READY ")
			
		elif self.msg["type"] == MsgType.START:
			print (" GAME START ")
			main.my_color = self.msg["color"]
			#return False		
			
		elif self.msg["type"] == MsgType.TURN:
			main.fm_flag = True
			print(main.fm_flag)
			self.time_limit = self.msg["time_limit"]
			self.opponent_put = self.msg["opponent_put"] # 상대방이 놓은 위치
			self.changed_points = self.msg["changed_points"] # 상대방이 놓은 수로 인해 뒤집어진 돌 리스트
			self.available_points = self.msg["available_points"] # type 2D list
			
			#print (self.opponent_put)
			if self.opponent_put != None:
				main.you_location = self.opponent_put
			
		elif self.msg["type"] == MsgType.GAMEOVER:
			return False
			
		return True
		
		
	def run(self):
		self.othello = Othello()
		self.othello.run_game()
		

if __name__ == "__main__":
	client = Client()
	#client.conn()