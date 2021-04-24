import attr
from attr import validators
import random
import dining
from philosopher import PhilosopherState
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
        dp = dining.DiningTable(self.n)
        #initiate metrics class as well that takes in Dining Philosophers instance?

        #------- MAIN SIM LOOP --------------
        for t in range(self.time):
            print("time step: ", t)
            
            #loop through the philosophers
            for philosopher, phil_id in zip(dp.philosophers, range(len(dp.philosophers))):
                #print("Initial", phil_id, ":", philosopher)
                if(philosopher.time > 0):
                    philosopher.time = philosopher.time - 1
                elif(philosopher.time == 0):
                    if(philosopher.state==PhilosopherState.THINKING):
                        #try to pick up 
                        if(self.get_hungry(dp.n_chairs) and dp.pick_up(phil_id, phil_id==3)):
                            philosopher.state=PhilosopherState.WAITING

                    elif(philosopher.state==PhilosopherState.EATING):
                        #count down, if time=0 then change state to THINKING
                        philosopher.state=PhilosopherState.THINKING
                        dp.put_down(phil_id)
                        dp.put_down(phil_id)

                    elif(philosopher.state==PhilosopherState.WAITING):
                        #try to pick up another chopstick, if successful, then change state to EATING, otherwise drop chopstick and change to THINKING
                        if(dp.pick_up(phil_id, phil_id==3)):
                            philosopher.state=PhilosopherState.EATING
                            philosopher.time=self.get_eating_time(self.eat_function, phil_id)
                        else:
                            dp.put_down(phil_id)
                            philosopher.state=PhilosopherState.THINKING
                        
                print("Final", phil_id, ":", philosopher)

            print(dp.chopsticks)
            print(self.deadlock)

            if(self.check_deadlock(dp)):
                self.deadlock = True
                self.recover_from_deadlock(dp, self.recovery)


    def get_eating_time(self, function, i) -> int:
        """ returns the time intervals t that a philosopher will eat for.
                t is a function of each individual philosopher i. 
                function allows simulation to select different function
        """
        t = 0
        if function==1: 
            t = i*i + 1
        elif function==2:
            t= i*i*i + 1
        #these are example functions, can be changed

        return t 
        
    def get_hungry(self, n) -> bool:
        """ returns if a philosopher is hungry or not -- incrementally decreases with more philosophers"""
        if random.randint(0, 2) == 0:
            return True

    def check_deadlock(self, dp) -> bool:
        """checks if simulation is in deadlock, and returns true if so"""
        #loop through all philosophers and if all are holding one chopstick, then it is in deadlock
        deadlock = True
        for philosopher in dp.philosophers:
            if philosopher.state == PhilosopherState.THINKING or philosopher.state == PhilosopherState.EATING:
                deadlock = False
        return deadlock
                

    def recover_from_deadlock(self, dp, recovery) -> int:
        """ if simulation becomes is in deadlock returns time before resetting """
        #wait the amount of time recovery
        for philosopher in dp.philosophers:
            philosopher.state = PhilosopherState.THINKING
            philosopher.time = recovery
        for x in range(len(dp.philosophers)):
            dp.put_down(x)
            dp.put_down(x)

if __name__== '__main__':
    sim = Simulation(5, 10, 2, 1)
    print(sim)
    sim.run_simulation()
