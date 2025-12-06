# Edit & Review Feature - Documentation

## Overview

The Financial Document Parser now includes an **interactive editing feature** that allows users to review and modify extracted financial data before finalizing. This feature is available through both the web UI and the REST API.

## What's New

### 🎯 Key Features

1. **Interactive Data Editor**: Review extracted data in an editable table format
2. **Real-time Editing**: Click any cell to modify values
3. **Row Management**: Add or remove financial metrics as needed
4. **Version Control**: Save changes to the original file or create a new edited version
5. **Change Tracking**: View a comparison of original vs. edited data
6. **Validation**: Data is validated before saving

### 📱 User Interface (Streamlit)

The Streamlit UI now has **3 tabs** instead of 2:

#### Tab 1: Upload & Parse

- Upload PDF documents
- Select company
- Parse and extract data
- Preview extracted results

#### Tab 2: Review & Edit ⭐ **NEW**

- View all extracted data in an editable table
- Edit individual cells by clicking on them
- Add new rows with the "+" button
- Delete rows with the "×" button
- See the "Key" (identifier) and "Particular" (description) for each metric
- Compare original vs. modified data
- Two save options:
  - **💾 Save Changes**: Overwrites the original JSON file
  - **📄 Save as New**: Creates a new file with `-edited` suffix

#### Tab 3: View Results

- View final financial data
- Export to JSON, CSV, or Markdown
- See all generated files

### 🌐 API Endpoint

#### POST `/api/update-financial-data`

Updates the financial data JSON file with edited values.

**Endpoint**: `http://localhost:5000/api/update-financial-data`

**Method**: POST

**Content-Type**: application/json

**Request Body**:

```json
{
  "company_name": "BRITANNIA",
  "document_name": "Britannia Unaudited Q2 June 2026",
  "financial_data": [
    {
      "particular": "Sale of goods",
      "key": "sale_of_goods",
      "values": {
        "30.06.2025": "1000.00",
        "31.03.2025": "950.00",
        "30.06.2024": "900.00",
        "31.03.2025_Y": "3800.00"
      }
    },
    {
      "particular": "Other operating revenues",
      "key": "other_operating_revenues",
      "values": {
        "30.06.2025": "50.00",
        "31.03.2025": "45.00",
        "30.06.2024": "40.00",
        "31.03.2025_Y": "180.00"
      }
    }
  ],
  "create_new": false
}
```

**Parameters**:

- `company_name` (required): Company name (must be from supported list)
- `document_name` (required): Name of the document (without extension)
- `financial_data` (required): Array of financial metrics with values
- `create_new` (optional): Boolean, default `false`
  - `false`: Overwrites existing file
  - `true`: Creates new file with `-edited` suffix

**Success Response** (200):

```json
{
  "success": true,
  "message": "Financial data updated successfully",
  "file_path": "output/BRITANNIA_Britannia Unaudited Q2 June 2026/Britannia Unaudited Q2 June 2026-financial-data.json"
}
```

**Error Response** (400/500):

```json
{
  "success": false,
  "error": "Error message description"
}
```

## Usage Examples

### Example 1: Using the Streamlit UI

1. **Parse a document**:

   ```
   - Go to "Upload & Parse" tab
   - Upload PDF and click "Parse Document"
   ```

2. **Review and edit**:

   ```
   - Switch to "Review & Edit" tab
   - Click on any cell to edit
   - Modify values as needed
   ```

3. **Save changes**:
   ```
   - Click "💾 Save Changes" to update the original file
   - Or click "📄 Save as New" to keep both versions
   ```

### Example 2: Using the API with Python

```python
import requests
import json

# Your edited data
updated_data = {
    "company_name": "BRITANNIA",
    "document_name": "Britannia Unaudited Q2 June 2026",
    "financial_data": [
        {
            "particular": "Sale of goods (Updated)",
            "key": "sale_of_goods",
            "values": {
                "30.06.2025": "1050.00",
                "31.03.2025": "1000.00",
                "30.06.2024": "950.00",
                "31.03.2025_Y": "4000.00"
            }
        }
    ],
    "create_new": True  # Create new version
}

# Send update request
response = requests.post(
    "http://localhost:5000/api/update-financial-data",
    json=updated_data
)

result = response.json()
if result['success']:
    print(f"✅ Saved to: {result['file_path']}")
else:
    print(f"❌ Error: {result['error']}")
```

### Example 3: Using cURL

```bash
curl -X POST http://localhost:5000/api/update-financial-data \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "BRITANNIA",
    "document_name": "Britannia Unaudited Q2 June 2026",
    "financial_data": [
      {
        "particular": "Sale of goods",
        "key": "sale_of_goods",
        "values": {
          "30.06.2025": "1000.00",
          "31.03.2025": "950.00"
        }
      }
    ],
    "create_new": false
  }'
```

## File Structure

After editing, files are saved in the output directory:

```
output/
├── BRITANNIA_Britannia Unaudited Q2 June 2026/
│   ├── Britannia Unaudited Q2 June 2026-financial-data.json          # Original
│   ├── Britannia Unaudited Q2 June 2026-financial-data-edited.json   # Edited (if create_new=true)
│   ├── Britannia Unaudited Q2 June 2026-table-1.csv
│   ├── Britannia Unaudited Q2 June 2026-table-1.html
│   └── Britannia Unaudited Q2 June 2026-table-1.md
```

## Data Structure

### Financial Data Format

Each financial metric in the array has:

```json
{
  "particular": "Human-readable description",
  "key": "unique_identifier_key",
  "values": {
    "30.06.2025": "value1",
    "31.03.2025": "value2",
    "30.06.2024": "value3",
    "31.03.2025_Y": "value4"
  }
}
```

- **particular**: Description of the metric (e.g., "Sale of goods")
- **key**: Unique identifier (e.g., "sale_of_goods")
- **values**: Object with date keys and corresponding values

## Best Practices

### When to Edit

✅ **Good reasons to edit**:

- Correct OCR errors in numbers
- Fix misaligned column data
- Add missing financial metrics
- Adjust labels for clarity
- Remove duplicate entries

❌ **Avoid**:

- Changing fundamental company data without verification
- Removing required metrics specified in config
- Altering keys without updating downstream processes

### Workflow Recommendations

1. **Parse First**: Always parse the document first to get the initial extraction
2. **Review Carefully**: Check the "Review & Edit" tab for accuracy
3. **Make Corrections**: Edit any incorrect values
4. **Save Strategically**:
   - Use "Save Changes" for minor corrections
   - Use "Save as New" for major revisions or experimental edits
5. **Verify**: Check the "View Results" tab to confirm changes

### Version Control Tips

- Use `create_new: true` when:

  - Making experimental changes
  - Creating different versions for comparison
  - Preserving original for audit purposes

- Use `create_new: false` when:
  - Correcting obvious errors
  - Final version is ready
  - Overwriting draft data

## Error Handling

### Common Errors and Solutions

**Error**: "Company name not provided"

- **Solution**: Ensure `company_name` is included in the request

**Error**: "Unsupported company"

- **Solution**: Check the company name against the supported list

**Error**: "Financial data is required"

- **Solution**: Ensure the `financial_data` array is not empty

**Error**: "Results not found"

- **Solution**: Parse the document first before trying to edit

## Testing

Test the edit endpoint with the provided test script:

```bash
python test_edit_endpoint.py
```

This script includes:

- Basic update test
- Create new version test
- Error handling examples

## Security Considerations

⚠️ **Important Notes**:

1. **No Authentication**: The current implementation does not include authentication
2. **File Overwrite**: Be cautious when using `create_new: false`
3. **Input Validation**: The API validates company names but not all financial data
4. **File Permissions**: Ensure proper file permissions in the output directory

For production use, consider adding:

- User authentication
- Request rate limiting
- Audit logging
- Data validation rules
- Backup mechanisms

## Future Enhancements

Potential improvements for future versions:

- [ ] Undo/Redo functionality
- [ ] Edit history tracking
- [ ] Multiple user collaboration
- [ ] Automated validation rules
- [ ] Bulk edit operations
- [ ] Export diff/comparison reports
- [ ] Integration with Excel for editing
- [ ] Role-based access control
- [ ] Change approval workflow

## Support

For issues or questions:

1. Check the error message in the API response
2. Review the Flask API logs in the terminal
3. Verify the document was parsed successfully first
4. Consult the main README.md for general troubleshooting

## Summary

The edit feature provides a flexible way to review and correct extracted financial data:

✨ **Benefits**:

- Improve data accuracy
- Handle OCR errors
- Customize output
- Maintain version history
- Interactive user experience

🎯 **Use Cases**:

- Quality assurance review
- Manual data correction
- Custom reporting needs
- Training and validation
- Audit trail creation

---

**Remember**: Always verify edited data before using it for business decisions or reporting purposes.
