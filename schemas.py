"""
Hand-written marshmallow schemas for the Organization hierarchy.
"""

from __future__ import annotations

import marshmallow as ma
import marshmallow.fields as mf

from models import (
    Author,
    Clause,
    Comment,
    Contract,
    Currency,
    Department,
    Employee,
    Organization,
    OrgType,
    Priority,
    Project,
    Reaction,
    Role,
    Status,
    SubTask,
    Task,
    Team,
    Terms,
)


class MaAuthorSchema(ma.Schema):  # L10
    id = mf.String(required=True)
    username = mf.String(required=True)
    display_name = mf.String(required=True)
    email = mf.String(required=True)
    verified = mf.Boolean(required=True)
    role = mf.Enum(Role, by_value=True)
    reputation = mf.Integer(required=True)
    joined_at = mf.DateTime(required=True)
    bio = mf.String(required=True)
    avatar_url = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Author(**data)


class MaReactionSchema(ma.Schema):  # L9
    id = mf.String(required=True)
    emoji = mf.String(required=True)
    label = mf.String(required=True)
    created_at = mf.DateTime(required=True)
    author = mf.Nested(MaAuthorSchema, required=True)
    count = mf.Integer(required=True)
    active = mf.Boolean(required=True)
    category = mf.String(required=True)
    weight = mf.Decimal(required=True, as_string=True)
    source = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Reaction(**data)


class MaCommentSchema(ma.Schema):  # L8
    id = mf.String(required=True)
    text = mf.String(required=True)
    created_at = mf.DateTime(required=True)
    updated_at = mf.DateTime(required=True)
    edited = mf.Boolean(required=True)
    author_name = mf.String(required=True)
    likes = mf.Integer(required=True)
    language = mf.String(required=True)
    status = mf.Enum(Status, by_value=True)
    reactions = mf.List(mf.Nested(MaReactionSchema), required=True)
    parent_id = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Comment(**data)


class MaSubTaskSchema(ma.Schema):  # L7
    id = mf.String(required=True)
    title = mf.String(required=True)
    description = mf.String(required=True)
    done = mf.Boolean(required=True)
    priority = mf.Enum(Priority, by_value=True)
    estimated_hours = mf.Decimal(required=True, as_string=True)
    actual_hours = mf.Decimal(required=True, as_string=True)
    assignee = mf.String(required=True)
    created_at = mf.Date(required=True)
    comment = mf.Nested(MaCommentSchema, required=True)
    due_date = mf.Date(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return SubTask(**data)


class MaClauseSchema(ma.Schema):  # L7
    id = mf.String(required=True)
    title = mf.String(required=True)
    body = mf.String(required=True)
    section = mf.String(required=True)
    mandatory = mf.Boolean(required=True)
    version = mf.Integer(required=True)
    effective_date = mf.Date(required=True)
    language = mf.String(required=True)
    category = mf.String(required=True)
    penalty_amount = mf.Decimal(load_default=None, dump_default=None, as_string=True)

    @ma.post_load
    def make(self, data, **_):
        return Clause(**data)


class MaTaskSchema(ma.Schema):  # L6
    id = mf.String(required=True)
    title = mf.String(required=True)
    description = mf.String(required=True)
    priority = mf.Enum(Priority, by_value=True)
    status = mf.Enum(Status, by_value=True)
    created_at = mf.DateTime(required=True)
    due_date = mf.Date(required=True)
    estimated_hours = mf.Decimal(required=True, as_string=True)
    assignee = mf.String(required=True)
    tags = mf.List(mf.String(), required=True)
    subtasks = mf.List(mf.Nested(MaSubTaskSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Task(**data)


class MaTermsSchema(ma.Schema):  # L6
    id = mf.String(required=True)
    title = mf.String(required=True)
    effective_date = mf.Date(required=True)
    expiry_date = mf.Date(required=True)
    governing_law = mf.String(required=True)
    jurisdiction = mf.String(required=True)
    version = mf.Integer(required=True)
    auto_renew = mf.Boolean(required=True)
    notice_days = mf.Integer(required=True)
    clauses = mf.List(mf.Nested(MaClauseSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Terms(**data)


class MaProjectSchema(ma.Schema):  # L5
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    budget = mf.Decimal(required=True, as_string=True)
    spent = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    started_at = mf.Date(required=True)
    status = mf.Enum(Status, by_value=True)
    owner = mf.String(required=True)
    tags = mf.List(mf.String(), required=True)
    tasks = mf.List(mf.Nested(MaTaskSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Project(**data)


class MaContractSchema(ma.Schema):  # L5
    id = mf.String(required=True)
    title = mf.String(required=True)
    contract_number = mf.String(required=True)
    signed_at = mf.DateTime(required=True)
    value = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    status = mf.Enum(Status, by_value=True)
    counterparty = mf.String(required=True)
    renewable = mf.Boolean(required=True)
    terms = mf.Nested(MaTermsSchema, required=True)
    notes = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Contract(**data)


class MaEmployeeSchema(ma.Schema):  # L4
    id = mf.String(required=True)
    name = mf.String(required=True)
    email = mf.String(required=True)
    phone = mf.String(required=True)
    hired_at = mf.Date(required=True)
    salary = mf.Decimal(required=True, as_string=True)
    currency = mf.Enum(Currency, by_value=True)
    role = mf.Enum(Role, by_value=True)
    active = mf.Boolean(required=True)
    contract = mf.Nested(MaContractSchema, required=True)
    projects = mf.List(mf.Nested(MaProjectSchema), required=True)
    tags = mf.List(mf.String(), required=True)
    note = mf.String(load_default=None, dump_default=None)

    @ma.post_load
    def make(self, data, **_):
        return Employee(**data)


class MaTeamSchema(ma.Schema):  # L3
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    lead_name = mf.String(required=True)
    lead_email = mf.String(required=True)
    created_at = mf.Date(required=True)
    status = mf.Enum(Status, by_value=True)
    room = mf.String(required=True)
    max_size = mf.Integer(required=True)
    members = mf.List(mf.Nested(MaEmployeeSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Team(**data)


class MaDepartmentSchema(ma.Schema):  # L2
    id = mf.String(required=True)
    name = mf.String(required=True)
    code = mf.String(required=True)
    floor = mf.Integer(required=True)
    budget = mf.Decimal(required=True, as_string=True)
    head_name = mf.String(required=True)
    head_email = mf.String(required=True)
    status = mf.Enum(Status, by_value=True)
    created_at = mf.Date(required=True)
    teams = mf.List(mf.Nested(MaTeamSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Department(**data)


class MaOrganizationSchema(ma.Schema):  # L1
    id = mf.String(required=True)
    name = mf.String(required=True)
    legal_name = mf.String(required=True)
    org_type = mf.Enum(OrgType, by_value=True)
    status = mf.Enum(Status, by_value=True)
    founded = mf.Date(required=True)
    tax_id = mf.String(required=True)
    country = mf.String(required=True)
    employee_count = mf.Integer(required=True)
    annual_revenue = mf.Decimal(required=True, as_string=True)
    departments = mf.List(mf.Nested(MaDepartmentSchema), required=True)

    @ma.post_load
    def make(self, data, **_):
        return Organization(**data)
