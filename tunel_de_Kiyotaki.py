########################################################################################
########################################################################################
###############                                                          ###############
###############            PRÁCTICA 2 - PROGRAMACIÓN PARALELA            ###############
###############                   Cristina Ávila Santos                  ###############
###############                   Isabel Beltrá Merino                   ###############
###############                   Claudia Viñas Jáñez                    ###############
###############                                                          ###############
########################################################################################
########################################################################################

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "SUR"
NORTH = "NORTE"

NCARS = 100

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.moving_south = Value('i', 0)
        self.moving_north = Value('i', 0)
        self.waiting_south = Value('i', 0)
        self.waiting_north = Value('i', 0)
        self.can_enter_south = Condition(self.mutex)
        self.can_enter_north = Condition(self.mutex)
        self.turn = Value('i', 0) #self.turn.value == 0 si es el turno de los coches que 
                #vienen del sur y self.turn.value == 1 si es de los que vienen del norte

    def can_enter_south_condition(self):
        return self.moving_north.value == 0 and (self.turn.value == 0 or \
                                                 self.waiting_north.value == 0)
    
    def can_enter_north_condition(self):
        return self.moving_south.value == 0 and (self.turn.value == 1 or \
                                                 self.waiting_south.value == 0)
    
    def wants_enter(self, direction):
        self.mutex.acquire()
        try:
            if direction == SOUTH:
                self.waiting_south.value += 1
                self.can_enter_south.wait_for(self.can_enter_south_condition)
                self.moving_south.value += 1
                self.waiting_south.value -= 1
            else:
                self.waiting_north.value += 1
                self.can_enter_north.wait_for(self.can_enter_north_condition)
                self.moving_north.value += 1
                self.waiting_north.value -= 1

        finally:
            self.mutex.release()
    
    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        try:
            if direction == SOUTH:
                self.moving_south.value -= 1
                self.turn.value = 1
                self.can_enter_north.notify_all()
            else:
                self.moving_north.value -= 1
                self.turn.value = 0
                self.can_enter_south.notify_all()
        finally:
            self.mutex.release()
            
def delay(n = 3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"COCHE {cid} en dirección {direction}: ha sido CREADO")
    delay(6)
    print(f"COCHE {cid} en dirección {direction}: QUIERE ENTRAR en el tunel")
    monitor.wants_enter(direction)
    print(f"COCHE {cid} en dirección {direction}: ENTRANDO en el tunel")
    delay(3)
    print(f"COCHE {cid} en dirección {direction}: SALIENDO del tunel")
    monitor.leaves_tunnel(direction)
    print(f"COCHE {cid} en dirección {direction}: FUERA del tunel")


def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0, 1) == 1 else SOUTH
        cid += 1
        p = Process(target = car, args = (cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) #cada 0.5 segundos se crea un coche nuevo

        
if __name__ == "__main__":
    main()