from __future__ import annotations

import os


class EasyDirectory:

    def __init__(self, path: str) -> None:
        self.path = path

    def create(self, data: str = '', *path: str) -> str:
        path = os.path.join(self.path, *path)
        folder = os.path.dirname(path)
        os.makedirs(folder, exist_ok=True)

        with open(path, 'w') as file:
            file.write(data)

        return path

    def join(self, *path: str) -> str:
        return os.path.join(self.path, *path)
