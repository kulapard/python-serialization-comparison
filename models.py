"""
Shared dataclass models — 10 levels of nesting, 10+ fields each.

Hierarchy:
  Organization                  # L1
  └── Department                # L2
      └── Team                  # L3
          └── Employee          # L4
              ├── Contract      # L5
              │   └── Terms     # L6
              │       └── Clause # L7
              └── Project       # L5
                  └── Task      # L6
                      └── SubTask # L7
                          └── Comment # L8
                              └── Reaction # L9
                                  └── Author # L10
"""

from __future__ import annotations

import dataclasses
import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional


# ── Enums ──

class OrgType(str, enum.Enum):
    CORP = "corp"
    STARTUP = "startup"
    NGO = "ngo"


class Status(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Role(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Currency(str, enum.Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


# ── L10: Author (10 fields) ──

@dataclasses.dataclass
class Author:
    id: str
    username: str
    display_name: str
    email: str
    verified: bool
    role: Role
    reputation: int
    joined_at: datetime
    bio: str
    avatar_url: Optional[str] = None


# ── L9: Reaction (10 fields) ──

@dataclasses.dataclass
class Reaction:
    id: str
    emoji: str
    label: str
    created_at: datetime
    author: Author
    count: int
    active: bool
    category: str
    weight: Decimal
    source: Optional[str] = None


# ── L8: Comment (11 fields) ──

@dataclasses.dataclass
class Comment:
    id: str
    text: str
    created_at: datetime
    updated_at: datetime
    edited: bool
    author_name: str
    likes: int
    language: str
    status: Status
    reactions: list[Reaction]
    parent_id: Optional[str] = None


# ── L7: SubTask (11 fields) ──

@dataclasses.dataclass
class SubTask:
    id: str
    title: str
    description: str
    done: bool
    priority: Priority
    estimated_hours: Decimal
    actual_hours: Decimal
    assignee: str
    created_at: date
    comment: Comment
    due_date: Optional[date] = None


# ── L7: Clause (10 fields) ──

@dataclasses.dataclass
class Clause:
    id: str
    title: str
    body: str
    section: str
    mandatory: bool
    version: int
    effective_date: date
    language: str
    category: str
    penalty_amount: Optional[Decimal] = None


# ── L6: Task (11 fields) ──

@dataclasses.dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: datetime
    due_date: date
    estimated_hours: Decimal
    assignee: str
    tags: list[str]
    subtasks: list[SubTask]


# ── L6: Terms (10 fields) ──

@dataclasses.dataclass
class Terms:
    id: str
    title: str
    effective_date: date
    expiry_date: date
    governing_law: str
    jurisdiction: str
    version: int
    auto_renew: bool
    notice_days: int
    clauses: list[Clause]


# ── L5: Project (11 fields) ──

@dataclasses.dataclass
class Project:
    id: str
    name: str
    code: str
    budget: Decimal
    spent: Decimal
    currency: Currency
    started_at: date
    status: Status
    owner: str
    tags: list[str]
    tasks: list[Task]


# ── L5: Contract (11 fields) ──

@dataclasses.dataclass
class Contract:
    id: str
    title: str
    contract_number: str
    signed_at: datetime
    value: Decimal
    currency: Currency
    status: Status
    counterparty: str
    renewable: bool
    terms: Terms
    notes: Optional[str] = None


# ── L4: Employee (12 fields) ──

@dataclasses.dataclass
class Employee:
    id: str
    name: str
    email: str
    phone: str
    hired_at: date
    salary: Decimal
    currency: Currency
    role: Role
    active: bool
    contract: Contract
    projects: list[Project]
    tags: list[str]
    note: Optional[str] = None


# ── L3: Team (10 fields) ──

@dataclasses.dataclass
class Team:
    id: str
    name: str
    code: str
    lead_name: str
    lead_email: str
    created_at: date
    status: Status
    room: str
    max_size: int
    members: list[Employee]


# ── L2: Department (10 fields) ──

@dataclasses.dataclass
class Department:
    id: str
    name: str
    code: str
    floor: int
    budget: Decimal
    head_name: str
    head_email: str
    status: Status
    created_at: date
    teams: list[Team]


# ── L1: Organization (11 fields) ──

@dataclasses.dataclass
class Organization:
    id: str
    name: str
    legal_name: str
    org_type: OrgType
    status: Status
    founded: date
    tax_id: str
    country: str
    employee_count: int
    annual_revenue: Decimal
    departments: list[Department]


# ── Factories ──

def make_author(i: int = 0) -> Author:
    return Author(
        id=str(uuid.UUID(int=i)),
        username=f"user_{i}",
        display_name=f"User {i}",
        email=f"user{i}@example.com",
        verified=i % 2 == 0,
        role=Role.EDITOR,
        reputation=i * 100 + 42,
        joined_at=datetime(2023, 3, 10, 8, 30, 0),
        bio=f"Author {i} is a seasoned contributor with many reviews.",
        avatar_url=f"https://cdn.example.com/avatars/{i}.png",
    )


def make_reaction(i: int = 0) -> Reaction:
    emojis = ["👍", "❤️", "🚀", "😄"]
    labels = ["thumbs_up", "heart", "rocket", "smile"]
    return Reaction(
        id=str(uuid.UUID(int=i + 1000)),
        emoji=emojis[i % len(emojis)],
        label=labels[i % len(labels)],
        created_at=datetime(2025, 6, 15, 12, i % 60, 0),
        author=make_author(i),
        count=i + 1,
        active=True,
        category="sentiment",
        weight=Decimal("1.50"),
        source="web",
    )


def make_comment(i: int = 0) -> Comment:
    return Comment(
        id=str(uuid.UUID(int=i + 2000)),
        text=f"This is comment #{i} with some details about progress.",
        created_at=datetime(2025, 6, 14, 10, 0, 0),
        updated_at=datetime(2025, 6, 14, 11, 30, 0),
        edited=i % 3 == 0,
        author_name=f"Commenter {i}",
        likes=i * 5,
        language="en",
        status=Status.ACTIVE,
        reactions=[make_reaction(j) for j in range(2)],
        parent_id=None,
    )


def make_subtask(i: int = 0) -> SubTask:
    return SubTask(
        id=str(uuid.UUID(int=i + 3000)),
        title=f"Subtask {i}: implementation detail",
        description=f"Detailed work item for subtask {i} covering edge cases.",
        done=i % 2 == 0,
        priority=Priority.MEDIUM,
        estimated_hours=Decimal("4.5"),
        actual_hours=Decimal("3.0"),
        assignee=f"dev{i}@example.com",
        created_at=date(2025, 5, 1),
        comment=make_comment(i),
        due_date=date(2025, 7, 15),
    )


def make_clause(i: int = 0) -> Clause:
    return Clause(
        id=str(uuid.UUID(int=i + 4000)),
        title=f"Clause {i}: Liability",
        body=f"The party shall be responsible for clause {i} obligations.",
        section=f"Section {i + 1}.A",
        mandatory=i % 2 == 0,
        version=1,
        effective_date=date(2025, 1, 1),
        language="en",
        category="liability",
        penalty_amount=Decimal("5000.00"),
    )


def make_task(i: int = 0) -> Task:
    return Task(
        id=str(uuid.UUID(int=i + 5000)),
        title=f"Task {i}: build feature",
        description=f"Detailed description for task {i}.",
        priority=Priority.HIGH,
        status=Status.ACTIVE,
        created_at=datetime(2025, 5, 1, 9, 0, 0),
        due_date=date(2025, 7, 1),
        estimated_hours=Decimal("40.0"),
        assignee=f"lead{i}@example.com",
        tags=["feature", "sprint-12", "backend"],
        subtasks=[make_subtask(j) for j in range(2)],
    )


def make_terms() -> Terms:
    return Terms(
        id=str(uuid.UUID(int=6000)),
        title="Standard Employment Terms v2",
        effective_date=date(2025, 1, 1),
        expiry_date=date(2026, 12, 31),
        governing_law="US-CA",
        jurisdiction="San Francisco, CA",
        version=2,
        auto_renew=True,
        notice_days=30,
        clauses=[make_clause(j) for j in range(2)],
    )


def make_project(i: int = 0) -> Project:
    return Project(
        id=str(uuid.UUID(int=i + 7000)),
        name=f"Project Alpha-{i}",
        code=f"PRJ-{i:04d}",
        budget=Decimal("150000.00"),
        spent=Decimal("42000.00"),
        currency=Currency.USD,
        started_at=date(2025, 3, 1),
        status=Status.ACTIVE,
        owner=f"pm{i}@example.com",
        tags=["q2", "core", "funded"],
        tasks=[make_task(j) for j in range(2)],
    )


def make_contract(i: int = 0) -> Contract:
    return Contract(
        id=str(uuid.UUID(int=i + 8000)),
        title=f"Employment Contract #{i}",
        contract_number=f"CTR-2024-{i:06d}",
        signed_at=datetime(2024, 12, 1, 9, 0, 0),
        value=Decimal("95000.00"),
        currency=Currency.USD,
        status=Status.ACTIVE,
        counterparty="Benchmark Corp",
        renewable=True,
        terms=make_terms(),
        notes=f"Standard contract for employee {i}",
    )


def make_employee(i: int = 0) -> Employee:
    return Employee(
        id=str(uuid.UUID(int=i + 9000)),
        name=f"Employee {i}",
        email=f"employee{i}@example.com",
        phone=f"+1-555-{i:04d}",
        hired_at=date(2024, 6, 15),
        salary=Decimal("95000.00"),
        currency=Currency.USD,
        role=Role.EDITOR,
        active=True,
        contract=make_contract(i),
        projects=[make_project(j) for j in range(2)],
        tags=["backend", "python", "senior"],
        note=f"Note about employee {i}",
    )


def make_team(i: int = 0) -> Team:
    return Team(
        id=str(uuid.UUID(int=i + 10000)),
        name=f"Team {i}",
        code=f"T-{i:03d}",
        lead_name=f"Lead {i}",
        lead_email=f"lead{i}@example.com",
        created_at=date(2023, 1, 15),
        status=Status.ACTIVE,
        room=f"Room {100 + i}",
        max_size=10,
        members=[make_employee(j) for j in range(2)],
    )


def make_department(i: int = 0) -> Department:
    return Department(
        id=str(uuid.UUID(int=i + 11000)),
        name=f"Engineering Dept {i}",
        code=f"ENG-{i:02d}",
        floor=i + 1,
        budget=Decimal("2000000.00"),
        head_name=f"Director {i}",
        head_email=f"director{i}@example.com",
        status=Status.ACTIVE,
        created_at=date(2020, 6, 1),
        teams=[make_team(j) for j in range(2)],
    )


def make_organization() -> Organization:
    return Organization(
        id="org-001",
        name="Benchmark Corp",
        legal_name="Benchmark Corporation Inc.",
        org_type=OrgType.CORP,
        status=Status.ACTIVE,
        founded=date(2020, 1, 1),
        tax_id="12-3456789",
        country="US",
        employee_count=500,
        annual_revenue=Decimal("50000000.00"),
        departments=[make_department(j) for j in range(2)],
    )


def make_organization_dict() -> dict:
    """Raw dict representation (as if received from an API)."""
    def _author(i):
        return {
            "id": str(uuid.UUID(int=i)),
            "username": f"user_{i}",
            "display_name": f"User {i}",
            "email": f"user{i}@example.com",
            "verified": i % 2 == 0,
            "role": "editor",
            "reputation": i * 100 + 42,
            "joined_at": "2023-03-10T08:30:00",
            "bio": f"Author {i} is a seasoned contributor with many reviews.",
            "avatar_url": f"https://cdn.example.com/avatars/{i}.png",
        }

    def _reaction(i):
        emojis = ["👍", "❤️", "🚀", "😄"]
        labels = ["thumbs_up", "heart", "rocket", "smile"]
        return {
            "id": str(uuid.UUID(int=i + 1000)),
            "emoji": emojis[i % len(emojis)],
            "label": labels[i % len(labels)],
            "created_at": "2025-06-15T12:00:00",
            "author": _author(i),
            "count": i + 1,
            "active": True,
            "category": "sentiment",
            "weight": "1.50",
            "source": "web",
        }

    def _comment(i):
        return {
            "id": str(uuid.UUID(int=i + 2000)),
            "text": f"This is comment #{i} with some details about progress.",
            "created_at": "2025-06-14T10:00:00",
            "updated_at": "2025-06-14T11:30:00",
            "edited": i % 3 == 0,
            "author_name": f"Commenter {i}",
            "likes": i * 5,
            "language": "en",
            "status": "active",
            "reactions": [_reaction(j) for j in range(2)],
            "parent_id": None,
        }

    def _subtask(i):
        return {
            "id": str(uuid.UUID(int=i + 3000)),
            "title": f"Subtask {i}: implementation detail",
            "description": f"Detailed work item for subtask {i} covering edge cases.",
            "done": i % 2 == 0,
            "priority": "medium",
            "estimated_hours": "4.5",
            "actual_hours": "3.0",
            "assignee": f"dev{i}@example.com",
            "created_at": "2025-05-01",
            "comment": _comment(i),
            "due_date": "2025-07-15",
        }

    def _clause(i):
        return {
            "id": str(uuid.UUID(int=i + 4000)),
            "title": f"Clause {i}: Liability",
            "body": f"The party shall be responsible for clause {i} obligations.",
            "section": f"Section {i + 1}.A",
            "mandatory": i % 2 == 0,
            "version": 1,
            "effective_date": "2025-01-01",
            "language": "en",
            "category": "liability",
            "penalty_amount": "5000.00",
        }

    def _task(i):
        return {
            "id": str(uuid.UUID(int=i + 5000)),
            "title": f"Task {i}: build feature",
            "description": f"Detailed description for task {i}.",
            "priority": "high",
            "status": "active",
            "created_at": "2025-05-01T09:00:00",
            "due_date": "2025-07-01",
            "estimated_hours": "40.0",
            "assignee": f"lead{i}@example.com",
            "tags": ["feature", "sprint-12", "backend"],
            "subtasks": [_subtask(j) for j in range(2)],
        }

    def _terms():
        return {
            "id": str(uuid.UUID(int=6000)),
            "title": "Standard Employment Terms v2",
            "effective_date": "2025-01-01",
            "expiry_date": "2026-12-31",
            "governing_law": "US-CA",
            "jurisdiction": "San Francisco, CA",
            "version": 2,
            "auto_renew": True,
            "notice_days": 30,
            "clauses": [_clause(j) for j in range(2)],
        }

    def _project(i):
        return {
            "id": str(uuid.UUID(int=i + 7000)),
            "name": f"Project Alpha-{i}",
            "code": f"PRJ-{i:04d}",
            "budget": "150000.00",
            "spent": "42000.00",
            "currency": "USD",
            "started_at": "2025-03-01",
            "status": "active",
            "owner": f"pm{i}@example.com",
            "tags": ["q2", "core", "funded"],
            "tasks": [_task(j) for j in range(2)],
        }

    def _contract(i):
        return {
            "id": str(uuid.UUID(int=i + 8000)),
            "title": f"Employment Contract #{i}",
            "contract_number": f"CTR-2024-{i:06d}",
            "signed_at": "2024-12-01T09:00:00",
            "value": "95000.00",
            "currency": "USD",
            "status": "active",
            "counterparty": "Benchmark Corp",
            "renewable": True,
            "terms": _terms(),
            "notes": f"Standard contract for employee {i}",
        }

    def _employee(i):
        return {
            "id": str(uuid.UUID(int=i + 9000)),
            "name": f"Employee {i}",
            "email": f"employee{i}@example.com",
            "phone": f"+1-555-{i:04d}",
            "hired_at": "2024-06-15",
            "salary": "95000.00",
            "currency": "USD",
            "role": "editor",
            "active": True,
            "contract": _contract(i),
            "projects": [_project(j) for j in range(2)],
            "tags": ["backend", "python", "senior"],
            "note": f"Note about employee {i}",
        }

    def _team(i):
        return {
            "id": str(uuid.UUID(int=i + 10000)),
            "name": f"Team {i}",
            "code": f"T-{i:03d}",
            "lead_name": f"Lead {i}",
            "lead_email": f"lead{i}@example.com",
            "created_at": "2023-01-15",
            "status": "active",
            "room": f"Room {100 + i}",
            "max_size": 10,
            "members": [_employee(j) for j in range(2)],
        }

    def _department(i):
        return {
            "id": str(uuid.UUID(int=i + 11000)),
            "name": f"Engineering Dept {i}",
            "code": f"ENG-{i:02d}",
            "floor": i + 1,
            "budget": "2000000.00",
            "head_name": f"Director {i}",
            "head_email": f"director{i}@example.com",
            "status": "active",
            "created_at": "2020-06-01",
            "teams": [_team(j) for j in range(2)],
        }

    return {
        "id": "org-001",
        "name": "Benchmark Corp",
        "legal_name": "Benchmark Corporation Inc.",
        "org_type": "corp",
        "status": "active",
        "founded": "2020-01-01",
        "tax_id": "12-3456789",
        "country": "US",
        "employee_count": 500,
        "annual_revenue": "50000000.00",
        "departments": [_department(j) for j in range(2)],
    }
