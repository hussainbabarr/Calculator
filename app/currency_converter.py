"""Currency conversion backed by a live exchange-rate API.

Improvements over the original browser-based version:
  * Explicit request timeout (the JS ``fetch`` call had none).
  * Rates are cached in memory with a time-to-live so every keystroke does
    not trigger a network request.
  * Errors are represented as a typed exception rather than a bare
    ``console.error`` + silently failing UI.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import requests

from . import config


class CurrencyConverterError(Exception):
    """Raised when exchange rates cannot be fetched or a conversion is invalid."""


@dataclass
class ConversionResult:
    amount: float
    from_currency: str
    to_currency: str
    converted_amount: float
    rate: float


class CurrencyConverter:
    """Fetches and caches USD-based exchange rates and performs conversions."""

    def __init__(
        self,
        api_url: str = config.EXCHANGE_RATE_API_URL,
        timeout: int = config.REQUEST_TIMEOUT_SECONDS,
        cache_ttl: int = config.RATE_CACHE_TTL_SECONDS,
    ) -> None:
        self._api_url = api_url
        self._timeout = timeout
        self._cache_ttl = cache_ttl
        self._rates: dict[str, float] = {}
        self._last_fetched_monotonic: float | None = None
        self._last_updated_label: str = ""

    @property
    def last_updated_label(self) -> str:
        """Human-readable label of when rates were last refreshed."""
        return self._last_updated_label

    def _is_cache_fresh(self) -> bool:
        return (
            bool(self._rates)
            and self._last_fetched_monotonic is not None
            and (time.monotonic() - self._last_fetched_monotonic) < self._cache_ttl
        )

    def refresh_rates(self, force: bool = False) -> None:
        """Fetch the latest USD exchange rates from the API.

        Args:
            force: If True, bypass the in-memory cache and always hit the network.

        Raises:
            CurrencyConverterError: On network failure, timeout, or an
                unexpected response payload.
        """
        if not force and self._is_cache_fresh():
            return

        try:
            response = requests.get(self._api_url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.Timeout as exc:
            raise CurrencyConverterError(
                "The exchange rate service timed out. Please try again."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise CurrencyConverterError(
                "Could not reach the exchange rate service. Check your internet connection."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            raise CurrencyConverterError(
                f"Exchange rate service returned an error: {exc.response.status_code}"
            ) from exc
        except ValueError as exc:  # JSON decoding failure
            raise CurrencyConverterError(
                "Received an unreadable response from the exchange rate service."
            ) from exc

        rates = payload.get("rates")
        if not isinstance(rates, dict) or not rates:
            raise CurrencyConverterError("Exchange rate response did not contain rates.")

        self._rates = rates
        self._last_fetched_monotonic = time.monotonic()
        self._last_updated_label = f"Last updated: {payload.get('date', 'unknown date')}"

    def convert(self, amount: float, from_currency: str, to_currency: str) -> ConversionResult:
        """Convert ``amount`` from one currency to another using cached rates.

        Raises:
            CurrencyConverterError: If rates have not been loaded yet or a
                requested currency code is unsupported.
        """
        if not self._rates:
            raise CurrencyConverterError("Exchange rates have not been loaded yet.")

        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        for code in (from_currency, to_currency):
            if code != "USD" and code not in self._rates:
                raise CurrencyConverterError(f"Unsupported currency code: {code}")

        if from_currency == to_currency:
            rate = 1.0
        elif from_currency == "USD":
            rate = self._rates[to_currency]
        elif to_currency == "USD":
            rate = 1.0 / self._rates[from_currency]
        else:
            rate = self._rates[to_currency] / self._rates[from_currency]

        return ConversionResult(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            converted_amount=amount * rate,
            rate=rate,
        )