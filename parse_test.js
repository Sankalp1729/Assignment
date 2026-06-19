import fs from 'fs';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const pdf = require('pdf-parse');

console.log("PDFParse type:", typeof pdf.PDFParse);
console.log("PDFParse properties:", Object.getOwnPropertyNames(pdf.PDFParse));
console.log("PDFParse prototype properties:", Object.getOwnPropertyNames(pdf.PDFParse.prototype));




