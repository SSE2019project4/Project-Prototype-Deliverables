###################################################################
#		server terminal functionality							  #
#	how to use - start the server with python server.py           #
#			   - execute the cient with python client.py          #
#			   - follow prompts.                                  #
#	                                                              #
#				- all existing account information                #
#				  is stored in the user's file                    #
#                                                                 #
#			input - 2 (sign in)									  #
#				  - 1 (voter)									  #
#				  - 2 (vote)									  #
#				  - (5,3,1,4,2,8) (above the line vote)			  #
#                                                                 #
#           output -                                              #
#  																  #           <--------- !!!!!!!!!!! put your output here when implemented !!!!!!!!!!!!!!
###################################################################

import socket 	
import sys
import datetime
import os

class party:						#class structure to store the delegate's party name and candidiate list.
	def __init__(self,n,c):
		self.name, self.candidates = n,c

def time():													#function to return the current time in a formatted string
	date = datetime.datetime.now()
	return '['+str(date.day)+'-'+str(date.month)+'-'+str(date.year)+']['+str(date.hour)+':'+'%2s'%(str(date.minute))+']'

def display(a, b, file):											#used to write error messages to log and print to terminal
	if b == 0:
		print('\033[1;32;40m'+a+'\033[1;37;40m')		#green output to display to user functionality
	else:
		print('\033[1;31;40m)'+a+'\033[1;37;40m')		#red text to send to user for unintended behaviour/alert server terminal
	
	t = time()
	file.write(t[12:] + ' ' + a + '\n')						#write minutes inside of dated log

def getInfo(info, sign, direct):							#get information from specified user file
	with open(direct +'/'+ sign + '.txt', 'r') as user:
		if info == 'privilege':								#argument to select privilege, party or party acronym
			return user.readlines()[1][0]

		if info == 'party':
			return user.readlines()[2]

		if info == 'sp':
			return user.readlines()[3]

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)		#create a socket for the client to connect to
	port = 3125
	s.bind(('0.0.0.0', port))									#bind socket to port 3125
	s.listen(10)												#listen on server for a connection							
	
	c, addr = s.accept()										#accept all connections over the port
	print('Connection Established')

	t = time()
	log = open('logs/'+t[1:-8]+'.txt', 'a+')					#create/open dated log

	signed = ''													#variables to store the signed in account and the state of the connection
	exit = 0

	while exit != 1:											#while connection is active
		direct = 'users'
		while signed == '':										# while you are not signed in
			flag = False	
			c.sendall('\033[1;34;40m1) Register Account\n2) Sign In\n9) Exit\033[0;37;40m')
			options = c.recv(1024)								#recieve the option from the client

			if options == '1':									#register account
				c.sendall('Register Account\nName:')
				name = c.recv(1024)								#request and recieve name and password of new account
				c.sendall('Password:')
				password = c.recv(1024)

				for filename in os.listdir('users'):			#check existing accounts in the users directory
					if name+'.txt' == filename:
						c.sendall("\033[1;31;40mUser account: "+name+" already exists.\n\033[1;37;40m")
						flag = True								#found existing user, display error to client and loop
						break						

				if flag == False:										#user not found in file
					file = open("users/"+name.strip()+".txt","w+")		#create user file and append password and privilege
					file.write(password.strip()+"\n3")
					display("New Account Added : "+ name + '(' + password + ')', 0, log)
					c.sendall('\033[1;32;40mAccount Successfully Created!\n\033[1;37;40m')

			elif options == '2':								#sign in as voter or delegate
				c.sendall("1) voter\n2) delegate")
				options = c.recv(1024)

				c.sendall('Sign In\nName:')
				name = c.recv(1024)								#request and recieve sign in credentials

				c.sendall('Password:')
				password = c.recv(1024)

				if options == '2':								#find directory of users or delegates
					direct = 'users/delegates'
				else:
					direct = 'users'

				for filename in os.listdir(direct):					#iterate over user files								
					if name+'.txt' == filename:							#check to seee if user exists
						with open(direct+'/'+filename, 'a+') as user:		#open user file and compare credentials
							if next(user).find(password) != -1:
								signed = name 
								display(signed + " has signed in", 0, log)
		
				if signed == '':										#credentials do not match any user, send an error message
					display('Attempted login '+ name + '(' + password + ')', 1, log)
					c.sendall('\033[1;31;40mAccount does not exist, check username and password\n\033[0;37;40m')

			elif options == '9':								#close the connection to the server
				c.sendall("\033[1;31;40mExiting\033[1;37;40m\n")	#tell client to close connection with -1 message
				c.sendall("-1")									
				signed = '.'
				exit = 1

			else:
				c.sendall('\033[1;34;40m1) Register Account\n2) Sign In\n4) Exit\033[0;37;40m')
				options = c.recv(1024)								#recieve the option from the client

		priv = getInfo('privilege', signed, direct)					#get account information
		if priv == '2':
			sp = getInfo('sp', signed, direct)						#if delegate account, get party information
			p = getInfo('party', signed, direct)
			candidates = []
			with open('users/delegates/'+signed+'.txt', 'rw') as cand:		#update the candidate list for the delegate from the user file
				index = 0
				for lines in cand:
					if index > 3:
							information = lines.split()
							temp = (information[0], information[1], information[2])		#build the delegate class' canddiate list
							candidates.append(temp)
					index+=1

			delegate = party(p, candidates)			#initialise the delegate

		while signed != '':
			if priv == '1':
				c.sendall('\033[1;32;40mSigned in as ' + signed + '\n\033[1;34;40m1) Sign Out\n2) Show Users\n9) Exit\033[1;37;40m')	#function list for admin
			
			elif priv == '2':
				c.sendall('\033[1;32;40mSigned in as ' + signed + '\n\033[1;34;40m1) Sign Out\n2) Add or Remove Candidates\n3) Show Candidates\n9) Exit\033[1;37;40m')		#function list for delegate
			
			elif priv == '3':
				c.sendall('\033[1;32;40mSigned in as ' + signed + '\n\033[1;34;40m1) Sign Out\n2) Vote\n3) Show Candidates\n9) Exit\033[1;37;40m')		#function list for voter

			options = c.recv(1024)

			if options == '1':			#sign out
				file.close()
				signed = ''
		    
			elif options == '2':		#request to see user table, but be signed in as administrator, else error message
					if priv == '1':
						c.sendall('--USER TABLE--\n')
						for filename in os.listdir('users'):		#iterate and print all users in the table
							if filename.find('.txt') != -1:
								c.sendall(filename[:-4]+'\n')
						for filename in os.listdir('users/delegates'):
								c.sendall(filename[:-4]+'\n')
						c.sendall('\n')

					elif priv == '2':								#add or remove candidates
						c.sendall('\033[1;34;40m1) Add Candidates\n2) Remove Candidates\n4) back\033[1;37;40m')
						options = c.recv(1024)

						if options == '1':							#add candidate
								c.sendall("ID:Surname:Given Name")
								options = c.recv(1024)
								information = options.split(':')	#client input eg. 10000:SURNAME:FIRSTNAME

								if len(information) != 3:
									c.send('\033[1;31;40m)Invalid Candidate Information\033[1;37;40m')		#not enough candidate information
									display('Bad Candidate information ' + options, 1, log)
								else:
									delegate.candidates.append((information[-3], information[-2], information[-1]))		#append candidate information to delegate file.
									c.sendall("Candidate Successfully Added")

						elif options == '2':											#remove candidate
								for x in range(len(delegate.candidates)):
									c.sendall(str(x)+') ' + delegate.candidates[x][1] + ' ' + delegate.candidates[x][2] + '\n')		#display to client all party candidates 

								c.sendall("Select a Candidate to Remove:")
								options = c.recv(1024)

								delegate.candidates.pop(int(options))	#remove selected candidate from party		

						elif options == '4':		#back to menu
							break 

					elif priv == '3':			#voter
						c.sendall('ballot')		#send signal to display the ballot to client
				
			elif options == '3':	#show candidates for selected delegate
				if priv == '2':		#delegate is signed in, delegate already selected
					for x in range(len(delegate.candidates)):
							c.sendall(delegate.candidates[x][0] + ' ' +delegate.candidates[x][1] + ' ' + delegate.candidates[x][2] + '\n') 
				
				else:				#signed in as voter, select delegate
					c.sendall("select a delegate using party acronym")
					options = c.recv(1024)

					with open('users/delegates/'+options+'.txt') as delfile:		#open selected delegate file and display condidates
						i = 0
						for lines in delfile:
							if i == 2:
								c.sendall(lines.strip()+' ('+options+')\n')			#print party
							if i > 3:
								c.sendall(lines)									#print candidates
							i += 1 
						c.sendall('\n\n')

			elif options == '9': 	#close the connection to the server
				c.sendall("\033[1;31;40mExiting\033[1;37;40m\n")	#tell client to close connection with -1 message
				c.sendall("-1")	
				signed = '.'	#sign out								
				exit = 1		#exit program
				
	log.close()					#close server log
	c.close()					#close socket to client	

main()							#open the server