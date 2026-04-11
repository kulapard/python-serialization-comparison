"""
Benchmark: marshmallow vs marshmallow-recipe vs pydantic
========================================================
Compares dump (serialization) and load (deserialization) performance
across three popular Python serialization libraries.
"""

from __future__ import annotations

import dataclasses
import enum
import gc
import statistics
import time
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import marshmallow as ma
import marshmallow.fields as mf
import marshmallow_recipe as mr
import pydantic

# ──────────────────────────────────────────────
# 1. Shared domain model (plain dataclass)
# ──────────────────────────────────────────────

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


@dataclasses.dataclass
class Address:
    street: str
    city: str
    zip_code: str
    country: str


@dataclasses.dataclass
class Transaction:
    id: str
    amount: Decimal
    currency: str
    timestamp: datetime
    description: Optional[str] = None


@dataclasses.dataclass
class Account:
    id: str
    owner_name: str
    email: str
    balance: Decimal
    status: AccountStatus
    opened_at: date
    address: Address
    tags: list[str]
    transactions: list[Transaction]
    note: Optional[str] = None


# ──────────────────────────────────────────────
# 2. marshmallow schemas (hand-written)
# ──────────────────────────────────────────────

class MaAddressSchema(ma.Schema):
    street = mf.String(required=True)
    city = mf.String(required=True)
    zip_code = mf.String(required=True)
    country = mf.String(required=True)

    @ma.post_load
    def make(self, data, **_):
        return Address(**data)


class MaTransactionSchema(ma.Schema):
    id = mf.String(required=True)
    amount = mf.Decimal(required=True, as_string=True)
    currency = mf.String(required=True)
    timestamp = mf.DateTime(required=True)
    description = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Transaction(**data)


class MaAccountSchema(ma.Schema):
    id = mf.String(required=True)
    owner_name = mf.String(required=True)
    email = mf.Email(required=True)
    balance = mf.Decimal(required=True, as_string=True)
    status = mf.Enum(AccountStatus, by_value=True)
    opened_at = mf.Date(required=True)
    address = mf.Nested(MaAddressSchema, required=True)
    tags = mf.List(mf.String(), required=True)
    transactions = mf.List(mf.Nested(MaTransactionSchema), required=True)
    note = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Account(**data)


# ──────────────────────────────────────────────
# 3. marshmallow-recipe (uses top-level functions)
# ──────────────────────────────────────────────
# mr.dump(obj), mr.load(Cls, data), mr.dump_many([...]), mr.load_many(Cls, [...])
# mr.nuked.dump(Cls, obj), mr.nuked.load(Cls, data)  — faster "nuked" backend


# ──────────────────────────────────────────────
# 4. pydantic TypeAdapter (reuses shared dataclasses)
# ──────────────────────────────────────────────

AccountAdapter = pydantic.TypeAdapter(Account)


# ──────────────────────────────────────────────
# 5. Test data factories
# ──────────────────────────────────────────────

def make_address() -> Address:
    return Address(
        street="123 Benchmark Lane",
        city="Perfville",
        zip_code="90210",
        country="US",
    )


def make_transaction(i: int = 0) -> Transaction:
    return Transaction(
        id=str(uuid.UUID(int=i)),
        amount=Decimal("49.99"),
        currency="USD",
        timestamp=datetime(2025, 6, 15, 12, 30, 0),
        description=f"Payment #{i}",
    )


def make_account(n_txns: int = 3) -> Account:
    return Account(
        id="acc-001",
        owner_name="Alice Bench",
        email="alice@example.com",
        balance=Decimal("12345.67"),
        status=AccountStatus.ACTIVE,
        opened_at=date(2024, 1, 15),
        address=make_address(),
        tags=["premium", "verified", "benchmark"],
        transactions=[make_transaction(i) for i in range(n_txns)],
        note="Benchmark test account",
    )


def make_account_dict() -> dict:
    """Raw dict representation (as if received from an API)."""
    return {
        "id": "acc-001",
        "owner_name": "Alice Bench",
        "email": "alice@example.com",
        "balance": "12345.67",
        "status": "active",
        "opened_at": "2024-01-15",
        "address": {
            "street": "123 Benchmark Lane",
            "city": "Perfville",
            "zip_code": "90210",
            "country": "US",
        },
        "tags": ["premium", "verified", "benchmark"],
        "transactions": [
            {
                "id": str(uuid.UUID(int=i)),
                "amount": "49.99",
                "currency": "USD",
                "timestamp": "2025-06-15T12:30:00",
                "description": f"Payment #{i}",
            }
            for i in range(3)
        ],
        "note": "Benchmark test account",
    }


# ──────────────────────────────────────────────
# 6. Benchmark harness
# ──────────────────────────────────────────────

def bench(fn, *, warmup: int = 50, rounds: int = 200):
    """Return median execution time in seconds."""
    for _ in range(warmup):
        fn()
    gc.disable()
    try:
        times = []
        for _ in range(rounds):
            t0 = time.perf_counter()
            fn()
            times.append(time.perf_counter() - t0)
    finally:
        gc.enable()
    return statistics.median(times)


def fmt_time(seconds: float) -> str:
    us = seconds * 1_000_000
    if us < 1000:
        return f"{us:.1f} us"
    ms = us / 1000
    if ms < 1000:
        return f"{ms:.1f} ms"
    return f"{seconds:.2f} s"


def speedup_str(base: float, other: float) -> str:
    if other == 0:
        return "-"
    ratio = base / other
    if ratio >= 1:
        return f"{ratio:.1f}x"
    return f"1/{1/ratio:.1f}x"


# ──────────────────────────────────────────────
# 7. Runners: each returns (name, seconds)
# ──────────────────────────────────────────────

def run_dump_marshmallow(n: int):
    schema = MaAccountSchema()
    objs = [make_account() for _ in range(n)]
    return bench(lambda: [schema.dump(o) for o in objs])


def run_load_marshmallow(n: int):
    schema = MaAccountSchema()
    dicts = [make_account_dict() for _ in range(n)]
    return bench(lambda: [schema.load(d) for d in dicts])


def run_dump_mr(n: int):
    objs = [make_account() for _ in range(n)]
    return bench(lambda: [mr.dump(o) for o in objs])


def run_load_mr(n: int):
    dicts = [make_account_dict() for _ in range(n)]
    return bench(lambda: [mr.load(Account, d) for d in dicts])


def run_dump_mr_nuked(n: int):
    objs = [make_account() for _ in range(n)]
    return bench(lambda: [mr.nuked.dump(Account, o) for o in objs])


def run_load_mr_nuked(n: int):
    dicts = [make_account_dict() for _ in range(n)]
    return bench(lambda: [mr.nuked.load(Account, d) for d in dicts])


def run_dump_pydantic(n: int):
    objs = [make_account() for _ in range(n)]
    return bench(lambda: [AccountAdapter.dump_python(o) for o in objs])


def run_load_pydantic(n: int):
    dicts = [make_account_dict() for _ in range(n)]
    return bench(lambda: [AccountAdapter.validate_python(d) for d in dicts])


# ──────────────────────────────────────────────
# 8. Table renderer
# ──────────────────────────────────────────────

def render_table(rows: list[list[str]], headers: list[str]) -> str:
    """Render a Unicode box-drawing table."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def pad(cells):
        return [f" {c:<{widths[i]}} " for i, c in enumerate(cells)]

    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    header = "│" + "│".join(pad(headers)) + "│"

    lines = [top, header, mid]
    for i, row in enumerate(rows):
        lines.append("│" + "│".join(pad(row)) + "│")
        if i < len(rows) - 1:
            lines.append(mid)
    lines.append(bot)
    return "\n".join(lines)


# ──────────────────────────────────────────────
# 9. Main
# ──────────────────────────────────────────────

def main():
    import importlib.metadata

    scales = [1, 100, 1000]
    operations = ["dump", "load"]

    lib_runners = {
        "marshmallow": {"dump": run_dump_marshmallow, "load": run_load_marshmallow},
        "mr-recipe": {"dump": run_dump_mr, "load": run_load_mr},
        "mr-recipe-nuked": {"dump": run_dump_mr_nuked, "load": run_load_mr_nuked},
        "pydantic": {"dump": run_dump_pydantic, "load": run_load_pydantic},
    }
    lib_names = list(lib_runners.keys())

    # Print versions
    ma_ver = importlib.metadata.version("marshmallow")
    mr_ver = importlib.metadata.version("marshmallow-recipe")
    pyd_ver = importlib.metadata.version("pydantic")
    print()
    print(f"  marshmallow        {ma_ver}")
    print(f"  marshmallow-recipe {mr_ver}")
    print(f"  pydantic           {pyd_ver}")
    print()

    # Collect results: results[op][n][lib] = seconds
    results: dict[str, dict[int, dict[str, float]]] = {}
    total = len(operations) * len(scales) * len(lib_names)
    done = 0

    for op in operations:
        results[op] = {}
        for n in scales:
            results[op][n] = {}
            for lib in lib_names:
                done += 1
                tag = f"{op} x {n:<4} [{lib}]"
                print(f"  [{done:>2}/{total}] {tag:40s} ...", end="", flush=True)
                t = lib_runners[lib][op](n)
                results[op][n][lib] = t
                print(f" {fmt_time(t)}")

    # ── Pairwise comparison tables ──
    comparisons = [
        ("marshmallow", "mr-recipe"),
        ("marshmallow", "mr-recipe-nuked"),
        ("marshmallow", "pydantic"),
        ("mr-recipe", "mr-recipe-nuked"),
    ]

    for base_lib, cmp_lib in comparisons:
        headers = ["Operation", base_lib, cmp_lib, "Speedup"]
        rows = []
        for op in operations:
            for n in scales:
                t_base = results[op][n][base_lib]
                t_cmp = results[op][n][cmp_lib]
                rows.append([
                    f"{op} x {n}",
                    fmt_time(t_base),
                    fmt_time(t_cmp),
                    speedup_str(t_base, t_cmp),
                ])

        print()
        print(f"  {base_lib} vs {cmp_lib}")
        print()
        for line in render_table(rows, headers).splitlines():
            print(f"  {line}")
        print()

    # ── Times table ──
    headers = ["Operation"] + lib_names
    rows = []
    for op in operations:
        for n in scales:
            cells = [f"{op} x {n}"]
            for lib in lib_names:
                cells.append(fmt_time(results[op][n][lib]))
            rows.append(cells)

    print()
    print("  Times")
    print()
    for line in render_table(rows, headers).splitlines():
        print(f"  {line}")
    print()

    # ── Speedup vs marshmallow table ──
    baseline = lib_names[0]  # marshmallow
    compare_libs = lib_names[1:]
    headers = ["Operation"] + [f"vs {lib}" for lib in compare_libs]
    rows = []
    for op in operations:
        for n in scales:
            t_base = results[op][n][baseline]
            cells = [f"{op} x {n}"]
            for lib in compare_libs:
                cells.append(speedup_str(t_base, results[op][n][lib]))
            rows.append(cells)

    print(f"  Speedup (vs {baseline})")
    print()
    for line in render_table(rows, headers).splitlines():
        print(f"  {line}")
    print()


if __name__ == "__main__":
    main()
