# REQ-002: Aliases in DCL instructions

## 1. Goal
Adapt `dcl-agent` to the refined `dcl-bundle` structure, enabling support for aliases defined in `index.yaml` and multi-bundle configurations.

## 2. Requirements

### 2.1 Bundle Structure Support
The agent must support the following bundle structure:
```text
bundle-root/
  index.yaml          # Defines aliases
  knowledges/         # Arbitrary resource files (ttl, json, etc.) and prompt modules (yaml files)
  [category]/         # Prompt modules (yaml files)
    [module].yaml
```

#### 2.1.1 Prompt Modules
- Located in various subfolders (e.g. `entities/`, `operations/`).
- Filenames are arbitrary.
- Identity (`id`) and Version (`version`) are defined in the YAML content metadata.
- **Constraint**: Multiple files defining the same `id` and `version` is a **Warning** condition (First-Wins strategy). It is NOT a fatal error.

#### 2.1.2 Knowledge Resources
- Located in `knowledges/` folder.
- **Mixed Content**: Can contain both:
    - **Prompt Modules** (YAML files with standard metadata `id`, `type`, `version`). Treated identical to modules in category folders.
    - **Raw Resources** (Arbitrary text formats: ttl, json, csv, or YAMLs without module metadata).
- **ID Resolution**:
    - **Prompt Modules**: Identified by their internal `id` (and `version`) from metadata.
    - **Raw Resources**: Identified by **Relative Path** (including filename) from the bundle root.
        - Example: `bundle-name/knowledges/ontology/dcl-core.ttl`
    - **Aliases**: Both types can be aliased in `index.yaml`.

#### 2.1.3 Index / Aliases
- `index.yaml` in the bundle root contains the alias mapping.
- Maps an alias (e.g. `WRITE`) to a specific versioned ID (e.g. `dcl-god-mode/operations/write/4.0`).
- **Usage Scope**:
    - Aliases are primarily used for `OPERATOR` and `ENTITY` (Operand) prompt modules.
    - Aliases are also valid and frequent in `USING` (Modifiers) and `FROM` (Sources) clauses, alongside Full IDs.
- **Precedence**:
    - 1. **Alias** (from `index.yaml`)
    - 2. **Full ID** (Internal ID for Modules, Path ID for Resources)
    - *Implicit aliasing (short-name)* is deprecated.

### 2.2 Multi-Bundle Support
- The agent must be capable of loading multiple bundles at initialization.
- Bundles are logically separated by namespaces corresponding to the bundle root directory name (or explicit configuration).
- Registry must aggregate resources from all loaded bundles.
- Aliases are resolved across all loaded bundles.
- Aliases from the first bundle are used if there are duplicates in other bundles.

### 2.3 Registry & Loading
- **Loader**:
    - Recursively scan for `*.yaml` (Prompt Modules / Knowledge YAMLs).
    - Recursively scan for other supported extensions in `knowledges/`.
- **Registry**:
    - Store resources by full ID (`id/version`).
    - Store aliases from `index.yaml`.
    - Provide resolution logic: Alias -> ID -> Resource.

## 3. Non-Functional Requirements
- Error reporting for duplicate versions (conflict detection).
- Error reporting for missing alias targets.
- Backward compatibility for single-file tests where applicable.

## 4. Acceptance Criteria
1. Agent initializes with a list of bundles (e.g. `dcl-god-mode`, `dcl-core`).
2. `PromptModuleRegistry` correctly indexes all modules and resources.
   - YAML modules by internal ID.
   - Other resources by path-based ID.
3. `PromptModuleRegistry` resolves aliases from `index.yaml` (e.g. `GRAMMAR` -> `dcl-core/knowledges/framework/dcl_grammar/2.2`).
4. Duplicate module versions in different files result in a **Warning** (first file wins).
