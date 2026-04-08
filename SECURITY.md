# Security Policy

## Supported scope

This project is an early-stage, read-only MCP server for DICOM query workflows.

Security fixes are best-effort. In practice, the latest code on the default branch is the supported line.

## Reporting a vulnerability

Please **do not** open a public GitHub issue for suspected vulnerabilities.

Preferred path:

1. Use GitHub **Private Vulnerability Reporting** for this repository, if enabled.
2. If that setting is not enabled yet, contact the maintainer privately via GitHub profile contact methods and share only the minimum needed details.

When reporting, include:

- affected version / commit
- impact summary
- reproduction steps
- whether real DICOM systems or data are involved
- any mitigations you already tested

## Sensitive data rule

Do not include PHI, real DICOM studies, patient identifiers, screenshots, or server credentials in reports.
Use de-identified or synthetic examples only.

## What to expect

The maintainer will try to:

- confirm receipt
- assess severity and scope
- work on a fix or mitigation
- coordinate a safe disclosure path when appropriate

## Operational guidance

This repository is not intended for direct use against live clinical systems with patient-sensitive data unless the operator fully understands and accepts the risk.

If you are unsure whether something is a vulnerability or a usage question, start with the safer assumption and report it privately.
