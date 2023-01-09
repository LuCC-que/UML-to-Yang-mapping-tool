import xmltodict
import json
import re
import pathlib
from operator import itemgetter


class BuildYang:

    def __init__(self, path) -> None:

        self.Graph = []
        self.records = {}
