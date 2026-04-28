# Release Roadmap Generator

Python script to generate a formatted Excel release/project roadmap.

## Features

- ✔ Creates structured roadmap table
- ✔ 12 features across 3 sprints (4 weeks each)
- ✔ Yellow highlighting for checkmarks (✔)
- ✔ Bold headers
- ✔ Center-aligned text
- ✔ Auto-adjusted column widths

## Installation

### Prerequisites
- Python 3.6+
- pip (Python package manager)

### Install Dependencies

```bash
pip install pandas openpyxl
```

## Usage

### Run the Script

```bash
python release_roadmap_generator.py
```

### Output

- **File:** `release_roadmap.xlsx`
- **Location:** Same directory as the script
- **Sheet:** "Roadmap"

## Data Structure

### Features (12 total)

1. Image Upload
2. Preprocessing
3. AI Prediction
4. Image Validation
5. Severity Detection
6. Recommendations
7. UI Improvements
8. Confidence Logic
9. Edge AI
10. History Tracking
11. Deployment
12. Maintenance

### Timeline

- **Sprint 1:** Weeks 1-4 (Proposal, Preprocessing, Core AI)
- **Sprint 2:** Weeks 1-4 (Features, Enhancements)
- **Sprint 3:** Weeks 1-4 (Edge AI, Deployment, Maintenance)

### Legend

- **✔** = Feature active during that week
- **Blank** = Feature not scheduled

## Excel Formatting

| Feature | Formatting |
|---------|-----------|
| Headers | Bold + Center-aligned |
| Checkmarks | Yellow background (#FFFF00) |
| All text | Center-aligned |
| Columns | Auto-width (max 20 chars) |

## File Structure

```
release_roadmap_generator.py     # Main script
release_roadmap.xlsx             # Generated output
README.md                         # This file
```

## Customization

Edit `release_roadmap_generator.py` to:

- Add/remove features (modify `roadmap_data['Feature']` list)
- Change timelines (modify sprint/week columns)
- Adjust colors (modify `yellow_fill` PatternFill)
- Modify formatting (adjust `bold_font`, `center_alignment`)

## Troubleshooting

### ModuleNotFoundError: No module named 'pandas'

```bash
pip install pandas openpyxl --upgrade
```

### File already exists error

Delete `release_roadmap.xlsx` before running again, or modify the filename in the script.

### Excel file won't open

Ensure you're using a compatible Excel version (2007+) that supports `.xlsx` format.

## Requirements Met

✅ Creates roadmap table with Feature + Sprint/Week columns  
✅ 12 features with specified timelines  
✅ Checkmarks (✔) represent completed weeks  
✅ Yellow fill highlighting for checkmarks  
✅ Bold headers  
✅ Auto-adjusted column widths  
✅ Center-aligned text  
✅ Exports to `release_roadmap.xlsx`  
✅ Includes usage instructions  

## License

This script is part of the DermaVision project.
