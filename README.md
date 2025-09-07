📝 Resume Generator (Python + LaTeX)

A Python-based resume generator that uses Jinja2 templating with a LaTeX backend to produce professional PDF resumes automatically.  
This project makes it simple to take structured data (like name, education, skills, experience) and compile it into a polished resume.

---

🚀 Features
- Write your resume data once in Python (JSON-style dictionaries).
- Automatically renders into a LaTeX template.
- Compiles into a professional PDF.
- Customizable LaTeX template with Jinja2 variables.
- Supports sections like:
  - Education
  - Technical Skills
  - Work Experience
  - Projects
  - Contact Info

---

## 📦 Requirements
- Python 3.9+  
- [MiKTeX](https://miktex.org/) (Windows) or [TeX Live](https://www.tug.org/texlive/) (Linux/macOS) installed  
- Python packages:
  ```bash
  pip install jinja2
