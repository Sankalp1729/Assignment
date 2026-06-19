import express from "express";
import { createServer } from "http";
import path from "path";
import { fileURLToPath } from "url";
import multer from "multer";
import fs from "fs";
import { parseReports } from "./pdfParser.js";
import { generateWordReport } from "./reportGenerator.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const server = createServer(app);

  app.use(express.json());

  // Configure uploads path
  const workspaceRoot = path.resolve(__dirname, "..");
  const uploadsDir = path.join(workspaceRoot, "uploads");
  if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
  }

  // Serve static files from uploads folder
  app.use("/uploads", express.static(uploadsDir));

  // Multer configuration
  const storage = multer.diskStorage({
    destination: (_req, _file, cb) => {
      cb(null, uploadsDir);
    },
    filename: (_req, file, cb) => {
      cb(null, `${Date.now()}_${file.originalname}`);
    }
  });
  const upload = multer({ storage });

  // API Route to Generate DDR
  app.post("/api/generate-ddr", upload.fields([
    { name: "inspectionReport", maxCount: 1 },
    { name: "thermalReport", maxCount: 1 }
  ]), async (req: any, res) => {
    try {
      const files = req.files as { [fieldname: string]: Express.Multer.File[] };
      if (!files || !files.inspectionReport || !files.thermalReport) {
        return res.status(400).json({ error: "Missing inspectionReport or thermalReport PDF files" });
      }

      const inspectionFile = files.inspectionReport[0];
      const thermalFile = files.thermalReport[0];

      console.log(`Processing reports: ${inspectionFile.path} and ${thermalFile.path}`);
      
      const ddrData = await parseReports(inspectionFile.path, thermalFile.path, uploadsDir);

      const wordFilename = `DDR_Report_${Date.now()}.docx`;
      const wordPath = path.join(uploadsDir, wordFilename);
      await generateWordReport(ddrData, uploadsDir, wordPath);

      // Clean up uploaded source files to save space
      try {
        fs.unlinkSync(inspectionFile.path);
        fs.unlinkSync(thermalFile.path);
      } catch (e) {
        console.error("Error deleting uploaded source files:", e);
      }

      return res.json({
        success: true,
        data: ddrData,
        downloadUrl: `/uploads/${wordFilename}`
      });
    } catch (error: any) {
      console.error("DDR generation failed:", error);
      return res.status(500).json({ error: error.message || "Failed to process files" });
    }
  });

  // Mock API Route to process pre-copied sample files automatically
  app.post("/api/generate-ddr-mock", async (_req, res) => {
    try {
      const inspectionPath = path.join(workspaceRoot, "Sample_Report.pdf");
      const thermalPath = path.join(workspaceRoot, "Thermal_Images.pdf");

      if (!fs.existsSync(inspectionPath) || !fs.existsSync(thermalPath)) {
        return res.status(400).json({ error: "Sample reports not found in the workspace root" });
      }

      console.log(`Processing sample reports: ${inspectionPath} and ${thermalPath}`);
      
      const ddrData = await parseReports(inspectionPath, thermalPath, uploadsDir);

      const wordFilename = `DDR_Report_Sample.docx`;
      const wordPath = path.join(uploadsDir, wordFilename);
      await generateWordReport(ddrData, uploadsDir, wordPath);

      return res.json({
        success: true,
        data: ddrData,
        downloadUrl: `/uploads/${wordFilename}`
      });
    } catch (error: any) {
      console.error("Sample DDR generation failed:", error);
      return res.status(500).json({ error: error.message || "Failed to process sample files" });
    }
  });

  // Serve static files from frontend/dist
  const staticPath = path.join(workspaceRoot, "frontend", "dist");

  app.use(express.static(staticPath));

  // Handle client-side routing - serve index.html for all routes
  app.get("*", (_req, res) => {
    res.sendFile(path.join(staticPath, "index.html"));
  });

  const port = process.env.PORT || 5000;

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
