# ResearchDownload Native Host

This repository contains a placeholder native messaging host for the
ResearchDownload browser extension.  The Python module
`native/researchdownload_host.py` exposes an entry point that should be
replaced with the real implementation that communicates with the
extension via standard input and output.

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
