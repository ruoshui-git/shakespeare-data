
import re

if __name__ == "__main__":
    cleaned = []

    lines = open('hamlet_old.txt').read()

    # remove all content in brackets
    lines = re.sub(r'\[[^\]]*\]', '', lines, flags=re.MULTILINE)

    # remove lines that are not important
    for line in lines.splitlines():
        if line.startswith('ACT'):
            pass
        elif line.startswith('Scene '):
            pass
        elif line.startswith('='):
            pass
        else:
            # separate name and script that are on a single line
            if re.match(r'^[A-Z]+$', line):
                cleaned.append(line + ':')
            else:
                match = re.search(r'^([A-Z]+)  (.+)$', line)
                if match:
                    cleaned.append(match.group(1) + ':')
                    cleaned.append(match.group(2))
                else:
                    cleaned.append(line)

    lines = '\n'.join(cleaned)

    # remove extra lines
    while re.search(r'\n{3}', lines):
        lines = re.sub(r'\n{3}', '\n\n', lines)

    with open('hamlet.txt', 'w') as fout:
        fout.write(lines)
