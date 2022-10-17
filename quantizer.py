import glob
import pretty_midi as pm
import pathlib
import sys
import os
from constants import *
from progress import Bar


class Quantize:
    def __init__(
        self,
        IN,
        OUT,
        recursive=False,
        progressbar=False,
    ):
        self.OUT = pathlib.Path(OUT)
        data_dir = pathlib.Path(IN)
        if recursive:
            self.files = glob.glob(str(data_dir / "**/*.mid*"))
        else:
            self.files = glob.glob(str(data_dir / "/*.mid*"))

    def quantize(self, note_type, stats=False):
        self.len_diff = []
        bar = Bar("Quantizing Midi files", len(self.files))
        for file_path in self.files:
            pfile = pm.PrettyMIDI(file_path)
            for instrument in pfile.instruments:
                program = instrument.program
                self._quantize(pfile, note_type, program)
            self.save(file_path, pfile)
            bar.update()
        if stats:
            self.stats()

    def stats(self):
        average_duration_difference = sum(self.len_diff) / len(self.len_diff)
        min_duration_difference = min(self.len_diff)
        max_duration_difference = max(self.len_diff)
        total_notes = len(self.len_diff)
        print("\n")
        print("Average duration difference:", average_duration_difference)
        print("Min duration difference:", min_duration_difference)
        print("Max duration difference:", max_duration_difference)
        print("Notes quantized:", total_notes)

    def save(self, filepath, pfile):
        basename = os.path.basename(filepath)
        if not os.path.exists(self.OUT):
            os.makedirs(self.OUT)

        filepath = str(self.OUT) + "/" + basename + ".mid"
        pfile.write(filepath)

    def steps_per_quarter(self, note_type):
        # Given a invalid note_type is supplied go to default 1/64th note.
        if note_type > NOTE_TYPE_MAX or note_type < 0:
            return STEPS_PER_QUARTER[SIXTY_FOURTH_NOTE]
        return STEPS_PER_QUARTER[note_type]

    # TPQ = Ticks per quater note can be extracted us pfile.resolution
    def steps_per_quarter_to_steps_per_second(self, steps_per_quarter, tempo):
        return steps_per_quarter * tempo / 60

    # The closer too 1 the cutoff is the less wiggle room for notes that start early.
    def quantize_to_step(self, seconds, steps_per_second, cutoff=1):
        steps = seconds * steps_per_second
        return int(steps + (1 - cutoff))

    def quantize_notes(self, notes, tempos, steps_per_quarter):
        tempo_index = 0
        change_time = sys.maxsize
        max_tempo_index = len(tempos[0])
        steps_per_second = 0
        # Set change time if the tempo changes during the track.
        if max_tempo_index > 1:
            change_time = tempos[CHANGE_TIME][tempo_index + 1]
        steps_per_second = self.steps_per_quarter_to_steps_per_second(
            steps_per_quarter, tempos[TEMPO][tempo_index]
        )
        for note in notes:
            # Used to calculate the diffrence between the old and new notes
            old_start = note.start
            old_end = note.end

            if old_start > change_time and tempo_index + 2 < max_tempo_index:
                tempo_index += 1
                change_time = tempos[CHANGE_TIME][tempo_index + 1]
                steps_per_second = self.steps_per_quarter_to_steps_per_second(
                    steps_per_quarter, tempos[TEMPO][tempo_index]
                )
            start = self.quantize_to_step(note.start, steps_per_second)
            end = self.quantize_to_step(note.end, steps_per_second)
            # A note cannot have a duration of zero. This ensures a minimum duration of the note_type.
            if start == end:
                end += 1
            note.start = start / steps_per_second
            note.end = end / steps_per_second
            old_duration = old_end - old_start
            new_duration = note.end - note.start
            if old_duration > new_duration:
                self.len_diff.append(old_duration - new_duration)
            else:
                self.len_diff.append(new_duration - old_duration)

    # Where note type is whole (1), half(2), quarter(3), eigth, sixtenth and so on.
    def _quantize(self, pfile, note_type, instrument):
        steps_per_quarter = self.steps_per_quarter(note_type)
        notes = pfile.instruments[instrument].notes
        self.quantize_notes(notes, pfile.get_tempo_changes(), steps_per_quarter)
