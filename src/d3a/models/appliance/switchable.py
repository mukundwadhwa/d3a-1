from d3a.models.appliance.mixins import SwitchableMixin
from d3a.models.appliance.simple import SimpleAppliance


class SwitchableAppliance(SwitchableMixin, SimpleAppliance):

    def __init__(self):
        super().__init__()

    def event_tick(self, *, area_id):
        if self.is_on:
            super().event_tick(area_id=area_id)
