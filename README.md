# ✨ ResumeAI

### Build. Customize. Impress.

> A modern, dynamic and user-friendly resume builder that helps job seekers create professional, ATS-friendly resumes using beautiful templates and an easy step-by-step workflow.

---

## 🌐 Overview

**ResumeAI** is a full-stack resume builder application designed to make professional resume creation simple, fast and accessible.

The application allows users to:

- Create an account
- Securely log in
- Build multiple resumes
- Choose from professional resume templates
- Enter personal, education, experience, project and skill information
- Preview resumes dynamically
- Edit existing resumes
- Search saved resumes
- Download resumes as PDF
- Manage resumes from a dedicated dashboard
- Manage profile information
- Delete resumes when no longer needed

The project combines a clean modern interface with a Flask backend and MongoDB Atlas database.

---

## 🎯 Why ResumeAI?

Creating a professional resume shouldn't require hours of formatting.

ResumeAI provides a structured workflow where users can focus on their **content and career information**, while the application handles the presentation.

### 💡 The goal

**Enter your information → Choose a template → Preview → Download → Apply**

---

## ✨ Key Features

### 🔐 Authentication

- User registration
- User login
- Email validation
- Duplicate email prevention
- Password confirmation during registration
- Login credential validation
- Flash messages for success and errors
- Session-based authentication
- Logout functionality

---

### 📊 Dashboard

The dashboard provides a centralized overview of the user's resume activity.

It includes:

- Personalized greeting
- Total resumes
- Most-used template
- Resume statistics
- Recently updated information
- Quick resume creation
- Navigation to all major sections

---

### 📄 Resume Builder

ResumeAI provides a structured resume-building workflow.

Users can enter:

- Personal information
- Professional title
- Contact information
- Professional summary
- Skills
- Education
- Work experience
- Projects
- Certifications
- Languages
- Additional information

The builder is designed to keep the resume creation process organized and easy to follow.

---

### 🎨 Resume Templates

ResumeAI includes multiple professionally designed templates.

| Template | Best For |
|---|---|
| 💼 Professional | Corporate jobs, placements and internships |
| ✨ Modern | Modern professionals and technology roles |
| 🎨 Creative | Designers and creative professionals |

Each template provides a different visual presentation while maintaining a professional resume structure.

---

### 👁️ Live Resume Preview

Users can preview their resume before downloading it.

The preview allows users to verify:

- Personal details
- Sections
- Formatting
- Template appearance
- Resume content

This helps users identify mistakes before submitting their resume.

---

### ✏️ Resume Management

The **My Resume** section allows users to manage all their created resumes from one place.

Users can:

- 🔍 Search resumes
- 👁️ Preview resumes
- ✏️ Edit resumes
- 📥 Download resumes
- 🗑️ Delete resumes
- ➕ Create new resumes

Users can maintain multiple resumes for different job roles.

---

### 📥 PDF Download

Users can download their completed resume as a PDF document.

This makes the resume ready for:

- Job applications
- Internship applications
- College placements
- Professional opportunities

---

### 👤 Profile Management

Users can manage their account information through the profile section.

The application maintains user-specific information and connects it with their resumes.

---

## 🖥️ Application Workflow

```text
                    ┌───────────────┐
                    │     Home      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Register/Login│
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   Dashboard   │
                    └───────┬───────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌───────────────┐       ┌───────────────┐
        │   Templates   │       │   My Resume   │
        └───────┬───────┘       └───────────────┘
                │
                ▼
        ┌───────────────┐
        │ Resume Builder│
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Resume Preview│
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │  PDF Download │
        └───────────────┘
