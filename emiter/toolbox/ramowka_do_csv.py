

from emiter_core import *

# class Audycja:

#     dni = []
#     dni_powt = []

#     start_h = 0
#     start_m = 0
#     end_h = 0
#     end_m = 0

#     p_start_h = 0
#     p_start_m = 0
#     p_end_h = 0
#     p_end_m = 0

#     def __init__(self,a):
#         self.slur = a['slur']
#         #print(a)

#     def list_to_comma(self,t):
#         if len(t) == 0:
#             return ""
#         else:
#             o = str(t[0])
        
#             for i in range(1,len(t)):
#                 o = o + "," + str(t[i])
#             return o

#     def toCsv(self):
#         s = ';'
#         return self.slur + s +str(self.start_h) + s+ str(self.start_m) + s + str(self.end_m) + s + str(self.end_m) + s + str(self.p_start_h) + s + str(self.p_start_m) + s + str(self.p_end_m) + s + str(self.p_end_m) + s + self.list_to_comma(self.dni) + s + self.list_to_comma(self.dni_powt) + s


def list_to_comma(t):
    if len(t) == 0:
        return ""
    else:
        o = str(t[0])
    
        for i in range(1,len(t)):
            o = o + "," + str(t[i])
        return o

r = schedule.Schedule("./data/ramowka.csv")

obiekty_audycji = []
przerobione = []
sc = ";"

for dzien in range(1,8):
    h = 0
    m = 0

    end = ""

    while True:
        aud = r.get_audition(False,False,dzien,h,m)

        #pobierz godzinę i minutę
        end = aud['end']
        hm = end.split(':')
        h = int(hm[0])
        m = int(hm[1]) #do następnej iteracji

        if aud['slur'].lower() != 'playlista' and aud['replay'] == False:

            bylo = False
            for p in przerobione:
                if aud['slur'] == p:
                    bylo = True

            if bylo == False:
                przerobione.append(aud['slur'])


        if end == "00:00":
            break
        

for a in przerobione:
    #dla każdej audycji
    #szukaj liczby powtórzeń w ramówce i ile powtórek

    dni = []
    dni_powt = []

    start_h = 0
    start_m = 0
    end_h = 0
    end_m = 0

    p_start_h = 0
    p_start_m = 0
    p_end_h = 0
    p_end_m = 0   

    for dzien in range(1,8):
        h = 0
        m = 0

        end = ""

        while True:


            aud = r.get_audition(False,False,dzien,h,m)
            end = aud['end']
            hm = end.split(':')
            h = int(hm[0])
            m = int(hm[1])

            start_hm = aud['start'].split(':')
            sh = int(start_hm[0])
            sm = int(start_hm[1])

            if aud['slur'] == a:
                if aud['replay']:
                    #powtorka
                    p_start_h = sh
                    p_start_m = sm 
                    p_end_h = h
                    p_end_m = m 

                    dni_powt.append(dzien)

                else:
                    #audycja
                    start_h = sh
                    start_m = sm 
                    end_h = h
                    end_m = m 

                    dni.append(dzien)


            if end == "00:00":
                break

    lista_dni = list_to_comma(dni)
    lista_powt = list_to_comma(dni_powt)

    start_h = str(start_h)
    start_m = str(start_m)
    end_h = str(end_h)
    end_m = str(end_m)

    p_start_h = str(p_start_h)
    p_start_m = str(p_start_m)
    p_end_h = str(p_end_h)
    p_end_m = str(p_end_m)

    print(a+sc+lista_dni+sc+start_h+sc+start_m+sc+end_h+sc+end_m+sc+lista_powt+sc+p_start_h+sc+p_start_m+sc+p_end_h+sc+p_end_m)
    








    

    


