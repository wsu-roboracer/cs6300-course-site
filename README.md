# RoboRacer Documentation

This repository contains the source files for [RoboRacer](http://roboracer.ai)'s documentation, written in reStructuredText (reST).

Web browsers cannot display `.rst` files as documentation pages. We use **Sphinx** to build the `.rst` source files into a website.

## Before You Start

Install these programs if they are not already installed:

- [Git](https://git-scm.com/downloads)
- [Python 3](https://www.python.org/downloads/)

On Windows, select **Add Python to PATH** during Python installation.

## Clone the Repository

You may clone this repository using your IDE's **Clone Repository** feature or with Git in a terminal.

This project uses a Git submodule. When using an IDE, enable an option such as **Clone submodules**, **Initialize submodules**, or **Recurse submodules** if it is available.

If you clone with an IDE and it does not initialize submodules, open a terminal in the cloned project folder and run:

```sh
git submodule update --init --recursive
```

To clone from a terminal instead, run:

```sh
git clone --recurse-submodules https://github.com/wsu-roboracer/cs6300-course-site.git
cd cs6300-course-site
```

## Quick Start: Windows (PowerShell)

These instructions work in Windows PowerShell, including terminals opened from Visual Studio, VS Code, Windows Terminal, or another editor.

### 1. Create a Project Python Environment

From the repository root, run:

```powershell
py -3 -m venv .venv
```

This creates a `.venv` folder containing Python packages only for this project. It prevents this project's dependencies from interfering with other Python projects.

You only need to create the virtual environment once.

### 2. Install the Required Packages

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\docs\requirements.txt
```

This installs the exact versions of Sphinx, the Read the Docs theme, and the other extensions used by this documentation project.

### 3. Build the Website

```powershell
.\.venv\Scripts\sphinx-build.exe -M html .\docs .\_build -j auto
```

Sphinx reads the documentation source files from `docs\` and creates the finished website in `_build\html\`.

The first build can take a few minutes.

### 4. Open the Built Website

After the build finishes, open this file in a browser:

```text
_build\html\index.html
```

For example, if the project is on your Desktop, the path may look like:

```text
C:\Users\<your-username>\Desktop\cs6300-course-site\_build\html\index.html
```

### Optional: Run a Local Preview Server

Instead of opening `index.html` directly, you can start a local web server:

```powershell
.\.venv\Scripts\python.exe -m http.server 8001 --directory .\_build\html
```

Then open:

```text
http://127.0.0.1:8001/
```

Leave the terminal open while using the preview server. Press `Ctrl+C` to stop it.

## After You Edit Documentation

1. Save changes to the relevant `.rst` file.
2. Run the **Build the Website** command again.
3. Refresh the browser page.

## Contributing changes

**Pull Requests should use the `main` branch by default. Only make Pull Requests against other branches (e.g. `2.1` or `3.0`) if your changes only apply to that specific version of RoboRacer.**

Though arguably less convenient to edit than a wiki, this git repository is meant to receive pull requests to always improve the documentation, add new pages, etc. Having direct access to the source files in a revision control system is a big plus to ensure the quality of our documentation.

### Editing existing pages

To edit an existing page, locate its .rst source file and open it in your favorite text editor. You can then commit the changes, push them to your fork and make a pull request.

### Adding new pages

To add a new page, create a .rst file with a meaningful name in the section you want to add a file to, e.g. `going_forward/more_cool_stuff.rst`. Write its content like you would do for any other file, and make sure to define a reference name for Sphinx at the beginning of the file (check other files for the syntax), based on the file name with a "doc_" prefix (e.g. `.. _doc_cool_stuff:`).

You should then add your page to the relevant "toctree" (table of contents, e.g. `tutorials/3d/index.rst`). By convention, the files used to define the various levels of toctree are prefixed with an underscore, so in the above example the file should be referenced in `tutorials/3d/_3d_graphics.rst`. Add your new filename to the list on a new line, using a relative path and no extension, e.g. here `light_baking`.

### Sphinx and reStructuredText syntax

Check Sphinx's [reST Primer](https://www.sphinx-doc.org/en/stable/rest.html) and the [official reference](http://docutils.sourceforge.net/rst.html) for details on the syntax.

Sphinx uses specific reST comments to do specific operations, like defining the table of contents (`:toctree:`) or cross-referencing pages. Check the [official Sphinx documentation](https://www.sphinx-doc.org/en/stable/index.html) for more details, or see how things are done in existing pages and adapt it to your needs.

### Adding images and attachments

To add images, please put them in an `img/` folder next to the .rst file with a meaningful name and include them in your page with:

```rst
.. image:: img/image_name.png
```

Similarly, you can include attachments (like assets as support material for a tutorial) by placing them into a `files/` folder next to the .rst file, and using this inline markup:

```rst
:download:`myfilename.zip <files/myfilename.zip>`
```

## License

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. To view a copy of this license, visit <https://creativecommons.org/licenses/by-nc-sa/4.0/> or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.