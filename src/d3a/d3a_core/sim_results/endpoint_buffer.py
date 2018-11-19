from d3a.d3a_core.sim_results.area_statistics import export_cumulative_grid_trades, \
    export_cumulative_loads, export_price_energy_day
from d3a.d3a_core.sim_results.export_unmatched_loads import export_unmatched_loads
from d3a.d3a_core.sim_results.stats import energy_bills
from collections import OrderedDict
from statistics import mean


_NO_VALUE = {
    'min': None,
    'avg': None,
    'max': None
}


class SimulationEndpointBuffer:
    def __init__(self, job_id, initial_params):
        self.job_id = job_id
        self.random_seed = initial_params["seed"] if initial_params["seed"] is not None else ''
        self.status = {}
        self.unmatched_loads = {}
        self.cumulative_loads = {}
        self.price_energy_day = {}
        self.cumulative_grid_trades = {}
        self.tree_summary = {}
        self.bills = {}

    def generate_result_report(self):
        return {
            "job_id": self.job_id,
            "random_seed": self.random_seed,
            **self.unmatched_loads,
            "cumulative_loads": self.cumulative_loads,
            "price_energy_day": self.price_energy_day,
            "cumulative_grid_trades": self.cumulative_grid_trades,
            "bills": self.bills,
            "tree_summary": self.tree_summary,
            "status": self.status
        }

    def update_stats(self, area, simulation_status):
        self.status = simulation_status
        self.unmatched_loads = {"unmatched_loads": export_unmatched_loads(area)}
        self.cumulative_loads = {
            "price-currency": "Euros",
            "load-unit": "kWh",
            "cumulative-load-price": export_cumulative_loads(area)
        }
        self.price_energy_day = {
            "price-currency": "Euros",
            "load-unit": "kWh",
            "price-energy-day": export_price_energy_day(area)
        }
        self.cumulative_grid_trades = export_cumulative_grid_trades(area)
        self._update_bills(area)
        self._update_tree_summary(area)

    def _update_tree_summary(self, area):
        price_energy_list = export_price_energy_day(area)

        def calculate_prices(key, functor):
            # Need to convert to euro cents to avoid having to change the backend
            # TODO: Both this and the frontend have to remove the recalculation
            energy_prices = [price_energy[key] for price_energy in price_energy_list]
            return round(100 * functor(energy_prices), 2) if len(energy_prices) > 0 else 0.0

        self.tree_summary[area.slug] = {
            "min_trade_price": calculate_prices("min_price", min),
            "max_trade_price": calculate_prices("max_price", max),
            "avg_trade_price": calculate_prices("av_price", mean),
        }
        for child in area.children:
            if child.children != []:
                self._update_tree_summary(child)

    def _update_bills(self, area):
        result = energy_bills(area)
        self.bills = OrderedDict(sorted(result.items()))