name: Pull Request

description: Create a pull request to contribute changes
labels: ["review"]

body:
  - type: markdown
    attributes:
      value: |
        Thank you for contributing to Smart Cloud Aggregator! Please describe your changes.

  - type: textarea
    id: description
    attributes:
      label: Description
      description: Describe the changes in this PR
      placeholder: |
        This PR implements...
        Changes include...
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation and Context
      description: Why is this change needed?
      placeholder: |
        This addresses issue #...
        The problem is...
    validations:
      required: true

  - type: textarea
    id: testing
    attributes:
      label: Testing
      description: How have you tested these changes?
      placeholder: |
        - [ ] Added unit tests
        - [ ] Added integration tests
        - [ ] Manual testing
        - [ ] Test case: ...
    validations:
      required: true

  - type: textarea
    id: breaking_changes
    attributes:
      label: Breaking Changes
      description: Does this PR introduce breaking changes?
      placeholder: |
        - None
        or
        - Changed output format of JSON reports
        - Modified CLI interface
    validations:
      required: false

  - type: textarea
    id: checklist_notes
    attributes:
      label: Additional Notes
      description: Any additional information reviewers should know
      placeholder: Notes for reviewers...

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I have tested these changes locally
          required: true
        - label: I have added tests for new functionality
          required: true
        - label: I have updated documentation
          required: false
        - label: I have checked for code style issues
          required: true
        - label: I have rebased on the latest main branch
          required: true
        - label: I have squashed commits into logical units
          required: false

  - type: input
    id: related_issues
    attributes:
      label: Related Issues
      description: Link related issues (e.g., "Closes #123")
      placeholder: "Closes #123"
