
import sys,termios, tty, os, time
import threading
from threading import Thread
import Queue
from keypressTester import KBHit
import csv 
import pickle

global key_dict, over, game_num, started, path, curr
path = './recorded_games/recorded-game-'

key_dict = {}
over = False
game_num = ""
started = False
curr = 0


def start(a):
	global over, game_num
	print("starting in 1 second")
	time.sleep(1)

	keyThread = threading.Thread(target = keypress)
	keyThread.start()

	#playback needs to be in main thread
	playback(a['gameNumber'])


def playback(rec_game):
	global over, game_num, path
	import pacman

	started = True
	game_num = str(rec_game)

	if not over:
		#f = 'python pacman.py --replay ./recorded_games/recorded-game-' + game_num
		import cPickle

		gtr = path + game_num
        f = open(gtr)
        try: recorded = cPickle.load(f)
        finally: f.close()
        import graphicsDisplay
        #graphicsDisplay.PacmanGraphics(options.zoom, frameTime = options.frameTime)
        recorded['display'] = graphicsDisplay.PacmanGraphics(1.0, frameTime = 0.1)

        pacman.replayGame(**recorded)

		#game has finished executing, do not get any more keypresses
        over = True
        print("game over") 


def keypress():
	#Initialize variables
	# import pacmanTerminalConfig, pacmanTerminalUpdater
	import pacman
	global over, started, curr

	available = True
	kb = KBHit()
	currentState = 0

	while True:
		if not over:		 

			# if pacman's state hasn't changed:
			if curr == pacman.GSTATE:
				#if a key hasn't been obtained for the current time interval/state -- not working?
				if available:
					
					#if a key is pressed, obtain key 
					if kb.kbhit():
						char = kb.getch()

						# print("pressed: ", char, available)

						if ord(char) == 27: # ESC
							print(key_dict)
							break

						#update dictionary, block keypresses for the rest of time period
						key_dict[curr] = char
						available = False

			#time limit is up, move to next state
			else:
				#if no key was pressed during the time period, set equal to null
				if not curr in key_dict:
					key_dict[curr] = ""

				#print the move number, key the user pressed
				print("move "+ str(curr) +": " + key_dict[curr])

				#reset counter and timer
				curr+=1
				available = True
				currentState +=1

				kb = KBHit()

		#if game over make csv or pkl file
		else:
			make_pkl()
			#make_csv()
			break

	kb.set_normal_term()

def make_csv():
	global game_num
	print("creating csv")

	f = './csv_data/merged_' + str(game_num) + ".csv"
	writer = csv.writer(open(f, 'w'))
	x = 0

	for row in  csv.reader(open('state_action.csv', 'r')):
    	#for every row, append user inp (make new column)
		writer.writerow(row + [key_dict[x]])
		x+=1

def make_pkl():
	import pacman
	global game_num, curr
	print("creating pickle and directory")

	nested_list = []

	for x in range(curr):
		curr = [pacman.PSA[x][0]] + [pacman.PSA[x][1]] + [key_dict[x]]
		#print(curr)
		nested_list.append(curr)

	# try:
	# 	if not os.path.isdir("./demo_data"):
	# 		os.mkdir("./demo_data")
	# 	os.chdir("./demo_data")
	# except OSError:
	# 	print ("Creation of the directory failed")

	tf = './pkl_data/merged_' + str(game_num) + ".pkl"
	outfile = open(tf, "wb")
	pickle.dump(nested_list, outfile)
	outfile.close()


def getCommand( argv ):
	from optparse import OptionParser
	usage = """
				USAGE:      python pacman.py <options>
			    EXAMPLES:   (1) python pacman.py
			                    - starts an interactive game
			                (2) python pacman.py --layout smallClassic --zoom 2
			                OR  python pacman.py -l smallClassic -z 2
			                    - starts an interactive game on a smaller board, zoomed in
			    """
	p = OptionParser(usage)

	p.add_option('-g', '--gameNumber', dest='gameNumber', type='int',
                      help='number of recorded game file', default=0)
	p.add_option('-p', '--filePath', dest='filePath', type='str',
                      help='path of recorded game', default='')


	opt, other = p.parse_args(argv)

	if len(other) != 0:
		raise Exception('Command line input not understood: ' + str(other))
	arg = {}

	arg['gameNumber'] = opt.gameNumber

	if opt.filePath:
		arg['filePath'] = opt.filePath

	print(arg)
	return arg



if __name__ == "__main__":
	global arg
	arg = getCommand( sys.argv[1:] )

	start(arg)