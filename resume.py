import os
import subprocess
import shutil
from jinja2 import Environment, Template

# Configure Jinja2 with custom delimiters to avoid conflict with LaTeX
env = Environment(
    variable_start_string="<<",
    variable_end_string=">>"
)

# Function to escape LaTeX special characters
def latex_escape(s):
    if not isinstance(s, str):
        return s
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}'
    }
    for key, val in replacements.items():
        s = s.replace(key, val)
    return s

# Recursive function to escape nested data
def escape_data(data):
    if isinstance(data, str):
        return latex_escape(data)
    elif isinstance(data, list):
        return [escape_data(item) for item in data]
    elif isinstance(data, dict):
        return {k: escape_data(v) for k, v in data.items()}
    else:
        return data

# LaTeX template
latex_template = r"""
\documentclass[letterpaper,11pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage{fontawesome5}
\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    urlcolor=blue,
    linkcolor=black
}
\begin{document}

\begin{center}
    {\Huge \scshape << name >>} \\ \vspace{1pt}
    << address >> \\ \vspace{1pt}
    \small \faPhone~<< phone >> ~
    \href{mailto:<< email >>}{\faEnvelope~\url{<< email_latex >>}} ~
    \href{<< linkedin >>}{\faLinkedin~<< linkedin_text >>} ~
    \href{<< github >>}{\faGithub~<< github_text >>}
\end{center}

\section*{Education}
\textbf{<< education.institution >>} \hfill << education.dates >> \\
\textit{<< education.degree >>} \hfill << education.location >>

{% if projects %}
\section*{Projects}
{% for proj in projects %}
\textbf{<< proj.title >>} \\
<< proj.description >> \\[4pt]
{% endfor %}
{% endif %}

\section*{Technical Skills}
\textbf{Languages:} << skills.languages >> \\
\textbf{Developer Tools:} << skills.tools >> \\
\textbf{Frameworks:} << skills.frameworks >>

{% if achievements %}
\section*{Achievements}
\begin{itemize}
{% for ach in achievements %}
    \item << ach >>
{% endfor %}
\end{itemize}
{% endif %}

\end{document}
"""

# Helper functions for interactive input
def get_input(prompt, default=""):
    value = input(f"{prompt} [{default}]: ")
    return value.strip() if value.strip() else default

def get_multientry(section_name, fields):
    entries = []
    print(f"\nEnter {section_name} (leave title empty to finish):")
    while True:
        entry = {}
        title = get_input(f"{section_name} Title", "")
        if not title:
            break
        entry["title"] = title
        for field, default in fields.items():
            entry[field] = get_input(f"{section_name} {field.capitalize()}", default)
        entries.append(entry)
    return entries

def get_list(section_name):
    items = []
    print(f"\nEnter {section_name} (leave empty to finish):")
    while True:
        item = get_input(f"{section_name} Item", "")
        if not item:
            break
        items.append(item)
    return items

# Collect user data interactively
user_data = {
    "name": get_input("Full Name", "John Doe"),
    "address": get_input("Address", "123 Cyber Street, Melbourne"),
    "phone": get_input("Phone", "+61 400 000 000"),
    "email": get_input("Email", "john@example.com"),
    "linkedin_text": get_input("LinkedIn display text", "LinkedIn"),
    "linkedin": get_input("LinkedIn URL", "https://linkedin.com/in/johndoe"),
    "github_text": get_input("GitHub display text", "GitHub"),
    "github": get_input("GitHub URL", "https://github.com/johndoe"),
    "education": {
        "institution": get_input("Education Institution", "Monash University"),
        "degree": get_input("Degree", "Bachelor of IT, Major in Cybersecurity"),
        "location": get_input("Education Location", "Clayton, VIC"),
        "dates": get_input("Education Dates", "2025–2027")
    },
    "projects": get_multientry(
        "Project",
        {"description": ""}
    ),
    "skills": {
        "languages": get_input("Programming Languages", "Python, Java, SQL"),
        "tools": get_input("Developer Tools", "Git, Docker, VS Code, Postman"),
        "frameworks": get_input("Frameworks", "Flask, Django, React")
    },
    "achievements": get_list("Achievement")
}

# Escape all user data for LaTeX (except URLs and email used with \url{})
user_data_escaped = escape_data(user_data)
user_data_escaped["email_latex"] = user_data["email"]  # raw text is fine inside \url{}
user_data_escaped["linkedin"] = user_data["linkedin"]  # keep raw URL for \href{}
user_data_escaped["github"] = user_data["github"]      # keep raw URL for \href{}
user_data_escaped["linkedin_text"] = user_data["linkedin_text"]
user_data_escaped["github_text"] = user_data["github_text"]

# Render template
template = env.from_string(latex_template)
latex_content = template.render(**user_data_escaped)

# Save LaTeX file
with open("resume.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)

# Compile to PDF
print("[*] Compiling LaTeX to PDF...")
if shutil.which("pdflatex") is None:
    print("[!] Error: 'pdflatex' not found. Install MiKTeX or TeX Live and add to PATH.")
else:
    try:
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "resume.tex"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("[+] Resume generated: resume.pdf")
    except subprocess.CalledProcessError as e:
        print("[!] LaTeX compilation failed.")
        with open("latex_error.log", "wb") as logf:
            logf.write(e.stdout)
            logf.write(b"\n--- STDERR ---\n")
            logf.write(e.stderr)
        print("LaTeX error log saved to latex_error.log")
