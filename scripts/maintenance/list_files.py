import os

def list_all_files(directory='.', exclude_dirs=['.git']):
    all_files = []
    for root, dirs, files in os.walk(directory):
        # 排除指定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)

    return sorted(all_files)

if __name__ == "__main__":
    files = list_all_files()
    for file in files:
        print(file)
