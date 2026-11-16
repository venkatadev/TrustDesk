"""Shared test setup."""

import pytest

from trustdesk.knowledge.store import get_policy_store, set_policy_store
from trustdesk.llm.drafting import get_drafter, set_drafter


@pytest.fixture(autouse=True)
def _restore_global_choices():
    """A test may choose its own policy store or drafter; never let that leak into the next test."""
    store, drafter = get_policy_store(), get_drafter()
    yield
    set_policy_store(store)
    set_drafter(drafter)
