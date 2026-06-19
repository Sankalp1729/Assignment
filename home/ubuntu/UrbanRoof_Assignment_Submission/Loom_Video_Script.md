# Loom Video Script: UrbanRoof AI DDR Workflow

**Duration:** 3–5 Minutes

---

## 1. Introduction (0:00 - 0:45)
- **Visual:** Show the "Detailed Diagnostic Report" on screen.
- **Script:** "Hi, I'm [Your Name]. Today I'm demonstrating the AI-driven workflow I built for UrbanRoof to automate the generation of Detailed Diagnostic Reports. The goal of this system is to take raw, technical data from site inspections and thermal imaging and turn it into a clear, professional, and actionable report for the client."

## 2. What was Built (0:45 - 1:30)
- **Visual:** Show the "System Design and Workflow" document.
- **Script:** "I've built a multi-stage pipeline. It starts by extracting data from two very different sources: the textual Inspection Report and the visual Thermal Report. The system doesn't just copy-paste; it logically merges them. For example, if an inspector notes dampness in the hall, the AI automatically finds the corresponding thermal image, extracts the coldspot temperature, and pairs them together to provide proof of the issue."

## 3. How it Works (1:30 - 2:45)
- **Visual:** Scroll through the "Merged Diagnostic Data" or the final "DDR".
- **Script:** "The core engine uses a reasoning layer to identify root causes. In this sample for Flat 103, the AI noticed that dampness in multiple rooms correlated with open tile joints in the bathrooms. It correctly identified 'capillary action' as the primary root cause. I've also built in strict guardrails: if information is missing, the system writes 'Not Available' instead of guessing, ensuring the report's integrity."

## 4. Limitations & Improvements (2:45 - 4:00)
- **Visual:** Show the "Limitations" section of the design document.
- **Script:** "Current limitations include the reliance on consistent photo ID mapping. To improve this, I would implement a computer vision model to automatically match site photos with thermal images based on visual features. I'd also look into a direct API integration with on-site inspection apps to generate these reports in real-time while the inspector is still on the property."

## 5. Conclusion (4:00 - 4:30)
- **Visual:** Back to the final DDR cover page.
- **Script:** "This system reduces the manual reporting time from hours to seconds while maintaining a high standard of accuracy and professionalism. Thanks for watching, and I'm looking forward to discussing how we can scale this at UrbanRoof."
