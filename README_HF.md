---
title: Cyber Risk Scenario Generator
emoji: 🛡️
colorFrom: red
colorTo: purple
sdk: gradio
sdk_version: 4.44.1
app_file: app_hf.py
pinned: false
---

# Cyber Risk Scenario Generator

A multi-agent AI system for cyber risk analysis using CrewAI.

## Features

- Upload IT environment documentation (PDF, DOCX, TXT)
- 5 specialized AI agents analyze your infrastructure
- Get prioritized CRITICAL and MONITOR risk categories

## Required Secrets

Configure these in your HuggingFace Space settings:

- `OPENAI_API_KEY` (required)
- `SERPER_API_KEY` (optional, for web search)
- `NVD_API_KEY` (optional, for CVE lookup)
- `LANGCHAIN_API_KEY` (optional, for tracing)
