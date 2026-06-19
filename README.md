# UrbanRoof DDR Generator

A web-based prototype for automating the creation of **Detailed Diagnostic Reports (DDRs)** from inspection and thermal data. The application is designed to help teams turn raw technical inputs into a cleaner, more professional client-ready report workflow.

## Overview

UrbanRoof DDR Generator combines a modern frontend interface with a lightweight backend server to support the end-to-end report workflow:

- upload inspection and thermal inputs
- extract relevant observations and evidence
- correlate findings across multiple sources
- generate a structured DDR output for review

## Key Features

- Upload-driven workflow for report inputs
- AI-assisted reasoning for root-cause and severity analysis
- Professional, client-friendly report structure
- Image-aware processing flow for inspection and thermal evidence
- Clean React-based UI for demo and review use cases

## Project Structure

- `client/` — frontend React/Vite application
- `server/` — Express server for serving the app
- `shared/` — shared constants and utilities
- `home/ubuntu/UrbanRoof_Assignment_Submission/` — assignment notes and workflow documentation

## Tech Stack

- React + TypeScript
- Vite
- Tailwind CSS
- Express
- pnpm

## Prerequisites

- Node.js 18+
- pnpm

## Getting Started

1. Install dependencies:

   ```bash
   corepack pnpm install
   ```

2. Start the development server:

   ```bash
   corepack pnpm dev
   ```

3. Open the local URL shown by Vite in your browser.

## Available Scripts

- `corepack pnpm dev` — run the frontend development server
- `corepack pnpm build` — build the project for production
- `corepack pnpm preview` — preview the production build
- `corepack pnpm check` — run TypeScript checks

## Workflow Summary

1. Upload inspection and thermal reports.
2. Extract observations, images, and thermal evidence.
3. Correlate findings across the two inputs.
4. Generate a structured DDR for downstream use.

## Documentation

Additional project context and workflow notes are available in:

- [home/ubuntu/UrbanRoof_Assignment_Submission/System_Design_and_Workflow.md](home/ubuntu/UrbanRoof_Assignment_Submission/System_Design_and_Workflow.md)
- [home/ubuntu/UrbanRoof_Assignment_Submission/Detailed_Diagnostic_Report_Flat103.md](home/ubuntu/UrbanRoof_Assignment_Submission/Detailed_Diagnostic_Report_Flat103.md)
- [home/ubuntu/UrbanRoof_Assignment_Submission/assignment_notes.md](home/ubuntu/UrbanRoof_Assignment_Submission/assignment_notes.md)

## Notes

This repository currently includes a working frontend prototype and supporting documentation. The report-generation logic can be expanded further with deeper PDF/image-processing automation and more advanced validation rules.
