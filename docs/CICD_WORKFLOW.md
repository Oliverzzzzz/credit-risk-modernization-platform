# CI/CD Workflow

The project uses GitHub Actions to validate changes before they are merged into `main`.

## Current CI Steps

```text
checkout repository
set up Python 3.11
install dependencies
compile Python modules
run pytest
```

## Branch Workflow

Development follows an issue-driven workflow:

1. Create a feature branch for a GitHub issue.
2. Make focused commits for documentation, implementation, tests, and usage notes.
3. Open a pull request.
4. Wait for GitHub Actions to pass.
5. Merge into `main`.

## Future CD Steps

A production deployment pipeline would add:

- Docker image build and scan
- container registry push
- staging deployment
- smoke tests
- production approval gate
- production deployment
- post-deployment health checks

## Validation Philosophy

CI focuses on reliable project behavior rather than benchmark scores. Model metrics can change with data, but importability, schema logic, API behavior, and artifact generation should remain stable.
