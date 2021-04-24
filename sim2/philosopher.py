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
    '''
    state = attr.ib(type=PhilosopherState, validator=validators.instance_of(
        PhilosopherState), default=PhilosopherState.THINKING)
    time = attr.ib(type=int, validator=validators.instance_of(int), default=0)
