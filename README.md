# Single-Cell-Data-UMAP-Viewer
A lightweight, interactive web application built with Shiny for Python and Scanpy to visualize single-cell transcriptomics data. This tool allows users to upload .h5ad datasets (packaged in ZIP files) and explore cell clusters via UMAP plots directly in the browser.

# Features
-ZIP Upload Support: Automatically extracts and processes .h5ad files from uploaded ZIP archives.

-Dynamic Metadata Selection: Detects available observation metadata (adata.obs) and allows you to recolor the UMAP on the fly.

-Auto-Computation: If your dataset doesn't have UMAP coordinates pre-computed, the app automatically runs sc.pp.neighbors and sc.tl.umap.

-Persistent Temp Storage: Manages a temporary directory for file processing to ensure stability during reactive updates.

# Getting Started
Prerequisites
Ensure you have Python 3.9+ installed. It is recommended to use a virtual environment.
*Installation*
1. Clone the repository:
  git clone https://github.com/enaufty/Single-Cell-Data-UMAP-Viewer.git
cd Single-Cell-Data-UMAP-Viewer
3. Install dependencies:
   pip install shiny scanpy matplotlib

# Running the App
Start the Shiny server by running:
shiny run --reload app.py 
Open your browser to the URL provided in the terminal (usually http://127.0.0.1:8000).

# Workflow
-Upload: Select a .zip file containing a valid .h5ad (AnnData) file.

-Extraction: The app saves the ZIP to a local temporary folder and extracts the contents.

-Processing: Scanpy reads the dataset and identifies metadata columns for the dropdown menu.

-Visualization: Select a metadata category (e.g., 'cell_type' or 'batch') to render the UMAP.
