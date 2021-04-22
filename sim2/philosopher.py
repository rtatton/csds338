import attr
from attr import validators
from enum import Enum


class PhilosopherState(Enum):
    EATING = "Eating" 
    WAITING_LEFT = "Waiting_Left"
    WAITING_RIGHT = "Waiting_Right"
    THINKING = "Thinking"


@attr.s(slots=True)
class Philosopher:
    '''
    Attributes:
        state: describes state that philosopher is in using enum PhilosopherState
        time: time remaining before next available action
    '''
    state = attr.ib(type=PhilosopherState, validator=validators.instance_of(PhilosopherState))
    time = attr.ib(type=int, validator=validators.instance_of(int))

    
    