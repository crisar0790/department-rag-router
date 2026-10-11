
# Technology Change Management Procedure

Document ID: TECH-007
Department: Technology
Version: 1.0
Effective date: 2026-01-01
Company: AR Cloud
Document type: Synthetic procedure for an educational project

## Purpose and scope

AR Cloud uses a structured technology change management process to reduce operational disruptions, protect company information, and maintain reliable business services.

Technology changes may affect applications, databases, cloud infrastructure, network configurations, security controls, integrations, and internal business platforms. Even relatively small modifications can create unexpected consequences when systems depend on shared services or configuration settings.

This procedure establishes how changes are requested, evaluated, approved, scheduled, implemented, validated, and documented.

It applies to production environments and other managed systems where a modification could affect business operations, information security, or service availability.

Routine employee support requests that do not modify shared technical environments remain governed by the Technology Support Procedure.

## Change categories

Technology classifies changes according to their operational risk, urgency, and implementation characteristics.

Standard changes are low-risk, repeatable modifications that follow an approved procedure and have predictable outcomes. Examples may include routine configuration updates performed under established technical instructions.

Normal changes require individual assessment because they may affect service availability, system behavior, integrations, or security configurations.

Emergency changes address urgent situations where delaying implementation could cause significant operational damage, prolonged service interruption, or an unacceptable security exposure.

Emergency classification does not eliminate the need for accountability. Emergency changes must still be authorized, documented, and reviewed after implementation.

Technology determines the appropriate category based on the actual impact of the proposed modification rather than the requester's preferred implementation timeline.

## Submitting a change request

A change request must describe the proposed modification and explain why it is necessary.

The request should identify the affected systems, expected business benefits, implementation requirements, potential risks, and requested completion date.

The requester must provide sufficient information for Technology to understand the purpose and expected outcome of the change.

Requests involving multiple applications or departments must identify relevant dependencies and stakeholders.

Technology may request additional technical details before beginning the assessment.

A change request should not be approved solely because a manager or employee considers it urgent.

Incomplete requests may be returned for clarification when essential information is missing.

## Impact and risk assessment

Technology evaluates proposed changes before authorizing their implementation.

The assessment considers service availability, information security, data integrity, performance, integration dependencies, and potential effects on employees or customers.

Changes affecting critical business systems require particular attention because failures may interrupt multiple departments.

The technical team must identify whether the proposed modification could affect authentication, data storage, external integrations, or backup processes.

Risk assessments should consider both the probability of failure and the consequences of an unsuccessful implementation.

When a change introduces significant uncertainty, Technology may require additional testing, peer review, or a revised implementation plan.

The assessment must identify the responsible personnel and the conditions under which the change may proceed.

## Change approval responsibilities

Approval requirements depend on the change category, risk level, and business impact.

Technology is responsible for technical evaluation and authorization according to established internal responsibilities.

System owners must participate when changes could significantly affect business functionality, operational workflows, or information availability.

Changes involving additional purchases, licensing costs, or contractual commitments must follow the appropriate Finance approval procedures.

A technical approval does not automatically authorize new spending or changes to contractual obligations.

Employees must not bypass required approvals by dividing a significant modification into smaller requests.

The final approval decision must be recorded before a normal change is implemented.

## Implementation planning

Approved changes must have an implementation plan appropriate to their complexity and operational risk.

The plan should identify the technical steps, responsible personnel, required resources, expected duration, and dependencies.

For changes affecting production services, Technology must determine whether implementation should occur during a maintenance window.

The implementation plan should describe how success will be verified and how unexpected problems will be handled.

When necessary, the plan must include preparation of current configuration records, relevant backups, or recovery resources.

Employees affected by a planned interruption should receive advance communication when practical.

Implementation must not begin if essential prerequisites remain incomplete.

## Testing before deployment

Changes should be tested in an appropriate non-production environment whenever technically feasible.

Testing must focus on the expected functionality and on potential effects on related systems.

For application changes, validation may include functional testing, integration checks, automated tests, and performance verification.

For infrastructure changes, validation may include connectivity checks, configuration verification, access control testing, and resource monitoring.

Test environments should avoid unnecessary exposure of real personal or confidential business information.

Testing results must be reviewed before a change is authorized for production deployment.

A successful test does not eliminate operational risk, but it provides evidence that the modification behaves as expected under the tested conditions.

## Production implementation

Only authorized personnel may implement approved changes in managed production environments.

Before starting, the responsible technician must verify that the required approvals, resources, and implementation instructions are available.

The technician must confirm that the target environment matches the assumptions used during planning.

Changes must follow the approved implementation sequence unless an unexpected condition requires reassessment.

Significant deviations from the approved plan must be communicated to the responsible technical personnel.

If implementation produces unexpected behavior, the technician must evaluate whether continuing could increase operational risk.

Changes must not be declared successful before the required post-implementation validation is completed.

## Rollback and recovery planning

Changes that could disrupt important services must include an appropriate rollback or recovery strategy.

A rollback plan describes how the previous operational state can be restored if the implementation fails.

The plan should identify required configuration records, recovery resources, responsible personnel, and conditions that trigger rollback.

Not every change can be reversed automatically. Database migrations, external integrations, and irreversible data transformations may require specialized recovery procedures.

Technology must identify these limitations before approving high-risk modifications.

If a rollback becomes necessary, the responsible personnel must coordinate restoration activities and communicate significant service impacts.

Recovery activities involving protected information must follow the Data Backup and Recovery Policy.

## Emergency change handling

Emergency changes may be required to contain a serious security vulnerability, restore an unavailable service, or prevent significant business disruption.

The responsible Technology personnel must evaluate the immediate risk and determine whether emergency implementation is justified.

Authorization should be obtained from the designated technical authority using the fastest approved communication channel.

Emergency implementation may use an abbreviated planning process when time constraints make the normal workflow impractical.

However, personnel must still consider essential security precautions, system dependencies, and potential recovery options.

After the emergency is resolved, Technology must document the change, explain the urgency, and review the outcome.

Emergency procedures must not be used as a routine alternative to normal planning and approval.

## Communication and stakeholder coordination

Technology communicates relevant changes to employees, system owners, and other affected stakeholders.

Notifications should describe the affected service, expected operational impact, planned implementation period, and available support channels.

Changes that require employee action must include clear instructions and an appropriate completion deadline.

If an implementation is postponed or cancelled, affected stakeholders should receive an updated notification.

Unexpected service interruptions must be communicated according to their severity and operational consequences.

Communication must avoid exposing sensitive technical details, privileged credentials, or security configurations to unauthorized recipients.

System owners are responsible for coordinating business activities that may be affected by a planned change.

## Post-implementation validation

After implementing a change, Technology verifies that the intended outcome has been achieved.

Validation may include application functionality checks, service availability monitoring, security verification, performance analysis, and confirmation from system owners.

The responsible technician must determine whether any unexpected effects remain unresolved.

When appropriate, Technology monitors the affected environment for a defined observation period.

A change may be considered completed only when required validation activities are successful and outstanding issues have been appropriately addressed.

If the change fails to meet acceptance criteria, Technology must determine whether corrective action, additional investigation, or rollback is necessary.

## Change records and auditability

Technology maintains records of significant changes to managed systems.

Each record should identify the change request, classification, affected systems, responsible personnel, approvals, implementation date, and final outcome.

Records should also include relevant testing results, incidents encountered, rollback actions, and post-implementation observations.

Documentation must be sufficiently clear to support future troubleshooting and operational reviews.

Technical personnel must not include passwords, authentication tokens, or other sensitive secrets in change records.

Change records may be reviewed to identify recurring failures, improve procedures, and support internal accountability.

## Roles and responsibilities

Technology coordinates the technical assessment, approval workflow, implementation, validation, and documentation of changes.

System owners communicate business requirements, evaluate operational impact, and participate in acceptance testing when appropriate.

Department managers coordinate affected employees and provide information about business priorities.

Finance evaluates purchasing, payment, and budget implications when a change introduces additional financial commitments.

Employees must follow approved procedures and must not independently modify shared technical environments without authorization.

External service providers participating in implementation must comply with applicable access, confidentiality, and security requirements.

## Procedure review and continuous improvement

Technology periodically reviews change management activities to identify opportunities for improving operational reliability.

Reviews may consider unsuccessful deployments, emergency change frequency, recurring incidents, incomplete documentation, and avoidable service interruptions.

Significant findings should result in appropriate corrective actions, updated technical instructions, or additional training.

Changes to this procedure must be communicated to personnel responsible for requesting, approving, or implementing technology modifications.

This procedure complements the Technology Support Procedure, Information Security Policy, Account Access Procedure, and Data Backup and Recovery Policy.

Exceptions must be documented and authorized by the responsible stakeholders before implementation.
