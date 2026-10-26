from app import app


def test_issue_report_uses_email_draft_without_server_submission():
    response = app.test_client().get("/pages/issue-report")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "bunnycontact.me@gmail.com" in html
    assert "Open Gmail draft" in html
    assert "https://mail.google.com/mail/?view=cm&fs=1" in html
    assert "not submitted automatically" in html
