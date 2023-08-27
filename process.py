from typing import List
import glob


class ParsedFile:
    def __init__(self, file_name: str, extract_keys: List[str] = None):
        self.file_name = file_name
        self.headers = {}
        self.rows = []
        self.tmp = {}
        self.extract_keys = [] if extract_keys is None else extract_keys

    def parse(self, line):
        if "header end" in line.lower():
            self.headers = self.tmp
            return

        if "logframe start" in line.lower():
            self.tmp = {}
            return

        if "logframe end" in line.lower()\
                and len(self.tmp) > 0\
                and self.headers != self.tmp:
            self.rows.append(self.tmp)
            self.tmp = {}
            return

        if ":" not in line:
            return

        key, value = line.strip().split(": ")
        if len(self.extract_keys) != 0 and key not in self.extract_keys:
            return

        self.tmp[key.strip()] = value.strip()

    def process(self):
        columns = set(self.headers.keys())
        for row in self.rows:
            for k in row.keys():
                columns.add(k)
        columns = sorted(columns, key=lambda x: int(x not in self.headers))

        res = [",".join(columns)]
        for row in self.rows:
            rs = []
            for cn in columns:
                if cn in self.headers:
                    rs.append(self.headers[cn])
                elif cn in row:
                    rs.append(row[cn])
                else:
                    rs.append("")
            res.append(",".join(rs))
        return "\n".join(res)

    def show(self):
        print(self.process())

    def save(self):
        with open(self.file_name.replace(".txt", ".csv"), "w") as f:
            f.write(self.process())


def main():
    extract_columns = [
        "Subject",
        "Stimulus",
        "Trigger",
        "Language",
        "Equivalent",
        "Response.ACC",
        "Response.RT"
    ]
    for file in glob.glob("*FINAL*.txt"):
        print(f"processing {file}")

        out = ParsedFile(file, extract_columns)
        with open(file, "rb") as f:
            text = f.read().decode('utf-16-le').rstrip('\x00')

        for line in text.split("\n"):
            out.parse(line)
        out.save()


if __name__ == "__main__":
    main()
