import attr
from attr import validators
from enum import Enum


class PhilosopherState(Enum):
    EATING = "Eating"
    WAITING = "Waiting"
    THINKING = "Thinking"


@attr.s(slots=True)
class Philosopher:
    '''
    Attributes:
        state: describes state that philosopher is in using enum PhilosopherState
        time: time remaining before next available action
        right_chop: int value that shows index of chopstick philosopher is holding in right hand: -1 if not holding anything
        left_chop: int value that shows index of chopstick philosopher is holding in right hand: -1 if not holding anything
    '''
    state = attr.ib(type=PhilosopherState, validator=validators.instance_of(
        PhilosopherState), default=PhilosopherState.THINKING)
    time = attr.ib(type=int, validator=validators.instance_of(int), default=0)
    right_chop = attr.ib(type=int, default=-1, validator=validators.instance_of(int))
    left_chop = attr.ib(type=int, default=-1, validator=validators.instance_of(int))
