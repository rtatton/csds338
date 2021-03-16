import attr
from attr import validators

import algorithm
import requests


@attr.s(slots=True)
class Simulator:
	request_stream = attr.ib(
		type=requests.RequestStream,
		validator=validators.instance_of(requests.RequestStream))
	algorithm = attr.ib(
		type=algorithm.Algorithm,
		validator=validators.instance_of(algorithm.Algorithm))
