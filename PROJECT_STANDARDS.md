# Project Standards: Authentic, Human-Made Engineering

This document outlines the core engineering principles and standards followed throughout this DevOps internship project.

---

### 1. Coding Style
- Write straightforward, readable code that a Computer Science student with practical Python and DevOps knowledge can realistically develop, explain, and maintain.
- Prefer simple, effective solutions over unnecessary abstractions, complex design patterns, or overengineering.
- Use natural and descriptive filenames, variable names, function names, and commit messages.
- Add concise comments only when explaining non-obvious engineering decisions. Avoid commenting on every line.
- Avoid generic boilerplate, repetitive explanations, excessive defensive code, and unnecessary dependencies.
- Preserve the existing working application and its architecture unless a genuine technical issue requires modification.

---

### 2. Realistic Project Scope
- Keep the scope aligned with a practical 2-week internship project: Python Flask API, automated pytest testing, Docker containerization, Docker Compose orchestration, and GitHub Actions CI/CD to Docker Hub.
- Do not add Kubernetes, cloud infrastructure, monitoring platforms, microservices, or external tools merely to make the project look more complex.
- Introduce a tool or feature only when it solves a real problem and can be clearly defended during an interview.
- Follow sensible security, container hygiene, and testing practices. Authentic engineering means solid fundamentals, not careless implementation.

---

### 3. README and Documentation
- Document the project from the perspective of a student who actually designed, implemented, and tested the software.
- Explain the problem, tools, local setup, API endpoints, Docker commands, CI/CD pipeline, and reproduction steps in natural, clear English.
- Avoid marketing language, buzzwords (e.g., "enterprise-ready", "production-grade microservice platform"), excessive emojis, and unnecessary sections.
- Document only features and results that have been implemented and verified locally.
- Explicitly distinguish between local verification and pending remote actions (e.g., GitHub Actions runs, Docker Hub pushes).
- Never fabricate test logs, badges, or deployment claims.

---

### 4. Version Control & CI/CD Workflow
- Maintain a clean, maintainable GitHub Actions workflow appropriate for the application.
- Write descriptive commit messages that clearly explain the changes made.
- Do not rewrite or falsify Git history.
- Never commit credentials, tokens, local virtual environments (`.venv`), or cache files.

---

### 5. Understanding and Ownership
- Ensure every technical decision can be explained in plain English.
- Understand what each file does, why it exists, and how to demonstrate it live in an interview.
- Never claim automated or third-party work as manual work without understanding the underlying mechanism.

---

### 6. Final Quality Checks
Before declaring any phase or the final project complete, verify:
- No unused dependencies in `requirements.txt`.
- No duplicate code or extraneous files.
- No generic placeholder text or unsupported claims.
- No secrets or sensitive configuration committed.
- Documentation accurately reflects the current codebase and configuration.
