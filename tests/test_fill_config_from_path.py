from pathlib import Path
from unittest import TestCase

from nx_config import Config, fill_config, ConfigSection

abs_resources_path = Path(__file__).parent / "resources"
rel_resources_path = abs_resources_path.relative_to(Path.cwd())

expected_valid_extensions = (".yaml", ".yml", ".YAML", ".YML")


class SmallConfig(Config):
    class SmallSection(ConfigSection):
        entry: int = 0

    sec: SmallSection


class TestFillFromPath(TestCase):
    def test_path_is_optional_arg(self):
        cfg = SmallConfig()
        fill_config(cfg)
        self.assertEqual(0, cfg.sec.entry)

    def test_path_is_keyword_only(self):
        with self.assertRaises(TypeError):
            # noinspection PyArgumentList
            fill_config(SmallConfig(), f"{abs_resources_path}/small.yaml")

    def test_accepts_str_and_pathlike(self):
        for p in (
            f"{abs_resources_path}/small.yaml",
            f"{rel_resources_path}/small.yaml",
            abs_resources_path / "small.yaml",
            rel_resources_path / "small.yaml",
        ):
            with self.subTest(path=p):
                cfg = SmallConfig()
                fill_config(cfg, path=p)
                self.assertEqual(42, cfg.sec.entry)

    def test_invalid_extensions(self):
        for p in (
            "invalid.txt",
            "invalid.exe",
            "invalid",
            ".yaml",
            "invalid.yaml.md",
            "invalid.env",
            "invalid.json",
            "invalid.ini",
        ):
            with self.subTest(path=p):
                with self.assertRaises(ValueError) as ctx:
                    fill_config(SmallConfig(), path=p)

                msg = str(ctx.exception)
                self.assertIn(f"'{p}'", msg)
                self.assertIn("extension", msg.lower())
                self.assertIn("support", msg.lower())

                for ext in expected_valid_extensions:
                    self.assertIn(ext, msg)

    def test_valid_extensions(self):
        for dot_ext in expected_valid_extensions:
            with self.subTest(extension=dot_ext):
                cfg = SmallConfig()
                fill_config(cfg, path=rel_resources_path / f"small{dot_ext}")
                self.assertEqual(42, cfg.sec.entry)
