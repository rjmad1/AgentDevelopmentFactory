# Core API Reference (`src/core.js`)

The `core.js` module provides the foundational deterministic engine for the Agent Development Factory. It handles revision lifecycle, state immutability, cryptographic hashing, real filesystem containment, and append-only evidence auditing.

---

## Exported Functions Summary

| Function | Signature | Description |
| :--- | :--- | :--- |
| [`sha256`](#sha256) | `function sha256(data)` | Domain function: `sha256`. |
| [`deterministicJsonString`](#deterministicjsonstring) | `function deterministicJsonString(obj)` | Domain function: `deterministicJsonString`. |
| [`validateIdentifier`](#validateidentifier) | `function validateIdentifier(id, fieldName = 'identifier')` | Domain function: `validateIdentifier`. |
| [`assertRealFsContainment`](#assertrealfscontainment) | `function assertRealFsContainment(allowedParentDir, targetPath)` | Domain function: `assertRealFsContainment`. |
| [`getCheckerImplementationHash`](#getcheckerimplementationhash) | `function getCheckerImplementationHash()` | Domain function: `getCheckerImplementationHash`. |
| [`evaluateEvidenceApplicability`](#evaluateevidenceapplicability) | `function evaluateEvidenceApplicability(check, currentArtifactHashes, currentCheckerHash)` | Domain function: `evaluateEvidenceApplicability`. |
| [`verifyEvidenceConsistency`](#verifyevidenceconsistency) | `function verifyEvidenceConsistency(revDir)` | Domain function: `verifyEvidenceConsistency`. |
| [`validateRequirements`](#validaterequirements) | `function validateRequirements(requirements)` | Domain function: `validateRequirements`. |
| [`generateSpecMarkdown`](#generatespecmarkdown) | `function generateSpecMarkdown({ revisionId, parentRevisionId, briefText, requirements, hashes, createdAt, })` | Domain function: `generateSpecMarkdown`. |
| [`generateManifest`](#generatemanifest) | `function generateManifest({ revisionId, parentRevisionId, briefText, requirements, hashes, createdAt, })` | Domain function: `generateManifest`. |
| [`initRevision`](#initrevision) | `function initRevision({ storeDir, revisionId, parentRevisionId = null, briefPath, requirementsPath, })` | Domain function: `initRevision`. |
| [`runCheck`](#runcheck) | `function runCheck({ storeDir, revisionId, checkId, failIntentionally = false, customCheckerImplementationHash = null, })` | Domain function: `runCheck`. |
| [`inspectRevision`](#inspectrevision) | `function inspectRevision({ storeDir, revisionId })` | Domain function: `inspectRevision`. |
| [`exportAgentYamlSpec`](#exportagentyamlspec) | `function exportAgentYamlSpec({ storeDir, revisionId, outputPath = null, })` | Domain function: `exportAgentYamlSpec`. |
| [`scaffoldRequirementsTemplate`](#scaffoldrequirementstemplate) | `function scaffoldRequirementsTemplate({ outputPath, title = 'Autonomous Analytical Processing Agent', author = 'Admin', })` | Domain function: `scaffoldRequirementsTemplate`. |
| [`importMcpToolDefinition`](#importmcptooldefinition) | `function importMcpToolDefinition({ mcpSchemaPath, registryPath = null, effectLevel = 'READ_PUBLIC', })` | Domain function: `importMcpToolDefinition`. |
| [`runDoctorCheck`](#rundoctorcheck) | `function runDoctorCheck({ projectRoot = null } = {})` | Domain function: `runDoctorCheck`. |
| [`triageSolutionComplexity`](#triagesolutioncomplexity) | `function triageSolutionComplexity({ briefText })` | S1/S2 Principle: Triage task into No-Agent, Deterministic Workflow, Single Agent... |
| [`estimateTokenAndCostFeasibility`](#estimatetokenandcostfeasibility) | `function estimateTokenAndCostFeasibility({ briefText, baseTokens = 1500 })` | S5 Principle: Estimate token consumption and cost feasibility. |
| [`evaluateAgentThreatModel`](#evaluateagentthreatmodel) | `function evaluateAgentThreatModel({ manifestPath })` | S18 (OWASP Agentic Top 10): Threat modeling evaluator for agent manifests. |
| [`generateGuardrailPolicy`](#generateguardrailpolicy) | `function generateGuardrailPolicy({ manifestPath, riskTier = 'T0' })` | Section 4.3: Generate Section 4.3 canonical YAML Guardrail Policy from manifest. |
| [`runAdversarialSecuritySuite`](#runadversarialsecuritysuite) | `function runAdversarialSecuritySuite({ manifestPath, riskTier = 'T0' })` | Section 5: Run SEC-01 through SEC-10 Adversarial Security Suite. |
| [`evaluateReleaseGates`](#evaluatereleasegates) | `function evaluateReleaseGates({ manifestPath, riskTier = 'T0', humanReviewConfirmed = false, retryAttempt = 1, })` | Section 6: Evaluate the 9 Release Gates before promoting an agent to production. |

---

## Function Details

### `sha256`

```javascript
function sha256(data)
```

Domain function: `sha256`.

---

### `deterministicJsonString`

```javascript
function deterministicJsonString(obj)
```

Domain function: `deterministicJsonString`.

---

### `validateIdentifier`

```javascript
function validateIdentifier(id, fieldName = 'identifier')
```

Domain function: `validateIdentifier`.

---

### `assertRealFsContainment`

```javascript
function assertRealFsContainment(allowedParentDir, targetPath)
```

Domain function: `assertRealFsContainment`.

---

### `getCheckerImplementationHash`

```javascript
function getCheckerImplementationHash()
```

Domain function: `getCheckerImplementationHash`.

---

### `evaluateEvidenceApplicability`

```javascript
function evaluateEvidenceApplicability(check, currentArtifactHashes, currentCheckerHash)
```

Domain function: `evaluateEvidenceApplicability`.

---

### `verifyEvidenceConsistency`

```javascript
function verifyEvidenceConsistency(revDir)
```

Domain function: `verifyEvidenceConsistency`.

---

### `validateRequirements`

```javascript
function validateRequirements(requirements)
```

Domain function: `validateRequirements`.

---

### `generateSpecMarkdown`

```javascript
function generateSpecMarkdown({ revisionId, parentRevisionId, briefText, requirements, hashes, createdAt, })
```

Domain function: `generateSpecMarkdown`.

---

### `generateManifest`

```javascript
function generateManifest({ revisionId, parentRevisionId, briefText, requirements, hashes, createdAt, })
```

Domain function: `generateManifest`.

---

### `initRevision`

```javascript
function initRevision({ storeDir, revisionId, parentRevisionId = null, briefPath, requirementsPath, })
```

Domain function: `initRevision`.

---

### `runCheck`

```javascript
function runCheck({ storeDir, revisionId, checkId, failIntentionally = false, customCheckerImplementationHash = null, })
```

Domain function: `runCheck`.

---

### `inspectRevision`

```javascript
function inspectRevision({ storeDir, revisionId })
```

Domain function: `inspectRevision`.

---

### `exportAgentYamlSpec`

```javascript
function exportAgentYamlSpec({ storeDir, revisionId, outputPath = null, })
```

Domain function: `exportAgentYamlSpec`.

---

### `scaffoldRequirementsTemplate`

```javascript
function scaffoldRequirementsTemplate({ outputPath, title = 'Autonomous Analytical Processing Agent', author = 'Admin', })
```

Domain function: `scaffoldRequirementsTemplate`.

---

### `importMcpToolDefinition`

```javascript
function importMcpToolDefinition({ mcpSchemaPath, registryPath = null, effectLevel = 'READ_PUBLIC', })
```

Domain function: `importMcpToolDefinition`.

---

### `runDoctorCheck`

```javascript
function runDoctorCheck({ projectRoot = null } = {})
```

Domain function: `runDoctorCheck`.

---

### `triageSolutionComplexity`

```javascript
function triageSolutionComplexity({ briefText })
```

S1/S2 Principle: Triage task into No-Agent, Deterministic Workflow, Single Agent, or Multi-Agent.

**Parameters:**

* `{Object} options`
* `{string} options.briefText - Brief content string`

**Returns:** `{Object} Triage recommendation`

---

### `estimateTokenAndCostFeasibility`

```javascript
function estimateTokenAndCostFeasibility({ briefText, baseTokens = 1500 })
```

S5 Principle: Estimate token consumption and cost feasibility.

**Parameters:**

* `{Object} options`
* `{string} options.briefText`
* `{number} [options.baseTokens=1500]`

**Returns:** `{Object} Feasibility and cost estimate`

---

### `evaluateAgentThreatModel`

```javascript
function evaluateAgentThreatModel({ manifestPath })
```

S18 (OWASP Agentic Top 10): Threat modeling evaluator for agent manifests.

**Parameters:**

* `{Object} options`
* `{string} options.manifestPath`

**Returns:** `{Object} Threat evaluation report`

---

### `generateGuardrailPolicy`

```javascript
function generateGuardrailPolicy({ manifestPath, riskTier = 'T0' })
```

Section 4.3: Generate Section 4.3 canonical YAML Guardrail Policy from manifest.

**Parameters:**

* `{Object} options`
* `{string} options.manifestPath`
* `{string} [options.riskTier='T0']`

**Returns:** `{Object} Guardrail policy definition and YAML string`

---

### `runAdversarialSecuritySuite`

```javascript
function runAdversarialSecuritySuite({ manifestPath, riskTier = 'T0' })
```

Section 5: Run SEC-01 through SEC-10 Adversarial Security Suite.

**Parameters:**

* `{Object} options`
* `{string} options.manifestPath`
* `{string} [options.riskTier='T0']`

**Returns:** `{Object} Adversarial security evaluation report`

---

### `evaluateReleaseGates`

```javascript
function evaluateReleaseGates({ manifestPath, riskTier = 'T0', humanReviewConfirmed = false, retryAttempt = 1, })
```

Section 6: Evaluate the 9 Release Gates before promoting an agent to production.

**Parameters:**

* `{Object} options`
* `{string} options.manifestPath`
* `{string} [options.riskTier='T0']`
* `{boolean} [options.humanReviewConfirmed=false]`
* `{number} [options.retryAttempt=1]`

**Returns:** `{Object} Release gate report`

---

