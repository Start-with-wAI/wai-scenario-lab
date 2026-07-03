Feature: Scenario Lab Analysis and ROI Calculation

  @id_cool_down_tax_01
  Scenario: The Cool Down Tax scenario triggers APPROVED state with strong evidence
    Given the user selects the "cool_down_tax" scenario
    And the user provides the following answers:
      | interaction_type | client complaint |
      | frequency        | weekly           |
      | minutes_lost     | 30               |
      | work_disrupted   | client follow-up |
    And the user's hourly rate is 50.0
    When the analysis pipeline runs the deterministic calculations
    Then the annual hours lost must be calculated as 26.0
    And the 1-year opportunity cost must be calculated as 1300.0
    And the release status must be "APPROVED"
    And the output brief must include the human-review reminder

  @id_brain_fog_01
  Scenario: Brain Fog scenario triggers APPROVED_WITH_LIMITATION state on partial evidence
    Given the user selects the "brain_fog" scenario
    And the user provides the following answers:
      | ideas_captured_weekly        | 5    |
      | ideas_lost_weekly            | 10   |
      | minutes_lost_reconstructing | 15   |
    And the user skips the clarification question
    When the analysis pipeline runs the deterministic calculations
    Then the capture yield must be calculated as 33.33 percent
    And the annual reconstruction hours wasted must be calculated as 130.0
    And the release status must be "APPROVED_WITH_LIMITATION"
    And the output brief must include the approved-with-limitation caution banner

  @id_blank_page_01
  Scenario: The Blank Page scenario triggers APPROVED state after PII redaction
    Given the user selects the "blank_page" scenario
    And the user provides answers containing PII:
      | content_type     | proposal template |
      | source_material  | email thread with John Doe from Acme Corp |
      | minutes_to_start | 60                |
      | starting_difficulty | organizing_ideas |
    When the analysis pipeline executes safety filters and calculations
    Then the customer details and PII must be redacted locally
    And the weekly marketing equity for "Proposal Templates" must be calculated as 300.0
    And the release status must be "APPROVED"
    And the output brief must mark the redaction applied flag as true
