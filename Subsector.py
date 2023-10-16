"""
Class for representing the subsectors in a sector
"""

import json
import random
import requests

from constants import COL_MULTIPLE, ROW_MULTIPLE
from dicebox import roll
from gabble import create_chain
from System import System

class Subsector:
    def __init__(self, start_x, start_y):
        self.start_x = start_x
        self.start_y = start_y
        self.system_threshold = random.randint(6, 8)
        self.generateNameCorpus()
        self.populateSystems()

    def generateNameCorpus(self):
        try:
            r = requests.get('https://travellermap.com/data?tag=Official|InReview|Preserve', timeout=10)
        except requests.ReadTimeout:
            raise RuntimeError('TravellerMap timed out. Please try again.')
        data = json.loads(r.text)
        names = [ sector['Names'][0]['Text'] for sector in data['Sectors'] ]
        sectors = []
        for i in range(3):
            sectors.append(random.choice(names))

        worlds = []
        for name in sectors:
            try:
                r = requests.get(f'https://travellermap.com/data/{name}/sec', timeout=10)
            except requests.ReadTimeout:
                raise RuntimeError('TravellerMap timed out. Please try again.')
            if r.status_code != 200:
                raise RuntimeError(f'TravellerMap responded with error: {r.status_code}')
            lines = r.text.splitlines()
            i = 0
            while lines[i][:4] != '....':
                i += 1
            worlds += [ world[:14].strip() for world in lines[i+2:] ]

        self.chain = create_chain(worlds, order=4)

    def populateSystems(self):
        self.systems = {}
        for y in range(self.start_y, self.start_y + ROW_MULTIPLE):
            for x in range(self.start_x, self.start_x + COL_MULTIPLE):
                if roll('2D6') > self.system_threshold:
                    coords = f'{x:02d}{y:02d}'
                    system = System().generate(self.chain, coords)
                    self.systems[coords] = system

    def __repr__(self):
        sys_strings = [ repr(s) for s in self.systems.values() ]
        return '\n'.join(sys_strings)
