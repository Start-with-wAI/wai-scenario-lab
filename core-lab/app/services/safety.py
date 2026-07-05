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

"""Deterministic safety and compliance validation utilities.

These deterministic checks are designed to support and preprocess inputs
for Agent 4 (Safety & Quality Review) rather than replace human judgment.
"""

import re

# Regex patterns for sensitive data detection
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
PASSWORD_REGEX = re.compile(r"\b(password|passcode|pwd|secret)\b\s*[:=]\s*\S+", re.IGNORECASE)
ACCOUNT_REGEX = re.compile(r"\b(account|routing|ssn|iban|checking|savings)\b[\s\w:=]{0,15}?\b\d{8,17}\b", re.IGNORECASE)

# Keywords for high risk domains
HIGH_RISK_KEYWORDS = {
    "legal": ["legal", "lawyer", "attorney", "court", "lawsuit", "sue", "litigation"],
    "medical": ["medical", "doctor", "physician", "patient", "treatment", "disease", "diagnosis", "symptom", "medicine"],
    "mental_health": ["mental health", "therapy", "therapist", "depression", "anxiety", "counseling", "psychiatrist"],
    "tax": ["tax", "taxes", "irs", "revenue", "filing", "audit"],
    "employment": ["employment", "employer", "employee", "hiring", "firing", "labor law", "union"],
    "lending": ["lending", "loan", "mortgage", "credit", "borrow", "lender"],
    "housing": ["housing", "rent", "tenant", "landlord", "lease", "eviction"],
    "insurance": ["insurance", "claim", "policy", "premium", "coverage"],
    "regulatory_compliance": ["regulatory", "compliance", "audit", "osha", "sec", "epa", "regulation"]
}

# Verbs for prohibited automation requests
PROHIBITED_VERBS = [
    "send",
    "publish",
    "purchase",
    "cancel",
    "connect account",
    "upload file",
    "make decision",
    "approve",
    "submit"
]

# Keywords for unsupported benefit claims
UNSUPPORTED_CLAIMS_KEYWORDS = [
    "roi",
    "dollars saved",
    "guaranteed savings",
    "annual value",
    "five-year value",
    "productivity guarantee",
    "opportunity cost",
    "marketing equity"
]


def detect_sensitive_data(text: str) -> dict:
    """Detects email addresses, phone numbers, password-like patterns, and likely account numbers."""
    emails = EMAIL_REGEX.findall(text)
    phones = PHONE_REGEX.findall(text)
    passwords = PASSWORD_REGEX.findall(text)
    accounts = ACCOUNT_REGEX.findall(text)

    detected = bool(emails or phones or passwords or accounts)
    categories = []
    if emails:
        categories.append("email_address")
    if phones:
        categories.append("phone_number")
    if passwords:
        categories.append("password")
    if accounts:
        categories.append("account_number")

    return {
        "sensitive_data_detected": detected,
        "categories": categories,
        "details": {
            "emails": emails,
            "phones": phones,
            "has_passwords": bool(passwords),
            "has_accounts": bool(accounts),
        }
    }


def detect_high_risk_domain(text: str) -> dict:
    """Detects legal, medical, tax, and other high-risk domain queries."""
    normalized = text.lower()
    flagged_domains = []
    matched_keywords = []

    for domain, keywords in HIGH_RISK_KEYWORDS.items():
        matches = []
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, normalized):
                matches.append(kw)
        if matches:
            flagged_domains.append(domain)
            matched_keywords.extend(matches)

    return {
        "high_risk_domain_flag": bool(flagged_domains),
        "flagged_domains": flagged_domains,
        "matched_keywords": list(set(matched_keywords))
    }


def detect_prohibited_automation(text: str) -> dict:
    """Detects requests for direct actions, automation, or third-party submissions."""
    normalized = text.lower()
    matched_verbs = [verb for verb in PROHIBITED_VERBS if verb in normalized]

    return {
        "prohibited_automation_flag": bool(matched_verbs),
        "matched_verbs": matched_verbs
    }


def detect_unsupported_claims(text: str) -> dict:
    """Detects claims about ROI, dollar savings, or other unsupported financial benefits."""
    normalized = text.lower()
    matched_claims = [claim for claim in UNSUPPORTED_CLAIMS_KEYWORDS if claim in normalized]

    return {
        "unsupported_claims_flag": bool(matched_claims),
        "matched_claims": matched_claims
    }


def sanitize_text(text: str) -> str:
    """Redacts email addresses, phone numbers, and potential account/password info.

    Replaces sensitive information with '[redacted]' to prevent repeating in output.
    """
    sanitized = EMAIL_REGEX.sub("[redacted]", text)
    sanitized = PHONE_REGEX.sub("[redacted]", sanitized)
    
    # We redact specific matched patterns rather than simple sub to keep formatting clean
    def redact_passwords(match):
        prefix = match.group(1)
        return f"{prefix}: [redacted]"
    sanitized = PASSWORD_REGEX.sub(redact_passwords, sanitized)

    def redact_accounts(match):
        prefix = match.group(1)
        return f"{prefix}: [redacted]"
    sanitized = ACCOUNT_REGEX.sub(redact_accounts, sanitized)

    return sanitized


def evaluate_safety_text(text: str) -> dict:
    """Runs all deterministic safety evaluations on the input text.

    Returns:
        A evaluation dict containing flags, categories, and recommended release status.
    """
    sensitive_res = detect_sensitive_data(text)
    risk_res = detect_high_risk_domain(text)
    automation_res = detect_prohibited_automation(text)
    claims_res = detect_unsupported_claims(text)

    # Detect absolute certainty words
    normalized = text.strip().casefold()
    prohibited_words = {"definitely", "always", "guaranteed", "proven"}
    words = set(re.findall(r"\b\w+\b", normalized))
    has_absolute_words = bool(prohibited_words & words)
    
    prohibited_openings = ("the real reason", "we determined", "you definitely", "this proves", "the cause is")
    has_prohibited_opening = any(normalized.startswith(opening) for opening in prohibited_openings)

    # Determine recommended release status
    # BLOCKED: if high risk domain or prohibited automation is found.
    # REVISE: if sensitive data, unsupported claims, or absolute certainty words are found.
    # APPROVED: if no issues are detected.
    if risk_res["high_risk_domain_flag"] or automation_res["prohibited_automation_flag"]:
        release_status = "BLOCKED"
    elif sensitive_res["sensitive_data_detected"] or claims_res["unsupported_claims_flag"] or has_absolute_words or has_prohibited_opening:
        release_status = "REVISE"
    else:
        release_status = "APPROVED"

    return {
        "sensitive_data_detected": sensitive_res["sensitive_data_detected"],
        "redaction_categories": sensitive_res["categories"],
        "high_risk_domain_flag": risk_res["high_risk_domain_flag"],
        "flagged_domains": risk_res["flagged_domains"],
        "prohibited_automation_flag": automation_res["prohibited_automation_flag"],
        "unsupported_claims": claims_res["unsupported_claims_flag"],
        "has_absolute_words": has_absolute_words or has_prohibited_opening,
        "release_status": release_status
    }
