import kagglehub
import os
import shutil

def download_dataset():
    print("Starting PlantVillage dataset download via kagglehub...")
    
    # Download latest version
    path = kagglehub.dataset_download("abdallahalidev/plantvillage-dataset")
    
    print(f"Downloaded to: {path}")
    
    # Target directory
    target_dir = os.path.join(os.path.dirname(__file__), "dataset", "plantvillage")
    
    # Create target directory if it doesn't exist
    os.makedirs(os.path.dirname(target_dir), exist_ok=True)
    
    # If it already exists, remove it to ensure a clean copy
    if os.path.exists(target_dir):
        print(f"Removing existing dataset directory: {target_dir}")
        shutil.rmtree(target_dir)
    
    # Move/Copy the dataset to the expected location
    # kagglehub usually returns a path to a folder containing the dataset files
    print(f"Moving dataset to: {target_dir}")
    shutil.copytree(path, target_dir)
    
    print("\nDataset setup complete!")
    print(f"Location: {target_dir}")
    print("You can now run 'make train' to start training.")

if __name__ == "__main__":
    download_dataset()
