import pytest
from kubernetes import client


@pytest.fixture
def sa_name():
    return "my-name"


@pytest.fixture
def namespace():
    return "my-ns"


@pytest.fixture
def rolebindings(sa_name, namespace) -> dict:
    roles = ["reader", "writer"]
    items = []
    for r in roles:
        items.append(
            client.V1RoleBinding(
                metadata=client.V1ObjectMeta(name=r, namespace=namespace),
                subjects=[
                    client.V1Subject(
                        kind="ServiceAccount",
                        name=sa_name,
                        api_group="rbac.authorization.k8s.io",
                    )
                ],
                role_ref=client.V1RoleRef(
                    kind="Role", name=r, api_group="rbac.authorization.k8s.io"
                ),
            )
        )
    return {"items": client.V1RoleBindingList(items=items), "roles": roles}


@pytest.fixture
def clusterrolebindings(sa_name, namespace) -> dict:
    roles = ["updater"]
    items = []
    for r in roles:
        items.append(
            client.V1ClusterRoleBinding(
                metadata=client.V1ObjectMeta(name=r, namespace=namespace),
                subjects=[
                    client.V1Subject(
                        kind="ServiceAccount",
                        name=sa_name,
                        namespace=namespace,
                        api_group="rbac.authorization.k8s.io",
                    )
                ],
                role_ref=client.V1RoleRef(
                    kind="Role", name=r, api_group="rbac.authorization.k8s.io"
                ),
            )
        )
    return {"items": client.V1RoleBindingList(items=items), "roles": roles}
