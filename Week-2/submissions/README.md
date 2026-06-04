# Submissions — Week 2

## How to Submit

1. Fork the repo
2. Create a folder: `submissions/your-name/`
3. Add your agent code inside it
4. Open a Pull Request

## Checklist

- [ ] Uses 2 real APIs (no hardcoded data)
- [ ] All tool inputs are Pydantic `BaseModel` subclasses
- [ ] Uses the `Tool` class pattern (not scattered functions)
- [ ] API errors handled — tool returns error string, doesn't crash
- [ ] Type hints on all functions and class attributes
- [ ] README shows 3 sample runs with output

## Folder Structure

```
submissions/your-name/
├── agent.py
├── requirements.txt
└── README.md    ← domain chosen + 3 sample outputs
```
