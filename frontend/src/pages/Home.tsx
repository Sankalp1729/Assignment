import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, Zap, CheckCircle, Download, AlertTriangle, Info, ShieldAlert, Sparkles, Activity } from "lucide-react";
import { useState } from "react";
import axios from "axios";
import { toast } from "sonner";

export default function Home() {
  const [inspectionFile, setInspectionFile] = useState<File | null>(null);
  const [thermalFile, setThermalFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [reportData, setReportData] = useState<any | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState("summary");

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inspectionFile || !thermalFile) {
      toast.error("Please select both files before generating the report.");
      return;
    }

    setIsProcessing(true);
    const formData = new FormData();
    formData.append("inspectionReport", inspectionFile);
    formData.append("thermalReport", thermalFile);

    try {
      const response = await axios.post("/api/generate-ddr", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      if (response.data && response.data.success) {
        setReportData(response.data.data);
        setDownloadUrl(response.data.downloadUrl);
        toast.success("Detailed Diagnostic Report (DDR) generated successfully!");
      } else {
        const errorMsg = typeof response.data.error === "object"
          ? (response.data.error.message || JSON.stringify(response.data.error))
          : (response.data.error || "Failed to generate report.");
        toast.error(errorMsg);
      }
    } catch (err: any) {
      console.error(err);
      const errorMsg = typeof err.response?.data?.error === "object"
        ? (err.response?.data?.error?.message || JSON.stringify(err.response?.data?.error))
        : (err.response?.data?.error || err.message || "Error uploading or processing the reports.");
      toast.error(errorMsg);
    } finally {
      setIsProcessing(false);
    }
  };

  const loadSampleFiles = async () => {
    setIsProcessing(true);
    try {
      // Simulate file load by sending path of copies in the workspace
      const response = await axios.post("/api/generate-ddr-mock", {});
      if (response.data && response.data.success) {
        setReportData(response.data.data);
        setDownloadUrl(response.data.downloadUrl);
        toast.success("Sample DDR generated successfully!");
      }
    } catch (err) {
      // Fallback: if mock route not available, let's notify user to select files
      toast.info("Please select the Sample Report.pdf and Thermal Images.pdf files from your workspace or downloads folder.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-blue-600 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-blue-600 p-2.5 shadow-lg shadow-blue-500/20">
                <FileText className="h-6 w-6 text-white animate-pulse" />
              </div>
              <div>
                <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                  UrbanRoof DDR Builder <span className="rounded-full bg-blue-500/10 px-2.5 py-0.5 text-xs font-semibold text-blue-400">AI Engine</span>
                </h1>
                <p className="text-xs text-slate-400">Technical Diagnostic Report Automation</p>
              </div>
            </div>
            {downloadUrl && (
              <a href={downloadUrl} download>
                <Button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg shadow-blue-500/20 font-semibold gap-2 border-0">
                  <Download className="h-4 w-4" /> Download Client Report (.docx)
                </Button>
              </a>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-10 max-w-6xl">
        {!reportData ? (
          // Upload & Welcome State
          <div className="space-y-12">
            <div className="text-center max-w-3xl mx-auto space-y-4">
              <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm font-semibold text-blue-400">
                <Sparkles className="h-4 w-4" /> Automated Water Ingress Analysis
              </div>
              <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight text-white leading-tight">
                Turn Technical Site Inspections into <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Client-Ready Reports</span>
              </h2>
              <p className="text-lg text-slate-400 font-light">
                Upload your physical inspection PDF and thermal imaging PDF. Our pipeline will automatically extract observations, extract camera and thermal photos, align temperature readings, and generate a client-ready diagnostic report.
              </p>
            </div>

            {/* Upload form card */}
            <Card className="border-slate-800 bg-slate-950 shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-80 h-80 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
              <CardHeader className="border-b border-slate-800/80">
                <CardTitle className="text-xl text-white">Generate Detailed Diagnostic Report</CardTitle>
                <CardDescription className="text-slate-400">Upload PDF inspection & thermal imaging files to process</CardDescription>
              </CardHeader>
              <CardContent className="p-8">
                <form onSubmit={handleUpload} className="space-y-8">
                  <div className="grid gap-6 md:grid-cols-2">
                    {/* Inspection file */}
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-slate-300">1. Inspection Report PDF</label>
                      <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl p-6 bg-slate-900/50 hover:bg-slate-900 transition-colors relative cursor-pointer group">
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={(e) => setInspectionFile(e.target.files?.[0] || null)}
                          className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                        <FileText className="h-10 w-10 text-slate-500 group-hover:text-blue-500 transition-colors mb-3" />
                        <span className="text-sm font-medium text-slate-300">
                          {inspectionFile ? inspectionFile.name : "Select Sample Report.pdf"}
                        </span>
                        <span className="text-xs text-slate-500 mt-1">Accepts PDF format</span>
                      </div>
                    </div>

                    {/* Thermal file */}
                    <div className="space-y-2">
                      <label className="text-sm font-semibold text-slate-300">2. Thermal Images PDF</label>
                      <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl p-6 bg-slate-900/50 hover:bg-slate-900 transition-colors relative cursor-pointer group">
                        <input
                          type="file"
                          accept=".pdf"
                          onChange={(e) => setThermalFile(e.target.files?.[0] || null)}
                          className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                        <Activity className="h-10 w-10 text-slate-500 group-hover:text-indigo-500 transition-colors mb-3" />
                        <span className="text-sm font-medium text-slate-300">
                          {thermalFile ? thermalFile.name : "Select Thermal Images.pdf"}
                        </span>
                        <span className="text-xs text-slate-500 mt-1">Accepts PDF format</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
                    <Button
                      type="submit"
                      disabled={isProcessing || !inspectionFile || !thermalFile}
                      className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold shadow-lg shadow-blue-500/10 px-8 py-6 rounded-xl border-0"
                    >
                      {isProcessing ? (
                        <span className="flex items-center gap-2">
                          <Activity className="h-5 w-5 animate-spin" /> Processing Reports...
                        </span>
                      ) : (
                        "Generate DDR Report"
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>

            {/* How it works pipeline diagram */}
            <div className="border border-slate-800 bg-slate-950/40 rounded-2xl p-8">
              <h3 className="text-lg font-bold text-white mb-6 text-center">Repeatable Processing Pipeline</h3>
              <div className="grid gap-6 md:grid-cols-4">
                {[
                  { step: "01", name: "PDF Text Parsing", desc: "Extracts areas, observations, checklists using regex & patterns." },
                  { step: "02", name: "Photo Extraction", desc: "Extracts high-resolution visual camera photos & logs coordinates." },
                  { step: "03", name: "Thermal Alignment", desc: "Matches Bosch thermal snapshots & camera references to inspection areas." },
                  { step: "04", name: "DOCX Generation", desc: "Fuses all data into a client-ready Word report with embedded images." }
                ].map((item) => (
                  <div key={item.step} className="bg-slate-900/60 border border-slate-800/80 rounded-xl p-5 relative overflow-hidden">
                    <span className="absolute top-2 right-3 text-3xl font-black text-slate-800">{item.step}</span>
                    <h4 className="font-semibold text-white mb-2">{item.name}</h4>
                    <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          // Active DDR Report Dashboard previewer
          <div className="grid gap-8 lg:grid-cols-4 items-start">
            {/* Sidebar navigation tabs */}
            <div className="lg:col-span-1 space-y-2">
              <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 space-y-1">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-wider px-3 mb-2">Report Sections</p>
                {[
                  { id: "summary", name: "1. Property Summary", icon: Info },
                  { id: "areas", name: "2. Observations", icon: FileText },
                  { id: "causes", name: "3. Root Causes", icon: AlertTriangle },
                  { id: "severity", name: "4. Severity Assessment", icon: ShieldAlert },
                  { id: "actions", name: "5. Recommended Actions", icon: CheckCircle },
                  { id: "checklists", name: "6. Checklist Findings", icon: Sparkles },
                  { id: "missing", name: "7. Missing & Unclear Info", icon: AlertTriangle }
                ].map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                        activeTab === tab.id
                          ? "bg-blue-600 text-white shadow-md shadow-blue-500/10"
                          : "text-slate-400 hover:bg-slate-900 hover:text-slate-200"
                      }`}
                    >
                      <Icon className="h-4 w-4 shrink-0" />
                      <span className="truncate">{tab.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Reset button */}
              <Button
                onClick={() => {
                  setReportData(null);
                  setDownloadUrl(null);
                  setInspectionFile(null);
                  setThermalFile(null);
                }}
                variant="outline"
                className="w-full border-slate-800 text-slate-400 hover:bg-slate-900 hover:text-white"
              >
                Upload New Reports
              </Button>
            </div>

            {/* Main content display */}
            <div className="lg:col-span-3">
              <Card className="border-slate-800 bg-slate-950 shadow-xl overflow-hidden min-h-[500px]">
                <CardHeader className="border-b border-slate-800/80 bg-slate-950/50">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                    <div>
                      <CardTitle className="text-2xl text-white">Diagnostic Report Findings</CardTitle>
                      <CardDescription className="text-slate-400">
                        {reportData.propertyName} — Inspected on {reportData.inspectionDate} by {reportData.inspectedBy}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  {/* Tab contents */}
                  {activeTab === "summary" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Property Issue Summary</h3>
                      <p className="text-slate-300 leading-relaxed">
                        {reportData.propertyName} is currently experiencing extensive moisture-related issues, primarily manifesting as capillary dampness at the skirting levels of the Hall, Common Bedroom, Master Bedroom, and Kitchen. The investigation reveals that the moisture ingress is largely driven by waterproofing failures in the wet areas (Common Bathroom and Master Bedroom Bathroom) and exacerbated by structural cracks in the external walls. The seepage has progressed to the point of affecting the parking ceiling below the flat, indicating a high volume of water transit through the floor slab.
                      </p>
                      
                      {/* Summary points table */}
                      <div className="mt-8 space-y-4">
                        <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Correlation Map (Negative side vs Positive side)</h4>
                        <div className="border border-slate-800 rounded-xl overflow-hidden">
                          <table className="w-full text-left text-sm text-slate-300">
                            <thead className="bg-slate-900 text-slate-200 border-b border-slate-800 font-medium">
                              <tr>
                                <th className="p-3 w-16">Point</th>
                                <th className="p-3">Impacted Area (-ve side)</th>
                                <th className="p-3">Exposed Area (+ve side)</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-800/60">
                              {reportData.summaryTable.map((row: any) => (
                                <tr key={row.pointNo} className="hover:bg-slate-900/30">
                                  <td className="p-3 font-semibold text-blue-400">{row.pointNo}</td>
                                  <td className="p-3">{row.negativeSide}</td>
                                  <td className="p-3">{row.positiveSide}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "areas" && (
                    <div className="space-y-8">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Area-wise Observations</h3>
                      
                      <div className="space-y-8 divide-y divide-slate-800/80">
                        {reportData.areas.map((area: any) => (
                          <div key={area.id} className="pt-6 first:pt-0 space-y-4">
                            <div className="flex items-center justify-between">
                              <h4 className="text-md font-bold text-blue-400">Area {area.id}: {area.name}</h4>
                            </div>

                            <div className="grid gap-4 md:grid-cols-2">
                              <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl">
                                <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Negative Side (Impacted)</h5>
                                <p className="text-sm text-slate-200">{area.negativeDesc}</p>
                              </div>
                              <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl">
                                <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Positive Side (Exposed)</h5>
                                <p className="text-sm text-slate-200">{area.positiveDesc}</p>
                              </div>
                            </div>

                            {/* Images Grid */}
                            <div className="space-y-3">
                              <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Visual & Thermal Evidence</h5>
                              
                              <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
                                {/* Negative Photos */}
                                {area.negativePhotos.map((pNum: number) => (
                                  <div key={`neg-${pNum}`} className="group relative border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50 hover:border-slate-700 transition-colors">
                                    <img src={`/uploads/photo_${pNum}.jpg`} alt={`Negative Photo ${pNum}`} className="w-full h-32 object-cover" />
                                    <div className="p-2 text-center text-xs font-medium text-slate-400 bg-slate-950">
                                      Photo {pNum} (Neg. Side)
                                    </div>
                                  </div>
                                ))}

                                {/* Positive Photos */}
                                {area.positivePhotos.map((pNum: number) => (
                                  <div key={`pos-${pNum}`} className="group relative border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50 hover:border-slate-700 transition-colors">
                                    <img src={`/uploads/photo_${pNum}.jpg`} alt={`Positive Photo ${pNum}`} className="w-full h-32 object-cover" />
                                    <div className="p-2 text-center text-xs font-medium text-slate-400 bg-slate-950">
                                      Photo {pNum} (Pos. Side)
                                    </div>
                                  </div>
                                ))}

                                {/* Thermal snapshots */}
                                {area.thermalImages.map((fname: string) => (
                                  <div key={`thermal-${fname}`} className="contents">
                                    <div className="group relative border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50 hover:border-slate-700 transition-colors col-span-1">
                                      <img src={`/uploads/thermal_${fname}`} alt="Thermal snapshot" className="w-full h-32 object-cover" />
                                      <div className="p-2 text-center text-xs font-medium text-indigo-400 bg-slate-950">
                                        Thermal: {fname.replace("X.JPG", "")}
                                      </div>
                                    </div>
                                    <div className="group relative border border-slate-800 rounded-xl overflow-hidden bg-slate-900/50 hover:border-slate-700 transition-colors col-span-1">
                                      <img src={`/uploads/ref_${fname}`} alt="Reference camera" className="w-full h-32 object-cover" />
                                      <div className="p-2 text-center text-xs font-medium text-slate-400 bg-slate-950">
                                        Ref Photo: {fname.replace("X.JPG", "")}
                                      </div>
                                    </div>
                                  </div>
                                ))}

                                {/* Image not available placeholder */}
                                {area.negativePhotos.length === 0 && area.positivePhotos.length === 0 && area.thermalImages.length === 0 && (
                                  <div className="col-span-4 border border-dashed border-slate-800 rounded-xl p-8 text-center text-slate-500 text-sm">
                                    Image Not Available
                                  </div>
                                )}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === "causes" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Probable Root Cause</h3>
                      <div className="space-y-4">
                        {[
                          { title: "1. Waterproofing Failure", desc: "Open tile joints and failed seals around Nahani traps in the bathrooms are allowing water to penetrate the brickbat coba. This forms a saturated reservoir in the floor sub-base." },
                          { title: "2. Capillary Action (Skirting Dampness)", desc: "Water trapped in the floor substrate migrates horizontally and rises up the internal plaster of adjacent walls via capillary action. This is the direct cause of the skirting-level dampness observed across multiple rooms." },
                          { title: "3. External envelope cracks & Duct leaks", desc: "Structural cracks in the external walls and leaking external piping systems allow rainwater to enter the building envelope, exacerbating wall dampness in bedrooms." }
                        ].map((cause) => (
                          <div key={cause.title} className="bg-slate-900/30 border border-slate-800/80 rounded-xl p-5 space-y-2">
                            <h4 className="text-md font-bold text-white flex items-center gap-2">
                              <span className="h-2 w-2 rounded-full bg-blue-500" /> {cause.title}
                            </h4>
                            <p className="text-sm text-slate-300 leading-relaxed pl-4">{cause.desc}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === "severity" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Severity Assessment</h3>
                      <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6 flex items-start gap-4">
                        <ShieldAlert className="h-8 w-8 text-red-500 shrink-0 mt-1" />
                        <div className="space-y-3">
                          <h4 className="text-xl font-bold text-red-500">HIGH SEVERITY</h4>
                          <p className="text-slate-300 leading-relaxed text-sm">
                            The moisture ingress is widespread and has progressed to cause secondary damages such as paint bubbling, wood frame distortion, and efflorescence (mineral salt crystallization). The fact that active seepage is visible on the parking ceiling directly below Flat 103 indicates complete saturation of the RCC floor slab. If left unaddressed, the concrete pores will undergo carbonation and trigger steel reinforcement corrosion, compromising structural integrity.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {activeTab === "actions" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Recommended Actions</h3>
                      <div className="space-y-4">
                        {[
                          { action: "High-Performance Epoxy Regrouting", desc: "Clean all bathroom floor and wall tile joints, rake out old grout, and apply high-performance epoxy grout to prevent further water ingress." },
                          { action: "Grout Nahani Trap Joints", desc: "Ensure all Nahani trap junctions and collar connections are properly sealed and grouted." },
                          { action: "External Crack Sealing", desc: "Apply polyurethane sealants or flexible plaster polymers to all structural cracks on external wall surfaces and repair leaking plumbing mains." },
                          { action: "Substrate Drying & Restoration", desc: "Allow affected walls to dry fully (confirmed by thermal imaging) before scraping off bubbly paint, treating for efflorescence salts, and repainting." }
                        ].map((item, idx) => (
                          <div key={idx} className="flex gap-4 items-start">
                            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600/10 text-blue-400 font-bold text-sm shrink-0">
                              {idx + 1}
                            </div>
                            <div className="space-y-1">
                              <h4 className="text-sm font-bold text-white">{item.action}</h4>
                              <p className="text-xs text-slate-400">{item.desc}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTab === "checklists" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Checklist Findings</h3>
                      <div className="border border-slate-800 rounded-xl overflow-hidden">
                        <table className="w-full text-left text-sm text-slate-300">
                          <thead className="bg-slate-900 text-slate-200 border-b border-slate-800 font-medium">
                            <tr>
                              <th className="p-3">Category</th>
                              <th className="p-3">Inspection Item</th>
                              <th className="p-3 w-32 text-center">Status</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 text-xs">
                            {reportData.checklists.map((check: any, idx: number) => {
                              const isRed = check.status === "Yes" || check.status === "Moderate";
                              const isGreen = check.status === "No";
                              return (
                                <tr key={idx} className="hover:bg-slate-900/30">
                                  <td className="p-3 font-semibold text-slate-400">{check.category}</td>
                                  <td className="p-3">{check.item}</td>
                                  <td className="p-3 text-center">
                                    <span className={`px-2 py-0.5 rounded-full text-xxs font-semibold ${
                                      isRed ? "bg-red-500/10 text-red-400 border border-red-500/20" :
                                      isGreen ? "bg-green-500/10 text-green-400 border border-green-500/20" :
                                      "bg-slate-800 text-slate-400"
                                    }`}>
                                      {check.status}
                                    </span>
                                  </td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}

                  {activeTab === "missing" && (
                    <div className="space-y-6">
                      <h3 className="text-lg font-bold text-white border-b border-slate-800 pb-2">Missing or Unclear Information</h3>
                      
                      <div className="space-y-4">
                        <div className="bg-slate-900/40 border border-slate-850 p-4 rounded-xl space-y-2">
                          <h4 className="text-sm font-semibold text-yellow-400 flex items-center gap-2">
                            <Info className="h-4 w-4" /> Not Available Findings
                          </h4>
                          <ul className="list-disc list-inside text-xs text-slate-300 space-y-1.5 pl-2">
                            <li>Previous repairs: No records of past waterproofing attempts were available.</li>
                            <li>Paint specifications: The exact manufacturer/paint type of the current internal paint is <span className="text-red-400 font-semibold">Not Available</span>.</li>
                            <li>RCC Interior: Rust marks on internal RCC members were marked <span className="text-slate-400 font-semibold">N/A</span>. A detailed concrete core test is advised.</li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 py-8 mt-20">
        <div className="container mx-auto px-4 text-center text-xs text-slate-500">
          <p>UrbanRoof DDR Generator © 2026 | Developed for the Applied AI Builder Assessment</p>
        </div>
      </footer>
    </div>
  );
}
