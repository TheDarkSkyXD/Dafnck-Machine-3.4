---
description: 
globs: 
alwaysApply: true
---
# Specialized AI Agents

This file contains specialized AI agents converted from the DafnckMachine agent system.
Each agent has specific expertise and can be invoked using @agent-name syntax.

## Usage
- MUST switch to a role agent if no role is specified; otherwise, the default agent @uber-orchestrator-agent will be used.
- Use @agent-name to invoke a specific agent
- Agents can collaborate with each other as specified in their connectivity
- Each agent has specialized knowledge and capabilities
- Agent detail can found on `cursor_agent/yaml-lib/<agent-name>/**/*.yaml`
- All documents created by agents need save on format `.md`, inside folder `.cursor/rules/02_AI-DOCS/GENERATE_BY_AI`, after create document, AI need be update document information to .cursor/rules/02_AI-DOCS/GENERATE_BY_AI/index.json
- Agent relative can update these document if needed
{
    document-(str): {
        name: str
        category: str
        description: str
        usecase: str
        task-id: str (actual Task ID or global)
        useby: [str] (list agent AI)
        created_at: ISOdate(format str),
        created_by: ISOdate(format str),
    }
}

## Available Agents

## @uber-orchestrator-agent

**🎩 Uber Orchestrator Agent (Talk with me)**

### Collaborates with:
- @development-orchestrator-agent
- @marketing-strategy-orchestrator
- @test-orchestrator-agent
- @swarm-scaler-agent
- @health-monitor-agent
- @devops-agent
- @system-architect-agent
- @security-auditor-agent
- @task-deep-manager-agent

---

## @nlu-processor-agent

**🗣️ NLU Processor Agent**

### Collaborates with:
- @elicitation-agent
- @uber-orchestrator-agent
- @idea-generation-agent

---

## @elicitation-agent

**💬 Requirements Elicitation Agent**

### Collaborates with:
- @nlu-processor-agent
- @compliance-scope-agent
- @idea-generation-agent

---

## @compliance-scope-agent

**📜 Compliance Scope Agent**

### Collaborates with:
- @elicitation-agent
- @compliance-testing-agent
- @security-auditor-agent

---

## @idea-generation-agent

**💡 Idea Generation Agent**

### Collaborates with:
- @coding-agent

---

## @idea-refinement-agent

**✨ Idea Refinement Agent**

### Collaborates with:
- @coding-agent

---

## @core-concept-agent

**🎯 Core Concept Agent**

### Collaborates with:
- @coding-agent

---

## @market-research-agent

**📈 Market Research Agent**

### Collaborates with:
- @idea-generation-agent
- @technology-advisor-agent
- @marketing-strategy-orchestrator

---

## @mcp-researcher-agent

**🔌 MCP Researcher Agent**

### Collaborates with:
- @technology-advisor-agent
- @mcp-configuration-agent
- @coding-agent

---

## @technology-advisor-agent

**🛠️ Technology Advisor Agent**

### Collaborates with:
- @system-architect-agent
- @security-auditor-agent
- @devops-agent
- @compliance-scope-agent
- @development-orchestrator-agent
- @task-planning-agent

---

## @system-architect-agent

**🏛️ System Architect Agent**

### Collaborates with:
- @prd-architect-agent
- @tech-spec-agent
- @coding-agent

---

## @branding-agent

**🎭 Branding Agent**

### Collaborates with:
- @coding-agent

---

## @design-system-agent

**🎨 Design System Agent**

### Collaborates with:
- @ui-designer-agent
- @branding-agent
- @prototyping-agent

---

## @ui-designer-agent

**🖼️ UI Designer Agent**

### Collaborates with:
- @design-system-agent
- @ux-researcher-agent
- @prototyping-agent

---

## @prototyping-agent

**🕹️ Prototyping Agent**

### Collaborates with:
- @coding-agent

---

## @design-qa-analyst

**🔍 Design QA Analyst**

### Collaborates with:
- @ui-designer-agent
- @ux-researcher-agent
- @compliance-testing-agent

---

## @ux-researcher-agent

**🧐 UX Researcher Agent**

### Collaborates with:
- @ui-designer-agent
- @design-system-agent
- @usability-heuristic-agent

---

## @tech-spec-agent

**⚙️ Technical Specification Agent**

### Collaborates with:
- @coding-agent

---

## @task-planning-agent

**📅 Task Planning Agent**

### Collaborates with:
- @uber-orchestrator-agent
- @prd-architect-agent
- @development-orchestrator-agent

---

## @prd-architect-agent

**📝 PRD Architect Agent**

### Collaborates with:
- @task-planning-agent
- @system-architect-agent
- @tech-spec-agent

---

## @mcp-configuration-agent

**🔧 MCP Configuration Agent**

### Collaborates with:
- @coding-agent

---

## @algorithmic-problem-solver-agent

**🧠 Algorithmic Problem Solver Agent**

### Collaborates with:
- @coding-agent

---

## @coding-agent

**💻 Coding Agent (Feature Implementation)**

### Collaborates with:
- @development-orchestrator-agent
- @code-reviewer-agent
- @tech-spec-agent

---

## @code-reviewer-agent

**🧐 Code Reviewer Agent**

### Collaborates with:
- @coding-agent
- @test-orchestrator-agent

---

## @documentation-agent

**📄 Documentation Agent**

### Collaborates with:
- @coding-agent
- @tech-spec-agent
- @knowledge-evolution-agent

---

## @development-orchestrator-agent

**🛠️ Development Orchestrator Agent**

### Collaborates with:
- @coding-agent
- @code-reviewer-agent
- @test-orchestrator-agent

---

## @test-case-generator-agent

**📝 Test Case Generator Agent**

### Collaborates with:
- @test-orchestrator-agent
- @functional-tester-agent
- @coding-agent

---

## @test-orchestrator-agent

**🚦 Test Orchestrator Agent**

### Collaborates with:
- @development-orchestrator-agent
- @functional-tester-agent
- @test-case-generator-agent

---

## @functional-tester-agent

**⚙️ Functional Tester Agent**

### Collaborates with:
- @test-orchestrator-agent
- @coding-agent

---

## @exploratory-tester-agent

**🧭 Exploratory Tester Agent**

### Collaborates with:
- @coding-agent

---

## @performance-load-tester-agent

**⏱️ Performance & Load Tester Agent**

### Collaborates with:
- @coding-agent

---

## @visual-regression-testing-agent

**🖼️ Visual Regression Testing Agent**

### Collaborates with:
- @coding-agent

---

## @uat-coordinator-agent

**🤝 UAT Coordinator Agent**

### Collaborates with:
- @coding-agent

---

## @lead-testing-agent

**🧪 Lead Testing Agent**

### Collaborates with:
- @coding-agent

---

## @compliance-testing-agent

**🛡️ Compliance Testing Agent**

### Collaborates with:
- @security-auditor-agent
- @test-orchestrator-agent
- @compliance-scope-agent

---

## @security-penetration-tester-agent

**🔐 Security & Penetration Tester Agent**

### Collaborates with:
- @security-auditor-agent
- @coding-agent

---

## @usability-heuristic-agent

**🧐 Usability & Heuristic Evaluation Agent**

### Collaborates with:
- @user-feedback-collector-agent
- @ux-researcher-agent
- @design-qa-analyst

---

## @adaptive-deployment-strategist-agent

**🚀 Adaptive Deployment Strategist Agent**

### Collaborates with:
- @devops-agent
- @health-monitor-agent
- @efficiency-optimization-agent

---

## @devops-agent

**⚙️ DevOps Agent**

### Collaborates with:
- @adaptive-deployment-strategist-agent
- @development-orchestrator-agent
- @security-auditor-agent

---

## @user-feedback-collector-agent

**🗣️ User Feedback Collector Agent**

### Collaborates with:
- @ux-researcher-agent
- @usability-heuristic-agent
- @analytics-setup-agent

---

## @efficiency-optimization-agent

**⏱️ Efficiency Optimization Agent**

### Collaborates with:
- @analytics-setup-agent
- @health-monitor-agent
- @knowledge-evolution-agent

---

## @knowledge-evolution-agent

**🧠 Knowledge Evolution Agent**

### Collaborates with:
- @documentation-agent
- @incident-learning-agent
- @efficiency-optimization-agent

---

## @security-auditor-agent

**🛡️ Security Auditor Agent**

### Collaborates with:
- @security-penetration-tester-agent
- @compliance-testing-agent
- @system-architect-agent

---

## @swarm-scaler-agent

**🦾 Swarm Scaler Agent**

### Collaborates with:
- @coding-agent

---

## @root-cause-analysis-agent

**🕵️ Root Cause Analysis Agent**

### Collaborates with:
- @coding-agent

---

## @remediation-agent

**🛠️ Remediation Agent**

### Collaborates with:
- @coding-agent

---

## @health-monitor-agent

**🩺 Health Monitor Agent**

### Collaborates with:
- @remediation-agent
- @root-cause-analysis-agent
- @incident-learning-agent
- @swarm-scaler-agent
- @devops-agent
- @performance-load-tester-agent
- @security-auditor-agent

---

## @incident-learning-agent

**📚 Incident Learning Agent**

### Collaborates with:
- @coding-agent

---

## @marketing-strategy-orchestrator

**📈 Marketing Strategy Orchestrator**

### Collaborates with:
- @campaign-manager-agent
- @content-strategy-agent
- @growth-hacking-idea-agent

---

## @campaign-manager-agent

**📣 Campaign Manager Agent**

### Collaborates with:
- @marketing-strategy-orchestrator
- @content-strategy-agent
- @social-media-setup-agent

---

## @content-strategy-agent

**📝 Content Strategy Agent**

### Collaborates with:
- @campaign-manager-agent
- @graphic-design-agent
- @seo-sem-agent

---

## @graphic-design-agent

**🎨 Graphic Design Agent**

### Collaborates with:
- @coding-agent

---

## @growth-hacking-idea-agent

**💡 Growth Hacking Idea Agent**

### Collaborates with:
- @marketing-strategy-orchestrator
- @coding-agent
- @analytics-setup-agent

---

## @video-production-agent

**🎬 Video Production Agent**

### Collaborates with:
- @coding-agent

---

## @analytics-setup-agent

**📊 Analytics Setup Agent**

### Collaborates with:
- @user-feedback-collector-agent
- @seo-sem-agent
- @efficiency-optimization-agent

---

## @seo-sem-agent

**🔍 SEO/SEM Agent**

### Collaborates with:
- @coding-agent

---

## @social-media-setup-agent

**📱 Social Media Setup Agent**

### Collaborates with:
- @coding-agent

---

## @community-strategy-agent

**🤝 Community Strategy Agent**

### Collaborates with:
- @coding-agent

---

## @project-initiator-agent

**🚀 Project Initiator Agent**

### Collaborates with:
- @coding-agent

---

## @task-deep-manager-agent

**🧠 Task Deep Manager Agent (Full Automation)**

### Collaborates with:
- @task-planning-agent
- @uber-orchestrator-agent
- @development-orchestrator-agent

---

## @debugger-agent

**🐞 Debugger Agent**

### Collaborates with:
- @coding-agent

---

## @task-sync-agent

**🔄 Task Sync Agent**

### Collaborates with:
- @task-planning-agent
- @uber-orchestrator-agent
- @task-deep-manager-agent

---

## @ethical-review-agent

**⚖️ Ethical Review Agent**

### Collaborates with:
- @coding-agent

---

## @workflow-architect-agent

**🗺️ Workflow Architect Agent**

### Collaborates with:
- @coding-agent

---

## @scribe-agent

**✍️ Scribe Agent**

### Collaborates with:
- @coding-agent

---

## @brainjs-ml-agent

**🧠 Brain.js ML Agent**

### Collaborates with:
- @coding-agent

---

## @deep-research-agent

**🔍 Deep Research Agent**

### Collaborates with:
- @coding-agent

---

