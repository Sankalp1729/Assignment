# Assignment Notes

Source: `/home/ubuntu/upload/Assignment.pdf`

## Overview
The assignment is for an **AI Generalist / Applied AI Builder** role and evaluates the candidate's ability to design an AI workflow that converts technical inspection data into a structured, client-ready report.

## Submission Requirements
The final submission is expected to include:

- Working output such as a project live link, repository, or screenshots
- A **3–5 minute Loom video** explaining:
  - What was built
  - How it works
  - Limitations
  - How it could be improved
- A single Google Drive folder link containing all required materials

## Core Task
Build an AI system that reads both of the following input document types and generates a **Main DDR (Detailed Diagnostic Report)**:

- Inspection Report (sample report): site observations and issue descriptions
- Thermal Report (thermal images document): temperature readings and thermal findings

## System Expectations
The system must:

- Extract relevant observations
- Combine information logically
- Avoid duplicate points
- Handle missing or conflicting details
- Present a clear client-friendly report

## Output Requirements for the DDR
The generated report must contain these sections:

1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing or Unclear Information (explicitly mention “Not Available” if needed)

## Image Handling Requirements
The system must extract **both textual observations and relevant images** from the provided documents.
Relevant images must be placed in the appropriate sections of the DDR.

Important image rules:

- Extract images directly from the source documents where relevant
- Place each image under the appropriate observation or section in the DDR
- Do not include unrelated images
- If an expected image is missing, mention **“Image Not Available.”**

## Important Rules
- Do not invent facts that are not present in the documents
- If information conflicts, explicitly mention the conflict
- If information is missing, write **“Not Available”**
- Use simple, client-friendly language
- Avoid unnecessary technical jargon
- The solution should generalize to similar reports, not just the sample files

## Evaluation Criteria
- Accuracy of extracted information
- Logical merging of inspection and thermal data
- Handling of missing/conflicting details
- Clarity of final DDR output
- System thinking and reliability (not UI design)

## Missing Inputs Needed From User
To complete the assignment properly, the following additional materials are still needed:

- The **Job Description (JD)**
- The actual **Inspection Report** sample document
- The actual **Thermal Report** sample document

Without the source inspection and thermal documents, the DDR system cannot be demonstrated on the required input set.

## Likely Deliverables To Prepare
- Completed DDR output based on the source documents
- Explanation of approach / system design
- Possibly code or a reproducible workflow
- Screenshots or working proof
- Loom script or speaking notes if needed

## Job Description Alignment Notes

Source: `/home/ubuntu/upload/JD.pdf`

The role is **AI ML Intern (Applied AI & Creative Systems)** at **UrbanRoof Private Limited**, based in **Pune**, with a preference for **on-site or hybrid work** and an emphasis on **immediate execution quality**.

The JD strongly emphasizes building **functional AI-driven systems** that solve real business problems rather than theoretical experimentation. The candidate is expected to design, prototype, and deploy usable solutions using AI tools, automation, APIs, and creative systems.

The most relevant expectations for this assignment are as follows:

| JD theme | Relevance to assignment |
| --- | --- |
| Build personalized AI agents | The DDR task should be framed as a task-specific AI workflow that reads documents, extracts observations, and produces structured outputs. |
| Prompting, memory, retrieval, and tool integrations | The solution should show structured prompting, controlled extraction, conflict handling, and possibly document/image extraction pipelines. |
| Rapid prototyping and coding | The deliverable should include a practical working prototype, not just a conceptual explanation. |
| API, workflow, and automation integration | If possible, the workflow should be modular and reproducible, showing system thinking beyond a one-off manual report. |
| Hallucination control and guardrails | This is directly aligned with the assignment rule to avoid inventing facts, flag conflicts, and mark missing data as “Not Available.” |
| End-to-end execution mindset | The final submission should include working output, documentation, and clear explanation of limitations and future improvements. |

The JD also highlights that UrbanRoof values **proof of work**, **real-world execution**, **curiosity with discipline**, and the ability to **explain outcomes, failures, and improvements**. Therefore, the assignment should be positioned as:

1. A practical AI document-processing workflow.
2. A reliable reporting pipeline with explicit safeguards.
3. A demonstrable prototype with clear limitations and improvement opportunities.

## Implication for Final Submission Strategy

To align with both the assignment and the JD, the final package should ideally include a working prototype or script, a sample DDR output, concise documentation of workflow logic, and a short explanation/script for the video walkthrough.

## Remaining Required Inputs

The task still cannot be fully executed without the actual source documents referenced by the assignment:

| Required input | Status |
| --- | --- |
| Assignment brief | Received |
| Job Description | Received |
| Inspection Report sample | Not yet provided |
| Thermal Report sample | Not yet provided |

Once the Inspection Report and Thermal Report are provided, the next step will be to design the extraction-and-merging workflow and generate the DDR deliverable.

