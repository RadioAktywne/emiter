#DEPRECATED


#schedule.py - zadania związane z spreadsheetami (ramówka,zajawki itd)

#slot - interwał czasowy obejmujący jedną komórkę (np jeśli dany wiersz ma godzinę 13:00 a następny 13:30 to slot jest równy pół godziny)
#audycja - ciąg slotów w tym samym dniu o tej samej nazwie będący jednolitą częścią ramówki 
 

import csv
import datetime

class Schedule:
	
	#init - pobiera ścieżkę do pliku csv i ładuje go do listy
	def __init__(self,path_schedule_file):

		#od którego wiersza zaczyna się ramówka
		self.first = 0
		
		self.schedule_table = []
		with open(path_schedule_file,mode='r',encoding='utf-8') as file:
			reader = csv.reader(file, delimiter=',')
			for row in reader:
				self.schedule_table.append(row)
			file.close()

	#pozycja ostatniego wiersza
	def last_row(self):
		row = len(self.schedule_table)-1

		for i in range(self.first,len(self.schedule_table)):
			if self.schedule_table[i+1][0] == '-' or self.schedule_table[i+1][0] == ' ':
				row = i
				break
		return row
		
	#czas teraz
	def now(self):
		time = datetime.datetime.now()
		h = time.hour
		m = time.minute
		wd = time.weekday()+1 #1=pon, 2=wt, ... 7-nd
		return {'wd': wd, 'h': h, 'm': m }

	#pobierz wszystkie slury
	def get_all_slurs(self):
		slurs = []
		first = self.first
		last = self.last_row()

		for wd in range(1,7):	
			for slot in range (first,last+1):
				#wczytaj i oddziel sufix powtórki (_p)
				cell = self.schedule_table[slot][wd].split("_")
				slur = cell[0]

				#czy to nie playlista?
				if slur.lower() != "playlista":
					#sprawdź, czy się nie powtarza
					repeats = False
					for i in range(0,len(slurs)):
						if slurs[i] == slur:
							repeats = True
							break

					if repeats == False:
						#nie powtarza się
						slurs.append(slur)
		return slurs



	
	#szukaj rekordu danego dnia tygodnia o danej godzinie
	#argument next sprawdza slot następny (np. jeśli jest 13:28 a sloty są półgodzinne to zwróci zawartośc slotu 13:30-14:00
	#zwraca słownik: row - wiersz(), wd - kolumna(dzien tygodnia)
	def get_from_schedule(self,prev,next,weekday,h,m):

		wd = weekday
		row = 0
		#print('Jest godzina '+str(h)+':'+str(m)+', '+str(wd)+'. dzien tygodnia.' )

		for i in range(self.first,self.last_row()+1):
			#szukaj odpowieniego slotu po czasie


			row_time_prev = self.schedule_table[i][0].split(":")
			prev_h = int(row_time_prev[0])
			prev_m = int(row_time_prev[1])

			if i == self.last_row():
				row_time_next = [24,0]
			else:
				row_time_next = self.schedule_table[i+1][0].split(":")

			next_h = int(row_time_next[0])
			next_m = int(row_time_next[1])
			
			if prev_h == next_h:
				#patrz na minuty
				if next_h == h and prev_m <= m  and next_m > m:
					row = i
					break

			else:
				#patrz na godziny
				if prev_h <= h and next_h > h:
					row = i
					break

		#obsługa next i prev

		if next:
			if row == self.last_row():
				#przeniesienie na następny dzień
				row = self.first
				wd += 1
				if wd > 7:
					wd = 1
			else:
				row += 1

		if prev:
			if row == self.first:
				#przeniesienie na poprzedni dzień
				row = self.last_row()
				wd -= 1
				if wd < 1:
					wd = 7
			else:
				row -= 1
		
		return {'row':row,'wd':wd}


	#pobiera pojedyńczy slot
	def get_slot(self,next,weekday,h,m):
		cell = self.get_from_schedule(False,next,weekday,h,m)
		row = cell['row']
		wd  = cell['wd']
		return self.schedule_table[row][wd]

	#szukaj audycji
	#argument next sprawdza slot następny (np. jeśli jest 13:28 a sloty są półgodzinne to zwróci zawartośc slotu 13:30-14:00
	#zwraca słownik: contains->zawartość init -> czy pierwszy slot w bloku, start -> godzina rozpoczęcia bloku, end -> godzina końca boloku
	def get_audition(self,prev,next,weekday,h,m):

		cell = self.get_from_schedule(prev,next,weekday,h,m)
		row = cell['row']
		wd  = cell['wd']

		#pobierz zawartość komórki
		slur = self.schedule_table[row][wd]

		initial_slot = True
		time_start = self.schedule_table[row][0]
		time_end = self.schedule_table[row][0]

		#skanowanie w górę
		if row > 2:
			for i in range(row-1, self.first-1, -1):
				if self.schedule_table[i][wd] == slur:
					initial_slot = False
					time_start = self.schedule_table[i][0]
				else:
					break

		#skanowanie w dół
		for i in range(row,self.last_row()+1):
			if self.schedule_table[i][wd] == slur:
				if i == self.last_row():
					time_end = self.schedule_table[self.first][0]
				else:
					time_end = self.schedule_table[i+1][0]

			else:
				break

		#sprawdzanie, czy to nie powtórka
		slursplit = slur.split("_")

		replay = False
		if len(slursplit) > 1:
			if slursplit[1] == "p":
				slur = slursplit[0]
				replay = True

	
		return {'slur':slur, 'init': initial_slot, 'replay':replay, 'start':time_start, 'end':time_end }

	#TODO
	#funkcja jak find_auditions w program.py
	


	#bindingi funkcji dla czasu teraz

	def get_from_schedule_now(self,prev,next):
		t = self.now()
		return self.get_from_schedule(prev,next,t['wd'],t['h'],t['m'])

	def get_slot_now(self,next):
		t = self.now()
		return self.get_slot(next,t['wd'],t['h'],t['m'])

	def get_audition_now(self,prev,next):
		t = self.now()
		return self.get_audition(prev,next,t['wd'],t['h'],t['m'])
	
	
	
