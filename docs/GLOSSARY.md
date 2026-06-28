# Glossary

**Owner**: Development Team  
**Review trigger**: When new domain terms are introduced  
Referenced by: [REQUIREMENTS.md](./REQUIREMENTS.md), [DESIGN.md](./DESIGN.md)

---

| Term | Definition |
|------|------------|
| Air-gapped | A computer system physically isolated from all networks (wired and wireless) |
| Chunk | A variable-size portion of file data (max 2800 bytes payload), preceded by a 20-byte binary header containing sequence number, total count, and CRC32 checksum |
| Grid size | The number of modules (black/white squares) along one side of a QR code (e.g., 800 means an 800×800 QR code) |
| Module | An individual black or white square in a QR code — the smallest unit of QR data |
| Frame | One QR code image in the output video sequence. Frame 0 is the metadata frame; all subsequent frames each encode one data chunk |
| Metadata frame | The first frame in a QR video; encodes file name, size, hash, chunk count, and transfer parameters |
| Encode | Convert a file into a QR code video suitable for display and camera capture |
| Decode | Convert a recorded QR code video back into the original file |
| Integrity | Assurance that data has not been altered, verified via cryptographic hash |
| Transfer speed | Effective data throughput of the full encode→display→capture→decode pipeline, measured in KB/sec |
| Chunk index | Zero-based sequence number identifying a chunk's position in the file |
| Magic bytes | A fixed 4-byte prefix (`QRFT`) at the start of every chunk, used to identify valid QR transfer data |
| Error correction level | A QR code parameter controlling how much data can be recovered if the code is partially obscured; this system uses level M (15% recovery capacity) |
| Cold storage | An air-gapped system used for long-term secure storage, typically with no running services |
