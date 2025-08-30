# The Resume Hub V0.5 (IN PROGRESS)

**Craft professional, polished resumes  — no LaTeX expertise required.**

The Resume Hub transforms your raw experiences into beautifully formatted, professional resumes. Simply input your information, and let our AI-powered tools handle the polishing and formatting while you focus on your content.

---

## **✨ Features**

### **🤖 AI-Powered Content Polishing**

- **About Me Enhancement**: Transform basic self-descriptions into compelling professional summaries
- **Education Section Refinement**: Highlight academic achievements with impactful language
- **Experience Optimization**: Revise job descriptions to emphasize accomplishments and key skills
- **Grammar & Style Checking**: Ensure error-free, professional language throughout

### **🎨 Automated LaTeX Generation**

- **Template-Based Formatting**: Beautiful, professional layouts without manual coding
- **Smart Content Fitting**: Intelligent spacing and organization that adapts to your content
- **Instant Preview**: See your formatted resume in real-time as you make changes
- **Export Ready**: Generate clean LaTeX code ready for compilation or further customization

### **⚡ Streamlined Workflow**

- **Section-by-Section Editing**: Focus on one part of your resume at a time
- **One-Click Polishing**: Enhance any section with AI assistance
- **Custom Sections**: Add specialized categories for your unique background

# Setup Instructions

1. Clone Repository

```bash
git clone https://github.com/AmyLu0828/the-resume-hub.git
```

```bash
cd the-resume-hub
```

1. Environment Configuration

```bash
cp .env.example .env
#Edit .env and add your OPENAI API Key
```

1. Install Dependencies

```bash
pip install -r requirements.txt
```

1. Start Services

```bash
#start ui
npm run dev

#start backend
cd backend
python main.py
```

# Project Structure

```bash
backend/
├── agents/           # AI agents for content polishing and LaTeX generation
├── models/           # Data models and schema definitions
├── services/         # Core business logic and application services
├── templates/        # LaTeX template files and styling assets
└── main.py           # FastAPI application entry point

src/
├── components/       # Reusable UI components
├── sections/         # Resume section components
├── types/            # TypeScript type definitions
├── hooks/            # Custom React hooks
├── index.css         # Global styles and CSS variables
└── main.tsx          # React application entry point
```