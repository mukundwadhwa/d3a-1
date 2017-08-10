import pytest

from d3a.models.area import DEFAULT_CONFIG
from d3a.models.market import Offer
from d3a.models.strategy.const import FRIDGE_MIN_NEEDED_ENERGY
from d3a.models.strategy.fridge import FridgeStrategy


class FakeArea():
    def __init__(self, count):
        self.appliance = None
        self.name = 'FakeArea'
        self.count = count

    @property
    def config(self):
        return DEFAULT_CONFIG

    @property
    def current_tick(self):
        return 5

    @property
    def historical_avg_price(self):
        avg_price = [30]
        return avg_price[self.count]

    @property
    def historical_min_max_price(self):
        min_max = [(30, 30)]
        return min_max[self.count]

    @property
    def markets(self):
        return {'next market': "new market"}


class FakeMarket:
    def __init__(self, count):
        self.count = count

    @property
    def sorted_offers(self):
        offers = [
            [Offer('id', (10 * (FRIDGE_MIN_NEEDED_ENERGY / 1000)),
                   (FRIDGE_MIN_NEEDED_ENERGY / 1000), 'A', self
                   )
             ],
            [Offer('id', 100000000,
                   (FRIDGE_MIN_NEEDED_ENERGY / 1000), 'A', self
                   )
             ]
        ]
        return offers[self.count]


"""TEST1"""


# Testing if fridge accepts an offer he should accept

@pytest.fixture
def market_test1():
    return FakeMarket(0)


@pytest.fixture
def area_test1():
    return FakeArea(0)


@pytest.fixture
def fridge_strategy_test1(market_test1, area_test1, called):
    f = FridgeStrategy()
    f.next_market = market_test1
    f.owner = area_test1
    f.area = area_test1
    f.accept_offer = called
    return f


def test_if_fridge_accepts_valid_offer(fridge_strategy_test1, area_test1, market_test1):
    fridge_strategy_test1.event_tick(area=area_test1)
    assert fridge_strategy_test1.accept_offer.calls[0][0][1] == repr(market_test1.sorted_offers[0])


"""TEST2"""


# Testing if fridge doesn't accept offer if he is cold enough

@pytest.fixture
def market_test2():
    return FakeMarket(0)


@pytest.fixture
def area_test2():
    return FakeArea(0)


@pytest.fixture
def fridge_strategy_test2(market_test2, area_test2, called):
    f = FridgeStrategy()
    f.next_market = market_test2
    f.owner = area_test2
    f.area = area_test2
    f.fridge_temp = 4
    f.accept_offer = called
    return f


def test_if_fridge_cools_too_much(fridge_strategy_test2, area_test2, market_test2):
    fridge_strategy_test2.event_tick(area=area_test2)
    assert len(fridge_strategy_test2.accept_offer.calls) == 0


"""TEST3"""


# Testing if fridge accepts every offer if he is too warm

@pytest.fixture
def market_test3():
    return FakeMarket(1)


@pytest.fixture
def area_test3():
    return FakeArea(0)


@pytest.fixture
def fridge_strategy_test3(market_test3, area_test3, called):
    f = FridgeStrategy()
    f.next_market = market_test3
    f.owner = area_test3
    f.area = area_test3
    f.fridge_temp = 7.9
    f.accept_offer = called
    return f


def test_if_warm_fridge_buys(fridge_strategy_test3, area_test3, market_test3):
    fridge_strategy_test3.event_tick(area=area_test3)
    assert fridge_strategy_test3.accept_offer.calls[0][0][1] == repr(market_test3.sorted_offers[0])


"""TEST4"""


# Testing if fridge listens to input of appliance

def test_if_fridge_listens_to_appliance(fridge_strategy_test1, area_test1, market_test1):
    fridge_strategy_test1.event_data_received({'temperature': 4.3})
    assert fridge_strategy_test1.fridge_temp == 4.3


"""TEST5"""


# Testing if market cycle works correct

def test_if_fridge_market_cycles(fridge_strategy_test1, area_test1, market_test1):
    fridge_strategy_test1.event_market_cycle()
    assert fridge_strategy_test1.next_market == "new market"


"""TEST6"""


# Testing if bought energy cools the fridge for the right amount

def test_if_fridge_temperature_decreases_correct(fridge_strategy_test1, area_test1, market_test1):
    fridge_strategy_test1.event_tick(area=area_test1)
    # 6.0 = start fridge temp, 0.05*2 = cooling_temperature, tick_length... = warming per tick
    assert fridge_strategy_test1.fridge_temp == ((6.0 - (0.05 * 2))
                                                 + (area_test1.config.tick_length.in_seconds()
                                                    * round((0.02 / 60), 6)
                                                    )
                                                 )
