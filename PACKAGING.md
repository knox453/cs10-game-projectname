# Packaging

## Mac

Run this on macOS:

```bash
bash package-mac.sh
```

Outputs:

- `dist/OneLongDay`
- `dist/OneLongDay.app`

## Windows

Run this on Windows:

```bat
package-windows.bat
```

Output:

- `dist\OneLongDay.exe`

PyInstaller builds for the operating system it is running on, so the Windows executable needs to be built on a Windows computer.
