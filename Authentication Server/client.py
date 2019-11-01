###################################################################
#		client terminal functionality							  #
#	how to use - start the server with python server.py           #
#			   - execute the cient with python client.py          #
#			   - follow prompts.                                  #
#	                                                              #
#				- all existing account information                #
#				  is stored in the user's file                    #
###################################################################

import socket
import sys
import subprocess

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)			#create a socket for connection 
s.connect(('localhost', 3125))														#connect to server 
print(s.recv(1024))										

received = ''

while received != '-1':										#while connection is still alive							
	s.sendall(str(raw_input()))							#construct message and send to server					
	subprocess.call(["clear"])							#clear terminal display		
	received = s.recv(1024)									#wait for server response

	if received.find('ballot') != -1:					#request ballot found, print ballot as client, send candidate list to server. 
		with open('candidateFormat.txt') as ballot:
			for lines in ballot:
				print(lines[:-1])
		continue

	elif received.find('-1') != -1:	 					#if response is not to break connection, print
		print("\033[1;31;40mExiting\033[1;37;40m")
		break

	else:
		print(received)

	while received[-1:] == '\n':						#multiple lines of responses from server
		received = s.recv(1024)
		print(received)

s.close()																	#close connection
