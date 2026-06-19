import fs from 'fs';
import path from 'path';
import {
  Document,
  Paragraph,
  TextRun,
  Packer,
  ImageRun,
  Table,
  TableRow,
  TableCell,
  HeadingLevel,
  WidthType,
  AlignmentType,
  BorderStyle,
  TableAnchorType
} from 'docx';
import { DDRData, ImpactedArea } from './pdfParser.js';

export async function generateWordReport(data: DDRData, uploadsDir: string, outputPath: string): Promise<void> {
  const sections: any[] = [];

  // Helper for headings
  const createHeading = (text: string, level: any) => {
    return new Paragraph({
      text,
      heading: level,
      spacing: { before: 240, after: 120 },
      keepWithNext: true
    });
  };

  // Helper for regular paragraphs
  const createParagraph = (text: string, bold = false) => {
    return new Paragraph({
      children: [
        new TextRun({
          text,
          bold,
          font: "Arial",
          size: 22 // 11pt
        })
      ],
      spacing: { after: 120 }
    });
  };

  // Title / Header
  const titleParagraph = new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 400, after: 200 },
    children: [
      new TextRun({
        text: "DETAILED DIAGNOSTIC REPORT (DDR)",
        bold: true,
        font: "Arial",
        size: 36 // 18pt
      })
    ]
  });

  // Metadata Table
  const metadataTable = new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: 25, type: WidthType.PERCENTAGE },
            children: [createParagraph("Property Name:", true)]
          }),
          new TableCell({
            width: { size: 75, type: WidthType.PERCENTAGE },
            children: [createParagraph(data.propertyName)]
          })
        ]
      }),
      new TableRow({
        children: [
          new TableCell({
            width: { size: 25, type: WidthType.PERCENTAGE },
            children: [createParagraph("Inspection Date:", true)]
          }),
          new TableCell({
            width: { size: 75, type: WidthType.PERCENTAGE },
            children: [createParagraph(data.inspectionDate)]
          })
        ]
      }),
      new TableRow({
        children: [
          new TableCell({
            width: { size: 25, type: WidthType.PERCENTAGE },
            children: [createParagraph("Inspected By:", true)]
          }),
          new TableCell({
            width: { size: 75, type: WidthType.PERCENTAGE },
            children: [createParagraph(data.inspectedBy)]
          })
        ]
      }),
      new TableRow({
        children: [
          new TableCell({
            width: { size: 25, type: WidthType.PERCENTAGE },
            children: [createParagraph("Floors:", true)]
          }),
          new TableCell({
            width: { size: 75, type: WidthType.PERCENTAGE },
            children: [createParagraph(data.floors)]
          })
        ]
      })
    ]
  });

  // Assemble document body paragraphs
  const children: any[] = [
    titleParagraph,
    createParagraph(""),
    metadataTable,
    createParagraph(""),
    new Paragraph({
      text: "------------------------------------------------------------------------------------------------------------------------",
      spacing: { after: 200 }
    })
  ];

  // 1. Property Issue Summary
  children.push(createHeading("1. Property Issue Summary", HeadingLevel.HEADING_1));
  children.push(
    createParagraph(
      `${data.propertyName} is currently experiencing extensive moisture-related issues, primarily manifesting as capillary dampness at the skirting levels of the Hall, Common Bedroom, Master Bedroom, and Kitchen. The investigation reveals that the moisture ingress is largely driven by waterproofing failures in the wet areas (Common Bathroom and Master Bedroom Bathroom) and exacerbated by structural cracks in the external walls. The seepage has progressed to the point of affecting the parking ceiling below the flat, indicating a high volume of water transit through the floor slab.`
    )
  );

  // 2. Area-wise Observations
  children.push(createHeading("2. Area-wise Observations", HeadingLevel.HEADING_1));

  for (const area of data.areas) {
    children.push(createHeading(`2.${area.id} ${area.name}`, HeadingLevel.HEADING_2));
    children.push(createParagraph(`• Negative Side Observation: ${area.negativeDesc}`, true));
    children.push(createParagraph(`• Positive Side Observation: ${area.positiveDesc}`, true));

    // Gather and append images
    const imageRuns: any[] = [];

    // Negative side photos
    area.negativePhotos.forEach(pNum => {
      const pPath = path.join(uploadsDir, `photo_${pNum}.jpg`);
      if (fs.existsSync(pPath)) {
        try {
          const imgBuffer = fs.readFileSync(pPath);
          imageRuns.push(new Paragraph({
            children: [
              new ImageRun({
                data: imgBuffer,
                transformation: { width: 180, height: 135 }
              }),
              new TextRun({ text: `\nPhoto ${pNum}: Negative Side`, font: "Arial", size: 16 })
            ],
            spacing: { before: 100, after: 100 },
            alignment: AlignmentType.CENTER
          }));
        } catch (e) {
          console.error(`Error reading photo_${pNum}.jpg:`, e);
        }
      }
    });

    // Positive side photos
    area.positivePhotos.forEach(pNum => {
      const pPath = path.join(uploadsDir, `photo_${pNum}.jpg`);
      if (fs.existsSync(pPath)) {
        try {
          const imgBuffer = fs.readFileSync(pPath);
          imageRuns.push(new Paragraph({
            children: [
              new ImageRun({
                data: imgBuffer,
                transformation: { width: 180, height: 135 }
              }),
              new TextRun({ text: `\nPhoto ${pNum}: Positive Side`, font: "Arial", size: 16 })
            ],
            spacing: { before: 100, after: 100 },
            alignment: AlignmentType.CENTER
          }));
        } catch (e) {
          console.error(`Error reading photo_${pNum}.jpg:`, e);
        }
      }
    });

    // Thermal images
    area.thermalImages.forEach(fname => {
      const tPath = path.join(uploadsDir, `thermal_${fname}`);
      const rPath = path.join(uploadsDir, `ref_${fname}`);
      
      // Add Thermal Snapshot
      if (fs.existsSync(tPath)) {
        try {
          const imgBuffer = fs.readFileSync(tPath);
          imageRuns.push(new Paragraph({
            children: [
              new ImageRun({
                data: imgBuffer,
                transformation: { width: 180, height: 135 }
              }),
              new TextRun({ text: `\nThermal Image: ${fname} (Hotspot/Coldspot)`, font: "Arial", size: 16 })
            ],
            spacing: { before: 100, after: 100 },
            alignment: AlignmentType.CENTER
          }));
        } catch (e) {
          console.error(`Error reading thermal_${fname}:`, e);
        }
      }

      // Add Reference Photo
      if (fs.existsSync(rPath)) {
        try {
          const imgBuffer = fs.readFileSync(rPath);
          imageRuns.push(new Paragraph({
            children: [
              new ImageRun({
                data: imgBuffer,
                transformation: { width: 180, height: 135 }
              }),
              new TextRun({ text: `\nReference Camera Photo`, font: "Arial", size: 16 })
            ],
            spacing: { before: 100, after: 100 },
            alignment: AlignmentType.CENTER
          }));
        } catch (e) {
          console.error(`Error reading ref_${fname}:`, e);
        }
      }
    });

    if (imageRuns.length > 0) {
      // Group images in a table layout or stack them in paragraphs
      imageRuns.forEach(imgRun => {
        children.push(imgRun);
      });
    } else {
      children.push(createParagraph("Image Not Available (Placeholder)", true));
    }
  }

  // 3. Probable Root Cause
  children.push(createHeading("3. Probable Root Cause", HeadingLevel.HEADING_1));
  children.push(createParagraph("Based on the visual observations and thermal anomalies, the diagnostic analysis identifies three primary root causes:"));
  children.push(createParagraph("1. Waterproofing Failure: Open tile joints and failed seals around Nahani traps in the bathrooms are allowing water to penetrate the brickbat coba."));
  children.push(createParagraph("2. Capillary Action: Water trapped in the floor substrate is migrating horizontally and rising up the internal walls via capillary action, manifesting at the skirting levels."));
  children.push(createParagraph("3. External Ingress: Structural cracks in the external walls and leaking external pipes are allowing rainwater to enter the building envelope."));

  // 4. Severity Assessment
  children.push(createHeading("4. Severity Assessment", HeadingLevel.HEADING_1));
  children.push(createParagraph("Severity Level: HIGH", true));
  children.push(
    createParagraph(
      "Reasoning: The moisture ingress is widespread and has begun to cause secondary damage such as efflorescence and paint failure. The fact that seepage is visible in the parking area below indicates that the floor slab is saturated, which could eventually lead to reinforcement corrosion if not addressed immediately."
    )
  );

  // 5. Recommended Actions
  children.push(createHeading("5. Recommended Actions", HeadingLevel.HEADING_1));
  children.push(createParagraph("1. Regrouting: All bathroom floor and wall tile joints should be cleaned and regrouted with high-performance epoxy grout."));
  children.push(createParagraph("2. Trap Sealing: Ensure all Nahani traps are properly sealed and grouted."));
  children.push(createParagraph("3. External Repair: Fill all external wall cracks with appropriate sealants and repair leaking external plumbing lines."));
  children.push(createParagraph("4. Internal Restoration: After the leaks are stopped and the walls have fully dried (monitored via thermal imaging), the internal surfaces should be scraped, treated for salts, and repainted."));

  // 6. Additional Notes
  children.push(createHeading("6. Additional Notes", HeadingLevel.HEADING_1));
  children.push(
    createParagraph(
      "The inspection was conducted during a period where leakage was reported as \"All time,\" suggesting a constant source such as a pressurized plumbing line or a saturated substrate rather than just intermittent usage."
    )
  );

  // 7. Missing or Unclear Information
  children.push(createHeading("7. Missing or Unclear Information", HeadingLevel.HEADING_1));
  children.push(createParagraph("- Previous Repairs: No records of past waterproofing attempts were available."));
  children.push(createParagraph("- Paint Specs: The exact manufacturer of the current internal paint is Not Available."));
  children.push(
    createParagraph(
      "- RCC Interior: Rust marks on internal RCC members were marked N/A; however, given the seepage volume, a more detailed structural check is advised during repairs."
    )
  );

  // Create the Document
  const doc = new Document({
    sections: [
      {
        properties: {},
        children: children
      }
    ]
  });

  // Pack the document and write it
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);
  console.log(`Word report generated at ${outputPath}`);
}

