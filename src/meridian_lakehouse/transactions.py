"""The core banking transaction record.

All fourteen fields are fraud-ready by design (see .claude/rules/transaction-schema.md).
Every column is always present; a value is None only where the field does not apply to
the channel, e.g. no device_id on a branch counter transaction.
"""

from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum


class Channel(StrEnum):
    WIRE = "wire"
    ACH = "ach"
    CARD = "card"
    ATM = "atm"
    BRANCH = "branch"


class Direction(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass(frozen=True, slots=True)
class Transaction:
    txn_id: str
    account_id: str
    counterparty_id: str
    counterparty_name: str | None
    amount: Decimal
    currency: str
    timestamp: datetime
    channel: Channel
    direction: Direction
    merchant_category: str | None
    country: str
    branch_id: str | None
    device_id: str | None
    ip_address: str | None

    def __post_init__(self) -> None:
        if self.timestamp.utcoffset() != timedelta(0):
            raise ValueError(f"timestamp must be tz-aware UTC, got {self.timestamp!r}")
        if self.amount <= 0:
            raise ValueError(f"amount must be positive (direction carries sign), got {self.amount}")
        if self.amount != self.amount.quantize(Decimal("0.01")):
            raise ValueError(f"amount must have at most 2 decimal places, got {self.amount}")
        if not isinstance(self.channel, Channel):
            raise TypeError(f"channel must be a Channel, got {self.channel!r}")
        if not isinstance(self.direction, Direction):
            raise TypeError(f"direction must be a Direction, got {self.direction!r}")


# Column order of every CSV the generator writes. Derived from the dataclass so the two
# cannot drift apart.
CSV_COLUMNS: tuple[str, ...] = tuple(f.name for f in fields(Transaction))
