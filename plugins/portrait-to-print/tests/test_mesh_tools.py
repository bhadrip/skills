"""Synthetic-only mesh tests. No portrait assets or retained output fixtures."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import trimesh

SCRIPT = Path(__file__).resolve().parents[1] / "skills/portrait-to-print/scripts/mesh_tools.py"
SPEC = importlib.util.spec_from_file_location("mesh_tools", SCRIPT)
mesh_tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mesh_tools)


class MeshToolsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="mesh-tools-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "synthetic-box.stl"
        self.mesh = trimesh.creation.box(extents=[2, 3, 4])
        self.mesh.apply_translation([3, -2, 9])
        self.mesh.export(self.source)
        self.source_hash = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], text=True, capture_output=True, check=False)

    def assert_source_unchanged(self):
        self.assertEqual(self.source_hash, hashlib.sha256(self.source.read_bytes()).hexdigest())

    def test_valid_check_and_expected_height(self):
        out = self.root / "check.json"
        result = self.cli("check", "--input", self.source, "--out", out, "--expected-height-mm", 4)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(out.read_text())
        self.assertTrue(report["input_check"]["structural_gate_passed"])
        self.assertEqual(report["input_check"]["component_count"], 1)
        self.assertEqual(report["input_check"]["intersection_check"]["status"], "not_checked")
        self.assertTrue(report["source_unchanged"])
        self.assert_source_unchanged()

    def test_prepare_reimport_uniform_scale_and_grounding(self):
        out = self.root / "prepared.stl"
        result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", 40)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(Path(str(out) + ".json").read_text())
        loaded, _ = mesh_tools.load_stl_exact(out)
        np.testing.assert_allclose(loaded.extents, [20, 30, 40], atol=1e-5)
        self.assertAlmostEqual(loaded.bounds[0, 2], 0, places=6)
        # No hidden centering or camera/orientation inference.
        np.testing.assert_allclose(loaded.centroid[:2], self.mesh.centroid[:2] * 10)
        self.assertTrue(report["reimport_verified"])
        self.assertTrue(report["output_check"]["structural_gate_passed"])
        self.assert_source_unchanged()

    def test_open_shell_not_repaired_or_published(self):
        mesh = trimesh.Trimesh(self.mesh.vertices, self.mesh.faces[:-1], process=False)
        mesh.export(self.source)
        original = self.source.read_bytes()
        out = self.root / "should-not-exist.stl"
        result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", 20)
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(Path(str(out) + ".json").read_text())
        self.assertIn("not_watertight", report["input_check"]["failure_reasons"])
        self.assertFalse(report["input_check"]["components"][0]["watertight"])
        self.assertFalse(out.exists())
        self.assertEqual(original, self.source.read_bytes())

    def test_multiple_components_reported_not_discarded(self):
        second = self.mesh.copy()
        second.apply_translation([10, 0, 0])
        trimesh.util.concatenate([self.mesh, second]).export(self.source)
        out = self.root / "multiple.json"
        result = self.cli("check", "--input", self.source, "--out", out)
        self.assertEqual(result.returncode, 1)
        report = json.loads(out.read_text())["input_check"]
        self.assertEqual(report["component_count"], 2)
        self.assertEqual(len(report["components"]), 2)
        self.assertEqual(report["triangles"], 24)

    def test_reverse_winding_is_not_silently_fixed(self):
        inverted = self.mesh.copy()
        inverted.invert()
        inverted.export(self.source)
        out = self.root / "inverted.json"
        result = self.cli("check", "--input", self.source, "--out", out)
        self.assertEqual(result.returncode, 1)
        report = json.loads(out.read_text())["input_check"]
        self.assertLess(report["signed_volume_mm3"], 0)
        self.assertIn("nonpositive_or_nonfinite_signed_volume", report["failure_reasons"])

    def test_duplicate_and_degenerate_triangles_are_detected(self):
        faces = np.vstack([self.mesh.faces, self.mesh.faces[:1], [0, 0, 1]])
        mesh = trimesh.Trimesh(self.mesh.vertices, faces, process=False)
        report = mesh_tools.inspect_mesh(mesh)
        self.assertEqual(report["duplicate_triangles_ignoring_winding"], 1)
        self.assertEqual(report["degenerate_triangles_area_le_1e_12_mm2"], 1)
        self.assertFalse(report["structural_gate_passed"])

    def test_unreferenced_and_nonfinite_vertices(self):
        unreferenced = trimesh.Trimesh(np.vstack([self.mesh.vertices, [100, 100, 100]]), self.mesh.faces, process=False)
        report = mesh_tools.inspect_mesh(unreferenced)
        self.assertEqual(report["unreferenced_vertices"], 1)
        invalid = self.mesh.copy()
        invalid.vertices[0, 0] = np.nan
        report = mesh_tools.inspect_mesh(invalid, intersections=True)
        self.assertIn("nonfinite_vertices", report["failure_reasons"])
        self.assertEqual(report["intersection_check"]["status"], "not_run_invalid_geometry")
        json.dumps(report, allow_nan=False)

    def test_nonfinite_stl_not_silently_cleaned_by_loader(self):
        invalid = self.mesh.copy()
        invalid.vertices[0, 0] = np.nan
        invalid.export(self.source)
        original = self.source.read_bytes()
        out = self.root / "nonfinite.json"
        result = self.cli("check", "--input", self.source, "--out", out)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("nonfinite_vertices", json.loads(out.read_text())["input_check"]["failure_reasons"])
        self.assertEqual(original, self.source.read_bytes())

    def test_malformed_stl_returns_operational_error(self):
        self.source.write_bytes(b"not an STL file")
        out = self.root / "malformed.json"
        result = self.cli("check", "--input", self.source, "--out", out)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("error", json.loads(result.stderr))

    def test_exact_indexing_does_not_weld_a_small_gap(self):
        triangles = self.mesh.vertices[self.mesh.faces].copy()
        triangles[0, 0, 0] += 1e-5
        mesh = trimesh.Trimesh(triangles.reshape(-1, 3), np.arange(triangles.size // 3).reshape(-1, 3), process=False)
        mesh.export(self.source)
        loaded, _ = mesh_tools.load_stl_exact(self.source)
        report = mesh_tools.inspect_mesh(loaded)
        self.assertFalse(report["watertight"])

    def test_wrong_expected_height_returns_validation_failure(self):
        out = self.root / "wrong-height.json"
        result = self.cli("check", "--input", self.source, "--out", out, "--expected-height-mm", 99)
        self.assertEqual(result.returncode, 1)
        self.assertIn("unexpected_height", json.loads(out.read_text())["input_check"]["failure_reasons"])

    def test_invalid_heights_rejected_before_writing(self):
        for value in ["0", "-1", "nan", "inf", "not-a-number"]:
            with self.subTest(value=value):
                out = self.root / "invalid.stl"
                result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", value)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(out.exists())
        self.assert_source_unchanged()

    def test_overwrites_and_input_as_output_rejected(self):
        existing = self.root / "existing.stl"
        existing.write_bytes(b"keep this exact content")
        result = self.cli("prepare", "--input", self.source, "--out", existing, "--height-mm", 40)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(existing.read_bytes(), b"keep this exact content")
        result = self.cli("prepare", "--input", self.source, "--out", self.source, "--height-mm", 40)
        self.assertEqual(result.returncode, 2)
        out = self.root / "new.stl"
        Path(str(out) + ".json").write_text("keep report")
        result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", 40)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(out.exists())
        self.assert_source_unchanged()

    def test_dangling_output_symlink_rejected(self):
        out = self.root / "link.stl"
        try:
            out.symlink_to(self.root / "missing.stl")
        except OSError:
            self.skipTest("Symlinks not available")
        result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", 40)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(out.is_symlink())
        self.assertFalse((self.root / "missing.stl").exists())

    def test_report_cannot_alias_new_mesh_output(self):
        out = self.root / "new.stl"
        child = self.root / "directory"
        child.mkdir()
        report_alias = child / ".." / "new.stl"
        result = self.cli("prepare", "--input", self.source, "--out", out, "--height-mm", 40, "--report", report_alias)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(out.exists())

    @unittest.skipUnless(importlib.util.find_spec("pymeshlab"), "Optional PyMeshLab is not installed")
    def test_optional_intersection_check_on_synthetic_box(self):
        report = mesh_tools.inspect_mesh(self.mesh, intersections=True)
        self.assertEqual(report["intersection_check"]["status"], "checked")
        self.assertEqual(report["intersection_check"]["flagged_faces"], 0)
        self.assertIn("coplanar", report["intersection_check"]["caveat"])

    @unittest.skipUnless(importlib.util.find_spec("pymeshlab"), "Optional PyMeshLab is not installed")
    def test_optional_intersection_flags_reject_overlapping_boxes(self):
        other = self.mesh.copy()
        other.apply_translation([0.7, 0.6, 0.8])
        mesh = trimesh.util.concatenate([self.mesh, other])
        report = mesh_tools.inspect_mesh(mesh, intersections=True)
        self.assertGreater(report["intersection_check"]["flagged_faces"], 0)
        self.assertIn("self_intersection_flags", report["failure_reasons"])
        self.assertFalse(report["structural_gate_passed"])


if __name__ == "__main__":
    unittest.main()
