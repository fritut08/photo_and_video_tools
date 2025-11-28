const DJISRTParser = require('/app/parser/index.js');
const fs = require('fs');

if (process.argv.length !== 3) {
    console.error('Usage: node parse_srt.js <srt_file_path>');
    process.exit(1);
}

const srtPath = process.argv[2];
const srtContent = fs.readFileSync(srtPath, 'utf-8');
const parser = DJISRTParser(srtContent, srtPath);
const metadata = parser.rawMetadata();

if (!metadata || metadata.length === 0) {
    console.error('No metadata entries found in SRT file');
    process.exit(1);
}

const first = metadata[0];

if (!first.latitude || !first.longitude || !first.abs_alt) {
    console.error('Missing required fields (latitude, longitude, abs_alt) in first SRT entry');
    console.error(`Available fields: ${Object.keys(first).join(', ')}`);
    process.exit(1);
}

console.log(JSON.stringify({
    latitude: parseFloat(first.latitude),
    longitude: parseFloat(first.longitude),
    altitude: parseFloat(first.abs_alt)
}));
