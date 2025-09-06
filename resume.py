import os
import subprocess
import shutil
from jinja2 import Environment, Template

# Configure Jinja2 with custom delimiters to avoid conflict with LaTeX
env = Environment(
    variable_start_string="<<",
    variable_end_string=">>"
)

# Helper to escape underscores in email for LaTeX
def escape_latex(text):
    # Escape all LaTeX special characters, & first!
    specials = [
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('_', r'\_'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\textasciitilde{}'),
        ('^', r'\textasciicircum{}'),
        ('\\', r'\textbackslash{}'),
    ]
    for char, escape in specials:
        text = text.replace(char, escape)
    return text

# Load LaTeX template with safer delimiters and fixed icon usage
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
    \small \faPhone~<< phone >>
    ~ \href{mailto:<< email >>}{\faEnvelope~\underline{<< email_latex >>}} ~
    \href{<< linkedin >>}{\faLinkedin~<< linkedin_text >>} ~
    \href{<< github >>}{\faGithub~<< github_text >>}
\end{center}

\section*{Education}
\textbf{<< education.institution >>} \hfill << education.dates >> \\
\textit{<< education.degree >>} \hfill << education.location >>

{% if experience %}
\section*{Experience}
{% for exp in experience %}
\textbf{<< exp.title >>} -- << exp.company >> \hfill << exp.dates >> \\
\textit{<< exp.location >>} \\
<< exp.description >> \\[4pt]
{% endfor %}
{% endif %}

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

\end{document}
"""

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

# Collect user data interactively
linkedin_text = get_input("LinkedIn display text", "LinkedIn")
linkedin_url = get_input("LinkedIn URL", "https://linkedin.com/in/johndoe")
github_text = get_input("GitHub display text", "GitHub")
github_url = get_input("GitHub URL", "https://github.com/johndoe")

# Experience and Projects
experience_entries = get_multientry(
    "Experience",
    {"company": "", "location": "", "dates": "", "description": ""}
)
project_entries = get_multientry(
    "Project",
    {"description": ""}
)

user_data = {
    "name": get_input("Full Name", "John Doe"),
    "address": get_input("Address", "123 Cyber Street, Melbourne"),
    "phone": get_input("Phone", "+61 400 000 000"),
    "email": get_input("Email", "john@example.com"),
    "linkedin_text": linkedin_text,
    "linkedin": linkedin_url,
    "github_text": github_text,
    "github": github_url,
    "experience": experience_entries,
    "projects": project_entries,
    "education": {
        "institution": get_input("Education Institution", "Monash University"),
        "degree": get_input("Degree", "Bachelor of IT, Major in Cybersecurity"),
        "location": get_input("Education Location", "Clayton, VIC"),
        "dates": get_input("Education Dates", "2025–2027")
    },
    "skills": {
        "languages": get_input("Programming Languages", "Python, Java, SQL"),
        "tools": get_input("Developer Tools", "Git, Docker, VS Code, Postman"),
        "frameworks": get_input("Frameworks", "Flask, Django, React")
    }
}

# Escape all user data for LaTeX, including lists of dicts
def escape_data(data):
    if isinstance(data, str):
        return escape_latex(data)
    elif isinstance(data, list):
        return [escape_data(item) for item in data]
    elif isinstance(data, dict):
        return {k: escape_data(v) for k, v in data.items()}
    else:
        return data

user_data = escape_data(user_data)
user_data["email_latex"] = user_data["email"]

# Render template
template = env.from_string(latex_template)
latex_content = template.render(**user_data)

with open("resume.tex", "w", encoding="utf-8") as f:
    f.write(latex_content)

# Compile to PDF
print("[*] Compiling LaTeX to PDF...")
if shutil.which("pdflatex") is None:
    print("[!] Error: 'pdflatex' not found. Please install a LaTeX distribution (e.g., MiKTeX or TeX Live) and ensure 'pdflatex' is in your PATH.")
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
        # Save log for debugging
        with open("latex_error.log", "wb") as logf:
            logf.write(e.stdout)
            logf.write(b"\n--- STDERR ---\n")
            logf.write(e.stderr)
        print("LaTeX error log saved to latex_error.log")
        print("Last 40 lines of log:")
        lines = e.stdout.decode(errors="ignore").splitlines()
        for line in lines[-40:]:
            print(line)

print("NOTE: Do not enter LaTeX commands or special characters unless you want them escaped (e.g., &, %, $, #, _, {, }, ~, ^, \\). They will be escaped automatically.")
