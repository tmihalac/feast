import assertpy
import pytest

from feast.permissions.action import AuthzedAction
from feast.permissions.decision import DecisionStrategy
from feast.permissions.permission import Permission
from feast.permissions.security_manager import assert_permissions, permitted_resources


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    Permission.set_global_decision_strategy(DecisionStrategy.UNANIMOUS)


@pytest.mark.parametrize(
    "user, requested_actions, allowed, allowed_single",
    [
        (None, [], False, [False, False]),
        ("r", [AuthzedAction.READ], False, [True, False]),
        ("r", [AuthzedAction.WRITE], False, [False, False]),
        ("w", [AuthzedAction.READ], False, [False, False]),
        ("w", [AuthzedAction.WRITE], False, [True, False]),
        ("rw", [AuthzedAction.READ], False, [True, False]),
        ("rw", [AuthzedAction.WRITE], False, [True, False]),
        ("rw", [AuthzedAction.READ, AuthzedAction.WRITE], False, [True, False]),
        ("admin", [AuthzedAction.READ, AuthzedAction.WRITE], True, [True, True]),
        ("admin", [AuthzedAction.QUERY, AuthzedAction.WRITE], True, [True, True]),
    ],
)
def test_access_SecuredFeatureView(
    security_manager, feature_views, user, requested_actions, allowed, allowed_single
):
    sm = security_manager
    resources = feature_views

    sm.set_current_user(user)
    result = permitted_resources(resources=resources, actions=requested_actions)
    if allowed:
        assertpy.assert_that(result).is_equal_to(resources)
    else:
        filtered = [r for i, r in enumerate(resources) if allowed_single[i]]
        assertpy.assert_that(result).is_equal_to(filtered)

    for i, r in enumerate(resources):
        if allowed_single[i]:
            result = assert_permissions(resource=r, actions=requested_actions)
            assertpy.assert_that(result).is_equal_to(r)
        else:
            with pytest.raises(PermissionError):
                assert_permissions(resource=r, actions=requested_actions)