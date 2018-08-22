#!/usr/bin/python

import sys
import logging
import threading

veicoli = []
T = 0
global total
total = 0

def from_file(file_name):
	global rows
	global cols
	global vehicles
	global rides
	global bonus
	#global T

	i=0

	with open(file_name, "r") as f:
		value = list(map(int,(f.readline()[:-1]).split(" ")))
		rows = int(value[0])
		cols = int(value[1])
		vehicles = int(value[2])
		rides = int(value[3])
		bonus = int(value[4])
		T = int(value[5])

		matrix = [[],[],[],[],[],[],[], []]
		for line in f:
			matrix[i%8].append({"indice": i, "partito": False, "info": list(map(int, (line[:-1]).split(" ")))})
			i += 1

		return matrix

def start_run(semaphore, m):
	#for i in range(0,T-1):
	while True:
		
		semaphore.acquire()
		if total == T-1:
			sys.exit(0)
		else:
			total += 1
		print("Missing step "+str(total))
		semaphore.release()

		for index, v in enumerate(veicoli):
			if v["occupato"] == False:
				semaphore.acquire()
				pos, status = corsa_migliore(v, m)
				semaphore.release()

				if status == False:
					wait_finish(m, semaphore)

				semaphore.acquire()
				if aggiorna_veicolo(index, [m[pos]["info"][0], m[pos]["info"][1]]) == False:
					continue
				
				if check_partenza(total, m[pos]["info"][4]):
					print("Assegnamento veicolo {} a corsa {}".format(str(index), str(m[pos]["indice"]+1)))
					v["occupato"] = True
					v["persone"].append(pos)
					v["p_index"].append(m[pos]["indice"]+1)
					m[pos]["partito"] = True
				semaphore.release()
			else:
				semaphore.acquire()
				aggiorna_coordinata(v, m)
					
				if check_arrivato(v, m):
					pos, status = corsa_migliore(v, m)
					
					if status == False:
						wait_finish(m, semaphore)

					if aggiorna_veicolo(index, [m[pos]["info"][0], m[pos]["info"][1]]) == False:
						continue

					if check_partenza(total, m[pos]["info"][4]):
						print("Assegnamento veicolo {} a corsa {}".format(str(index), str(m[pos]["indice"]+1)))
						v["occupato"] = True
						v["persone"].append(pos)
						v["p_index"].append(m[pos]["indice"]+1)
						m[pos]["partito"] = True
				semaphore.release()

def stampa_prova(output_file):
	temp = []
	with open(output_file, "r+") as f:
		for line in f:
			to_app = (line[:-1]).split(" ")
			temp.append(to_app)

	with open(output_file, "w+") as f:
		for index, v in enumerate(veicoli):
			stringa = str(index+1)
			for t in temp:
				if t[0]==index+1:
					for i in range(1, len(t)):
						stringa += " "+str(t[i])

			for corsa in v["persone"]:
				stringa += " "+str(corsa)

			stringa += "\n"
			f.write(stringa)

def aggiorna_veicolo(index, start):
	if veicoli[index]["posizione"][0] == start[0] and \
	veicoli[index]["posizione"][1] == start[1]:
		return True
	else:
		if veicoli[index]["posizione"][0] != start[0]:
			if veicoli[index]["posizione"][0] < start[0]:
				veicoli[index]["posizione"][0] += 1
			else:
				veicoli[index]["posizione"][0] -= 1
		else:
			if veicoli[index]["posizione"][1] < start[1]:
				veicoli[index]["posizione"][1] += 1
			else:
				veicoli[index]["posizione"][1] -= 1

def wait_finish(m, semaphore):
	s = True
	#for i in range(indice, T-1):
	while True:
		semaphore.acquire()
		if total == T-1:
			sys.exit(0)
		else:
			total += 1

		for v in veicoli:
			aggiorna_coordinata(v, m)
			if check_arrivato(v, m):
				v["occupato"]=False

		for v in veicoli:
			if v["occupato"] == True:
				s = False
		semaphore.release()

		if s:
			print("Thread terminated")
			sys.exit(0)
	
	#stampa_risultati(sys.argv[2])
	#sys.exit(0)

def stampa_risultati(out_file):
	with open(out_file, "w+") as f:
		for index, v in enumerate(veicoli):
			stringa = str(index+1)
			for corsa in v["p_index"]:
				stringa += " "+str(corsa)

			stringa += "\n"
			f.write(stringa)

def check_partenza(time, start):
	if time >= int(start):
		return True

	return False	

def check_arrivato(veicolo, m):
	if not len(veicolo["persone"]) or not len(m):
		return False

	p = veicolo["persone"][len(veicolo["persone"])-1]
	if veicolo["posizione"][0] == m[p]["info"][2] and \
	veicolo["posizione"][1] == m[p]["info"][3]:
		return True

	return False

def aggiorna_coordinata(veicolo, m):
	if not len(veicolo["persone"]) or not len(m):
		return

	p = veicolo["persone"][len(veicolo["persone"])-1]
	if veicolo["posizione"][0] != m[p]["info"][2]:
		if veicolo["posizione"][0] < m[p]["info"][2]:
			veicolo["posizione"][0] += 1
		else:
			veicolo["posizione"][0] -= 1
	else:
		if veicolo["posizione"][1] < m[p]["info"][3]:
			veicolo["posizione"][1] += 1
		else:
			veicolo["posizione"][1] -= 1

def corsa_migliore(veicolo, m):
	status = False
	for index, persona in enumerate(m):
		if persona["partito"]==False:
			migliore = persona
			indice = index
			status = True
			break
		
	if status == False:
		return -1, status

	for index, persona in enumerate(m):
		if persona["partito"] == False:
			if calcola_distanza(veicolo["posizione"], [persona["info"][0], persona["info"][1]]) < \
			calcola_distanza(veicolo["posizione"], [migliore["info"][0], migliore["info"][1]]) or \
			calcola_distanza(veicolo["posizione"], [persona["info"][0], persona["info"][1]]) == \
			calcola_distanza(veicolo["posizione"], [migliore["info"][0], migliore["info"][1]]) and \
			persona["info"][4] < migliore["info"][4]:
				migliore = persona
				indice = index
	
	return indice, status

def calcola_distanza(inizio, fine):
	return abs(int(inizio[0]) - int(fine[0]))+abs(int(fine[1])-int(inizio[1]))

if __name__ == "__main__":
	threads = []
	matrix = from_file(sys.argv[1])

	for i in range(0, vehicles):
		veicoli.append({"posizione": [0,0], "persone":[], "p_index":[], "occupato": False, "in_pos": False})

	#semaphore = threading.Semaphore(value=1)
	semaphore = threading.RLock()

	for i in range(0,8):
		temp = threading.Thread(target=start_run, args=(semaphore,matrix[i]))
		threads.append(temp)
		temp.start()

	stop = True
	while stop:
		stop = False
		for t in threads:
			if t.is_alive():
				stop = True

	print("Main thread, all child terminated")

	stampa_risultati(sys.argv[2])
