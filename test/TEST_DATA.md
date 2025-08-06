# Test Data Requirements

The `test/data/` directory contains test images for facial recognition testing but is excluded from git tracking for PII protection.

## Required Test Images

For the test scripts to work properly, you need to manually add the following face image files to `test/data/`:

- `analyst-gaming.jpg` - Face image for Analyst-Gaming role testing
- `analyst-non-gaming.jpeg` - Face image for Analyst-Non-Gaming role testing  
- `leadership-gaming.jpeg` - Face image for Leadership-Gaming role testing
- `leadership-non-gaming.jpeg` - Face image for Leadership-Non-Gaming role testing
- `login-test.jpg` - Default face image for basic testing (can be a copy of any of the above)

## Important Security Note

⚠️ **These image files contain PII and are intentionally excluded from git tracking via .gitignore rules.**

## Setup Instructions

1. Create the `test/data/` directory if it doesn't exist
2. Add 4-5 different face images with the names listed above
3. Ensure each role has a unique person's face for proper testing
4. Run the test scripts to verify functionality

The `data/` directory exclusion in .gitignore protects against accidentally committing sensitive test data.
