import attr
from attr import validators
import dining
from philosopher import PhilosopherState



@attr.s(slots=True)
class Metrics:
    '''
    Attributes:
        dp: Dining Philosophers instance to track as it runs through simulation
        deadlocks: int amount of times the program experienced deadlock
        total_wait_time: int amount of time philosophers were waiting to get a second chopstick
    '''
    dp = attr.ib(type=dining.DiningTable, validator=validators.instance_of(dining.DiningTable))
    deadlocks = attr.ib(type=int, default=0, validator=validators.instance_of(int))
    total_wait_time = attr.ib(type=int, default=0, validator=validators.instance_of(int))

    def run_metrics(self, dp):
        """Basic call that updates all metrics after every time step of a simulation"""
        self.update_dp(dp)

    def update_dp(self, dp):
        """updates the dp instance in the metrics"""
        self.dp = dp
    
    def increase_deadlock(self):
        """adds to total time in deadlock if dining philosophers are in deadlock"""
        self.deadlocks += 1

    def get_total_wait_time(self):
        for philosopher in self.dp.philosophers:
            if philosopher.state == PhilosopherState.WAITING:
                self.total_wait_time += 1
    
    def print_metrics(self):
        print("Total Deadlocks:", self.deadlocks)

