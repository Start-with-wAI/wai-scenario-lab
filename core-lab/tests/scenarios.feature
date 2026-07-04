Feature: wAI Scenario Lab MVP Scenario Briefs

  The public capstone MVP helps a micro business owner examine one fictional
  workflow-friction scenario and receive one grounded interpretation, one
  practical next action, one observation measurement, and a human-review
  reminder.

  The Scenario Lab must not calculate ROI, opportunity cost, dollar savings,
  annual value, marketing equity, productivity guarantees, or other financial
  valuation outputs.

  @id_cool_down_tax_01
  Scenario: The Cool Down Tax scenario returns one observation measure without ROI
    Given the user selects the "cool_down_tax" scenario
    And the user provides the following answers:
      | interaction_type | vendor delay with little notice  |
      | frequency        | weekly                           |
      | minutes_lost     | 45                               |
      | work_disrupted   | project follow-up and scheduling |
    When the Scenario Lab pipeline assembles the Scenario Brief
    Then the release status must be "APPROVED"
    And the output brief must include the measurement "Recovery time per incident"
    And the measurement unit must be "minutes"
    And the baseline display must include "45 minutes"
    And the output brief must include exactly one next action
    And the output brief must include the human-review reminder
    And the output brief must include the responsible-use limitation
    And the output brief must not include ROI, opportunity cost, dollar savings, annual value, marketing equity, or productivity guarantees

  @id_brain_fog_01
  Scenario: Brain Fog scenario returns a capture observation measure with limitations when evidence is incomplete
    Given the user selects the "brain_fog" scenario
    And the user provides the following answers:
      | idea_context           | while driving between appointments  |
      | current_capture_method | memory and occasional notes app     |
      | ideas_lost_weekly      | 3                                   |
      | capture_constraint     | opening the app takes too many steps |
    And the user skips the clarification question
    When the Scenario Lab pipeline assembles the Scenario Brief
    Then the release status must be "APPROVED_WITH_LIMITATION"
    And the output brief must include the measurement "Ideas successfully captured per week"
    And the measurement unit must be "ideas"
    And the output brief must include an approved-with-limitation caution banner
    And the output brief must include exactly one next action
    And the output brief must include the human-review reminder
    And the output brief must include the responsible-use limitation
    And the output brief must not include ROI, opportunity cost, dollar savings, annual value, marketing equity, or productivity guarantees

  @id_blank_page_01
  Scenario: The Blank Page scenario redacts sensitive details and returns one starting-friction measure
    Given the user selects the "blank_page" scenario
    And the user provides answers containing sensitive identifiers:
      | content_type        | proposal template                         |
      | source_material     | email thread with John Doe from Acme Corp |
      | minutes_to_start    | 60                                        |
      | starting_difficulty | organizing_ideas                          |
    When the Scenario Lab pipeline executes safety filters and assembles the Scenario Brief
    Then the release status must be "APPROVED"
    And the sensitive identifiers must be redacted from the visible brief
    And the output brief must include the measurement "Time to first usable outline"
    And the measurement unit must be "minutes"
    And the baseline display must include "60 minutes"
    And the output brief must include exactly one next action
    And the output brief must include the human-review reminder
    And the output brief must include the responsible-use limitation
    And the redaction applied flag must be true
    And the output brief must not include ROI, opportunity cost, dollar savings, annual value, marketing equity, or productivity guarantees

  @id_high_risk_scope_block_01
  Scenario: High-risk professional advice requests are blocked before a completed brief is rendered
    Given the user selects the "cool_down_tax" scenario
    And the user asks for legal, tax, employment, lending, housing, insurance, medical, mental health, or regulatory compliance advice
    When the Scenario Lab pipeline executes safety filters
    Then the release status must be "BLOCKED"
    And no completed Scenario Brief sections must be rendered
    And the user must receive a scope and safety message
    And the output must not include ROI, opportunity cost, dollar savings, annual value, marketing equity, or productivity guarantees
