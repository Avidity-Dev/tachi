# Development Plan for tachi CLI Tool

## Project Overview
tachi is a simple Python CLI tool that generates GitHub Actions workflows for Azure Container Apps deployments. The focus is on simplicity, rapid delivery, and avoiding premature abstractions.

## Development Timeline: 2 Weeks

### Week 1: Core Functionality (Days 1-5)

#### Phase 1: Project Setup (Days 1-2)
**Objective**: Set up the project foundation with uv package manager and basic CLI structure.

**Tasks for Agent D**:

1. **Initialize project with uv**
   - Create project directory structure
   - Initialize with `uv init`
   - Set up pyproject.toml with required dependencies:
     - click (CLI framework)
     - jinja2 (templating)
     - pyyaml (config parsing)
     - Python 3.10+ requirement

2. **Create basic project structure**
   ```
   tachi/
   ├── pyproject.toml
   ├── README.md
   ├── src/
   │   └── tachi/
   │       ├── __init__.py
   │       ├── cli.py
   │       ├── config.py
   │       ├── azure_generator.py
   │       ├── templates/
   │       │   └── azure/
   │       └── validator.py
   └── tests/
       ├── test_config.py
       ├── test_generator.py
       └── test_cli.py
   ```

3. **Implement minimal CLI entry point**
   - Create basic Click CLI group in cli.py
   - Add placeholder commands: `generate` and `validate`
   - Ensure CLI is installable and runnable via `uv run tachi`

**Acceptance Criteria**:
- [ ] Project initializes with uv successfully
- [ ] Basic directory structure created
- [ ] CLI runs with `uv run tachi --help`
- [ ] Dependencies installed via pyproject.toml

#### Phase 2: Configuration Dataclasses (Days 3-4)
**Objective**: Implement configuration models with validation using simple dataclasses.

**Tasks for Agent D**:

1. **Implement config.py dataclasses**
   - Create Service dataclass with fields:
     - name, dockerfile, port, external, cpu, memory, min_replicas, max_replicas, context
   - Create AzureConfig dataclass with fields:
     - resource_group, registry, location, log_analytics_workspace_id, log_analytics_workspace_key
   - Create ProjectConfig dataclass with fields:
     - name, strategy, azure, services

2. **Add validation methods**
   - Service.validate(): Check port range, CPU > 0, replica constraints
   - ProjectConfig.validate(): Check strategy values, duplicate service names, call service validations
   - Return list of error strings (no exceptions)

3. **Implement YAML parsing**
   - Create _parse_config() function to convert YAML dict to ProjectConfig
   - Handle optional fields with defaults
   - No complex error handling - let YAML errors bubble up

**Acceptance Criteria**:
- [ ] All dataclasses implemented as specified
- [ ] Validation returns meaningful error messages
- [ ] Can parse sample tachi.yaml into ProjectConfig
- [ ] Total config.py under 120 lines

#### Phase 3: Azure Generator Implementation (Day 5)
**Objective**: Implement the core generator logic without templates.

**Tasks for Agent D**:

1. **Create AzureGenerator class**
   - Constructor accepts template_dir Path
   - Set up Jinja2 Environment with FileSystemLoader
   - Configure trim_blocks and lstrip_blocks

2. **Implement generate() method**
   - Create output directory structure (.github/workflows, container-apps/configs)
   - Determine workflows based on strategy (trunk-release vs trunk-direct)
   - Call helper methods for each generation task

3. **Implement helper methods**
   - _get_workflows_for_strategy(): Return workflow list based on strategy
   - _generate_workflow(): Render single workflow (stub - templates not ready)
   - _generate_container_configs(): Generate container app configs (stub)
   - _generate_setup_instructions(): Create SETUP.md with required secrets

d

### Week 2: Templates & Polish (Days 6-10)

#### Phase 4: Template Creation (Days 6-7)
**Objective**: Create Jinja2 templates based on ca-1099-risk-assessment examples.

**Tasks for Agent D**:

1. **Create workflow templates in templates/azure/**
   - dev-deploy.yaml.j2: Development deployment workflow
   - stage-deploy.yaml.j2: Staging deployment (trunk-release only)
   - prod-deploy.yaml.j2: Production deployment workflow
   - pr-cleanup.yaml.j2: PR environment cleanup

2. **Create container app template**
   - container-apps/app.yaml.j2: Container Apps configuration

3. **Template requirements**
   - Use provided variables: project, azure, services
   - Support multi-service deployments
   - Include proper environment variables and secrets

**Acceptance Criteria**:
- [ ] All templates render valid YAML
- [ ] Templates handle multiple services correctly
- [ ] Environment-specific configurations work

#### Phase 5: CLI Integration (Day 8)
**Objective**: Complete CLI implementation with file I/O.

**Tasks for Agent D**:

1. **Implement generate command**
   - Support --config flag for YAML file
   - Support --output flag for output directory
   - Load and parse YAML configuration
   - Run validation and display errors
   - Call generator and show success message

2. **Implement validate command**
   - Load configuration file
   - Run validation
   - Display results with clear formatting

3. **Add interactive mode** (stretch goal)
   - If no config file provided, run interactive prompts
   - Basic service configuration wizard

**Acceptance Criteria**:
- [ ] Generate command creates all expected files
- [ ] Validate command provides helpful error messages
- [ ] CLI provides good user feedback

#### Phase 6: Testing & Documentation (Days 9-10)
**Objective**: Add basic tests and documentation.

**Tasks for Agent D**:

1. **Write essential tests**
   - Config validation tests (test_config.py)
   - Generator directory creation tests (test_generator.py)
   - CLI command tests (test_cli.py)

2. **Create documentation**
   - README.md with installation and usage
   - Example tachi.yaml configuration
   - Include both strategies as examples

**Acceptance Criteria**:
- [ ] Core functionality has test coverage
- [ ] README provides clear getting started guide
- [ ] Example configurations work out of the box

## Implementation Guidelines

### Code Style
- **No abstractions**: Direct implementation only
- **Simple validation**: Return error lists, no custom exceptions
- **Flat structure**: All code in main package directory
- **Clear naming**: Descriptive variable and function names
- **Minimal dependencies**: Only click, jinja2, pyyaml



### What NOT to Do
- Don't introduce complexity earlier
- Do not introduce abstract classes where not needed -- revert to duck typing
- Don't implement provider interfaces
- Don't add logging frameworks
- Don't create custom template inheritance
- Don't add configuration schemas beyond dataclasses

## Success Metrics
1. **Functional**: Generates working GitHub Actions workflows
2. **Simple**: New developers productive in < 2 hours
3. **Fast**: Complete implementation in 2 weeks
4. **Focused**: Azure Container Apps only
5. **Maintainable**: Easy to modify and extend

## Handoff to Agent D

Agent D should:
1. Start with Phase 1 immediately
2. Complete each phase before moving to the next
3. Keep implementation as simple as possible
4. Ask for clarification if requirements unclear
5. Deliver working code at each phase

Remember: We're building a tool to ship quickly and get feedback. Every line of code should directly contribute to generating workflows. Save abstractions for version 2.0 after we have real user feedback.