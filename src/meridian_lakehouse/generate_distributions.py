"""Seeded sampling for the synthetic core banking generator.

Everything here is pure: the same seed always yields the same records. No I/O and no
dirt. Dirt is applied to rendered rows in generate_dirt.py.
"""

import math
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta, timezone
from decimal import Decimal
from itertools import accumulate

from faker import Faker

from meridian_lakehouse.transactions import Channel, Direction, Transaction

N_ACCOUNTS = 2_000
N_HIGH_VOLUME = 20
HIGH_VOLUME_WEIGHT = 20.0
N_MERCHANTS = 400
N_PARTIES = 600
N_BRANCHES = 20
BASE_ROWS_PER_WEEKDAY = 500

# Bank local time, used for business-hour weighting. Fixed offset (US Eastern standard);
# DST is ignored because it adds a tzdata dependency on Windows and changes nothing downstream.
BANK_TZ = timezone(timedelta(hours=-5))

WEEKDAY_FACTOR = (1.0, 1.0, 1.0, 1.0, 1.1, 0.6, 0.4)  # Monday..Sunday

# Relative weight of each local hour, 00..23.
HOUR_WEIGHTS = (
    0.2, 0.2, 0.2, 0.2, 0.2, 0.3,
    0.5, 1.0, 2.0, 4.0, 4.0, 4.0,
    5.0, 4.0, 4.0, 4.0, 4.0, 3.0,
    2.5, 2.0, 1.5, 1.0, 0.6, 0.3,
)  # fmt: skip

CHANNEL_WEIGHTS = {
    Channel.CARD: 55,
    Channel.ACH: 20,
    Channel.ATM: 10,
    Channel.BRANCH: 10,
    Channel.WIRE: 5,
}

# (median, sigma, cap) of the log-normal amount for each channel.
AMOUNT_PARAMS = {
    Channel.CARD: (35.0, 1.0, 5_000.0),
    Channel.ACH: (400.0, 1.1, 50_000.0),
    Channel.ATM: (80.0, 0.6, 1_000.0),
    Channel.BRANCH: (300.0, 1.2, 50_000.0),
    Channel.WIRE: (5_000.0, 1.3, 1_000_000.0),
}

CREDIT_SHARE = {
    Channel.CARD: 0.03,  # refunds
    Channel.ACH: 0.40,  # payroll, transfers in
    Channel.ATM: 0.0,
    Channel.BRANCH: 0.50,  # deposits vs withdrawals
    Channel.WIRE: 0.50,
}

# MCC codes: grocery, restaurants, fuel, misc retail, taxi, electronics. Gambling (7995) and
# quasi-cash (6051) are rare on purpose so MCC risk scoring has something to find.
MCC_WEIGHTS = {
    "5411": 25, "5812": 20, "5541": 15, "5999": 15,
    "4121": 8, "5732": 7, "7995": 1, "6051": 1,
}  # fmt: skip

FOREIGN_COUNTRY_WEIGHTS = {
    "GB": 25, "CA": 20, "DE": 15, "MX": 15, "FR": 10,
    "CN": 8, "AE": 4, "PA": 2, "CY": 1,
}  # fmt: skip

CURRENCY_BY_COUNTRY = {
    "US": "USD", "GB": "GBP", "CA": "CAD", "DE": "EUR", "MX": "MXN",
    "FR": "EUR", "CN": "CNY", "AE": "AED", "PA": "USD", "CY": "EUR",
}  # fmt: skip

MERCHANT_FOREIGN_SHARE = 0.02
PARTY_FOREIGN_SHARE = 0.15
PARTY_PERSON_SHARE = 0.60
CARD_NOT_PRESENT_SHARE = 0.30
SECOND_DEVICE_SHARE = 0.10
UNUSUAL_IP_SHARE = 0.05


@dataclass(frozen=True, slots=True)
class Account:
    account_id: str
    home_branch: str
    primary_device: str
    secondary_device: str
    ip_address: str
    weight: float


@dataclass(frozen=True, slots=True)
class Counterparty:
    counterparty_id: str
    name: str
    country: str


# ATM and branch transactions are against the bank itself.
BANK_COUNTERPARTY = Counterparty("CP-MERIDIAN", "Meridian Bank", "US")


@dataclass(frozen=True, slots=True)
class Population:
    """Accounts and counterparties shared by every day of one generator run."""

    accounts: tuple[Account, ...]
    account_cum_weights: tuple[float, ...]
    branches: tuple[str, ...]
    merchants: tuple[Counterparty, ...]
    parties: tuple[Counterparty, ...]
    domestic_parties: tuple[Counterparty, ...]


def _pick[K](rng: random.Random, weights: dict[K, float]) -> K:
    return rng.choices(tuple(weights), weights=tuple(weights.values()))[0]


def _device_id(rng: random.Random) -> str:
    return f"DEV-{rng.getrandbits(48):012x}"


def _ip_address(rng: random.Random) -> str:
    return ".".join(
        str(octet)
        for octet in (rng.randint(11, 223), rng.randint(0, 255), rng.randint(0, 255),
                      rng.randint(1, 254))
    )


def _country(rng: random.Random, foreign_share: float) -> str:
    return _pick(rng, FOREIGN_COUNTRY_WEIGHTS) if rng.random() < foreign_share else "US"


def build_population(seed: int) -> Population:
    rng = random.Random(f"{seed}:population")
    fake = Faker("en_US")
    fake.seed_instance(seed)

    branches = tuple(f"BR-{i:03d}" for i in range(1, N_BRANCHES + 1))
    high_volume = set(rng.sample(range(N_ACCOUNTS), N_HIGH_VOLUME))
    accounts = tuple(
        Account(
            account_id=f"ACC-{i + 1:07d}",
            home_branch=rng.choice(branches),
            primary_device=_device_id(rng),
            secondary_device=_device_id(rng),
            ip_address=_ip_address(rng),
            weight=HIGH_VOLUME_WEIGHT if i in high_volume else rng.uniform(0.5, 1.5),
        )
        for i in range(N_ACCOUNTS)
    )
    merchants = tuple(
        Counterparty(f"MER-{i + 1:05d}", fake.company(), _country(rng, MERCHANT_FOREIGN_SHARE))
        for i in range(N_MERCHANTS)
    )
    parties = tuple(
        Counterparty(
            f"CP-{i + 1:06d}",
            fake.name() if rng.random() < PARTY_PERSON_SHARE else fake.company(),
            _country(rng, PARTY_FOREIGN_SHARE),
        )
        for i in range(N_PARTIES)
    )
    return Population(
        accounts=accounts,
        account_cum_weights=tuple(accumulate(a.weight for a in accounts)),
        branches=branches,
        merchants=merchants,
        parties=parties,
        domestic_parties=tuple(p for p in parties if p.country == "US"),
    )


def day_rng(seed: int, day: date) -> random.Random:
    """Independent stream per day, so day N is identical whatever --days is."""
    return random.Random(f"{seed}:{day.isoformat()}")


def rows_for_day(day: date, rng: random.Random) -> int:
    factor = WEEKDAY_FACTOR[day.weekday()] * rng.uniform(0.9, 1.1)
    return round(BASE_ROWS_PER_WEEKDAY * factor)


def sample_timestamp(day: date, rng: random.Random) -> datetime:
    hour = rng.choices(range(24), weights=HOUR_WEIGHTS)[0]
    local = datetime.combine(day, time(hour, rng.randrange(60), rng.randrange(60)), BANK_TZ)
    return local.astimezone(UTC)


def sample_amount(channel: Channel, rng: random.Random) -> Decimal:
    median, sigma, cap = AMOUNT_PARAMS[channel]
    raw = min(rng.lognormvariate(math.log(median), sigma), cap)
    if channel is Channel.ATM:
        return Decimal(max(20, round(raw / 20) * 20)).quantize(Decimal("0.01"))
    return max(Decimal(f"{raw:.2f}"), Decimal("1.00"))


def _sample_transaction(
    txn_id: str, timestamp: datetime, rng: random.Random, population: Population
) -> Transaction:
    account = rng.choices(population.accounts, cum_weights=population.account_cum_weights)[0]
    channel = _pick(rng, CHANNEL_WEIGHTS)
    credit = rng.random() < CREDIT_SHARE[channel]

    if channel is Channel.CARD:
        counterparty = rng.choice(population.merchants)
    elif channel is Channel.ACH:
        counterparty = rng.choice(population.domestic_parties)  # ACH is domestic-only
    elif channel is Channel.WIRE:
        counterparty = rng.choice(population.parties)
    else:
        counterparty = BANK_COUNTERPARTY

    if channel is Channel.BRANCH:
        branch_id = account.home_branch
    elif channel is Channel.ATM:
        branch_id = rng.choice(population.branches)
    else:
        branch_id = None

    online = channel in (Channel.ACH, Channel.WIRE) or (
        channel is Channel.CARD and rng.random() < CARD_NOT_PRESENT_SHARE
    )
    device_id = ip_address = None
    if online:
        use_second = rng.random() < SECOND_DEVICE_SHARE
        device_id = account.secondary_device if use_second else account.primary_device
        unusual_ip = rng.random() < UNUSUAL_IP_SHARE
        ip_address = _ip_address(rng) if unusual_ip else account.ip_address

    return Transaction(
        txn_id=txn_id,
        account_id=account.account_id,
        counterparty_id=counterparty.counterparty_id,
        counterparty_name=counterparty.name,
        amount=sample_amount(channel, rng),
        currency=CURRENCY_BY_COUNTRY[counterparty.country],
        timestamp=timestamp,
        channel=channel,
        direction=Direction.CREDIT if credit else Direction.DEBIT,
        merchant_category=_pick(rng, MCC_WEIGHTS) if channel is Channel.CARD else None,
        country=counterparty.country,
        branch_id=branch_id,
        device_id=device_id,
        ip_address=ip_address,
    )


def generate_day(day: date, seed: int, population: Population) -> list[Transaction]:
    """Clean transactions for one business day, ordered by timestamp."""
    rng = day_rng(seed, day)
    timestamps = sorted(sample_timestamp(day, rng) for _ in range(rows_for_day(day, rng)))
    return [
        _sample_transaction(f"TXN-{day:%Y%m%d}-{seq:06d}", ts, rng, population)
        for seq, ts in enumerate(timestamps, start=1)
    ]
