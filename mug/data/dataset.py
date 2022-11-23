import numpy as np
import torch
import librosa
import soundfile
import sqlite3
import audioread.ffdec
import yaml
from pytorch_lightning import Callback
from torch.utils.data import Dataset

from mug.data.convertor import *
from mug import util


class OsuDataset(Dataset):
    def __init__(self,
                 txt_file,
                 feature_yaml=None,
                 sr=22050,
                 n_fft=2048,
                 max_audio_frame=16384,
                 n_mels=128,
                 mirror_p=0,
                 random_p=0,
                 shift_p=0,
                 feature_dropout_p=0,
                 rate=None,
                 test_txt_file=None,
                 with_audio=False,
                 with_feature=False,
                 cache_dir=None
                 ):
        self.data_paths = txt_file
        with open(self.data_paths, "r", encoding='utf-8') as f:
            self.beatmap_paths = f.read().splitlines()
        random.shuffle(self.beatmap_paths)
        self.beatmap_paths = self.filter_beatmap_paths(self.beatmap_paths)

        self.feature_yaml = None
        self.feature_conn = None
        self.with_feature = with_feature
        self.feature_dropout_p = feature_dropout_p
        if feature_yaml is not None and with_feature:
            self.feature_yaml = yaml.safe_load(open(feature_yaml))
            self.feature_conn = sqlite3.Connection(os.path.join(
                os.path.dirname(txt_file),
                "feature.db"
            ))

        if test_txt_file is not None:
            with open(test_txt_file, "r", encoding='utf-8') as f:
                test_paths = f.read().splitlines()
                self.beatmap_paths = test_paths + self.beatmap_paths

        self.audio_hop_length = n_fft // 4
        self.audio_frame_duration = self.audio_hop_length / sr
        self.convertor_params = {
            "frame_ms": self.audio_frame_duration * 2 * 1000,
            "max_frame": max_audio_frame // 2
        }
        self.mirror_p = mirror_p
        self.random_p = random_p
        self.shift_p = shift_p
        self.with_audio = with_audio
        self.rate = rate
        self.sr = sr
        self.n_mels = n_mels
        self.max_audio_frame = max_audio_frame
        self.n_fft = n_fft
        self.max_duration = self.audio_frame_duration * max_audio_frame
        self.cache_dir = cache_dir
        self.error_audio = []
        if cache_dir is not None:
            os.makedirs(cache_dir, exist_ok=True)
            error_path = os.path.join(self.cache_dir, "error.txt")
            if os.path.isfile(error_path):
                self.error_audio = list(map(lambda x: x.strip(), open(error_path).readlines()))

    def __len__(self):
        return len(self.beatmap_paths)

    def load_audio_wave(self, audio_path, fallback_load_method=None):
        if len(fallback_load_method) == 0:
            raise ValueError(f"Cannot load: {audio_path}")
        try:
            audio = fallback_load_method[0](audio_path)
            y, sr = librosa.load(audio, sr=self.sr, duration=self.max_duration)
            if len(y) == 0:
                raise ValueError("")
            return y, sr
        except:
            return self.load_audio_wave(audio_path, fallback_load_method[1:])

    def load_audio_without_cache(self, audio_path):
        y, sr = self.load_audio_wave(audio_path, [audioread.ffdec.FFmpegAudioFile,
                                                  lambda x: x,
                                                  soundfile.SoundFile
                                                  ])
        y = librosa.feature.melspectrogram(y=y, sr=sr,
                                           n_mels=self.n_mels,
                                           hop_length=self.audio_hop_length,
                                           n_fft=self.n_fft
                                           )
        y = np.log1p(y).astype(np.float16)
        return y

    def load_audio(self, audio_path):
        audio_path = audio_path.strip()
        if self.cache_dir is None:
            return self.load_audio_without_cache(audio_path)
        if audio_path in self.error_audio:
            raise ValueError()
        cache_name = (f"{os.path.basename(os.path.dirname(audio_path))}-"
                      f"{os.path.basename(audio_path)}.npz")
        cache_path = os.path.join(self.cache_dir, cache_name)
        if os.path.isfile(cache_path):
            return np.load(cache_path)['y']

        if not os.path.isfile(audio_path):
            raise ValueError("File not exist: " + audio_path)
        try:
            y = self.load_audio_without_cache(audio_path)
        except:
            self.error_audio.append(audio_path)
            with open(os.path.join(self.cache_dir, "error.txt"), "a+") as f:
                f.write(audio_path + "\n")
            raise
        np.savez_compressed(cache_path, y=y)
        return y

    def load_feature(self, path, dropout_prob=0):
        name = os.path.basename(path)
        set_name = os.path.basename(os.path.dirname(path))
        cursor = self.feature_conn.execute("SELECT * FROM Feature WHERE name = ? AND set_name = ?",
                                           [name, set_name])
        column_names = [description[0] for description in list(cursor.description)]
        result = cursor.fetchone()
        feature_dict = {}
        if result is not None:
            for i in range(len(column_names)):
                if random.random() >= dropout_prob:
                    feature_dict[column_names[i]] = result[i]
        emb_ids = util.feature_dict_to_embedding_ids(feature_dict, self.feature_yaml)
        return emb_ids

    def __getitem__(self, i):
        path = self.beatmap_paths[i]
        convertor_params = self.convertor_params.copy()
        convertor_params["mirror"] = np.random.random() < self.mirror_p
        convertor_params["random"] = np.random.random() < self.random_p
        convertor_params["offset_ms"] = 0
        convertor_params["rate"] = 1.0
        if self.rate is not None:
            assert not self.with_audio, "Cannot change audio rate currently!"
            convertor_params["rate"] = np.random.random() * (self.rate[1] - self.rate[0]) + \
                                       self.rate[0]
        if np.random.random() < self.shift_p:
            assert not self.with_audio, "Cannot shift audio currently!"
            convertor_params["offset_ms"] = random.randint(0, int(convertor_params["max_frame"] *
                                                                  convertor_params["frame_ms"] / 2))
        try:
            objs, beatmap_meta = parse_osu_file(path, convertor_params)
            obj_array, valid_flag = beatmap_meta.convertor.objects_to_array(objs, beatmap_meta)
            example = {
                "meta": beatmap_meta.for_batch(),
                "convertor": convertor_params,
                "note": obj_array,
                "valid_flag": valid_flag
            }
            if self.with_audio:
                audio = self.load_audio(beatmap_meta.audio).astype(np.float32)
                t = audio.shape[1]
                if t < self.max_audio_frame:
                    audio = np.concatenate([
                        audio,
                        np.zeros(self.n_mels, self.max_audio_frame - t)
                    ], axis=1)
                elif t > self.max_audio_frame:
                    audio = audio[:, :self.max_audio_frame]
                example["audio"] = audio
            if self.with_feature:
                example["feature"] = self.load_feature(beatmap_meta.path, self.feature_dropout_p)
            return example
        except:
            # raise
            return self.__getitem__(random.randint(0, len(self.beatmap_paths) - 1))

    def filter_beatmap_paths(self, beatmap_paths):
        return beatmap_paths


class OsuTrainDataset(OsuDataset):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def filter_beatmap_paths(self, beatmap_paths):
        return beatmap_paths[:int(len(beatmap_paths) * 0.8)]


class OsuValidDataset(OsuDataset):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def filter_beatmap_paths(self, beatmap_paths):
        return beatmap_paths[int(len(beatmap_paths) * 0.8):]


class BeatmapLogger(Callback):
    def __init__(self, log_batch_idx, count, splits=None, log_images_kwargs=None):
        super().__init__()
        self.log_batch_idx = log_batch_idx
        self.splits = splits
        self.count = count
        if log_images_kwargs is None:
            log_images_kwargs = {}
        self.log_images_kwargs = log_images_kwargs

    def log_img(self, pl_module, batch, batch_idx, split="train"):
        if batch_idx not in self.log_batch_idx:
            return
        if split not in self.splits:
            return
        if not hasattr(pl_module, "log_beatmap") or not callable(pl_module.log_beatmap):
            return
        is_train = pl_module.training
        if is_train:
            pl_module.eval()

        pl_module.log_beatmap(batch, split=split, count=self.count, **self.log_images_kwargs)

        if is_train:
            pl_module.train()

    def on_train_batch_end(self, trainer, pl_module, outputs, batch, batch_idx, *args, **kwarg):
        self.log_img(pl_module, batch, batch_idx, split="train")

    def on_validation_batch_end(self, trainer, pl_module, outputs, batch, batch_idx,
                                *args, **kwarg):
        self.log_img(pl_module, batch, batch_idx, split="val")

    def on_train_epoch_start(self, trainer, pl_module):
        torch.cuda.empty_cache()


if __name__ == '__main__':
    from tqdm import tqdm

    os.makedirs(os.path.join("data", "audio_cache_log_16"), exist_ok=True)
    base = (os.path.join("data", "audio_cache"))
    for name in tqdm(os.listdir(base)):
        if name.endswith("npz"):
            y = np.load(os.path.join(base, name))['y']
            y = np.log1p(y).astype(np.float16)
            np.savez_compressed(os.path.join(os.path.join("data", "audio_cache_log_16"), name), y=y)
