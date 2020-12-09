import shutil
from pathlib import Path
import re
from re import U
from sys import prefix, stderr
from typing import Iterator, List, Optional, Union
import fire


def _next_line(lines: Iterator[str]) -> str:
    return next(lines).rstrip()


class SPPlay:
    '''Parse and clean a Shakespeare play

    The plays are taken from Folger in txt fromat
    '''

    ACT_HEADER = re.compile(r'ACT \d')
    ACTORS_HEADER = 'Characters in the Play'

    title_section: List[str]
    '''Does not include header "Characters in the Play"'''
    actors_section: List[str]
    '''Does not include header like "ACT 1"'''
    acts: List[str]

    def __init__(self, path: Path) -> None:
        '''Read and parse a play from `path`'''

        self.title_section = []
        self.actors_section = [self.ACTORS_HEADER]
        self.acts = []

        with path.open('r', encoding='utf-8') as f:
            lines = iter(f)

            while (line := _next_line(lines)) != self.ACTORS_HEADER:
                self.title_section.append(line)

            while not self.ACT_HEADER.match(line := _next_line(lines)):
                self.actors_section.append(line)

            # lines like "ACT 1" are discarded

            current_act = []
            for line in lines:
                # here we strip() instead of rstrip() so spacing on left is preserved
                line = line.rstrip()
                if not self.ACT_HEADER.match(line):
                    current_act.append(line)
                else:
                    assert len(current_act) > 0, 'error: current act is empty'
                    self.acts.append('\n'.join(current_act))
                    current_act = []

            # one more act left
            self.acts.append('\n'.join(current_act))

    def __repr__(self) -> str:
        return f'Shakespeare play {self.title_section[0]} with {len(self.acts)} acts'

    @staticmethod
    def process_act(act: str) -> List[str]:
        """
        Returns the lines with actor names formatted

        For now, the function will

        - separate name and script that are on a single line, and add ":" after the name
          For example: 
            ```
            BERTRAM  His good remembrance, sir,
            ```
            becomes
            ```
            BERTRAM:
            His good remembrance, sir,
            ```

            Examples to consider:

            - COUNTESS (regular, add ":")
            - FIRST LORD (two words)

            - HELEN  Do not you love him, madam? (regular, mixed line)
            - HELEN, [kneeling]  Then I confess (comma after name)
            - 

            Weird edge case:
                "I, after him, do after him wish too," (1 char CAP word)
        """

        # remove all content in brackets
        # act = re.sub(r'\[[^\]]*\]', '', act, flags=re.MULTILINE)

        fmtted = []
        for line in act.splitlines():

            # Each name should have >=2 chars
            if re.match(r'^(?:[A-Z]{2,}| )+$', line):
                fmtted.append(line.rstrip() + ':')
            else:
                # comma is discarded
                if (match := re.search(r'^(?P<name>(?:[A-Z]{2,}| )+),?(?P<line>.+)$', line)):
                    fmtted.append(match.group('name').rstrip() + ':')
                    fmtted.append(match.group('line'))

                else:
                    fmtted.append(line)
        return fmtted

    @staticmethod
    def _strip_folger_info(text: str) -> str:
        return re.subn(r'Edited by.+?version (?:\d\.)+\d[\n]', '', text, 1, re.DOTALL)[0]

    def get_fmtted_text(self, prefix_id: Optional[int] = None, strip_play_header=True, strip_actor_list=True, strip_folger_info=True) -> str:
        '''Return the formatted play text

        `prefix_id`: prefix an id to every line of the play, like: "2024|Text text text"
                    If given int, prefix int. Do not append if no id is provided.
        '''

        title_section = self.title_section
        actors_section = self.actors_section
        acts = [self.process_act(act) for act in self.acts]

        fmtted: List[str] = []

        if strip_folger_info:
            fmtted.extend(title_section[:2])
        else:
            fmtted.extend(title_section)

        if not strip_actor_list:
            fmtted.extend(actors_section)

        for index, act in enumerate(acts):
            if strip_play_header:
                fmtted.extend(line for line in act if not (
                    re.match(r'Scene \d', line) or line.startswith('=')))
            else:
                fmtted.append(f'ACT {index + 1}')
                fmtted.extend(act)

        if prefix_id is None:
            return '\n'.join(fmtted)
        else:
            return '\n'.join(f'{prefix_id}|{line}' for line in fmtted)


class Main:

    @staticmethod
    def rstrip(dir: Union[str, Path], out_dir_name: Union[str, Path], ending: str = '_TXT_FolgerShakespeare.txt'):
        '''Strip away ending of files in dir, but preserve the suffix.

        By default, strip away _TXT_FolgerShakespeare.txt. So 'hamlet_TXT_FolgerShakespeare.txt' becomes 'hamlet.txt'
        '''
        if not isinstance(dir, Path):
            dir = Path(dir)
        assert dir.is_dir()

        if not isinstance(out_dir_name, Path):
            out_dir_name = Path(out_dir_name)

        renamed = dir.joinpath(out_dir_name)
        renamed.mkdir()

        for path in dir.iterdir():
            if path.name.endswith(ending):
                shutil.copyfile(path.resolve(),
                                renamed.joinpath(
                                    # preserve ending (e.g. '.txt')
                                    path.name.replace(ending, path.suffix)
                ).resolve()
                )

    @staticmethod
    def clean(text: Union[str, Path]) -> str:
        '''Clean metadata specific to folger.'''

        path = Path(text)
        if path.exists():
            text = path

        if isinstance(text, Path):
            assert text.is_file(), 'Only a file can be `clean`ed'
            text = text.read_text()

        return re.subn(r'Edited by.+?(?=\sCharacters in the Play)', '', text, 1, re.DOTALL)[0]

    @staticmethod
    def process(dir: Union[str, Path], out_file: Union[str, Path], startoftext: str = '', endoftext: str = '<|endoftext|>'):
        '''Concatenate all plays in `dir`, wrap in `startoftext` and `endoftext`.

        The content will be `clean`ed before being wrapped in the markers.
        '''
        if not isinstance(dir, Path):
            dir = Path(dir)
        assert dir.is_dir()

        outfile_lines = []
        play_index = []

        for i, file in enumerate(dir.iterdir()):
            # try:
            outfile_lines.append(startoftext)
            play = SPPlay(file)
            title = play.title_section[0]
            play_index.append(title)
            outfile_lines.append(play.get_fmtted_text(prefix_id=i))
            outfile_lines.append(endoftext)
            # except Exception as e:
            #     print(f'error {e} in file {file.name}', file=stderr)

        if not isinstance(out_file, Path):
            out_file = Path(out_file)

        out_file.write_text('\n'.join(outfile_lines), encoding='utf-8')
        print('Name of plays with their ids: ')
        import json
        print(json.dumps(play_index))


if __name__ == "__main__":
    Main.process('shakespeares-works/plays/', 'sp-prefix.txt')
    # fire.Fire(Main)
