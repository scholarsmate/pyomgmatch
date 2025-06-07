# GitHub CI/CD Setup Instructions

This document explains how to set up the GitHub repository for automated CI/CD pipeline that builds, tests, and publishes the pyomgmatch package to PyPI.

## Required GitHub Secrets

To enable automatic publishing to PyPI, you need to configure the following secrets in your GitHub repository:

### Setting up GitHub Secrets

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

#### Required Secrets

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `PYPI_API_TOKEN` | PyPI API token for publishing releases | 1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)<br>2. Create API token with scope for this project<br>3. Copy the token (starts with `pypi-`) |
| `TEST_PYPI_API_TOKEN` | Test PyPI API token for testing releases | 1. Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/)<br>2. Create API token with scope for this project<br>3. Copy the token (starts with `pypi-`) |

### Creating PyPI API Tokens

#### For PyPI (Production)
1. Go to [https://pypi.org/manage/account/token/](https://pypi.org/manage/account/token/)
2. Click "Add API token"
3. Enter token name: `pyomgmatch-github-actions`
4. Select scope: "Entire account" (initially) or specific project after first upload
5. Click "Add token"
6. **Important**: Copy the token immediately (it starts with `pypi-`)
7. Add this as `PYPI_API_TOKEN` secret in GitHub

#### For Test PyPI (Testing)
1. Go to [https://test.pypi.org/manage/account/token/](https://test.pypi.org/manage/account/token/)
2. Follow the same steps as above
3. Add this as `TEST_PYPI_API_TOKEN` secret in GitHub

## GitHub Environments

The workflows use GitHub environments for additional security:

### Creating Environments

1. Go to **Settings** → **Environments**
2. Create two environments:
   - `release` - for production releases
   - `development` - for development builds

### Environment Protection Rules (Optional but Recommended)

For the `release` environment:
1. Enable "Required reviewers" and add trusted maintainers
2. Enable "Wait timer" for a short delay before deployment
3. Restrict to protected branches only

## Workflow Overview

### 1. Pull Request Workflow (`.github/workflows/pr.yml`)
- **Triggers**: When PRs are opened or updated
- **Actions**:
  - Code linting and formatting checks
  - Security scanning
  - Cross-platform testing (Linux, Windows, macOS)
  - Coverage reporting

### 2. CI/CD Pipeline (`.github/workflows/ci.yml`)
- **Triggers**: 
  - Push to main branch (development builds)
  - Push tags starting with 'v' (release builds)
- **Actions**:
  - Full cross-platform testing
  - Build native libraries using Docker
  - Create wheel with all dependencies
  - Publish to Test PyPI (development builds)
  - Publish to PyPI (tagged releases)

### 3. Release Workflow (`.github/workflows/release.yml`)
- **Triggers**: Manual workflow dispatch or GitHub releases
- **Actions**:
  - Build and verify cross-platform wheel
  - Test wheel installation
  - Publish to PyPI
  - Create GitHub release with artifacts

## Creating a Release

### Method 1: Using Git Tags (Recommended)
```bash
# Create and push a version tag
git tag v0.1.2
git push origin v0.1.2
```

### Method 2: Using GitHub Releases
1. Go to your repository on GitHub
2. Click **Releases** → **Create a new release**
3. Tag: `v0.1.2` (or your version)
4. Title: `Release 0.1.2`
5. Describe changes in the release notes
6. Click **Publish release**

### Method 3: Manual Workflow Dispatch
1. Go to **Actions** → **Release**
2. Click **Run workflow**
3. Enter the version number (e.g., `0.1.2`)
4. Optionally select "Test PyPI only" for testing
5. Click **Run workflow**

## Testing the Pipeline

### Before First Release
1. Test the build process:
   ```bash
   # Make sure the build works locally
   ./build.sh
   ```

2. Test with a development build:
   - Push to main branch
   - Check that the development build appears on Test PyPI

3. Test with a pre-release:
   ```bash
   git tag v0.1.0-rc1
   git push origin v0.1.0-rc1
   ```

## Monitoring and Troubleshooting

### Check Workflow Status
- Go to **Actions** tab in your GitHub repository
- Click on any workflow run to see detailed logs
- Check individual job logs for errors

### Common Issues

1. **Build fails on Windows**: 
   - Check that Docker is properly configured
   - Verify that `build.sh` works in Git Bash environment

2. **Missing native libraries in wheel**:
   - Check the "Verify wheel contents" step in the workflow
   - Ensure all 6 files are included (3 .so/.dll + 3 Windows DLLs)

3. **PyPI upload fails**:
   - Verify API tokens are correctly set
   - Check that package name isn't already taken
   - Ensure version number is unique (can't republish same version)

4. **Tests fail**:
   - Check that all dependencies are properly installed
   - Verify that native libraries load correctly on all platforms

### Debugging Tips

- Use the "Re-run failed jobs" button to retry flaky builds
- Check the "Artifacts" section of workflow runs for build outputs
- Enable debug logging by setting `ACTIONS_STEP_DEBUG: true` in workflow

## Package Verification

After a successful release, verify the package:

```bash
# Install from PyPI
pip install pyomgmatch

# Test basic functionality
python -c "
import omg
matcher = omg.Matcher(['test', 'hello'])
result = matcher.match('hello world test case')
print('Package works:', len(result) > 0)
"
```

## Security Considerations

- API tokens should be kept secure and rotated periodically
- Use environment protection rules for production releases
- Review dependency updates from Dependabot before merging
- Monitor security scan results in PR workflows

## Support

If you encounter issues with the CI/CD pipeline:
1. Check the workflow logs for detailed error messages
2. Review this setup guide for missing configuration
3. Test the build process locally to isolate issues
4. Consult GitHub Actions documentation for advanced troubleshooting
