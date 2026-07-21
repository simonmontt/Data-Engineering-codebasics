# StayNest Azure Data Factory Pipeline

## Overview

This project uses Azure Data Factory to move CSV files from the `raw` folder to the `bronze` folder in Azure Storage.

The final metadata-driven pipeline reads the contents of the `raw` folder with a **Get Metadata** activity, loops through the returned `childItems` with a **ForEach** activity, and copies each file to `bronze` using `@item().name`.

Because the file name is passed dynamically, the same pipeline can process any number of files without creating a separate Copy activity for each one.

## Azure Data Factory Objects

### Linked Service

- `ls_staynest_storage`
- Connects Azure Data Factory to the Azure Storage account containing the `staynest` container.

### Datasets

- `ds_source`
  - Delimited-text dataset.
  - Points to the `staynest/raw` folder.
  - Uses the `fileName` parameter for the source file name.

- `ds_sink`
  - Delimited-text dataset.
  - Points to the `staynest/bronze` folder.
  - Uses the `fileName` parameter for the destination file name.

- `ds_raw_folder`
  - Folder-level dataset.
  - Points to `staynest/raw`.
  - Used by Get Metadata to return the folder's `childItems`.

## Pipeline Flow

```text
Get Metadata
    ↓
ForEach file in childItems
    ↓
Copy current file from raw to bronze
```

The ForEach activity uses:

```text
@activity('Get_Raw_Folder_Metadata').output.childItems
```

The Copy activity passes the current file name with:

```text
@item().name
```

## How to Run

1. Open the pipeline in Azure Data Factory Studio.
2. Select **Validate** and confirm there are no errors.
3. Select **Debug**.
4. Wait for the activities to show **Succeeded**.
5. Open the `staynest/bronze` folder in Azure Storage and confirm the CSV files were copied successfully.

The expected files in `bronze` are:

- `hotels.csv`
- `customers.csv`
- `bookings.csv`
