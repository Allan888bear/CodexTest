# ResearchDownload Native Host

This repository contains a fully functioning native messaging host for
the ResearchDownload browser extension. The Python module
`native/researchdownload_host.py` implements the Chrome native messaging
protocol and provides a handful of diagnostic commands that are helpful
while integrating with the accompanying browser extension.

## Host commands

The reference host currently supports the following commands:

| Command        | Description |
| -------------- | ----------- |
| `ping`         | Responds with `{"type": "pong"}` and echoes the provided `payload`. |
| `echo`         | Returns the provided `payload` unchanged. |
| `get_version`  | Emits the host version string. |
| `get_manifest` | Returns the manifest JSON when the host was started with `--manifest`. |
| `shutdown`     | Acknowledges the request and terminates the host loop. |

Every successful response preserves a `requestId` field when it is
supplied in the incoming message. Errors are reported using
`{"type": "error", "error": {"code": ..., "message": ...}}` to make
debugging straightforward during extension development.

## Windows launcher

A Windows-friendly launcher is provided at
`native\dist\researchdownload_host.cmd`.  The script looks for a Python
interpreter (`py -3`, `py.exe`, or `python`) and delegates execution to
`native\researchdownload_host.py`.  This allows the native messaging
manifest to reference a concrete executable path without relying on
PowerShell.

## Installing the host on Windows

1. Open a PowerShell prompt.
2. From the root of the repository, run:

   ```powershell
   ./scripts/install-host-windows.ps1
   ```

   Pass `-Browser edge` if you want to install the manifest for Microsoft Edge
   instead of Chrome.

The installer copies `native/com.yourorg.researchdownload.json` to the
appropriate Native Messaging Hosts directory and rewrites the manifest's
`path` field to point at the resolved
`native\dist\researchdownload_host.cmd` launcher.

## Development notes

* The manifest stored in `native/com.yourorg.researchdownload.json` keeps a
  relative path (`native\\dist\\researchdownload_host.cmd`) so that the
  repository remains cross-platform.  The install script resolves the path to
  an absolute location during installation, ensuring that the JSON string
  contains correctly escaped backslashes for Windows.
* If you update `native/researchdownload_host.py`, rerun the install script to
  propagate the changes to the Windows Native Messaging Hosts directory.
* Execute `python -m unittest discover -s tests` from the repository root to
  run the automated tests that exercise the native messaging host command
  handling.
