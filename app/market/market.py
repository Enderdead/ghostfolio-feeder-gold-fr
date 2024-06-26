from .mvis import mvis
from .corriere import corriere
from .byblos import byblos
from .boerse_frankfurt import boerse_frankfurt
from .fondofonte import fondofonte
from .local import local
from .gold import gold_fr


class Market:
    """
    Represents the market and provides methods to fetch data from different sources.

    Attributes:
        ticker (str): The ticker symbol of the asset.
        start_date (str): The start date for fetching data (optional).
        end_date (str): The end date for fetching data (optional).
    """

    def __init__(
            self, ticker: str, start_date: str | None = None, end_date: str | None = None
        ) -> None:
        if ticker is None:
            raise ValueError("To create the object you have to insert a ticker")
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date


    def mvis(self) -> list:
        """Fetches market data from MVIS."""
        return mvis(self.ticker, self.start_date, self.end_date)

    def corriere(self) -> list:
        """Fetches market data from Corriere."""
        return corriere(self.ticker, self.start_date, self.end_date)

    def byblos(self) -> list:
        """Fetches market data from Byblos."""
        return byblos(self.ticker, self.start_date, self.end_date)

    def boerse_frankfurt(self) -> list:
        """Fetches market data from Börse Frankfurt."""
        return boerse_frankfurt(self.ticker, self.start_date, self.end_date)

    def fondofonte(self) -> list:
        """Fetches market data from Fondofonte."""
        return fondofonte(self.ticker, self.start_date, self.end_date)

    def local(self) -> list:
        """Fetches market data from local source."""
        return local(self.ticker, self.start_date, self.end_date)

    def gold(self) -> list:
        """Fetches stock data from MVIS."""
        return gold_fr(self.ticker, self.start_date, self.end_date)


data_source_mapping = {
    "mvis": Market.mvis,
    "corriere": Market.corriere,
    "byblos": Market.byblos,
    "boerse_frankfurt": Market.boerse_frankfurt,
    "fondofonte": Market.fondofonte,
    "local": Market.local,
    "gold_fr": Market.gold
}
