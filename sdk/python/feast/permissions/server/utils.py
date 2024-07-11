"""
A module with utility functions to support the authorization management in Feast servers.
"""

import enum
import logging

import feast
from feast.permissions.auth.auth_manager import (
    AllowAll,
    AuthManager,
    set_auth_manager,
)
from feast.permissions.auth.auth_type import AuthType
from feast.permissions.auth.kubernetes_token_parser import KubernetesTokenParser
from feast.permissions.auth.oidc_token_parser import OidcTokenParser
from feast.permissions.auth.token_extractor import TokenExtractor
from feast.permissions.auth.token_parser import TokenParser
from feast.permissions.security_manager import (
    SecurityManager,
    no_security_manager,
    set_security_manager,
)
from feast.permissions.server.arrow_flight_token_extractor import (
    ArrowFlightTokenExtractor,
)
from feast.permissions.server.grpc_token_extractor import GrpcTokenExtractor
from feast.permissions.server.rest_token_extractor import RestTokenExtractor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ServerType(enum.Enum):
    """
    Identify the server type.
    """

    REST = "rest"
    ARROW = "arrow"
    GRPC = "grpc"  # TODO RBAC: to be completed


def str_to_auth_type(value: str) -> AuthType:
    for t in AuthType.__members__.values():
        if t.value.lower() == value.lower():
            return t

    logger.warning(
        f"Requested unmanaged AuthManagerType of value {value}. Using NONE instead."
    )
    return AuthType.NONE


def init_security_manager(auth_type: AuthType, fs: "feast.FeatureStore"):
    """
    Initialize the global security manager.
    Must be invoked at Feast server initialization time to create the `SecurityManager` instance.

    Args:
        auth_type: The authorization manager type.
        registry: The feature store registry.
    """
    if auth_type == AuthType.NONE:
        no_security_manager()
    else:
        # TODO permissions from registry
        set_security_manager(
            SecurityManager(
                project=fs.project,
                registry=fs.registry,
            )
        )


def init_auth_manager(server_type: ServerType, auth_type: AuthType):
    """
    Initialize the global authorization manager.
    Must be invoked at Feast server initialization time to create the `AuthManager` instance.

    Args:
        server_type: The server type.
        auth_type: The authorization manager type.

    Raises:
        ValueError: If any input argument has an unmanaged value.
    """
    if auth_type == AuthType.NONE:
        set_auth_manager(AllowAll())
    else:
        token_extractor: TokenExtractor
        token_parser: TokenParser

        if server_type == ServerType.REST:
            token_extractor = RestTokenExtractor()
        elif server_type == ServerType.ARROW:
            token_extractor = ArrowFlightTokenExtractor()
        elif server_type == ServerType.GRPC:
            token_extractor = GrpcTokenExtractor()
        else:
            raise ValueError(f"Unmanaged server type {server_type}")

        if auth_type == AuthType.KUBERNETES:
            token_parser = KubernetesTokenParser()
        elif auth_type == AuthType.OIDC:
            token_parser = OidcTokenParser()
        else:
            raise ValueError(f"Unmanaged authorization manager type {auth_type}")

        auth_manager = AuthManager(
            token_extractor=token_extractor, token_parser=token_parser
        )
        set_auth_manager(auth_manager)
