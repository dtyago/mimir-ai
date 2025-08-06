# Test Directory

This directory contains test files and test scripts for the Mimir AI project.

## Directory Structure

```
test/
├── README.md                      # This file
├── TEST_DATA.md                   # Test data setup instructions
├── data/                          # Test images (excluded from git for PII protection)
│   ├── role1.jpg                  # Face image for first configured role
│   ├── role2.jpeg                 # Face image for second configured role
│   ├── role3.jpeg                 # Face image for third configured role
│   ├── role4.jpeg                 # Face image for fourth configured role
│   └── default.jpg                # Default test image (fallback)
└── scripts/                       # Test scripts directory
    ├── test_devcontainer.py       # DevContainer environment validation
    ├── test_admin_apis.py          # Admin API endpoints testing
    ├── test_comprehensive_apis.py  # Complete workflow testing
    ├── test_enhanced_rag.py        # Enhanced RAG system testing
    ├── test_all_roles.py           # Multi-role face recognition testing
    ├── test_role_storage.py        # Role storage verification
    ├── debug_registration.py      # Registration process debugging
    ├── post_rebuild_check.py      # Post-rebuild verification
    ├── test_env_fallbacks.py      # Environment variable fallback testing
    └── validate_environment.py    # Environment validation utilities
```

## Test Scripts

### Comprehensive Testing
- **`test_comprehensive_apis.py`**: End-to-end workflow testing
  - Health endpoint validation
  - User registration with face images
  - Face-based authentication
  - Document upload and processing
  - AI chat functionality
  - Admin interface testing

- **`test_enhanced_rag.py`**: Enhanced RAG system testing
  - Multi-source data integration
  - Role-specific AI responses based on environment configuration
  - Document-aware conversations
  - Vector database operations
  - Configurable test cases based on defined roles

### Multi-Role Face Recognition
- **`test_all_roles.py`**: Tests all configured role types with unique faces
  - Dynamically reads roles from environment configuration
  - Tests each environment-specific role
  - Role-specific face image validation
  - Supports any number of roles defined in .env

- **`test_role_storage.py`**: Verifies role data persistence
  - ChromaDB role storage validation
  - User metadata verification
  - Role retrieval testing
  - Environment-agnostic role validation

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

### Run Comprehensive Test Suite
```bash
cd /workspaces/mimir-ai
python3 test/scripts/test_comprehensive_apis.py
```

### Run Enhanced RAG System Tests
```bash
cd /workspaces/mimir-ai
python3 test/scripts/test_enhanced_rag.py
```

### Test Multi-Role Face Recognition
```bash
cd /workspaces/mimir-ai
# Tests all roles defined in environment configuration
python3 test/scripts/test_all_roles.py
```

### Run All Environment Tests
```bash
cd /workspaces/mimir-ai
python3 test/scripts/test_devcontainer.py
```

### Run API Tests
```bash
cd /workspaces/mimir-ai
python3 test/scripts/test_admin_apis.py
```

### Debug Registration Issues
```bash
cd /workspaces/mimir-ai
python3 test/scripts/debug_registration.py
```

### Verify Role Storage
```bash
cd /workspaces/mimir-ai
python3 test/scripts/test_role_storage.py
```

### Verify Post-Rebuild Setup
```bash
cd /workspaces/mimir-ai
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

⚠️ **Test images contain PII and are excluded from git tracking for security.**

### Required Test Images (stored in `test/data/`)

The test images should correspond to the roles defined in your environment configuration:

- **`role1.jpg`**: Face image for first configured role
- **`role2.jpeg`**: Face image for second configured role  
- **`role3.jpeg`**: Face image for third configured role
- **`role4.jpeg`**: Face image for fourth configured role
- **`default.jpg`**: Default face image for basic testing (fallback)

### Environment Configuration

Roles are defined in your `.env` file using environment variables:

```bash
# Example role configuration
MIMIR_ROLES=human,analyst,leadership,admin
# or
MIMIR_ROLES=doctor,nurse,administrator,patient
# or any custom roles for your specific use case
```

### Dynamic Role Setup

1. **Configure roles** in your `.env` file based on your specific use case
2. **Create test images** with naming convention matching your roles
3. **Ensure each role** has a unique person's face for proper testing
4. **Default role** is "human" if no specific roles are configured

### Image Naming Convention

- Use role names as defined in `MIMIR_ROLES` environment variable
- Supported formats: `.jpg`, `.jpeg`, `.png`
- Fallback to `default.jpg` for any missing role images

### Setup Instructions

1. Create the `test/data/` directory if it doesn't exist
2. Add face images matching your configured role names
3. Ensure each role has a unique person's face for proper testing
4. See `test/TEST_DATA.md` for detailed setup instructions

### Security Note

The `data/` directory is excluded from git tracking via `.gitignore` to protect PII. Test images must be added locally and should never be committed to the repository.

## Test Results

### Current Status (All Passing ✅)

- **Comprehensive APIs**: 6/6 tests passing (100%)
- **Enhanced RAG System**: Configurable test cases passing (100%)  
- **All Roles**: All environment-configured roles working correctly
- **Face Recognition**: Properly distinguishes between different users

### Environment-Specific Results

Test results adapt to your configured roles:
- Number of test cases scales with defined roles
- Role-specific AI responses validated per environment
- User isolation verified across all configured roles

## Framework Features

### Generic Role Configuration
- **Environment-driven**: Roles defined in `.env` configuration
- **Flexible deployment**: Same codebase works for any domain
- **Scalable testing**: Test suites adapt to any number of roles
- **Default fallback**: "human" role as universal default

### Use Case Examples
- **Healthcare**: `doctor,nurse,administrator,patient`
- **Education**: `teacher,student,administrator,parent`  
- **Gaming**: `analyst-gaming,analyst-non-gaming,leadership-gaming,leadership-non-gaming`
- **Corporate**: `employee,manager,executive,contractor`
- **Generic**: `human` (default single-role deployment)

## Notes

- All test scripts are designed to work with both devcontainer and production environments
- Environment variables are automatically detected and used appropriately
- Tests validate persistent storage functionality across container rebuilds
- Face recognition tests require role-specific images in `test/data/`
- Multi-role testing ensures proper user isolation and role-based access control
- Enhanced RAG tests verify document-aware AI responses with role-specific context
- **Framework is domain-agnostic**: Configure any roles for any use case
- **Test suites dynamically adapt**: To the number and types of roles configured
