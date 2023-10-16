"""
Class for representing an individual system in a sector
"""

import random

from dicebox import roll

NAME_LENGTH = 15
COORDS_LENGTH = 4
UWP_LENGTH = 10
BASES_LENGTH = 7
TRADE_CODES_LENGTH = 17
TRAVEL_CODE_LENGTH = 1

HEXADECIMAL = [
    '0', '1', '2', '3', '4', '5', '6', '7',
    '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'
]
STARPORT_CODES = ['A', 'B', 'C', 'D', 'E', 'X']
BASE_CODES = ['C', 'G', 'N', 'P', 'R', 'S', 'T']
TRADE_CODES = [
    'Ag', 'As', 'Ba', 'De', 'Fl', 'Ga', 'Hi', 'Ht', 'Ie',
    'In', 'Lo', 'Lt', 'Na', 'Ni', 'Po', 'Ri', 'Va', 'Wa', ''
]
TRAVEL_CODES = ['A', 'R', '']

class System:
    """ SYSTEM PARSING """
    def parse(self, sys_string):
        self.pos = 0
        self.sys_string = sys_string

        self.name = self.consumeChunk(NAME_LENGTH).strip()
        self.coords = self.consumeChunk(COORDS_LENGTH)
        self.uwp = self.consumeChunk(UWP_LENGTH).strip()
        self.parseUWP()
        self.bases = self.consumeChunk(BASES_LENGTH).replace(' ', '')
        self.trade_codes = self.consumeChunk(TRADE_CODES_LENGTH).strip().split(' ')
        self.travel_code = self.consumeChunk(TRAVEL_CODE_LENGTH).strip()

        self.validateSystemData()

        return self

    def consumeChunk(self, amount):
        string = self.sys_string[self.pos:self.pos + amount]
        self.pos += amount + 1 # Add one for whitespace

        return string

    def parseUWP(self):
        def hex_2_int(hex_str):
            return int(hex_str, 16)

        self.starport_class = self.uwp[0]
        self.size = hex_2_int(self.uwp[1])
        self.atmosphere = hex_2_int(self.uwp[2])
        self.hydrographics = hex_2_int(self.uwp[3])
        self.population = hex_2_int(self.uwp[4])
        self.government = hex_2_int(self.uwp[5])
        self.law_level = hex_2_int(self.uwp[6])
        self.tech_level = int(self.uwp[8:])

    def validateSystemData(self):
        # Name
        if not self.name:
            self.throwValidationError("Invalid Name", self.name)

        # Coordinates
        try:
            x = int(self.coords[:2])
            y = int(self.coords[2:])
        except:
            self.throwValidationError("Invalid Coordinates", self.coords)

        # UWP
        # TODO: Validate each code individually to ensure correctness
        if self.uwp[0] not in STARPORT_CODES:
            self.throwValidationError("Invalid Starport Code", self.uwp[0])
        for code in self.uwp[1:7]:
            if code not in HEXADECIMAL:
                self.throwValidationError("Invalid UWP Code",
                                          f'{code}" in UWP "{self.uwp}')
        if self.uwp[7] != '-':
            self.throwValidationError("Invalid UWP",
                                      'Missing Separator (-)" in UWP "{self.uwp}')
        for code in self.uwp[8:]:
            if code not in HEXADECIMAL:
                self.throwValidationError("Invalid UWP Code",
                                          f'{code}" in UWP "{self.uwp}')

        # Bases
        for base in self.bases:
            if base not in BASE_CODES:
                self.throwValidationError("Invalid Base Code",
                                          f'{base}" in Bases "{self.bases}')

        # Trade Codes
        for code in self.trade_codes:
            if code not in TRADE_CODES:
                self.throwValidationError("Invalid Trade Code",
                                          f'{code}" in Trade Codes "{self.trade_codes}')

        # Travel Code
        if self.travel_code not in TRAVEL_CODES:
            self.throwValidationError("Invalid Travel Code", self.travel_code)

    def throwValidationError(self, prefix, problem):
        error_msg = self.constructErrorString(prefix, problem)
        raise ValueError(error_msg)

    def constructErrorString(self, prefix, problem):
        return f'{prefix}: "{problem}" in System String "{self.sys_string}"'

    @property
    def starport_class_score(self):
        if self.starport_class == 'X':
            return 0
        elif self.starport_class == 'E':
            return 1
        elif self.starport_class == 'D':
            return 3
        elif self.starport_class == 'C':
            return 5
        elif self.starport_class == 'B':
            return 10
        elif self.starport_class == 'A':
            return 15

    @property
    def population_score(self):
        try:
            return int(self.population)
        except:
            if self.population == 'A':
                return 12
            elif self.population == 'B':
                return 15
            elif self.population == 'C':
                return 20

    """ SYSTEM GENERATION """
    def generate(self, chain, coords):
        self.chain = chain
        self.coords = coords
        self.name = self.chain.generateRandom(length=15)

        self.calculateSize()
        self.calculateAtmosphere()
        self.calculateTemperature()
        self.calculateHydrographics()
        self.calculatePopulation()
        self.calculateGovernment()
        self.calculateFactions()
        self.calculateCulture()
        self.calculateLawLevel()
        self.calculateStarport()
        self.calculateTechLevel()
        self.constructUWP()
        self.determineTravelCode()
        self.determineTradeCodes()

        self.validateSystemData()

        return self

    def calculateSize(self):
        self.size = roll('2D6-2')

    def calculateAtmosphere(self):
        self.atmosphere = min(max(roll('2D6-7') + self.size, 0), 15)

    def calculateTemperature(self):
        self.swings = False
        if self.atmosphere in [0, 1]:
            self.swings = True
            atmos_dm = 0
        elif self.atmosphere in [2, 3]:
            atmos_dm = -2
        elif self.atmosphere in [4, 5, 14]:
            atmos_dm = -1
        elif self.atmosphere in [6, 7]:
            atmos_dm = 0
        elif self.atmosphere in [8, 9]:
            atmos_dm = 1
        elif self.atmosphere in [10, 13, 15]:
            atmos_dm = 2
        elif self.atmosphere in [11, 12]:
            atmos_dm = 6
        else:
            raise ValueError(f'Invalid value for atmosphere: {self.atmosphere}')

        self.temperature = roll('2D6') + atmos_dm

    def calculateHydrographics(self):
        if self.size in [0, 1]:
            self.hydrographics = 0
            return

        atmos_dm = -4 if self.atmosphere in [0, 1, 10, 11, 12] else 0
        if self.atmosphere not in [13, 15] and self.temperature in [10, 11]:
            temp_dm = -2
        elif self.atmosphere not in [13, 15] and self.temperature >= 12:
            temp_dm = -6
        else:
            temp_dm = 0

        self.hydrographics = min(max(roll('2D6-7') + self.atmosphere + atmos_dm + temp_dm, 0), 10)

    def calculatePopulation(self):
        self.population = roll('2D6-2')

    def calculateGovernment(self):
        if self.population == 0:
            self.government = 0
            return

        self.government = min(max(roll('2D6-7') + self.population, 0), 12)

    def calculateFactions(self):
        if self.government in [0, 7]:
            gov_dm = 1
        elif self.government >= 10:
            gov_dm = -1
        else:
            gov_dm = 0

        num_factions = roll('1D3') + gov_dm
        self.factions = []
        for i in range(num_factions):
            faction = min(max(roll('2D6-7') + self.population, 0), 12)
            strength = roll('2D6')
            self.factions.append((faction, strength))

    def calculateCulture(self):
        self.culture = roll('1D6 * 10 + 1D6')

        if self.culture == 25:
            self.influence = roll('1D6 * 10 + 1D6')
            while self.influence in [25, 26]:
                self.influence = roll('1D6 * 10 + 1D6')
        else:
            self.influence = None

        if self.culture == 26:
            self.fusion_1 = roll('1D6 * 10 + 1D6')
            while self.fusion_1 in [25, 26]:
                self.fusion_1 = roll('1D6 * 10 + 1D6')

            self.fusion_2 = roll('1D6 * 10 + 1D6')
            while self.fusion_2 in [25, 26]:
                self.fusion_2 = roll('1D6 * 10 + 1D6')
        else:
            self.fusion_1 = None
            self.fusion_2 = None

    def calculateLawLevel(self):
        if self.population == 0:
            self.law_level = 0
            return

        self.law_level = min(max(roll('2D6-7') + self.government, 0), 9)

    def calculateStarport(self):
        self.generatePortName()
        self.calculatePortClass()
        self.determineFacilities()

    def generatePortName(self):
        port_prefix = self.chain.generateRandom()

        port_words = [
            'Station', 'Port', 'Landing', 'Hub',
            'Center', 'Terminal', 'Base', 'Outpost',
            'Colony', 'Perch', 'Ring', 'Junction',
            'Starport', 'Dock', 'Bay Station', 'Lookout',
            'Complex', 'Gate', 'Passage', 'Number',
            'Designation', 'Greek'
        ]

        numbers = [
            'One', 'Two', 'Three', 'Four', 'Five',
            'Six', 'Seven', 'Eight', 'Nine', 'Ten',
            'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen',
            'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen', 'Twenty'
        ]

        designations = [
            'Prime', 'Superior', 'Nexus', 'Zone', 'Core',
        ]

        greeks = [
            'Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta',
            'Eta', 'Theta', 'Iota', 'Kappa', 'Lambda', 'Mu',
            'Nu', 'Xi', 'Omicron', 'Pi', 'Rho', 'Sigma',
            'Tau', 'Upsilon', 'Phi', 'Chi', 'Psi', 'Omega'
        ]

        port_word = random.choice(port_words)

        number = None
        while port_word == 'Number':
            port_word = random.choice(port_words)
            number = random.choice(numbers)

        designation = None
        while port_word == 'Designation':
            port_word = random.choice(port_words)
            designation = random.choice(designations)

        greek = None
        while port_word == 'Greek':
            port_word = random.choice(port_words)
            greek = random.choice(greeks)

        while port_word in ['Number', 'Designation', 'Greek']:
            port_word = random.choice(port_words)

        if number:
            self.port_name = f'{port_prefix} {port_word} {number}'
        elif designation:
            self.port_name = f'{port_prefix} {port_word} {designation}'
        elif greek:
            self.port_name = f'{port_prefix} {port_word} {greek}'
        else:
            self.port_name = f'{port_prefix} {port_word}'

    def calculatePortClass(self):
        if self.population >= 10:
            pop_dm = 2
        elif self.population >= 8:
            pop_dm = 1
        elif self.population <= 2:
            pop_dm = -2
        elif self.population <= 4:
            pop_dm = -1
        else:
            pop_dm = 0

        class_num = roll('2D6') + pop_dm

        if class_num <= 2:
            self.starport_class = 'X'
        elif class_num in [3, 4]:
            self.starport_class = 'E'
        elif class_num in [5, 6]:
            self.starport_class = 'D'
        elif class_num in [7, 8]:
            self.starport_class = 'C'
        elif class_num in [9, 10]:
            self.starport_class = 'B'
        elif class_num >= 11:
            self.starport_class = 'A'
        else:
            raise ValueError('Unable to derive starport class')

    def determineFacilities(self):
        self.determineQuality()
        self.calculateBerthingCost()
        self.determineFuel()
        self.determineShipFacilities()
        self.calculateBases()

    def determineQuality(self):
        qualities = {
            'A': 'Excellent',
            'B': 'Good',
            'C': 'Routine',
            'D': 'Poor',
            'E': 'Frontier',
            'X': 'No Starport'
        }

        self.starport_quality = qualities[self.starport_class]

    def calculateBerthingCost(self):
        costs = {
            'A': 1000,
            'B': 500,
            'C': 100,
            'D': 10,
            'E': 0,
            'X': 0
        }

        self.berthing_cost = roll('1D6') * costs[self.starport_class]

    def determineFuel(self):
        fuels = {
            'A': 'Refined',
            'B': 'Refined',
            'C': 'Unrefined',
            'D': 'Unrefined',
            'E': 'None',
            'X': 'None'
        }

        self.available_fuel = fuels[self.starport_class]

    def determineShipFacilities(self):
        facilities = {
            'A': ['Shipyard (all)', 'Repair'],
            'B': ['Shipyard (spacecraft)', 'Repair'],
            'C': ['Shipyard (small craft)', 'Repair'],
            'D': ['Limited Repair'],
            'E': ['None'],
            'X': ['None']
        }

        self.starport_facilities = facilities[self.starport_class]

    def calculateBases(self):
        thresholds = {
            'A': { 'N': 8,  'S': 10, 'R': 8,  'T': 0,  'C': 9,  'P': 99 },
            'B': { 'N': 8,  'S': 8,  'R': 10, 'T': 0,  'C': 11, 'P': 99 },
            'C': { 'N': 99, 'S': 8,  'R': 10, 'T': 10, 'C': 99, 'P': 99 },
            'D': { 'N': 99, 'S': 7,  'R': 99, 'T': 99, 'C': 99, 'P': 12 },
            'E': { 'N': 99, 'S': 99, 'R': 99, 'T': 99, 'C': 99, 'P': 10 },
            'X': { 'N': 99, 'S': 99, 'R': 99, 'T': 99, 'C': 99, 'P': 10 },
        }

        self.bases = ''
        for base, threshold in thresholds[self.starport_class].items():
            if roll('2D6') >= threshold:
                self.bases += base

        if roll('2D6') <= 10:
            self.bases += 'G'

    def calculateTechLevel(self):
        if self.population == 0:
            self.tech_level = 0
            return

        overall_dm = 0

        starport_dms = {
            'A': 6,
            'B': 4,
            'C': 2,
            'D': 0,
            'E': 0,
            'X': -4
        }
        overall_dm += starport_dms[self.starport_class]

        size_dms = [
            2, 2, 1, 1, 1, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0
        ]
        overall_dm += size_dms[self.size]

        atmosphere_dms = [
            1, 1, 1, 1, 0, 0, 0, 0,
            0, 0, 1, 1, 1, 1, 1, 1
        ]
        overall_dm += atmosphere_dms[self.atmosphere]

        hydrographics_dms = [
            1, 0, 0, 0, 0, 0, 0, 0,
            0, 1, 2, 0, 0, 0, 0, 0
        ]
        overall_dm += hydrographics_dms[self.hydrographics]

        population_dms = [
            0, 1, 1, 1, 1, 1, 0, 0,
            1, 2, 4, 0, 0, 0, 0, 0
        ]
        overall_dm += population_dms[self.population]

        government_dms = [
            1, 0, 0, 0, 0, 1, 0, 2,
            0, 0, 0, 0, 0, -2, -2, 0
        ]
        overall_dm += government_dms[self.government]

        tech_level = max(roll('1D6') + overall_dm, 0)

        minimums = [
            8, 8, 5, 5, 3, 0, 0, 3,
            0, 3, 8, 9, 10, 5, 5, 8
        ]
        min_tech_level = minimums[self.atmosphere]

        self.tech_level = max(tech_level, min_tech_level)

    def constructUWP(self):
        def hex_string(num):
            return f'{num:X}'

        uwp = ''

        uwp += self.starport_class
        uwp += hex_string(self.size)
        uwp += hex_string(self.atmosphere)
        uwp += hex_string(self.hydrographics)
        uwp += hex_string(self.population)
        uwp += hex_string(self.government)
        uwp += hex_string(self.law_level)
        uwp += '-'
        uwp += f'{self.tech_level}'

        self.uwp = uwp

    def determineTravelCode(self):
        self.travel_code = ''

        if self.atmosphere >= 10 or self.government in [0, 7, 10] \
                                 or self.law_level == 0 \
                                 or self.law_level >= 9:
            if roll('2D6') >= 9:
                self.travel_code = 'A'

        if not self.travel_code:
            if roll('2D6') == 12:
                self.travel_code = 'R'

    @property
    def travel_code_word(self):
        if not self.travel_code:
            return 'None'
        elif self.travel_code == 'A':
            return 'Amber'
        elif self.travel_code == 'R':
            return 'Red'
        else:
            return 'Unknown'

    def determineTradeCodes(self):
        trade_codes = {
            'Ag': [self.atmosphere in range(4, 10), self.hydrographics in range(4, 9), self.population in range(5, 8)],
            'As': [self.size == 0, self.atmosphere == 0, self.hydrographics == 0],
            'Ba': [self.population == 0, self.government == 0, self.law_level == 0],
            'De': [self.atmosphere >= 2, self.hydrographics == 0],
            'Fl': [self.atmosphere >= 10, self.hydrographics >= 1],
            'Ga': [self.size in range(6, 9), self.atmosphere in [5, 6, 8], self.hydrographics in range(5, 8)],
            'Hi': [self.population >= 9],
            'Ht': [self.tech_level >= 12],
            'Ie': [self.atmosphere in [0, 1], self.hydrographics >= 1],
            'In': [self.atmosphere in [0, 1, 2, 4, 7, 9], self.population >= 9],
            'Lo': [self.population <= 3],
            'Lt': [self.tech_level <= 5],
            'Na': [self.atmosphere in range(0, 4), self.hydrographics in range(0, 4), self.population >= 6],
            'Ni': [self.population in range(0, 7)],
            'Po': [self.atmosphere in range(2, 6), self.hydrographics in range(0, 4)],
            'Ri': [self.atmosphere in [6, 8], self.population in range(6, 9), self.government in range(4, 10)],
            'Va': [self.atmosphere == 0],
            'Wa': [self.hydrographics >= 10]
        }

        self.trade_codes = []
        for code, predicates in trade_codes.items():
            if all(predicates):
                self.trade_codes.append(code)

    def __repr__(self):
        # NAME_LENGTH = 15
        # COORDS_LENGTH = 4
        # UWP_LENGTH = 10
        # BASES_LENGTH = 7
        # TRADE_CODES_LENGTH = 17
        # TRAVEL_CODE_LENGTH = 1
        string = ''

        string += self.name.ljust(16)
        string += self.coords.ljust(5)
        string += self.uwp.ljust(11)
        string += self.bases.ljust(8)
        string += ' '.join(self.trade_codes).ljust(18)
        string += self.travel_code.ljust(2)

        return string

    def allData(self):
        # TODO: Return string like __repr__, but with *ALL* system data
        pass
