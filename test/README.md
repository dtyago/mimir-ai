# Test Directory

This directory contains test files and test scripts for the Mimir API project.

## Directory Structure

```
test/
├── README.md                    # This file
├── login-test.jpg              # Test image for face recognition testing
└── scripts/                    # Test scripts directory
    ├── test_devcontainer.py    # DevContainer environment validation
    ├── test_admin_apis.py      # Admin API endpoints testing
    ├── debug_registration.py   # Registration process debugging
    ├── post_rebuild_check.py   # Post-rebuild verification
    ├── test_env_fallbacks.py   # Environment variable fallback testing
    └── validate_environment.py # Environment validation utilities
```

## Test Scripts

### Environment Testing
- **`test_devcontainer.py`**: Validates devcontainer environment setup
  - Checks environment variables
  - Verifies directory permissions
  - Tests admin function imports
  - Validates health endpoints

### API Testing  
- **`test_admin_apis.py`**: Comprehensive admin API testing
  - Health endpoint validation
  - Admin login page testing
  - User registration with face images
  - Face-based user login
  - Admin functionality testing

### Debugging & Verification
- **`debug_registration.py`**: Step-by-step registration debugging
  - Import validation
  - Face processing testing
  - Database connectivity
  - Full registration flow testing

- **`post_rebuild_check.py`**: Post-rebuild environment verification
  - User context validation
  - Environment variable checks
  - Directory permission verification

## Usage

### Run All Environment Tests
```bash
cd /workspaces/mimir-api
python3 test/scripts/test_devcontainer.py
```

### Run API Tests
```bash
cd /workspaces/mimir-api
python3 test/scripts/test_admin_apis.py
```

### Debug Registration Issues
```bash
cd /workspaces/mimir-api
python3 test/scripts/debug_registration.py
```

### Verify Post-Rebuild Setup
```bash
cd /workspaces/mimir-api
python3 test/scripts/post_rebuild_check.py
```

### Test Against Different Environments
```bash
# Test local development
python3 test/scripts/test_admin_apis.py

# Test Azure deployment (example)
python3 test/scripts/test_admin_apis.py https://your-app.azurewebsites.net
```

## Test Data

- **`login-test.jpg`**: Sample face image for testing registration and login functionality
  - Used by registration tests
  - Used by face-based login tests
  - Required for face recognition validation

## Notes

- All test scripts are designed to work with both devcontainer and production environments
- Environment variables are automatically detected and used appropriately
- Tests validate persistent storage functionality across container rebuilds
- Face recognition tests require the `login-test.jpg` image file
