---
trigger: always_on
description: Требует синхронизацию upstream/downstream артефактов (REQ → TSD → IMP → Code)
---

# Rule: Artifact Consistency (Back-Propagation)

**Scope:** Applies to all work involving project artifacts (REQ, TSD, IMP, code).

---

## Principle

All project artifacts form a chain: **REQ → TSD → IMP → Code**.

Any downstream artifact (e.g., Code) must be consistent with all upstream artifacts (e.g., TSD, REQ). If a conflict is discovered, the upstream artifact must be updated first.

---

## Rule

**Never implement or design something that contradicts an approved upstream artifact.**

### Algorithm (Upstream Synchronization)

**IMPORTANT:** When you discover conflicts during feedback processing, handle ALL feedback items first (batch processing), then resolve conflicts.

When you discover a conflict between your current work and an upstream artifact:

1. **Detect:** Identify the discrepancy (e.g., "This API design contradicts the requirement").

2. **Batch Processing:** If this is part of feedback review, continue processing ALL other feedback items before halting.

3. **Halt:** Stop work on editing the current (downstream) artifact.

4. **Notify User in Chat (do NOT edit artifacts yet):**
   - Describe the conflict clearly
   - Identify affected upstream artifact (REQ, TSD, IMP)
   - Ask clarifying questions about desired behavior
   - **Propose resolution options:**
     a) Update upstream artifact (describe specific changes)
     b) Modify current approach to fit existing upstream
     c) Reject the feedback/requirement if fundamentally incompatible

5. **Wait for User Decision:** Do NOT proceed until user chooses an option.

6. **Execute Approved Resolution:**
   - If option (a): Update upstream artifact, increment version, request approval
   - If option (b): Modify current work to align with upstream
   - If option (c): Document rejection reason and proceed

7. **Re-Align:** Update all intermediate artifacts down the chain, if necessary.

8. **Resume:** Continue work on the current artifact using approved resolution.

---

## Examples

### Example 1: Code vs TSD Conflict

**Scenario:** While implementing a method, you realize the TSD-specified API signature is inconvenient (e.g., takes too many parameters).

**Correct Approach:**
1. HALT code implementation.
2. **Notify user in chat:**
   - "The TSD specifies `register(alias, target, bundle_id, priority)` but during implementation I found this is overly complex. The bundle_id and priority can be inferred from context."
   - "Should I: (a) Update TSD to use simpler signature `register(alias, target)`, (b) Keep TSD signature and add wrapper method, or (c) Accept complexity as necessary?"
3. **Wait for user decision.**
4. **If option (a) chosen:**
   - Update `TSD-002.md` → API Contracts section → revise method signature
   - Increment version to `TSD-002 v1.1`
   - Request user approval for updated TSD
5. After approval, implement code with new API.

**Incorrect Approach:**
- Implement code with the "better" API without discussing with user.
- Result: Code and TSD are out of sync. User may have had reasons for original API.

---

### Example 2: TSD vs REQ Conflict

**Scenario:** While designing a technical solution, you discover a requirement is technically infeasible or ambiguous.

**Correct Approach:**
1. HALT TSD work.
2. **Notify user in chat:**
   - "REQ-003 states 'Aliases must be globally unique across all bundles', but this conflicts with the First-Wins strategy in the same requirement. Global uniqueness would require rejection, not First-Wins."
   - "Should I: (a) Update REQ to clarify 'First bundle wins, others log warning', (b) Change strategy to reject duplicates with error, or (c) Keep both with priority: global check before First-Wins?"
3. **Wait for user decision.**
4. **If option (a) chosen:**
   - Update `REQ-003.md` → clarify the requirement
   - Increment version to `REQ-003 v1.1`
   - Request user approval
5. After approval, resume TSD with clarified requirement.

**Incorrect Approach:**
- Assume what the requirement "probably means" and proceed with TSD.
- Result: TSD may not match user's actual intent.

---

### Example 3: Refactoring During Implementation

**Scenario:** While coding, you find a better way to structure the component that differs from the IMP.

**Correct Approach:**
1. HALT coding.
2. **Notify user in chat:**
   - "IMP-004 specifies separate classes RegistryAliases and RegistryModules, but I found they share 90% of code. A single Registry class with two dictionaries would be simpler."
   - "Should I: (a) Update IMP and TSD to use single Registry class, (b) Keep separate classes as designed for future extensibility, or (c) Implement shared base class?"
3. **Wait for user decision.**
4. **If option (a) chosen:**
   - Update `IMP-004.md` → revise affected tasks/milestones
   - Optionally update `TSD-004.md` if architectural impact
   - Request user approval
5. After approval, proceed with new structure.

**Incorrect Approach:**
- "It's just a refactoring, no need to update IMP."
- Result: IMP becomes outdated and misleading for future reference.

---

## Exception: Trivial Implementation Details

You do NOT need to back-propagate **trivial implementation details** that do not affect:
- API contracts
- Architecture
- Component responsibilities
- Test requirements

Examples of trivial details:
- Variable naming (if not part of public API)
- Internal helper functions
- Code comments
- Log messages

Use judgment: If unsure whether a change is trivial, err on the side of updating upstream artifacts.

---

## Why This Matters

- **Single Source of Truth:** All artifacts remain consistent and trustworthy.
- **Traceability:** Every design decision has a documented rationale in upstream artifacts.
- **Prevents Drift:** Code doesn't diverge from approved design over time.
- **Facilitates Onboarding:** New developers can trust that TSD reflects actual implementation.
