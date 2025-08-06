# Test Data Requirements

The `test/data/` directory contains test images for facial recognition testing but is excluded from git tracking for PII protection.

## Environment-Based Role Configuration

Roles are defined in your `.env` file and test images should match these roles:

```bash
# Example role configurations for different use cases:

# Healthcare environment
MIMIR_ROLES=doctor,nurse,administrator,patient
DEFAULT_ROLE=human

# Education environment  
MIMIR_ROLES=teacher,student,administrator,parent
DEFAULT_ROLE=human

# Gaming/Analytics environment
MIMIR_ROLES=Analyst-Gaming,Analyst-Non-Gaming,Leadership-Gaming,Leadership-Non-Gaming
DEFAULT_ROLE=human

# Corporate environment
MIMIR_ROLES=employee,manager,executive,contractor
DEFAULT_ROLE=human

# Simple/Generic environment
MIMIR_ROLES=human
DEFAULT_ROLE=human
```

## Dynamic Test Image Setup

For the test scripts to work properly, you need to add face image files to `test/data/` that correspond to your configured roles:

### Image Naming Convention

1. **Role-based naming**: Convert role names to safe filenames
   - Replace spaces with underscores: `Project Manager` → `project_manager`
   - Replace hyphens with underscores: `Analyst-Gaming` → `analyst_gaming`
   - Use lowercase: `Doctor` → `doctor`

2. **Supported formats**: `.jpg`, `.jpeg`, `.png`

3. **Fallback options**: 
   - `default.jpg` - Universal fallback image
   - `login-test.jpg` - Backward compatibility fallback

### Example Setup

For a healthcare environment with `MIMIR_ROLES=doctor,nurse,administrator,patient`:

```
test/data/
├── doctor.jpg              # Face image for doctor role
├── nurse.jpeg              # Face image for nurse role  
├── administrator.png       # Face image for administrator role
├── patient.jpg             # Face image for patient role
└── default.jpg             # Fallback image
```

For a gaming environment with `MIMIR_ROLES=Analyst-Gaming,Leadership-Gaming`:

```
test/data/
├── analyst_gaming.jpg      # Face image for Analyst-Gaming role
├── leadership_gaming.jpeg  # Face image for Leadership-Gaming role
└── default.jpg             # Fallback image
```

## Important Security Note

⚠️ **These image files contain PII and are intentionally excluded from git tracking via .gitignore rules.**

## Setup Instructions

1. **Configure your roles** in `.env` file using `MIMIR_ROLES`
2. **Create test images** following the naming convention above
3. **Ensure each role** has a unique person's face for proper testing
4. **Add fallback image** (`default.jpg`) for any missing role images
5. **Test the setup** by running role-specific test scripts

## Framework Benefits

- **Environment-specific**: Same codebase works for any domain
- **Scalable testing**: Test suites adapt to any number of roles  
- **Generic deployment**: Configure roles per environment
- **PII protection**: Images never committed to repository
- **Flexible naming**: Handles any role naming convention
