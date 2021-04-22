import attr
from attr import validators
import dining
#from .metrics import Metrics

@attr.s(slots=True)
class Simulation:
    """
    Attributes:
        n: number of philosophers present in simulation
        time: time intervals the simulation will run for
        deadlock: boolean value that shows whether the simulation is currently in 
            a place of deadlock or not
        recovery: int time t that details time after deadlock to reset simulation
        eat_function: int value that selects type of function used to calculate eating
            time based on the philosopher i
    """
    n = attr.ib(type=int, validator=validators.instance_of(int))
    time = attr.ib(type=int, validator=validators.instance_of(int))
    deadlock = attr.ib(type=bool, default=False, kw_only=True)
    recovery = attr.ib(type=int, validator=validators.instance_of(int))
    eat_function = attr.ib(type=int, validator=validators.instance_of(int))

    def run_simulation(self):
        """ runs simulation of dining philosophers """
        dp = dining.DiningPhilosophers(self.n)
        #initiate metrics class as well that takes in Dining Philosophers instance?

        #------- MAIN SIM LOOP --------------
        for t in range(self.time):
            print("time step:" + t)
            for philosopher in dp.philosophers:
                print("loop")
            #loop through philosophers at each time step and do whatever they need to do depending on state (drop, continue eating)
            #check deadlock throughout


    def get_eating_time(self, function, i) -> int:
        """ returns the time intervals t that a philosopher will eat for.
                t is a function of each individual philosopher i. 
                function allows simulation to select different function
        """
        t = 0
        if function==1: 
            t = i*i
        elif function==2:
            t= i*i*i
        #these are example functions, can be changed

        return t 
        
    def get_hungry(self) -> bool:
        """ returns if a philosopher is hungry or not"""

    def check_deadlock(self, dp) -> bool:
        """checks if simulation is in deadlock, and returns true if so"""
        #loop through all philosophers and if all are holding one chopstick, then it is in deadlock

    def recover_from_deadlock(self, recovery) -> int:
        """ if simulation becomes is in deadlock returns time before resetting """
        #wait the amount of time recovery

if __name__== '__main__':
    sim = Simulation(5, 10, 1)
    print(sim)
