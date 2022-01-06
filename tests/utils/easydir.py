import os


class EasyDirectory:

    def __init__(self, path: str) -> None:
        self.path = path

    def create(self, relpath: str, data: str = '') -> str:
        path = os.path.join(self.path, relpath)
        folder = os.path.dirname(path)
        os.makedirs(folder, exist_ok=True)

        with open(path, 'w') as file:
            file.write(data)

        return path
