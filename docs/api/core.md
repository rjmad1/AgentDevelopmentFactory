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

