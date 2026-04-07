# Setup Guide for The Ghost Hunter Fork

## Prerequisites

- Tweego (Twee/Twine compiler)
  - Download from: https://github.com/tmedwards/tweego
  - Or use the automated setup script below

## Quick Setup

### Automated Setup (Recommended)

Run the setup script to automatically download and install Tweego:

```bash
./setup.sh
```

This will:

1. Download Tweego 2.1.1 for Linux x64
2. Extract it to the appropriate directory
3. Make build scripts executable

### Manual Setup

If you prefer to set up Tweego manually:

1. Download Tweego from: https://github.com/tmedwards/tweego/releases
2. Extract the archive to the project root
3. Ensure the path in `build.sh` matches your Tweego location:
   - Default: `../tweego-2.1.1-linux-x64/tweego`
   - Or update the `TWEEGO_PATH` variable in `build.sh`

## Building the Project

### Using VS Code (Recommended)

1. Open the project in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Run Task" and select "Tasks: Run Task"
4. Choose "Build Story" to build the project

### Using Command Line

```bash
# Build the story
./build.sh

# Start development server
./start.sh
```

## VS Code Integration

### Keyboard Shortcuts

- `Ctrl+Shift+B` (or `Cmd+Shift+B` on Mac): Run Build Task
- `Ctrl+Shift+P` → "Run Task": Select from available tasks

### Debugging

1. Start the development server using the "Start Development Server" task
2. Press `F5` to launch the debugger
3. Choose your preferred browser (Chrome or Firefox)

## Development Workflow

### With File Watching

If you have `inotify-tools` installed:

```bash
npm run watch
```

This will automatically rebuild the story whenever source files change.

### With npm (if Node.js is available)

```bash
# Install dependencies
npm install

# Build
npm run build

# Start server
npm start

# Watch for changes
npm run watch
```

## Troubleshooting

### Tweego not found

- Ensure Tweego is installed and in your PATH
- Or update the `TWEEGO_PATH` variable in `build.sh`

### No .tw files found

- Verify that your story passages are in the `passages/` directory
- Ensure files have the `.tw` extension

### Build fails

- Check that all required files exist
- Verify file permissions (build.sh should be executable)
- Check the error output for specific issues

## Output

The build process creates `tgh-fork.html` in the project root directory, which can be:

- Opened directly in a web browser
- Served using a local development server
- Deployed to a web server

## Customization

You can customize the build process by editing:

- `build.sh`: Main build script
- `start.sh`: Development server startup script
- `.vscode/tasks.json`: VS Code task definitions
- `.vscode/launch.json`: VS Code debug configurations
