import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { parseReports } from './server/pdfParser.ts';
import { generateWordReport } from './server/reportGenerator.ts';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function main() {
  const uploadsDir = path.resolve(__dirname, 'uploads');
  const inspectionPath = path.resolve(__dirname, 'Sample_Report.pdf');
  const thermalPath = path.resolve(__dirname, 'Thermal_Images.pdf');
  const outputPath = path.join(uploadsDir, 'DDR_Report_Sample.docx');

  console.log("=== Start Verification ===");
  console.log("Uploads Directory:", uploadsDir);
  console.log("Inspection PDF:", inspectionPath);
  console.log("Thermal PDF:", thermalPath);

  if (!fs.existsSync(inspectionPath)) {
    throw new Error("Missing Sample_Report.pdf in workspace root");
  }
  if (!fs.existsSync(thermalPath)) {
    throw new Error("Missing Thermal_Images.pdf in workspace root");
  }

  console.log("Running parseReports...");
  const ddrData = await parseReports(inspectionPath, thermalPath, uploadsDir);
  
  console.log("Report Metadata Extracted:");
  console.log(`- Property Name: ${ddrData.propertyName}`);
  console.log(`- Inspection Date: ${ddrData.inspectionDate}`);
  console.log(`- Inspected By: ${ddrData.inspectedBy}`);
  console.log(`- Number of Impacted Areas: ${ddrData.areas.length}`);
  console.log(`- Checklist Items: ${ddrData.checklists.length}`);
  console.log(`- Summary Table Rows: ${ddrData.summaryTable.length}`);

  console.log("Running generateWordReport...");
  await generateWordReport(ddrData, uploadsDir, outputPath);

  console.log("Verifying output files on disk...");
  const docExists = fs.existsSync(outputPath);
  console.log(`- DOCX Report Exists: ${docExists} (${docExists ? fs.statSync(outputPath).size : 0} bytes)`);

  const photo1Exists = fs.existsSync(path.join(uploadsDir, 'photo_1.jpg'));
  const photo64Exists = fs.existsSync(path.join(uploadsDir, 'photo_64.jpg'));
  console.log(`- photo_1.jpg Exists: ${photo1Exists}`);
  console.log(`- photo_64.jpg Exists: ${photo64Exists}`);

  const thermalImageExists = fs.existsSync(path.join(uploadsDir, 'thermal_RB02380X.JPG'));
  const refImageExists = fs.existsSync(path.join(uploadsDir, 'ref_RB02380X.JPG'));
  console.log(`- thermal_RB02380X.JPG Exists: ${thermalImageExists}`);
  console.log(`- ref_RB02380X.JPG Exists: ${refImageExists}`);

  console.log("=== Verification Successful! ===");
}

main().catch(err => {
  console.error("=== Verification Failed ===");
  console.error(err);
});

