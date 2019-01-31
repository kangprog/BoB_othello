import socket
import json
import struct
from enum import IntEnum

class MsgType(IntEnum):
  READY    = 0
  START    = 1
  TURN     = 2
  ACCEPT   = 3
  TIMEOUT  = 4
  NOPOINT  = 5
  GAMEOVER = 6
  ERROR    = 7
  FULL     = 8

class OpponentStatus(IntEnum):
  NORMAL  = 0
  TIMEOUT = 1
  NOPOINT = 2

class Color(IntEnum):
  EMPTY = 0
  BLACK = 1
  WHITE = 2

class Result(IntEnum):
  LOSE = 0
  WIN  = 1
  DRAW = 2


class ClntType(IntEnum):
  PUT = 0

host = "localhost"
port = 8472

dict = {"type" : 0, "point" : 32}
message = json.dumps(dict)

#print (message.encode())

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))
client_socket.settimeout(1)
while 1:
	try:	
		msg = deserialize(sock)
	except:
		continue
	
	print (msg)
	
	if msg["type"] == MsgType.TURN:
		availabe_point = msg["availabe_point"]
		sock.sendall(serialize(dict))
	elif msg["type"] == MsgType.GAMEOVER:
		break
	

def serialize(msg):
    body = json.dumps(msg).encode()
    msg_len = struct.pack('>L', len(body))
    return msg_len + body


def deserialize(sock):
    _msg_len = sock.recv(4)
    if len(_msg_len) < 4:
        raise ConnectionResetError
    msg_len = struct.unpack('>L', _msg_len)[0]
    msg_raw = sock.recv(msg_len)
    while len(msg_raw) < msg_len:
        msg_raw += sock.recv(msg_len - len(msg_raw))
    msg = json.loads(msg_raw)
    return msg
