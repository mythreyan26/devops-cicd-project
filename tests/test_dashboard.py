"""Automated tests for the DevOps web dashboard interface."""


def test_dashboard_route_success(client):
    """Verify that GET /dashboard renders 200 OK with HTML and essential UI components."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "text/html" in response.content_type

    html = response.get_data(as_text=True)
    assert "DevOps Service Dashboard" in html
    assert 'id="themeToggleBtn"' in html
    assert 'id="refreshHealthBtn"' in html
    assert 'id="calcForm"' in html
    assert 'id="responseCodeBox"' in html
    assert "https://github.com/mythreyan26/devops-cicd-project" in html
    assert "https://hub.docker.com/repository/docker/mythreyan26/devops-cicd-service/tags" in html


def test_root_route_serves_dashboard(client):
    """Verify that GET / serves the web dashboard cleanly."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.content_type

    html = response.get_data(as_text=True)
    assert "DevOps Service Dashboard" in html
