import argparse
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

import kagglehub

DEFAULT_DATASETS = [
    "abdallahalidev/plantvillage-dataset",
    "jay7080dev/rice-plant-diseases-dataset",
    "abdulahad0296/indoor-plant-disease-detection-dataset"
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}


def is_image_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS


def has_image_files(directory: Path) -> bool:
    return any(is_image_file(path) for path in directory.rglob("*"))


def find_dataset_root(path: Path) -> Path | None:
    if path.is_file():
        return None

    # Get subdirectories that contain images
    subdirs_with_images = [child for child in path.iterdir() if child.is_dir() and has_image_files(child)]
    
    # If there are multiple subdirectories with images, this is likely the root of class folders
    if len(subdirs_with_images) > 1:
        return path
    
    # If there is only one subdirectory with images, go deeper to find the actual classes
    if len(subdirs_with_images) == 1:
        nested_root = find_dataset_root(subdirs_with_images[0])
        return nested_root if nested_root else subdirs_with_images[0]
    
    # If this folder contains images directly and no image-containing subdirs, it's the root
    if has_image_files(path):
        return path

    return None


def copy_image_tree(src_dir: Path, dest_dir: Path) -> None:
    for root, _, files in os.walk(src_dir):
        root_path = Path(root)
        target_root = dest_dir / root_path.relative_to(src_dir)
        target_root.mkdir(parents=True, exist_ok=True)

        for file_name in files:
            source_file = root_path / file_name
            if not is_image_file(source_file):
                continue

            destination_file = target_root / source_file.name
            counter = 1
            while destination_file.exists():
                destination_file = target_root / f"{source_file.stem}_{counter}{source_file.suffix}"
                counter += 1

            shutil.copy2(source_file, destination_file)


def download_dataset(dataset_id: str, merged_root: Path) -> None:
    print(f"\nDownloading dataset: {dataset_id}")
    downloaded_path = kagglehub.dataset_download(dataset_id)
    downloaded_path = Path(downloaded_path)
    print(f"Downloaded to: {downloaded_path}")

    if downloaded_path.is_file() and zipfile.is_zipfile(downloaded_path):
        temp_dir = Path(tempfile.mkdtemp(prefix="kaggle_download_"))
        print(f"Extracting zip archive to: {temp_dir}")
        with zipfile.ZipFile(downloaded_path, "r") as zf:
            zf.extractall(temp_dir)
        dataset_root = find_dataset_root(temp_dir)
    else:
        dataset_root = find_dataset_root(downloaded_path)

    if not dataset_root:
        raise RuntimeError(
            "Unable to locate image class folders in the downloaded dataset. "
            "Please inspect the downloaded files and make sure the dataset contains class subdirectories."
        )

    print(f"Using dataset root: {dataset_root}")

    for child in dataset_root.iterdir():
        if not child.is_dir() or not has_image_files(child):
            continue

        dest = merged_root / child.name
        print(f"Copying class folder: {child.name} -> {dest}")
        copy_image_tree(child, dest)

    print(f"Finished importing dataset: {dataset_id}")


def parse_dataset_ids(args: argparse.Namespace) -> list[str]:
    if args.datasets:
        return args.datasets

    env_datasets = os.getenv("KAGGLE_DATASETS")
    if env_datasets:
        return [ds.strip() for ds in env_datasets.split(",") if ds.strip()]

    return DEFAULT_DATASETS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Download Kaggle datasets and merge them into a single training dataset folder."
    )
    parser.add_argument(
        "datasets",
        nargs="*",
        help="Kaggle dataset IDs to download, e.g. jay7080dev/rice-plant-diseases-dataset"
    )
    parser.add_argument(
        "--target-dir",
        default=str(Path(__file__).parent / "dataset" / "merged_dataset"),
        help="Target directory where downloaded class folders will be merged."
    )
    args = parser.parse_args()

    dataset_ids = parse_dataset_ids(args)
    if not dataset_ids:
        raise SystemExit("No Kaggle datasets provided. Use command-line args or KAGGLE_DATASETS environment variable.")

    merged_root = Path(args.target_dir).resolve()
    print(f"Using merged dataset directory: {merged_root}")

    if merged_root.exists():
        print(f"Removing existing merged dataset directory: {merged_root}")
        shutil.rmtree(merged_root)
    merged_root.mkdir(parents=True, exist_ok=True)

    for dataset_id in dataset_ids:
        download_dataset(dataset_id, merged_root)

    print("\nDataset setup complete!")
    print(f"Merged dataset location: {merged_root}")
    print("Update DATASET_DIR to point to this folder, then run 'make train' or 'python backend/model/train_model.py'.")


if __name__ == "__main__":
    main()
