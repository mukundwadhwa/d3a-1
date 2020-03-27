from d3a.models.market.grid_fees import BaseClassGridFees
from d3a.models.market.market_structures import TradeBidInfo


class ConstantGridFees(BaseClassGridFees):

    def update_incoming_bid_with_fee(self, source_bid, original_bid):
        if source_bid is None:
            return original_bid
        return source_bid

    def update_incoming_offer_with_fee(self, source_offer_price, original_offer_price):
        if source_offer_price is None:
            return original_offer_price + self.grid_fee_rate
        return source_offer_price + self.grid_fee_rate

    def calculate_original_trade_rate_from_clearing_rate(
            self, original_bid_rate, propagated_bid_rate,
            clearing_rate):
        """
        Used only for 2-sided pay as clear market. The purpose of this function is to adapt the
        clearing rate calculated via the clearing algorithm to match the expected price the
        original device has to pay once the trade chain settles. The clearing rate is scaled
        with regards to the demand side tax (to be precise, the ratio of the original bid rate to
        the propagated bid rate).
        :param original_bid_rate: Original bid rate
        :param propagated_bid_rate: Propagated bid rate
        :param clearing_rate: Clearing rate calculated by the 2-sided pay as clear algorithm
        :return: Original trade rate, that the original device has to pay once the trade
        chain settles.
        """
        return clearing_rate + (original_bid_rate - propagated_bid_rate)

    def update_forwarded_bid_with_fee(self, source_bid, original_bid):
        if source_bid is None:
            return original_bid - self.grid_fee_rate
        return source_bid - self.grid_fee_rate

    def update_forwarded_offer_with_fee(self, source_offer, original_offer):
        return source_offer

    def update_forwarded_bid_trade_original_info(self, trade_original_info, market_bid):
        if not trade_original_info:
            return None
        original_offer_rate, offer_rate, trade_rate_source = trade_original_info
        return [market_bid.original_bid_price / market_bid.energy,
                market_bid.energy_rate,
                original_offer_rate,
                offer_rate,
                trade_rate_source]

    def update_forwarded_offer_trade_original_info(self, trade_original_info, market_offer):
        if not trade_original_info:
            return None
        original_bid_rate, bid_rate, trade_rate_source = trade_original_info
        trade_bid_info = TradeBidInfo(
            original_bid_rate=original_bid_rate, propagated_bid_rate=bid_rate,
            original_offer_rate=market_offer.original_offer_price / market_offer.energy,
            propagated_offer_rate=market_offer.energy_rate,
            trade_rate=trade_rate_source)
        return trade_bid_info

    def propagate_original_bid_info_on_offer_trade(self, trade_original_info):
        if trade_original_info is None:
            return None
        original_bid_rate, bid_rate, _, _, trade_rate_source = trade_original_info
        bid_rate = bid_rate - self.grid_fee_rate
        return [original_bid_rate, bid_rate, trade_rate_source]

    def propagate_original_offer_info_on_bid_trade(self, trade_original_info):
        _, _, original_offer_rate, offer_rate, trade_rate_source = trade_original_info
        offer_rate = offer_rate + self.grid_fee_rate
        return [original_offer_rate, offer_rate, trade_rate_source]

    def calculate_trade_price_and_fees(self, trade_bid_info):
        original_bid_rate, bid_rate, original_offer_rate, \
            offer_rate, trade_rate_source = trade_bid_info

        return trade_rate_source - self.grid_fee_rate, self.grid_fee_rate, trade_rate_source