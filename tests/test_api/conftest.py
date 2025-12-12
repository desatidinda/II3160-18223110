import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.manajemen_parkir.api.dependencies import (
    get_auth_service,
    get_user_repository,
    get_slot_repository,
    get_sesi_repository,
    get_slot_service,
)
from src.manajemen_parkir.application.services import AuthService
from src.manajemen_parkir.application.slot_service import SlotParkirService


@pytest.fixture(scope="session")
def setup_api_dependencies(shared_auth_repo, shared_user_repo, shared_slot_repo, shared_sesi_repo):
    """Set up API dependencies for test"""
    auth_service = AuthService(shared_auth_repo, shared_user_repo)
    slot_service = SlotParkirService(shared_slot_repo)
    
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    app.dependency_overrides[get_user_repository] = lambda: shared_user_repo
    app.dependency_overrides[get_slot_repository] = lambda: shared_slot_repo
    app.dependency_overrides[get_sesi_repository] = lambda: shared_sesi_repo
    app.dependency_overrides[get_slot_service] = lambda: slot_service
    
    yield
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def api_client(setup_api_dependencies):
    return TestClient(app)
