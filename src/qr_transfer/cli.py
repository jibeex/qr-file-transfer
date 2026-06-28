"""Command-line interface for qr-transfer."""

import argparse
import sys
from pathlib import Path

from qr_transfer import __version__
from qr_transfer.errors import QRTransferError


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qr-transfer",
        description="Air-gapped file transfer using animated QR codes.",
    )
    parser.add_argument("--version", action="version", version=f"qr-transfer {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # encode
    enc = sub.add_parser("encode", help="Encode a file into a QR code video.")
    enc.add_argument("input_file", help="Path to the file to encode.")
    enc.add_argument("output_video", help="Path for the output video file.")
    enc.add_argument("-g", "--grid-size", type=int, default=800, metavar="SIZE",
                     help="QR code grid size in modules (177–1000, default: 800).")
    enc.add_argument("-f", "--fps", type=int, default=10, metavar="RATE",
                     help="Video frame rate (5–30, default: 10).")
    enc.add_argument("--no-compress", action="store_true",
                     help="Skip gzip compression.")
    enc.add_argument("--anonymize-metadata", action="store_true",
                     help="Strip filename from metadata frame.")
    enc.add_argument("-q", "--quiet", action="store_true",
                     help="Suppress all progress output.")
    enc.add_argument("-v", "--verbose", action="store_true",
                     help="Enable verbose debug logging.")

    # decode
    dec = sub.add_parser("decode", help="Decode a QR video back to the original file.")
    dec.add_argument("input_video", help="Path to the recorded video.")
    dec.add_argument("output_file", help="Path for the decoded output file.")
    dec.add_argument("--force", action="store_true",
                     help="Overwrite output_file if it already exists.")
    dec.add_argument("--partial", action="store_true",
                     help="Write partial file even if some chunks are missing.")
    dec.add_argument("-q", "--quiet", action="store_true",
                     help="Suppress all progress output.")
    dec.add_argument("-v", "--verbose", action="store_true",
                     help="Enable verbose debug logging.")

    # verify
    ver = sub.add_parser("verify", help="Verify a QR video without decoding.")
    ver.add_argument("input_video", help="Path to the QR video to verify.")
    ver.add_argument("-d", "--detailed", action="store_true",
                     help="Show per-chunk information.")

    # info
    inf = sub.add_parser("info", help="Display metadata embedded in a QR video.")
    inf.add_argument("input_video", help="Path to the QR video.")

    # secure-delete
    sd = sub.add_parser("secure-delete", help="Securely overwrite and delete files.")
    sd.add_argument("files", nargs="+", metavar="file",
                    help="Files to securely delete.")

    return parser


def _cmd_encode(args: argparse.Namespace) -> None:
    from qr_transfer.core.encoder import FileEncoder

    encoder = FileEncoder(
        grid_size=args.grid_size,
        fps=args.fps,
        compression=not args.no_compress,
    )
    result = encoder.encode(
        input_path=args.input_file,
        output_path=args.output_video,
        anonymize_metadata=args.anonymize_metadata,
    )
    if not args.quiet:
        print(f"Encoded to {args.output_video} ({result.frames} frames, {result.duration:.1f}s)")


def _cmd_decode(args: argparse.Namespace) -> None:
    from qr_transfer.core.decoder import FileDecoder

    decoder = FileDecoder()
    result = decoder.decode(
        input_path=args.input_video,
        output_path=args.output_file,
        force=args.force,
    )
    if not args.quiet:
        print(f"Decoded to {args.output_file} ({result.file_size} bytes)")


def _cmd_verify(args: argparse.Namespace) -> None:
    from qr_transfer.core.decoder import FileDecoder

    decoder = FileDecoder()
    result = decoder.verify(input_path=args.input_video, detailed=args.detailed)
    print(f"{result.decoded_chunks}/{result.total_chunks} chunks found ({(result.decoded_chunks / result.total_chunks * 100) if result.total_chunks else 0.0:.1f}% complete)")
    if args.detailed and result.missing:
        print(f"Missing chunks: {result.missing}")


def _cmd_info(args: argparse.Namespace) -> None:
    from qr_transfer.core.decoder import FileDecoder

    decoder = FileDecoder()
    info = decoder.get_info(input_path=args.input_video)
    print(f"Filename:      {info.filename}")
    print(f"File size:     {info.file_size} bytes")
    print(f"Total chunks:  {info.total_chunks}")
    print(f"Compressed:    {info.compressed}")
    print(f"SHA-256:       {info.sha256}")
    print(f"Version:       {info.version}")


def _cmd_secure_delete(args: argparse.Namespace) -> None:
    from qr_transfer.utils.file_ops import FileOps

    for file_path in args.files:
        FileOps.secure_delete(Path(file_path))
        print(f"Securely deleted: {file_path}")


_DISPATCH = {
    "encode": _cmd_encode,
    "decode": _cmd_decode,
    "verify": _cmd_verify,
    "info": _cmd_info,
    "secure-delete": _cmd_secure_delete,
}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        _DISPATCH[args.command](args)
        sys.exit(0)
    except QRTransferError as e:
        print(e.format_user_message(), file=sys.stderr)
        sys.exit(e.error_code)
    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
