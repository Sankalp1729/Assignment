'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface Report {
  success: boolean;
  document_id: string;
  total_observations: number;
  merged_observations: number;
  conflicts_found: number;
  report?: Record<string, unknown>;
  observations?: unknown[];
}

export default function DDRGenerator() {
  const [inspection, setInspection] = useState<File | null>(null);
  const [thermal, setThermal] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [backendConnected, setBackendConnected] = useState<boolean | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Test backend connection on component mount
  useEffect(() => {
    const checkConnection = async () => {
      const connected = await testBackendConnection();
      setBackendConnected(connected);
    };
    checkConnection();
  }, []);

  // 🔗 Test backend connection
  const testBackendConnection = async () => {
    try {
      console.log('Testing connection to backend:', API_URL);
      const response = await axios.get(`${API_URL}/health`, {
        timeout: 5000,
      });
      console.log('✅ Backend connection successful:', response.data);
      return true;
    } catch (err) {
      console.error('❌ Backend connection failed:', err);
      if (axios.isAxiosError(err)) {
        console.error('Error details:', {
          message: err.message,
          status: err.response?.status,
          data: err.response?.data,
        });
      }
      return false;
    }
  };

  // 🎯 Validation: Check file size
  const validateFile = (file: File): string | null => {
    const MAX_SIZE = 25 * 1024 * 1024; // 25MB
    if (file.size > MAX_SIZE) {
      return `File size exceeds 25MB limit. File size: ${(file.size / 1024 / 1024).toFixed(2)}MB`;
    }
    if (file.type !== 'application/pdf') {
      return 'Only PDF files are allowed';
    }
    return null;
  };

  // 📥 Handle file upload with validation
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, setter: (file: File | null) => void) => {
    const file = e.target.files?.[0];
    if (file) {
      // STEP 1: Debug file object immediately
      console.log('========== FILE SELECTED ==========');
      console.log('File object:', file);
      console.log('File name:', file.name);
      console.log('File size:', file.size, 'bytes');
      console.log('File type:', file.type);
      console.log('Is File object:', file instanceof File);
      console.log('===================================');
      
      const validationError = validateFile(file);
      if (validationError) {
        setError(`✗ ${validationError}`);
        return;
      }
      setError(null);
      setter(file);
      console.log('✓ File set successfully');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inspection || !thermal) {
      setError('✗ Please upload both inspection and thermal PDFs');
      return;
    }

    // Check backend connection first
    if (!backendConnected) {
      const connected = await testBackendConnection();
      if (!connected) {
        setError(`✗ Cannot connect to backend at ${API_URL}. Please check your internet connection and try again.`);
        return;
      }
    }

    // ★★★ STEP 1: CRITICAL DEBUG — Verify file objects ★★★
    console.log('\n========== STEP 1: FILE OBJECT VERIFICATION ==========');
    console.log('Inspection file object:');
    console.log('  Name:', inspection.name);
    console.log('  Size:', inspection.size, 'bytes');
    console.log('  Type:', inspection.type);
    console.log('  Is File:', inspection instanceof File);
    
    console.log('Thermal file object:');
    console.log('  Name:', thermal.name);
    console.log('  Size:', thermal.size, 'bytes');
    console.log('  Type:', thermal.type);
    console.log('  Is File:', thermal instanceof File);
    console.log('=====================================================\n');

    // Check for zero-size files
    if (inspection.size === 0 || thermal.size === 0) {
      setError('✗ One or more files are empty. Please upload valid PDFs.');
      console.error('ERROR: Zero-size file detected!');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // ★★★ STEP 3: Create FormData with filename parameter ★★★
      console.log('\n========== STEP 3: FORMDATA CREATION ==========');
      const formData = new FormData();
      formData.append('inspection', inspection, inspection.name);
      formData.append('thermal', thermal, thermal.name);
      console.log('FormData created successfully');
      console.log('FormData keys:', Array.from(formData.entries()).map(([k, v]) => `${k}: ${v instanceof File ? `File(${v.name}, ${v.size}B)` : v}`));
      console.log('========================================\n');

      console.log('Sending request to:', `${API_URL}/api/v1/generate-ddr`);

      // ★★★ STEP 4: Remove manual Content-Type header ★★★
      const response = await axios.post(
        `${API_URL}/api/v1/generate-ddr`,
        formData,
        {
          timeout: 300000, // 5 minutes
        }
      );

      console.log('API Response:', response.data);
      
      // ★★★ STEP 2: VERIFY DATA STRUCTURE ★★★
      console.log('\n========== STEP 2: VERIFY RESPONSE STRUCTURE ==========');
      const responseData = response.data;
      console.log('Response keys:', Object.keys(responseData));
      console.log('success:', responseData.success);
      console.log('document_id:', responseData.document_id);
      console.log('total_observations:', responseData.total_observations);
      console.log('merged_observations:', responseData.merged_observations);
      console.log('conflicts_found:', responseData.conflicts_found);
      console.log('report type:', typeof responseData.report);
      console.log('observations type:', typeof responseData.observations);
      console.log('observations length:', Array.isArray(responseData.observations) ? responseData.observations.length : 'NOT AN ARRAY');
      console.log('conflicts type:', typeof responseData.conflicts);
      console.log('conflicts length:', Array.isArray(responseData.conflicts) ? responseData.conflicts.length : 'NOT AN ARRAY');
      console.log('========================================\n');
      
      // ★★★ STEP 3: LOG SAMPLE DATA ★★★
      console.log('\n========== STEP 3: SAMPLE DATA ==========');
      if (Array.isArray(responseData.observations) && responseData.observations.length > 0) {
        console.log('First observation:', responseData.observations[0]);
      } else {
        console.log('No observations found in response!');
      }
      if (Array.isArray(responseData.conflicts) && responseData.conflicts.length > 0) {
        console.log('First conflict:', responseData.conflicts[0]);
      } else {
        console.log('No conflicts found in response!');
      }
      console.log('Report sample:', JSON.stringify(responseData.report).substring(0, 200));
      console.log('========================================\n');
      
      // Set all data correctly
      setReport(responseData);
      setError(null);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        console.error('\n========== API ERROR DETAILS ==========');
        console.error('Status:', err.response?.status);
        console.error('Status Text:', err.response?.statusText);
        console.error('Error Data:', err.response?.data);
        console.error('Error Message:', err.message);
        console.error('Error Code:', err.code);
        console.error('========================================\n');
        
        if (err.code === 'ECONNABORTED') {
          setError('✗ Request timeout. Backend is taking too long to respond.');
        } else if (err.response?.status === 422) {
          setError(`✗ Validation error: ${JSON.stringify(err.response?.data?.detail || 'Invalid request format')}`);
        } else if (err.response?.status === 500) {
          setError('✗ Backend error: Internal server error. Check that PDFs are valid.');
        } else if (err.response?.status === 0 || !err.response) {
          setError(`✗ Cannot reach backend. URL: ${API_URL}`);
        } else {
          setError(
            `✗ Error (${err.response?.status}): ${err.response?.data?.detail || err.message}`
          );
        }
      } else {
        console.error('Unexpected Error:', err);
        setError('✗ An unexpected error occurred');
      }
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  // 📥 Download Report as Text File
  const downloadReportAsText = () => {
    if (!report) return;

    const text = `AI DDR GENERATOR - DETAILED DIAGNOSTIC REPORT
═══════════════════════════════════════════════════════════════

DOCUMENT ID: ${report.document_id}
GENERATED: ${new Date().toLocaleString()}

SUMMARY
───────────────────────────────────────────────────────────────
Total Observations:     ${report.total_observations}
Merged Observations:    ${report.merged_observations}
Conflicts Found:        ${report.conflicts_found}

FULL REPORT
───────────────────────────────────────────────────────────────
${JSON.stringify(report.report, null, 2)}

OBSERVATIONS
───────────────────────────────────────────────────────────────
${JSON.stringify(report.observations, null, 2)}

═══════════════════════════════════════════════════════════════
Generated by AI DDR Generator
`;

    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `DDR_Report_${report.document_id}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 📋 Download Report as JSON
  const downloadReportAsJSON = () => {
    if (!report) return;

    const blob = new Blob([JSON.stringify(report, null, 2)], { 
      type: 'application/json;charset=utf-8' 
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `DDR_Report_${report.document_id}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  // 📋 Copy Document ID to clipboard
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // 🔄 Reset form
  const resetForm = () => {
    setInspection(null);
    setThermal(null);
    setReport(null);
    setError(null);
    setCopied(false);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Navigation */}
      <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold">🏠</span>
              </div>
              <h1 className="text-white font-bold text-lg">AI DDR Generator</h1>
            </div>
            <div className="flex items-center gap-4 text-sm">
              <div className="text-slate-400">
                API: <span className="font-mono text-blue-400">{API_URL}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${
                  backendConnected === true ? 'bg-green-500' :
                  backendConnected === false ? 'bg-red-500' :
                  'bg-yellow-500'
                }`} />
                <span className={`text-xs ${
                  backendConnected === true ? 'text-green-400' :
                  backendConnected === false ? 'text-red-400' :
                  'text-yellow-400'
                }`}>
                  {backendConnected === true ? '✓ Connected' :
                   backendConnected === false ? '✗ Disconnected' :
                   '⏳ Checking...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-white mb-4">
            Detailed Diagnostic Report Generator
          </h2>
          <p className="text-slate-400 text-lg">
            Upload inspection and thermal imaging PDFs to generate comprehensive property analysis reports.
          </p>
        </div>

        {/* Upload Form */}
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Error Message */}
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* File Uploads */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Inspection PDF Upload */}
            <div>
              <label className="block text-white font-semibold mb-3">
                📝 Inspection Report (PDF)
              </label>
              <div className={`border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer ${
                inspection 
                  ? 'border-green-500 bg-green-500/5' 
                  : 'border-slate-600 hover:border-blue-500 hover:bg-blue-500/5'
              }`}
                   onClick={() => document.getElementById('inspection')?.click()}>
                <input
                  id="inspection"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => handleFileChange(e, setInspection)}
                  className="hidden"
                />
                <div className="text-center">
                  <div className="text-4xl mb-2">{inspection ? '✅' : '📄'}</div>
                  <p className="text-slate-300 font-medium">
                    {inspection ? inspection.name : 'Click to upload PDF'}
                  </p>
                  {inspection && (
                    <p className="text-green-400 text-sm mt-1">
                      ✓ {(inspection.size / 1024 / 1024).toFixed(2)}MB
                    </p>
                  )}
                  {!inspection && (
                    <p className="text-slate-500 text-sm mt-1">PDF only • Max 25MB</p>
                  )}
                </div>
              </div>
            </div>

            {/* Thermal PDF Upload */}
            <div>
              <label className="block text-white font-semibold mb-3">
                🌡️ Thermal Report (PDF)
              </label>
              <div className={`border-2 border-dashed rounded-lg p-8 transition-all cursor-pointer ${
                thermal 
                  ? 'border-green-500 bg-green-500/5' 
                  : 'border-slate-600 hover:border-blue-500 hover:bg-blue-500/5'
              }`}
                   onClick={() => document.getElementById('thermal')?.click()}>
                <input
                  id="thermal"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => handleFileChange(e, setThermal)}
                  className="hidden"
                />
                <div className="text-center">
                  <div className="text-4xl mb-2">{thermal ? '✅' : '🔥'}</div>
                  <p className="text-slate-300 font-medium">
                    {thermal ? thermal.name : 'Click to upload PDF'}
                  </p>
                  {thermal && (
                    <p className="text-green-400 text-sm mt-1">
                      ✓ {(thermal.size / 1024 / 1024).toFixed(2)}MB
                    </p>
                  )}
                  {!thermal && (
                    <p className="text-slate-500 text-sm mt-1">PDF only • Max 25MB</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={loading || !inspection || !thermal}
              className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105 disabled:hover:scale-100"
            >
              {loading ? (
                <span className="inline-flex items-center gap-2">
                  <svg className="w-5 h-5 animate-spin" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" strokeWidth="2" opacity="0.2" />
                    <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Processing...
                </span>
              ) : (
                '✨ Generate Report'
              )}
            </button>
            {report && (
              <button
                type="button"
                onClick={resetForm}
                className="bg-slate-700 hover:bg-slate-600 text-white font-bold py-3 px-6 rounded-lg transition-all"
              >
                ↻ Start New
              </button>
            )}
          </div>
        </form>

        {/* Results */}
        {report && (
          <div className="mt-12 space-y-8 animate-fade-in">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-all transform hover:scale-105">
                <p className="text-slate-400 text-sm mb-2">📊 Total Observations</p>
                <p className="text-4xl font-bold text-white">{report.total_observations}</p>
              </div>
              <div className="bg-gradient-to-br from-blue-900 to-slate-900 rounded-lg p-6 border border-blue-700 hover:border-blue-600 transition-all transform hover:scale-105">
                <p className="text-blue-300 text-sm mb-2">🔄 Merged Observations</p>
                <p className="text-4xl font-bold text-blue-400">{report.merged_observations}</p>
              </div>
              <div className="bg-gradient-to-br from-orange-900 to-slate-900 rounded-lg p-6 border border-orange-700 hover:border-orange-600 transition-all transform hover:scale-105">
                <p className="text-orange-300 text-sm mb-2">⚠️ Conflicts Found</p>
                <p className="text-4xl font-bold text-orange-400">{report.conflicts_found}</p>
              </div>
            </div>

            {/* Download Buttons */}
            <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg p-6 border border-slate-700">
              <h3 className="text-white font-bold text-lg mb-4">💾 Download Report</h3>
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={downloadReportAsText}
                  className="flex-1 min-w-[200px] bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                >
                  📄 Download as Text
                </button>
                <button
                  onClick={downloadReportAsJSON}
                  className="flex-1 min-w-[200px] bg-purple-600 hover:bg-purple-700 text-white font-bold py-2 px-4 rounded-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2"
                >
                  📋 Download as JSON
                </button>
              </div>
            </div>

            {/* Report Details */}
            <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 space-y-6">
              <h3 className="text-white font-bold text-2xl">📋 Report Details</h3>
              
              {/* Document ID with Copy */}
              <div className="bg-slate-900 rounded-lg p-4 border border-slate-700">
                <p className="text-slate-400 text-sm mb-2">🏷️ Document ID</p>
                <div className="flex items-center justify-between gap-4">
                  <p className="text-white font-mono text-lg break-all">{report.document_id}</p>
                  <button
                    onClick={() => copyToClipboard(report.document_id)}
                    className={`px-4 py-2 rounded-lg font-semibold whitespace-nowrap transition-all ${
                      copied
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                    }`}
                  >
                    {copied ? '✓ Copied' : '📋 Copy'}
                  </button>
                </div>
              </div>

              {/* Full Report */}
              {report.report && (
                <div>
                  <p className="text-slate-400 text-sm mb-3">📊 Full Report Analysis</p>
                  <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 overflow-auto max-h-96">
                    <pre className="text-slate-300 text-xs font-mono whitespace-pre-wrap break-words">
                      {JSON.stringify(report.report, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Observations */}
              {report.observations && report.observations.length > 0 && (
                <div>
                  <p className="text-slate-400 text-sm mb-3">
                    🔍 Observations ({report.observations.length})
                  </p>
                  <div className="bg-slate-900 rounded-lg p-4 border border-slate-700 overflow-auto max-h-96">
                    <pre className="text-slate-300 text-xs font-mono whitespace-pre-wrap break-words">
                      {JSON.stringify(report.observations, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Status */}
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <p className="text-green-400 flex items-center gap-2">
                  <span className="text-xl">✅</span>
                  Report successfully generated and ready for download
                </p>
              </div>
            </div>
          </div>
        )}

        {/* API Documentation Link */}
        <div className="mt-12 pt-8 border-t border-slate-700">
          <p className="text-slate-400 text-center">
            📚 <a 
              href={`${API_URL}/docs`} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              View API Documentation
            </a>
          </p>
        </div>
      </div>
    </main>
  );
}
