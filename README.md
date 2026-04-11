# serialization-benchmark

Benchmark comparing **marshmallow**, **marshmallow-recipe**, and **pydantic** serialization performance on deeply nested dataclass models.

All libraries operate on the same plain `@dataclasses.dataclass` types — no library-specific model definitions.

## TL;DR

| | marshmallow | marshmallow-recipe | mr-recipe nuked | pydantic |
|---|:---:|:---:|:---:|:---:|
| **Speed (vs marshmallow)** | 1x | ~1x load / 0.2x dump | 7-27x | 9-38x |
| **Install size** | 0.4 MB | 1.7 MB | _(included)_ | 8.1 MB |
| **Backend** | Pure Python | Pure Python | Rust (PyO3) | Rust (pydantic-core) |
| **Schema definition** | Hand-written | Auto from dataclasses | _(same)_ | Auto (multiple ways) |
| **Features** | Flexible hooks, plugins | Minimal, ergonomic | _(same)_ | Richest (JSON Schema, OpenAPI, strict mode, generics) |
| **Best for** | Existing marshmallow codebases | Dataclass-centric projects on marshmallow | _(same, need speed)_ | New projects needing speed + features |

## Model structure

A 10-level-deep `Organization` hierarchy with lists, nested objects, enums, `Decimal`, `date`, `datetime`, and `Optional` fields:

```
Organization                          # L1
└── Department                        # L2
    └── Team                          # L3
        └── Employee                  # L4
            ├── Contract              # L5
            │   └── Terms             # L6
            │       └── Clause        # L7
            └── Project               # L5
                └── Task              # L6
                    └── SubTask       # L7
                        └── Comment   # L8
                            └── Reaction  # L9
                                └── Author    # L10
```

A single `Organization` object contains **2 departments x 2 teams x 2 employees**, each with **1 contract** (2 clauses) and **2 projects** (2 tasks each, 2 subtasks each, 1 comment with 2 reactions).

## Libraries under test

| Library | Version | Backend | How it's used |
|---|---|---|---|
| **marshmallow** | 3.26.2 | Pure Python | Hand-written `Schema` classes with `@post_load` |
| **marshmallow-recipe** | 0.0.93 | Pure Python | `mr.dump(obj)` / `mr.load(Cls, data)` — auto-generated from dataclasses |
| **marshmallow-recipe (nuked)** | 0.0.93 | Rust (PyO3) | `mr.nuked.dump(Cls, obj)` / `mr.nuked.load(Cls, data)` |
| **pydantic** | 2.12.5 | Rust (pydantic-core) | `TypeAdapter(Cls).dump_python(obj)` / `.validate_python(data)` |

## Test conditions

| Parameter | Value |
|---|---|
| Machine | Apple M1 Pro, 32 GB RAM |
| OS | macOS 26.3.1 (arm64) |
| Python | 3.14.3 |
| Timing | Median of adaptive runs (min 10 rounds, 2 s budget per benchmark) |
| GC | Disabled during measurement |
| Scales | 1, 100, 1000 objects per call |

## Results

### Times

```
┌─────────────┬─────────────┬───────────┬─────────────────┬──────────┐
│ Operation   │ marshmallow │ mr-recipe │ mr-recipe-nuked │ pydantic │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ dump x 1    │ 2.1 ms      │ 11.7 ms   │ 206.8 us        │ 156.6 us │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ dump x 100  │ 222.2 ms    │ 1.20 s    │ 24.2 ms         │ 19.0 ms  │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ dump x 1000 │ 2.17 s      │ 12.65 s   │ 315.9 ms        │ 238.1 ms │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ load x 1    │ 11.3 ms     │ 9.9 ms    │ 423.4 us        │ 297.6 us │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ load x 100  │ 1.10 s      │ 984.4 ms  │ 46.0 ms         │ 34.6 ms  │
├─────────────┼─────────────┼───────────┼─────────────────┼──────────┤
│ load x 1000 │ 10.99 s     │ 9.85 s    │ 463.8 ms        │ 351.0 ms │
└─────────────┴─────────────┴───────────┴─────────────────┴──────────┘
```

### Speedup vs marshmallow

```
┌─────────────┬──────────────┬────────────────────┬─────────────┐
│ Operation   │ vs mr-recipe │ vs mr-recipe-nuked │ vs pydantic │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ dump x 1    │ 1/5.6x       │ 10.1x              │ 13.3x       │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ dump x 100  │ 1/5.4x       │ 9.2x               │ 11.7x       │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ dump x 1000 │ 1/5.8x       │ 6.9x               │ 9.1x        │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ load x 1    │ 1.1x         │ 26.7x              │ 37.9x       │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ load x 100  │ 1.1x         │ 24.0x              │ 31.8x       │
├─────────────┼──────────────┼────────────────────┼─────────────┤
│ load x 1000 │ 1.1x         │ 23.7x              │ 31.3x       │
└─────────────┴──────────────┴────────────────────┴─────────────┘
```

### marshmallow-recipe: standard vs nuked

```
┌─────────────┬───────────┬─────────────────┬─────────┐
│ Operation   │ mr-recipe │ mr-recipe-nuked │ Speedup │
├─────────────┼───────────┼─────────────────┼─────────┤
│ dump x 1    │ 11.7 ms   │ 206.8 us        │ 56.4x   │
├─────────────┼───────────┼─────────────────┼─────────┤
│ dump x 100  │ 1.20 s    │ 24.2 ms         │ 49.5x   │
├─────────────┼───────────┼─────────────────┼─────────┤
│ dump x 1000 │ 12.65 s   │ 315.9 ms        │ 40.0x   │
├─────────────┼───────────┼─────────────────┼─────────┤
│ load x 1    │ 9.9 ms    │ 423.4 us        │ 23.4x   │
├─────────────┼───────────┼─────────────────┼─────────┤
│ load x 100  │ 984.4 ms  │ 46.0 ms         │ 21.4x   │
├─────────────┼───────────┼─────────────────┼─────────┤
│ load x 1000 │ 9.85 s    │ 463.8 ms        │ 21.2x   │
└─────────────┴───────────┴─────────────────┴─────────┘
```

### Installed size

```
┌───────────────────────────────────────┬────────┬──────────────────────────────────────┐
│ Library (with dependencies)           │ Total  │ Breakdown                            │
├───────────────────────────────────────┼────────┼──────────────────────────────────────┤
│ marshmallow                           │ 0.4 MB │ marshmallow 0.4 MB                   │
├───────────────────────────────────────┼────────┼──────────────────────────────────────┤
│ marshmallow-recipe (+ marshmallow)    │ 1.7 MB │ mr-recipe 1.3 MB + marshmallow 0.4 MB│
├───────────────────────────────────────┼────────┼──────────────────────────────────────┤
│ pydantic (+ pydantic-core)            │ 8.1 MB │ pydantic 3.8 MB + core 4.4 MB        │
└───────────────────────────────────────┴────────┴──────────────────────────────────────┘
```

Rust binary (`.so`) sizes:
- **marshmallow-recipe** `_nuked.so` — 0.7 MB
- **pydantic-core** `_pydantic_core.so` — 4.0 MB

## Feature comparison

### Schema definition

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| Hand-written schemas | Yes | — | Yes (`BaseModel`) |
| Auto from dataclasses | — | Yes | Yes (`TypeAdapter`) |
| Auto from TypedDict | — | — | Yes |
| Dynamic model creation | — | — | Yes (`create_model()`) |
| Generic models | — | — | Yes (`Generic[T]`) |
| Computed fields | — | — | Yes (`@computed_field`) |

### Validation

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| Built-in validators | Range, Length, OneOf, NoneOf, Equal, Regexp, URL, Email | regexp, email | All via `Annotated` constraints (`gt`, `lt`, `min_length`, `pattern`, ...) |
| Custom validators | `@validates`, `@validates_schema` | `mr.validate(fn)` | `@field_validator`, `@model_validator` |
| Before/after modes | — | — | Yes (`mode='before'`/`'after'`/`'wrap'`) |
| Strict mode | — | — | Yes (global or per-field) |
| Validate on assignment | — | — | Yes (`validate_assignment=True`) |
| Validate defaults | — | — | Yes (`validate_default=True`) |
| Fail fast (stop on first error) | — | — | Yes (`FailFast`) |

### Serialization & deserialization

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| Dump to dict | `schema.dump(obj)` | `mr.dump(obj)` | `adapter.dump_python(obj)` |
| Load from dict | `schema.load(data)` | `mr.load(Cls, data)` | `adapter.validate_python(data)` |
| Dump to JSON string | — | — | Yes (`dump_json()`) |
| Load from JSON string | — | — | Yes (`validate_json()`) |
| Load from string values | — | — | Yes (`validate_strings()`) |
| Many (batch) | `many=True` | `dump_many()` / `load_many()` | Yes (via `TypeAdapter(list[T])`) |
| Partial loading | Yes (`partial=True`) | — | — |
| Nested objects | Yes (`Nested()`) | Yes (auto) | Yes (auto) |

### Pre/post processing hooks

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| `pre_load` | Yes | Yes (`@mr.pre_load`) | Yes (`mode='before'`) |
| `post_load` | Yes | — | Yes (`model_post_init`) |
| `pre_dump` | Yes | — | — |
| `post_dump` | Yes | — | — |

### Field types

| Type | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| str, int, float, bool | Yes | Yes | Yes |
| Decimal | Yes | Yes | Yes |
| datetime, date, time | Yes | Yes | Yes |
| timedelta | Yes | — | Yes |
| UUID | Yes | Yes | Yes |
| Enum (str/int) | Yes | Yes | Yes |
| list, set, frozenset | Yes | Yes | Yes |
| dict | Yes | Yes | Yes |
| tuple (homogeneous) | Yes | Yes | Yes |
| tuple (heterogeneous) | Yes | Standard only | Yes |
| Union | — | Yes | Yes |
| Discriminated union | — | — | Yes |
| Literal | — | Yes | Yes |
| Optional | Yes | Yes | Yes |
| bytes | Yes | Yes | Yes |
| IP address / network | Yes | — | Yes |
| URL | Yes | — | Yes |
| Email (validated) | Yes | Yes (validator) | Yes (`EmailStr`) |
| FilePath / DirectoryPath | — | — | Yes |
| SecretStr / SecretBytes | — | — | Yes |
| Json (raw) | — | Yes (`JsonRawField`) | Yes (`Json`) |
| Base64 | — | — | Yes |
| PaymentCardNumber | — | — | Yes |

### Naming & aliasing

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| Per-field alias | Yes (`data_key`) | Yes (`mr.meta(name=...)`) | Yes (`Field(alias=...)`) |
| Separate validation/serialization alias | — | — | Yes |
| camelCase convention | Manual | Yes (`CAMEL_CASE`) | Yes (`alias_generator`) |
| UPPER_SNAKE_CASE | Manual | Yes (`UPPER_SNAKE_CASE`) | Yes (`alias_generator`) |
| CapitalCamelCase | Manual | Yes (`CAPITAL_CAMEL_CASE`) | Yes (`alias_generator`) |

### Ecosystem & integrations

| Feature | marshmallow | marshmallow-recipe | pydantic |
|---|:---:|:---:|:---:|
| JSON Schema generation | Via plugin | Yes (`mr.json_schema()`) | Yes (built-in) |
| OpenAPI support | Via apispec | — | Yes (built-in) |
| Settings management | — | — | Via pydantic-settings |
| `None` value handling | — | Yes (`NoneValueHandling`) | Yes (via serialization options) |
| Unknown fields handling | RAISE / EXCLUDE / INCLUDE | — | `'forbid'` / `'ignore'` / `'allow'` |

### Key takeaways

**Performance**
- **pydantic v2** is the fastest overall (9-38x over marshmallow), powered by its Rust core
- **marshmallow-recipe nuked** is a strong second (7-27x over marshmallow), powered by Rust via PyO3
- **marshmallow-recipe standard** (`mr.dump`/`mr.load`) is ~5-6x *slower* than raw marshmallow for dump, roughly equal for load
- The **nuked** backend of marshmallow-recipe is 21-56x faster than its standard backend
- Performance gaps **widen with deeper nesting** compared to flat models

**Installed size**
- **marshmallow** is the lightest at 0.4 MB — pure Python, zero compiled code
- **marshmallow-recipe** is 1.7 MB total (with marshmallow); its Rust binary is only 0.7 MB — 5.7x smaller than pydantic-core's
- **pydantic** is the heaviest at 8.1 MB (with pydantic-core) — nearly 5x larger than marshmallow-recipe, though the Rust core is what makes it the fastest

**Features**
- **pydantic** has the richest feature set: JSON Schema, OpenAPI, strict mode, discriminated unions, computed fields, generics, direct JSON string serialization, and the widest field type coverage
- **marshmallow** offers the most flexible hook system (pre/post load/dump), partial loading, and a mature plugin ecosystem (apispec, marshmallow-jsonschema)
- **marshmallow-recipe** is the most ergonomic for dataclass-heavy codebases: zero boilerplate schema definitions, built-in naming conventions (camelCase, UPPER_SNAKE), and JSON Schema generation — all while staying compatible with the marshmallow ecosystem

**When to use what**
- **pydantic** — best overall choice when performance, features, and JSON/OpenAPI integration matter most, and install size is not a concern
- **marshmallow-recipe (nuked)** — best for dataclass-centric projects that need fast serialization with a small footprint, especially when already using marshmallow
- **marshmallow** — best when you need maximum control over schema behavior, custom hooks, or have an existing marshmallow-based codebase

## Running

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install marshmallow marshmallow-recipe pydantic
python3 bench.py
```
