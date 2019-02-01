two_point = [[0,2],[0,3],[0,4],[0,5]
			,[1,2],[1,3],[1,4],[1,5]
			,[2,0],[2,1],[2,6],[2,7]
			,[3,0],[3,1],[3,6],[3,7]
			,[4,0],[4,1],[4,6],[4,7]
			,[5,0],[5,1],[5,6],[5,7]
			,[6,2],[6,3],[6,4],[6,5]
			,[7,2],[7,3],[7,4],[7,5]]
			
three_point = [[2,2],[2,3],[2,4],[2,5]
			, [3,2], [3,5],[4,2],[4,5]
			, [5,2], [5,3],[5,4],[5,5]]

four_point = [[0,0], [0,7]
			, [7,0], [7,7]]

#
# 반대편 대각선에 존재하는 돌까지 탐색 후, 내 돌만 있으면 4점, 상대방의 돌이 존재하면 1점, 돌이 중간에 없다면 1점
#
special_point_1 = [[1,1],[1,6]
				, [6,1], [6,6]]

#
# 모서리 돌 체크 후 내 돌이 존재하면 4점, 상대 돌이 있으면 1점, 돌이 없으면 1점
#
special_point_2 = [[0,1],[0,6]
				, [1,0], [1,7]
				, [6,0], [6,7]
				, [7,1], [7,6]]
				
point_dict = {"2" : two_point, "3" : three_point, "4" : four_point}


#
# black 1
# white 2
#
test_board = [[1, 1, 1, 1, 1, 1, 1, 1]
			,[1, 1, 1, 1, 1, 2, 2, 1] 
			,[1, 2, 1, 1, 2, 2, 2, 1]
			,[1, 2, 1, 1, 2, 1, 2, 1]
			,[1, 2, 2, 2, 1, 2, 2, 1]
			,[1, 2, 1, 1, 1, 1, 2, 1]
			,[1, 2, 0, 0, 0, 0, 2, 1]
			,[1, 2, 0, 0, 0, 0, 2, 1]]


def calcPointLocation(board, available_points, color): # board는 현재 상황판 np[][] (8x8), available_points는 2중 리스트., color는 내 돌 색깔
	result_point = []
	cmp_point = 0
	s_cmp_point = 0
	
	empty = 0
	
	if color == 2:
		you_color = 1
	elif color == 1:
		you_color = 2
		
		
	for point in available_points:
		if (not point in special_point_1) or (not point in special_point_2):
			for dic in point_dict.keys():
				if point in point_dict[dic]:
					if (int(dic) > cmp_point):
						cmp_point = int(dic)
						if cmp_point == s_cmp_point:
							result_point.append(point)
						elif cmp_point > s_cmp_point:
							result_point = [point]
							
					elif (int(dic) == cmp_point):
						result_point.append(point)
		
		if point in special_point_1:
			if point == [1,1]: # [1,1] -> [6,6]
				for inc in range(6)[1:]:
					if board[point[0]+inc][point[1]+inc] == color:
						s_cmp_point = 3
					else:
						s_cmp_point = 1
						break
						
				if s_cmp_point == 3 and cmp_point == 3:
					result_point.append(point)
				
				elif s_cmp_point > cmp_point:
					cmp_point = s_cmp_point
					result_point = [point]
					
				elif s_cmp_point == 1 and cmp_point == 1:
					result_point.append(point)
			
			
			if point == [1,6]:
				for inc in range(6)[1:]:
					if board[point[0]+inc][point[1]-inc] == color:
						s_cmp_point = 3
					else:
						s_cmp_point = 1
						break
						
				if s_cmp_point == 3 and cmp_point == 3:
					result_point.append(point)
				
				elif s_cmp_point > cmp_point:
					cmp_point = s_cmp_point
					result_point = [point]
					
				elif s_cmp_point == 1 and cmp_point == 1:
					result_point.append(point)
					
					
			if point == [6,1]:
				for inc in range(6)[1:]:
					if board[point[0]-inc][point[1]+inc] == color:
						s_cmp_point = 3
					else:
						s_cmp_point = 1
						break
						
				if s_cmp_point == 3 and cmp_point == 3:
					result_point.append(point)
				
				elif s_cmp_point > cmp_point:
					cmp_point = s_cmp_point
					result_point = [point]
					
				elif s_cmp_point == 1 and cmp_point == 1:
					result_point.append(point)
					
					
			if point == [6,6]:
				for inc in range(6)[1:]:
					if board[point[0]-inc][point[1]-inc] == color:
						s_cmp_point = 3
					else:
						s_cmp_point = 1
						break
						
				if s_cmp_point == 3 and cmp_point == 3:
					result_point.append(point)
				
				elif s_cmp_point > cmp_point:
					cmp_point = s_cmp_point
					result_point = [point]
					
				elif s_cmp_point == 1 and cmp_point == 1:
					result_point.append(point)
					
							
			
		if point in special_point_2:
			if point == [0,1] or point == [7,1]:
				if board[point[0]][point[1]-1] == color:
					s_cmp_point = 4
				else:
					s_cmp_point = 1
				
				
			if point == [1,0] or point == [1,7]:
				if board[point[0]-1][point[1]] == color:
					s_cmp_point = 4
				else:
					s_cmp_point = 1
				
				
			if point == [6,0] or point == [6,7]:
				if board[point[0]+1][point[1]] == color:
					s_cmp_point = 4
				else:
					s_cmp_point = 1
				
				
			if point == [0,6] or point == [7,6]:
				if board[point[0]][point[1]+1] == color:
					s_cmp_point = 4
				else:
					s_cmp_point = 1
				
	
			if s_cmp_point == 4 and cmp_point == 4:
				result_point.append(point)
			
			elif s_cmp_point > cmp_point:
					cmp_point = s_cmp_point
					result_point = [point]
					
			elif s_cmp_point == 1 and cmp_point == 1:
				result_point.append(point)
	

	print (result_point)
	return result_point

if __name__ == "__main__":
	calcPointLocation(test_board ,[[6, 2], [6, 5], [7, 2], [7, 5]], 1) #test code
	