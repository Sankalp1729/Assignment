import fs from 'fs';
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { PDFParse } = require('pdf-parse');

async function main() {
    console.log("Loading Sample_Report.pdf...");
    const sampleBuffer = fs.readFileSync('c:/Users/Sanjay Das/Desktop/Urbanroof/Sample_Report.pdf');
    const sampleParser = new PDFParse({ data: sampleBuffer });
    
    console.log("Extracting text from Sample_Report.pdf...");
    const sampleTextResult = await sampleParser.getText();
    fs.writeFileSync('c:/Users/Sanjay Das/Desktop/Urbanroof/Sample_Report_Text.txt', sampleTextResult.text);
    console.log("Text saved to Sample_Report_Text.txt");

    console.log("Extracting images from Sample_Report.pdf...");
    const sampleImageResult = await sampleParser.getImage({ imageBuffer: true, imageDataUrl: false });
    console.log(`Extracted images from Sample_Report.pdf. Total pages processed:`, sampleImageResult.pages.length);
    let photoIndex = 1;
    const seenHashes = new Set();
    
    for (const pageInfo of sampleImageResult.pages) {
        const pageNum = pageInfo.pageNumber;
        const pageImages = pageInfo.images;
        
        let validOnPage = 0;
        pageImages.forEach((img) => {
            // Check if it is a photo (not logo banner)
            if (img.width > 200 && img.height > 200 && img.width !== 2099) {
                // Generate a simple hash of image data to avoid duplicates
                const hash = img.data.length + "_" + img.width + "_" + img.height;
                if (!seenHashes.has(hash)) {
                    seenHashes.add(hash);
                    validOnPage++;
                    console.log(`Saved photo_${photoIndex}.jpg (Page ${pageNum}, Size: ${img.data.length} bytes, Dim: ${img.width}x${img.height})`);
                    photoIndex++;
                }
            }
        });
        if (validOnPage > 0) {
            console.log(`Page ${pageNum} yielded ${validOnPage} unique photos.`);
        }
    }

    console.log("Loading Thermal_Images.pdf...");
    const thermalBuffer = fs.readFileSync('c:/Users/Sanjay Das/Desktop/Urbanroof/Thermal_Images.pdf');
    const thermalParser = new PDFParse({ data: thermalBuffer });

    console.log("Extracting text from Thermal_Images.pdf...");
    const thermalTextResult = await thermalParser.getText();
    fs.writeFileSync('c:/Users/Sanjay Das/Desktop/Urbanroof/Thermal_Images_Text.txt', thermalTextResult.text);
    console.log("Text saved to Thermal_Images_Text.txt");

    console.log("Extracting images from Thermal_Images.pdf...");
    const thermalImageResult = await thermalParser.getImage({ imageBuffer: true, imageDataUrl: false });
    console.log(`Extracted images from Thermal_Images.pdf. Total pages processed:`, thermalImageResult.pages.length);
    for (const pageInfo of thermalImageResult.pages) {
        const pageNum = pageInfo.pageNumber;
        const pageImages = pageInfo.images;
        console.log(`Page ${pageNum} has ${pageImages.length} images.`);
        pageImages.forEach((img, idx) => {
            console.log(`  Image ${idx}: ${img.name} (${img.width}x${img.height}), size: ${img.data ? img.data.length : 0} bytes`);
        });
    }

    await sampleParser.destroy();
    await thermalParser.destroy();
}

main().catch(console.error);

