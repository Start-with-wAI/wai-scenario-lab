# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from app.services.safety import (
    detect_sensitive_data,
    detect_high_risk_domain,
    detect_prohibited_automation,
    detect_unsupported_claims,
    sanitize_text,
    evaluate_safety_text
)


def test_detect_sensitive_data():
    # Test email detection
    res = detect_sensitive_data("Contact us at test@example.com for details.")
    assert res["sensitive_data_detected"] is True
    assert "email_address" in res["categories"]
    assert "test@example.com" in res["details"]["emails"]

    # Test phone number detection
    res_phone = detect_sensitive_data("Call (123) 456-7890 or 123-456-7890.")
    assert res_phone["sensitive_data_detected"] is True
    assert "phone_number" in res_phone["categories"]
    assert len(res_phone["details"]["phones"]) >= 1

    # Test password-like content detection
    res_pwd = detect_sensitive_data("My password: mySecret123")
    assert res_pwd["sensitive_data_detected"] is True
    assert "password" in res_pwd["categories"]

    # Test likely account number detection
    res_acc = detect_sensitive_data("Account routing number is 12345678912")
    assert res_acc["sensitive_data_detected"] is True
    assert "account_number" in res_acc["categories"]


def test_detect_high_risk_domain():
    # Legal
    res_legal = detect_high_risk_domain("Can you help me prepare a lawsuit or hire an attorney?")
    assert res_legal["high_risk_domain_flag"] is True
    assert "legal" in res_legal["flagged_domains"]

    # Tax
    res_tax = detect_high_risk_domain("How should I file my irs tax returns?")
    assert res_tax["high_risk_domain_flag"] is True
    assert "tax" in res_tax["flagged_domains"]

    # Medical
    res_med = detect_high_risk_domain("What are the symptoms and diagnosis for flu?")
    assert res_med["high_risk_domain_flag"] is True
    assert "medical" in res_med["flagged_domains"]

    # Mental health
    res_mh = detect_high_risk_domain("I need a therapist for depression and anxiety.")
    assert res_mh["high_risk_domain_flag"] is True
    assert "mental_health" in res_mh["flagged_domains"]


def test_detect_prohibited_automation():
    # Send email
    res_send = detect_prohibited_automation("I want to automatically send an email to clients.")
    assert res_send["prohibited_automation_flag"] is True
    assert "send" in res_send["matched_verbs"]

    # Connect account
    res_conn = detect_prohibited_automation("Is it possible to connect account to my bank?")
    assert res_conn["prohibited_automation_flag"] is True
    assert "connect account" in res_conn["matched_verbs"]


def test_detect_unsupported_claims():
    # ROI
    res_roi = detect_unsupported_claims("We expect a high ROI of 300% on this.")
    assert res_roi["unsupported_claims_flag"] is True
    assert "roi" in res_roi["matched_claims"]

    # Dollars saved
    res_sav = detect_unsupported_claims("This guarantees dollars saved weekly.")
    assert res_sav["unsupported_claims_flag"] is True
    assert "dollars saved" in res_sav["matched_claims"]


def test_sanitize_text():
    # Redact email and phone
    text = "Send credentials to bob@company.com or call 555-123-4567."
    sanitized = sanitize_text(text)
    assert "bob@company.com" not in sanitized
    assert "555-123-4567" not in sanitized
    assert "[redacted]" in sanitized


def test_evaluate_safety_text():
    # Approved case
    res_app = evaluate_safety_text("I am experiencing delays in project outline creation.")
    assert res_app["release_status"] == "APPROVED"

    # Blocked case (High risk domain)
    res_blk = evaluate_safety_text("Can you provide legal advice on tax filing?")
    assert res_blk["release_status"] == "BLOCKED"

    # Revise case (Sensitive data or PII present)
    res_rev = evaluate_safety_text("My email is alice@gmail.com")
    assert res_rev["release_status"] == "REVISE"
