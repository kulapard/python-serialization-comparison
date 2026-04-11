"""
Shared dataclass models — 10 levels of nesting.

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


# ── L10: Author ──

@dataclasses.dataclass
class Author:
    id: str
    username: str
    display_name: str
    verified: bool


# ── L9: Reaction ──

@dataclasses.dataclass
class Reaction:
    id: str
    emoji: str
    created_at: datetime
    author: Author


# ── L8: Comment ──

@dataclasses.dataclass
class Comment:
    id: str
    text: str
    created_at: datetime
    edited: bool
    reactions: list[Reaction]


# ── L7: SubTask ──

@dataclasses.dataclass
class SubTask:
    id: str
    title: str
    done: bool
    priority: Priority
    comment: Comment


# ── L7: Clause ──

@dataclasses.dataclass
class Clause:
    id: str
    title: str
    body: str
    mandatory: bool


# ── L6: Task ──

@dataclasses.dataclass
class Task:
    id: str
    title: str
    description: str
    priority: Priority
    due_date: date
    subtasks: list[SubTask]


# ── L6: Terms ──

@dataclasses.dataclass
class Terms:
    id: str
    effective_date: date
    governing_law: str
    clauses: list[Clause]


# ── L5: Project ──

@dataclasses.dataclass
class Project:
    id: str
    name: str
    budget: Decimal
    started_at: date
    tasks: list[Task]


# ── L5: Contract ──

@dataclasses.dataclass
class Contract:
    id: str
    title: str
    signed_at: datetime
    value: Decimal
    terms: Terms


# ── L4: Employee ──

@dataclasses.dataclass
class Employee:
    id: str
    name: str
    email: str
    hired_at: date
    salary: Decimal
    contract: Contract
    projects: list[Project]
    tags: list[str]
    note: Optional[str] = None


# ── L3: Team ──

@dataclasses.dataclass
class Team:
    id: str
    name: str
    lead_name: str
    members: list[Employee]


# ── L2: Department ──

@dataclasses.dataclass
class Department:
    id: str
    name: str
    floor: int
    teams: list[Team]


# ── L1: Organization (root) ──

@dataclasses.dataclass
class Organization:
    id: str
    name: str
    org_type: OrgType
    founded: date
    departments: list[Department]


# ── Factories ──

def make_author(i: int = 0) -> Author:
    return Author(
        id=str(uuid.UUID(int=i)),
        username=f"user_{i}",
        display_name=f"User {i}",
        verified=i % 2 == 0,
    )


def make_reaction(i: int = 0) -> Reaction:
    emojis = ["👍", "❤️", "🚀", "😄"]
    return Reaction(
        id=str(uuid.UUID(int=i + 1000)),
        emoji=emojis[i % len(emojis)],
        created_at=datetime(2025, 6, 15, 12, i % 60, 0),
        author=make_author(i),
    )


def make_comment(i: int = 0) -> Comment:
    return Comment(
        id=str(uuid.UUID(int=i + 2000)),
        text=f"This is comment #{i} with some details about progress.",
        created_at=datetime(2025, 6, 14, 10, 0, 0),
        edited=i % 3 == 0,
        reactions=[make_reaction(j) for j in range(2)],
    )


def make_subtask(i: int = 0) -> SubTask:
    return SubTask(
        id=str(uuid.UUID(int=i + 3000)),
        title=f"Subtask {i}: implementation detail",
        done=i % 2 == 0,
        priority=Priority.MEDIUM,
        comment=make_comment(i),
    )


def make_clause(i: int = 0) -> Clause:
    return Clause(
        id=str(uuid.UUID(int=i + 4000)),
        title=f"Clause {i}: Liability",
        body=f"The party shall be responsible for clause {i} obligations.",
        mandatory=i % 2 == 0,
    )


def make_task(i: int = 0) -> Task:
    return Task(
        id=str(uuid.UUID(int=i + 5000)),
        title=f"Task {i}: build feature",
        description=f"Detailed description for task {i}.",
        priority=Priority.HIGH,
        due_date=date(2025, 7, 1),
        subtasks=[make_subtask(j) for j in range(2)],
    )


def make_terms() -> Terms:
    return Terms(
        id=str(uuid.UUID(int=6000)),
        effective_date=date(2025, 1, 1),
        governing_law="US-CA",
        clauses=[make_clause(j) for j in range(2)],
    )


def make_project(i: int = 0) -> Project:
    return Project(
        id=str(uuid.UUID(int=i + 7000)),
        name=f"Project Alpha-{i}",
        budget=Decimal("150000.00"),
        started_at=date(2025, 3, 1),
        tasks=[make_task(j) for j in range(2)],
    )


def make_contract(i: int = 0) -> Contract:
    return Contract(
        id=str(uuid.UUID(int=i + 8000)),
        title=f"Employment Contract #{i}",
        signed_at=datetime(2024, 12, 1, 9, 0, 0),
        value=Decimal("95000.00"),
        terms=make_terms(),
    )


def make_employee(i: int = 0) -> Employee:
    return Employee(
        id=str(uuid.UUID(int=i + 9000)),
        name=f"Employee {i}",
        email=f"employee{i}@example.com",
        hired_at=date(2024, 6, 15),
        salary=Decimal("95000.00"),
        contract=make_contract(i),
        projects=[make_project(j) for j in range(2)],
        tags=["backend", "python", "senior"],
        note=f"Note about employee {i}",
    )


def make_team(i: int = 0) -> Team:
    return Team(
        id=str(uuid.UUID(int=i + 10000)),
        name=f"Team {i}",
        lead_name=f"Lead {i}",
        members=[make_employee(j) for j in range(2)],
    )


def make_department(i: int = 0) -> Department:
    return Department(
        id=str(uuid.UUID(int=i + 11000)),
        name=f"Engineering Dept {i}",
        floor=i + 1,
        teams=[make_team(j) for j in range(2)],
    )


def make_organization() -> Organization:
    return Organization(
        id="org-001",
        name="Benchmark Corp",
        org_type=OrgType.CORP,
        founded=date(2020, 1, 1),
        departments=[make_department(j) for j in range(2)],
    )


def make_organization_dict() -> dict:
    """Raw dict representation (as if received from an API)."""
    def _author(i):
        return {
            "id": str(uuid.UUID(int=i)),
            "username": f"user_{i}",
            "display_name": f"User {i}",
            "verified": i % 2 == 0,
        }

    def _reaction(i):
        emojis = ["👍", "❤️", "🚀", "😄"]
        return {
            "id": str(uuid.UUID(int=i + 1000)),
            "emoji": emojis[i % len(emojis)],
            "created_at": "2025-06-15T12:00:00",
            "author": _author(i),
        }

    def _comment(i):
        return {
            "id": str(uuid.UUID(int=i + 2000)),
            "text": f"This is comment #{i} with some details about progress.",
            "created_at": "2025-06-14T10:00:00",
            "edited": i % 3 == 0,
            "reactions": [_reaction(j) for j in range(2)],
        }

    def _subtask(i):
        return {
            "id": str(uuid.UUID(int=i + 3000)),
            "title": f"Subtask {i}: implementation detail",
            "done": i % 2 == 0,
            "priority": "medium",
            "comment": _comment(i),
        }

    def _clause(i):
        return {
            "id": str(uuid.UUID(int=i + 4000)),
            "title": f"Clause {i}: Liability",
            "body": f"The party shall be responsible for clause {i} obligations.",
            "mandatory": i % 2 == 0,
        }

    def _task(i):
        return {
            "id": str(uuid.UUID(int=i + 5000)),
            "title": f"Task {i}: build feature",
            "description": f"Detailed description for task {i}.",
            "priority": "high",
            "due_date": "2025-07-01",
            "subtasks": [_subtask(j) for j in range(2)],
        }

    def _terms():
        return {
            "id": str(uuid.UUID(int=6000)),
            "effective_date": "2025-01-01",
            "governing_law": "US-CA",
            "clauses": [_clause(j) for j in range(2)],
        }

    def _project(i):
        return {
            "id": str(uuid.UUID(int=i + 7000)),
            "name": f"Project Alpha-{i}",
            "budget": "150000.00",
            "started_at": "2025-03-01",
            "tasks": [_task(j) for j in range(2)],
        }

    def _contract(i):
        return {
            "id": str(uuid.UUID(int=i + 8000)),
            "title": f"Employment Contract #{i}",
            "signed_at": "2024-12-01T09:00:00",
            "value": "95000.00",
            "terms": _terms(),
        }

    def _employee(i):
        return {
            "id": str(uuid.UUID(int=i + 9000)),
            "name": f"Employee {i}",
            "email": f"employee{i}@example.com",
            "hired_at": "2024-06-15",
            "salary": "95000.00",
            "contract": _contract(i),
            "projects": [_project(j) for j in range(2)],
            "tags": ["backend", "python", "senior"],
            "note": f"Note about employee {i}",
        }

    def _team(i):
        return {
            "id": str(uuid.UUID(int=i + 10000)),
            "name": f"Team {i}",
            "lead_name": f"Lead {i}",
            "members": [_employee(j) for j in range(2)],
        }

    def _department(i):
        return {
            "id": str(uuid.UUID(int=i + 11000)),
            "name": f"Engineering Dept {i}",
            "floor": i + 1,
            "teams": [_team(j) for j in range(2)],
        }

    return {
        "id": "org-001",
        "name": "Benchmark Corp",
        "org_type": "corp",
        "founded": "2020-01-01",
        "departments": [_department(j) for j in range(2)],
    }
