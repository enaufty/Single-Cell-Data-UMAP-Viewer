from shiny import App, ui, render, reactive
import os
import zipfile
import tempfile
import scanpy as sc
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import traceback

# Create persistent temp directory (survives reactivity)
TEMP_DIR = tempfile.mkdtemp(prefix="shiny_umap_")
    #Creates a temporary folder to save and use user's values.

print(f"Temp directory created: {TEMP_DIR}")

app_ui = ui.page_fluid(
    ui.h1("🔬Single-Cell UMAP Viewer"),
    ui.p("Upload a ZIP file containing an .h5ad dataset"),

    ui.input_file("file_upload", "Choose ZIP file", accept=[".zip"], multiple=False),
    ui.input_select("color_by", "Color cells by:", choices=["Loading metadata..."], selected=None),

    ui.output_ui("status_box"),
    ui.output_ui("umap_plot"),

    ui.tags.hr(),
    ui.tags.div(
        ui.tags.small("Temp files stored in: ", ui.tags.code(TEMP_DIR)),
        style="color: #666; font-size: 0.8em;"
    )
)
    #This code block creates UI.

def server(input, output, session):
    # Store path to extracted .h5ad file
    h5ad_path = reactive.Value(None)

    # HANDLE FILE UPLOAD & EXTRACTION
    @reactive.Effect
    @reactive.event(input.file_upload)
    def handle_upload():
        file_info = input.file_upload()

        if not file_info:
            h5ad_path.set(None)
            return

        print(f"\n Upload detected: {file_info[0]['name']} ({file_info[0]['size']} bytes)")

        try:
            # Copy from Shiny's temp cache BEFORE it auto deletes
            original_path = file_info[0]["datapath"]
            zip_dest = os.path.join(TEMP_DIR, file_info[0]["name"])

            with open(original_path, "rb") as src, open(zip_dest, "wb") as dst:
                dst.write(src.read())

            print(f"ZIP saved to: {zip_dest}")

            # Unzip
            with zipfile.ZipFile(zip_dest, 'r') as zip_ref:
                zip_ref.extractall(TEMP_DIR)

            # Find .h5ad file
            h5ad_files = [f for f in os.listdir(TEMP_DIR) if f.endswith(".h5ad")] #filter mechanism
            print(f"Found .h5ad files: {h5ad_files}")

            if not h5ad_files:
                raise FileNotFoundError("No .h5ad file found in ZIP archive!")

            extracted_path = os.path.join(TEMP_DIR, h5ad_files[0])
            h5ad_path.set(extracted_path)
            print(f"✅ .h5ad loaded: {extracted_path}")

            # Update color options
            adata = sc.read_h5ad(extracted_path) #Read all .h5ad files and saves into RAM as adata object
            cols = list(adata.obs.columns) #adata.obs = contains cells meta datas
            ui.update_select("color_by", choices=cols, selected=cols[0] if cols else None)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"{error_msg}")
            print(traceback.format_exc())
            h5ad_path.set(None)
            ui.update_select("color_by", choices=[f"ERROR: {str(e)}"])

    # STATUS DISPLAY
    @output
    @render.ui #format of output
    def status_box():
        if not input.file_upload():
            return ui.div("Upload a ZIP file to begin", class_="alert alert-info")

        if h5ad_path():
            return ui.div("File processed successfully!", class_="alert alert-success")
        else:
            return ui.div("Processing failed - check console for errors", class_="alert alert-danger")

    # UMAP PLOT RENDERING
    @output
    @render.ui
    def umap_plot():
        path = h5ad_path()
        if not path:
            return ui.div()

        try:
            print(f"Generating UMAP plot (color by: {input.color_by()})...")
            adata = sc.read_h5ad(path)

            # Compute UMAP if missing
            if 'X_umap' not in adata.obsm:
                print("⚠UMAP coordinates missing - computing now...")
                sc.pp.neighbors(adata, use_rep='X')
                sc.tl.umap(adata)

            # Plot
            fig, ax = plt.subplots(figsize=(10, 8))
            color_var = input.color_by() if input.color_by() in adata.obs.columns else None
            sc.pl.umap(adata, color=color_var, ax=ax, show=False, size=30)
            plt.tight_layout()

            # Convert to base64
            buf = BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
            plt.close(fig)
            buf.seek(0)
            img_base64 = base64.b64encode(buf.read()).decode('utf-8')

            print("UMAP plot rendered successfully")
            return ui.img(src=f"data:image/png;base64,{img_base64}", style="max-width: 100%;")

        except Exception as e:
            print(f"Plot error: {str(e)}")
            print(traceback.format_exc())
            return ui.div(
                f"Plot error: {str(e)}",
                style="color: red; padding: 15px; border: 1px solid #f00; border-radius: 4px;"
            )


app = App(app_ui, server)
