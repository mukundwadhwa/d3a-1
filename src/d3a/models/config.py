import ast
from pendulum import duration, Duration

from d3a.d3a_core.exceptions import D3AException
from d3a.d3a_core.util import format_interval
from d3a.models.const import ConstSettings
from d3a.models.read_user_profile import read_arbitrary_profile
from d3a.models.read_user_profile import InputProfileTypes


class SimulationConfig:
    def __init__(self, duration: duration, slot_length: duration, tick_length: duration,
                 market_count: int, cloud_coverage: int, market_maker_rate, iaa_fee: int,
                 pv_user_profile=None):
        self.duration = duration
        self.slot_length = slot_length
        self.tick_length = tick_length
        self.market_count = market_count
        self.ticks_per_slot = self.slot_length / self.tick_length
        if self.ticks_per_slot != int(self.ticks_per_slot):
            raise D3AException(
                "Non integer ticks per slot ({}) are not supported. "
                "Adjust simulation parameters.".format(self.ticks_per_slot))
        self.ticks_per_slot = int(self.ticks_per_slot)
        if self.ticks_per_slot < 10:
            raise D3AException("Too few ticks per slot ({}). Adjust simulation parameters".format(
                self.ticks_per_slot
            ))
        self.total_ticks = self.duration // self.slot_length * self.ticks_per_slot
        # TODO: Once the d3a uses a common API to the d3a-web, this should be removed
        # since this limitation already exists on d3a-web
        if 0 <= cloud_coverage <= 2:
            self.cloud_coverage = cloud_coverage
        else:
            raise D3AException("Invalid cloud coverage value ({}).".format(cloud_coverage))

        self.pv_user_profile = None \
            if pv_user_profile is None \
            else read_arbitrary_profile(InputProfileTypes.POWER,
                                        ast.literal_eval(pv_user_profile),
                                        self.slot_length)
        self.market_maker_rate = read_arbitrary_profile(InputProfileTypes.IDENTITY,
                                                        ast.literal_eval(market_maker_rate),
                                                        self.slot_length)

        if iaa_fee is None:
            self.iaa_fee = ConstSettings.IAASettings.FEE_PERCENTAGE
        else:
            self.iaa_fee = iaa_fee

    def __repr__(self):
        return (
            "<SimulationConfig("
            "duration='{s.duration}', "
            "slot_length='{s.slot_length}', "
            "tick_length='{s.tick_length}', "
            "market_count='{s.market_count}', "
            "ticks_per_slot='{s.ticks_per_slot}', "
            "cloud_coverage='{s.cloud_coverage}', "
            "pv_user_profile='{s.pv_user_profile}'. "
            "market_maker_rate='{s.market_maker_rate}', "
            ")>"
        ).format(s=self)

    def as_dict(self):
        fields = {'duration', 'slot_length', 'tick_length', 'market_count', 'ticks_per_slot',
                  'total_ticks', 'cloud_coverage'}
        return {
            k: format_interval(v) if isinstance(v, Duration) else v
            for k, v in self.__dict__.items()
            if k in fields
        }
