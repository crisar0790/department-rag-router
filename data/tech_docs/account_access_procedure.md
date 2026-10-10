# Account Access and Recovery Procedure

Document ID: TECH-001
Department: Technology
Version: 1.0
Effective date: 2026-01-01
Company: AR Cloud
Document type: Synthetic procedure for an educational project

## Purpose and scope

This procedure explains how AR Cloud employees activate company
accounts, troubleshoot sign-in failures, and request account
recovery.

It applies to company-managed identities used for the employee
portal and approved internal applications.

Customer product accounts follow a separate customer access
procedure. Employees must not assume that internal recovery
steps apply to a customer's organization.

This fictional procedure does not authorize the support
assistant to reset credentials or inspect account records.

## Initial account activation

Technology Support sends account activation instructions through
the onboarding contact channel after the manager's provisioning
request has been approved.

The activation message identifies the company account and
provides a time-limited activation link. The link expires
24 hours after issuance.

Employees must complete activation using their own account.
They must not forward the link to another person or ask a
colleague to activate the account on their behalf.

If the link expires, employees must contact Technology Support
to request a replacement. HR may coordinate an onboarding
blocker but cannot issue an activation link.

## Multi-factor authentication setup

Employees must configure multi-factor authentication during
account activation.

The approved method is the company-supported authenticator
application or an approved hardware security key.

Technology Support provides setup instructions and confirms
which methods are supported. Employees must not assume that
a personal authentication method is approved.

Recovery codes must be stored in the approved secure location
specified during setup. They must not be pasted into support
tickets, team messages, or shared documents.

The support assistant must never request passwords, one-time
codes, recovery codes, or activation links.

## Basic sign-in checks

Before opening a ticket, employees should confirm that they
are using the company sign-in page and their assigned company
account identifier.

Employees should check whether Caps Lock is enabled and whether
the browser is using credentials saved for a different account.

If the page appears to contain outdated session information,
employees may retry in a private browser window.

These checks do not require sharing credentials or disabling
security controls.

If a suspicious page asks for credentials, employees must stop
and report the page through the security incident channel
rather than continue troubleshooting there.

## Password reset

Employees who remember their account identifier but cannot
sign in with their password should use the password reset
option on the official company sign-in page.

The reset flow verifies the employee using an approved recovery
method. A reset request does not guarantee successful recovery
if that method is unavailable.

Reset links expire 30 minutes after issuance. Employees must
request a new link if the previous one has expired.

Employees must not repeatedly request links and assume that
an older link remains valid. They should use the most recently
issued link and follow the instructions displayed by the
official reset flow.

If the reset process cannot be completed, employees should
contact Technology Support.

## Temporary account lockout

Five consecutive failed password attempts temporarily lock
the account for 15 minutes.

Employees should stop retrying and wait for the lockout period
before making another attempt.

A temporary lockout is different from a security suspension.
Waiting 15 minutes does not resolve an account suspended for
review.

If the sign-in page indicates suspension or the account remains
unavailable after the lockout period, employees must contact
Technology Support.

The support assistant cannot confirm whether an individual
account is locked, suspended, or active.

## Lost authentication device

Employees who lose access to their authentication device should
use an approved alternative factor or recovery method if one
is available.

If no approved method is available, they must submit an account
recovery request to Technology Support.

The request should include the company account identifier,
a safe contact method, and a description of the access problem.
It must not include passwords or authentication secrets.

Technology Support verifies identity through the approved
recovery process before changing authentication methods.

A manager's message may support coordination but does not
replace identity verification or authorize a security bypass.

## Suspected account compromise

Employees who receive unexpected authentication prompts,
notice unrecognized account activity, or suspect that their
credentials were exposed must report a security incident
immediately through the designated incident channel.

They should not approve an unexpected authentication prompt
or continue testing a possibly compromised account.

Technology Support coordinates the incident response and
determines whether account restrictions or credential changes
are required.

This document does not define the complete incident response
process. Routine password reset steps do not replace reporting
a suspected compromise.

## Access requests and permissions

An activated account does not automatically provide access
to every application.

Employees requesting additional permissions must provide
the application name, required role, business reason, and
manager reference.

The application owner approves permissions. Technology Support
implements the approved request.

Employees must not use a colleague's account while waiting
for access or treat an onboarding checklist as permission
approval.

If sign-in succeeds but a required application denies access,
the employee should report a permission issue rather than
repeatedly reset the account password.

## Support ticket information

A routine access ticket should include the affected application,
the approximate time of failure, the error message, and whether
other approved applications remain accessible.

Screenshots must exclude passwords, authentication codes,
recovery links, and unrelated personal information.

Technology Support aims to provide an initial response within
one working day during its published support hours.

This is an acknowledgment target, not a guaranteed recovery
or permission completion time. Requests requiring identity
verification or application owner approval may take longer.

## Department boundaries

Technology Support handles activation, authentication failures,
password recovery, lockouts, and technical permission requests.

HR handles employee record corrections and onboarding schedule
questions. Finance handles billing and payment questions.

A failure to sign in before downloading an invoice belongs
to Technology. A question about an incorrect invoice amount
belongs to Finance.

The support assistant may explain documented recovery steps
and identify the responsible team. It cannot verify identity,
reset passwords, deactivate authentication factors, grant
permissions, or confirm the status of an account.